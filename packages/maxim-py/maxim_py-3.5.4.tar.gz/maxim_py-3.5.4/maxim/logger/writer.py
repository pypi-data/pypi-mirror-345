import logging
import os
import re
import tempfile
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from typing import Optional

from ..apis import MaximAPI
from .components.types import CommitLog

maximLogger = logging.getLogger("MaximSDK")


class LogWriterConfig:

    def __init__(
        self,
        base_url,
        api_key,
        repository_id,
        auto_flush=True,
        flush_interval: Optional[int] = 10,
        is_debug=False,
        raise_exceptions=False,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.repository_id = repository_id
        self.auto_flush = auto_flush
        self.flush_interval = flush_interval
        self.is_debug = is_debug
        self.raise_exceptions = raise_exceptions
        maximLogger.setLevel(logging.DEBUG if is_debug else logging.INFO)


class LogWriter:
    def __init__(self, config: LogWriterConfig):
        self.is_running = True
        self.id = str(uuid.uuid4())
        self.config = config
        self.maxim_api = MaximAPI(config.base_url, config.api_key)
        self.queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.max_in_memory_logs = 100
        self.is_debug = config.is_debug
        self.raise_exceptions = config.raise_exceptions
        self.logs_dir = os.path.join(
            tempfile.gettempdir(), f"maxim-sdk/{self.id}/maxim-logs"
        )
        self.__flush_thread = None
        try:
            os.makedirs(self.logs_dir, exist_ok=True)
        except Exception:
            maximLogger.info("Maxim library does not have FS access")
        if self.config.auto_flush:
            if self.config.flush_interval:
                maximLogger.debug(
                    "Starting flush thread with interval {%s} seconds",
                    self.config.flush_interval,
                )
                self.__flush_thread = threading.Thread(target=self.__sync_timer)
                self.__flush_thread.daemon = True
                self.__flush_thread.start()
            else:
                raise ValueError(
                    "flush_interval is set to None.flush_interval has to be a number"
                )

    def __sync_timer(self):
        while self.is_running:
            self.flush()
            if self.config.flush_interval is None:
                raise ValueError(
                    "flush_interval is set to None. flush_interval has to be a number"
                )
            time.sleep(self.config.flush_interval)

    def is_running_on_lambda(self):
        return "AWS_LAMBDA_FUNCTION_NAME" in os.environ

    def write_to_file(self, logs):
        try:
            filename = f"logs-{time.strftime('%Y-%m-%dT%H:%M:%SZ')}.log"
            filepath = os.path.join(self.logs_dir, filename)
            maximLogger.debug(f"Writing logs to file: {filename}")
            with open(filepath, "w") as file:
                for log in logs:
                    file.write(log.serialize() + "\n")
            return filepath
        except Exception as e:
            maximLogger.error(
                f"Failed to write logs to file. We will keep it in memory. Error: {e}"
            )
            if self.raise_exceptions:
                raise e
            return None

    def flush_log_files(self):
        try:
            if not os.path.exists(self.logs_dir):
                return
            files = os.listdir(self.logs_dir)
            for file in files:
                with open(os.path.join(self.logs_dir, file), "r") as f:
                    logs = f.read()
                try:
                    self.maxim_api.push_logs(self.config.repository_id, logs)
                    os.remove(os.path.join(self.logs_dir, file))
                except Exception as e:
                    maximLogger.warn(f"Failed to access filesystem. Error: {e}")
                    if self.raise_exceptions:
                        raise Exception(e)
        except Exception as e:
            maximLogger.warn(f"Failed to access filesystem. Error: {e}")

    def can_access_filesystem(self):
        try:
            return os.access(tempfile.gettempdir(), os.W_OK)
        except Exception:
            return False

    def flush_logs(self, logs):
        try:
            # Pushing old logs first
            if self.can_access_filesystem():
                self.flush_log_files()
            # Pushing new logs
            # Serialize all logs
            serialized_logs = [log.serialize() for log in logs]
            # Maximum size for each batch (5MB)
            MAX_BATCH_SIZE = 5 * 1024 * 1024
            # Split logs into batches to ensure each batch is under 5MB
            current_batch = []
            current_size = 0
            for log_str in serialized_logs:
                # Calculate size of this log plus a newline character
                log_size = len(log_str.encode("utf-8")) + 1
                # If adding this log would exceed the limit, push current batch and start a new one
                if current_size + log_size > MAX_BATCH_SIZE and current_batch:
                    batch_content = "\n".join(current_batch)
                    self.maxim_api.push_logs(self.config.repository_id, batch_content)
                    current_batch = []
                    current_size = 0
                # Add log to current batch
                current_batch.append(log_str)
                current_size += log_size
            # Push any remaining logs
            if current_batch:
                batch_content = "\n".join(current_batch)
                self.maxim_api.push_logs(self.config.repository_id, batch_content)
            maximLogger.debug("Flush complete")
        except Exception as e:
            if self.is_running_on_lambda():
                maximLogger.debug(
                    "As we are running on lamda - we will keep logs in memory for next attempt"
                )
                for log in logs:
                    self.queue.put(log)
                    maximLogger.debug("Logs added back to queue for next attempt")
            else:
                if self.can_access_filesystem():
                    self.write_to_file(logs)
                    maximLogger.warning(
                        f"Failed to push logs to server. Writing logs to file. Error: {e}"
                    )
                else:
                    for log in logs:
                        self.queue.put(log)
                        maximLogger.debug("Logs added back to queue for next attempt")

    def commit(self, log: CommitLog):      
        if not re.match(r'^[a-zA-Z0-9_-]+$', log.entity_id):
            if self.raise_exceptions:
                raise ValueError(f"Invalid ID: {log.entity_id}. ID must only contain alphanumeric characters, hyphens, and underscores. Event will not be logged.")
            # Silently drop the log
            return
        self.queue.put(log)
        if self.queue.qsize() > self.max_in_memory_logs:
            self.flush()

    def flush(self):
        items = []
        while not self.queue.empty():
            items.append(self.queue.get())
        if len(items) == 0:
            self.flush_log_files()
            maximLogger.debug("No logs to flush")
            return
        maximLogger.debug(
            f"Flushing logs to server {time.strftime('%Y-%m-%dT%H:%M:%S')}"
        )
        if self.is_debug:
            for item in items:
                maximLogger.debug(f"{item.serialize()}")
        self.executor.submit(self.flush_logs, items)

    def cleanup(self):
        maximLogger.debug("Cleaning up writer")
        self.is_running = False
        self.flush()
        maximLogger.debug("Waiting for executor to shutdown")
        self.executor.shutdown(wait=True)
        maximLogger.debug("Writer cleanup complete")
