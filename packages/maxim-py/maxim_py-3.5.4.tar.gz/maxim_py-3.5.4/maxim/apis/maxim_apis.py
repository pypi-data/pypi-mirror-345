import contextlib
import json

from typing import Any, Dict, List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from urllib3.util import Retry, Timeout

from maxim.models.prompt import ImageUrls

from ..models import (
    AgentResponse,
    ChatCompletionMessage,
    DatasetEntry,
    DatasetRow,
    Evaluator,
    ExecutePromptForDataResponse,
    ExecuteWorkflowForDataResponse,
    Folder,
    HumanEvaluationConfig,
    PromptResponse,
    RunType,
    TestRun,
    TestRunEntry,
    TestRunResult,
    TestRunStatus,
    TestRunWithDatasetEntry,
    Tool,
    VersionAndRulesWithPromptChainId,
    VersionAndRulesWithPromptId,
)


class ConnectionPool:
    def __init__(self):
        self.session = requests.Session()
        retries = Retry(
            connect=5,
            read=3,
            redirect=1,
            status=3,
            backoff_factor=0.4,
            status_forcelist=frozenset({413, 429, 500, 502, 503, 504}),
        )
        self.http = PoolManager(
            num_pools=2,
            maxsize=3,
            retries=retries,
            timeout=Timeout(connect=10, read=10),
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.session.mount("http://", HTTPAdapter(max_retries=retries))

    @contextlib.contextmanager
    def get_session(self):
        try:
            yield self.session
        finally:
            self.session.close()

    @contextlib.contextmanager
    def get_connection(self):
        try:
            yield self.http
        finally:
            self.http.clear()


class MaximAPI:
    connection_pool: ConnectionPool

    def __init__(self, base_url: str, api_key: str):
        self.connection_pool = ConnectionPool()
        self.base_url = base_url
        self.api_key = api_key

    def __make_network_call(
        self,
        method: str,
        endpoint: str,
        body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> bytes:
        if headers is None:
            headers = {}
        headers["x-maxim-api-key"] = self.api_key
        url = f"{self.base_url}{endpoint}"
        with self.connection_pool.get_session() as session:
            response = session.request(method, url, data=body, headers=headers)
            response.raise_for_status()
            return response.content

    def get_prompt(self, id: str) -> VersionAndRulesWithPromptId:
        try:
            res = self.__make_network_call(
                method="GET", endpoint=f"/api/sdk/v4/prompts?promptId={id}"
            )
            data = json.loads(res.decode())["data"]
            return VersionAndRulesWithPromptId.from_dict(data)
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def get_prompts(self) -> List[VersionAndRulesWithPromptId]:
        try:
            res = self.__make_network_call(method="GET", endpoint="/api/sdk/v4/prompts")
            return [
                VersionAndRulesWithPromptId.from_dict(data)
                for data in json.loads(res)["data"]
            ]
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def getPromptChain(self, id: str) -> VersionAndRulesWithPromptChainId:
        try:
            res = self.__make_network_call(
                method="GET", endpoint=f"/api/sdk/v4/prompt-chains?promptChainId={id}"
            )
            json_response = json.loads(res.decode())
            return VersionAndRulesWithPromptChainId.from_dict(obj=json_response["data"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def get_prompt_chains(self) -> List[VersionAndRulesWithPromptChainId]:
        try:
            res = self.__make_network_call(
                method="GET", endpoint="/api/sdk/v4/prompt-chains"
            )
            json_response = json.loads(res.decode())
            return [
                VersionAndRulesWithPromptChainId.from_dict(elem)
                for elem in json_response["data"]
            ]
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def run_prompt(
        self,
        model: str,
        messages: List[ChatCompletionMessage],
        tools: Optional[List[Tool]] = None,
        **kwargs,
    ):
        try:
            payload: dict[str, Any] = {
                "type": "custom",
                "model": model,
                "messages": messages,
                "tools": tools,
            }
            if kwargs is not None:
                for key, value in kwargs.items():
                    if value is not None:
                        payload[key] = value
            payload = {k: v for k, v in payload.items() if v is not None}
            res = self.__make_network_call(
                method="POST",
                endpoint="/api/sdk/v4/prompts/run",
                body=json.dumps(payload),
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"]["message"])
            return PromptResponse.from_dict(json_response["data"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def run_prompt_version(self, prompt_version_id:str, input:str,image_urls:Optional[List[ImageUrls]], variables:Optional[dict[str, str]])->Optional[PromptResponse]:
        try:
            payload =  {
                "type":"maxim",
                "promptVersionId": prompt_version_id,
                "input": input,
                "imageUrls": image_urls,
                "variables": variables or {},
            }
            payload = {k: v for k, v in payload.items() if v is not None}
            res = self.__make_network_call(
                method="POST",
                endpoint="/api/sdk/v4/prompts/run",
                body=json.dumps(payload),
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"]["message"])
            return PromptResponse.from_dict(json_response["data"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def run_prompt_chain_version(
        self,
        prompt_chain_version_id: str,
        input: str,
        variables: Optional[dict[str, str]],
    ) -> Optional[AgentResponse]:
        try:
            res = self.__make_network_call(
                method="POST",
                endpoint="/api/sdk/v4/agents/run",
                body=json.dumps(
                    {
                        "versionId": prompt_chain_version_id,
                        "input": input,
                        "variables": variables or {},
                    }
                ),
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"]["message"])
            return AgentResponse.from_dict(json_response["data"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def get_folder(self, id: str) -> Folder:
        try:
            res = self.__make_network_call(
                method="GET", endpoint=f"/api/sdk/v3/folders?folderId={id}"
            )
            json_response = json.loads(res.decode())
            if "tags" not in json_response:
                json_response["tags"] = {}
            return Folder.from_dict(json_response["data"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)
    def get_folders(self) -> List[Folder]:
        try:
            res = self.__make_network_call(method="GET", endpoint="/api/sdk/v3/folders")
            json_response = json.loads(res.decode())
            for elem in json_response["data"]:
                if "tags" not in elem:
                    elem["tags"] = {}
            return [Folder.from_dict(elem) for elem in json_response["data"]]
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def add_dataset_entries(
        self, dataset_id: str, dataset_entries: List[DatasetEntry]
    ) -> dict[str, Any]:
        try:
            res = self.__make_network_call(
                method="POST",
                endpoint="/api/sdk/v3/datasets/entries",
                body=json.dumps(
                    {
                        "datasetId": dataset_id,
                        "entries": [entry.to_json() for entry in dataset_entries],
                    }
                ),
            )
            return json.loads(res.decode())
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def get_dataset_total_rows(self, dataset_id: str) -> int:
        try:
            res = self.__make_network_call(
                method="GET",
                endpoint=f"/api/sdk/v1/datasets/total-rows?datasetId={dataset_id}",
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"])
            return json_response["data"]
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def get_dataset_row(self, dataset_id: str, row_index: int) -> Optional[DatasetRow]:
        try:
            res = self.__make_network_call(
                method="GET",
                endpoint=f"/api/sdk/v2/datasets/row?datasetId={dataset_id}&row={row_index}",
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"])
            return DatasetRow.dict_to_class(json_response["data"])
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
        except Exception as e:
            raise Exception(e)

    def get_dataset_structure(self, dataset_id: str) -> Dict[str, str]:
        try:
            res = self.__make_network_call(
                method="GET",
                endpoint=f"/api/sdk/v1/datasets/structure?datasetId={dataset_id}",
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"]["message"])
            return json_response["data"]
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def does_log_repository_exist(self, logger_id: str) -> bool:
        try:
            res = self.__make_network_call(
                method="GET",
                endpoint=f"/api/sdk/v3/log-repositories?loggerId={logger_id}",
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                return False
            return True
        except Exception:
            return False

    def push_logs(self, repository_id: str, logs: str) -> None:
        try:
            res = self.__make_network_call(
                method="POST",
                endpoint=f"/api/sdk/v3/log?id={repository_id}",
                body=logs,
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"]["message"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def fetch_platform_evaluator(self, name: str, in_workspace_id: str) -> Evaluator:
        try:
            res = self.__make_network_call(
                method="GET",
                endpoint=f"/api/sdk/v1/evaluators?name={name}&workspaceId={in_workspace_id}",
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"])
            return Evaluator.dict_to_class(json_response["data"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def create_test_run(
        self,
        name: str,
        workspace_id: str,
        workflow_id: Optional[str],
        prompt_version_id: Optional[str],
        prompt_chain_version_id: Optional[str],
        run_type: RunType,
        evaluator_config: list[Evaluator],
        requires_local_run: bool,
        human_evaluation_config: Optional[HumanEvaluationConfig] = None,
    ) -> TestRun:
        try:
            res = self.__make_network_call(
                method="POST",
                endpoint="/api/sdk/v2/test-run/create",
                body=json.dumps(
                    {
                        k: v
                        for k, v in {
                            "name": name,
                            "workspaceId": workspace_id,
                            "runType": run_type.value,
                            "workflowId": (
                                workflow_id if workflow_id is not None else None
                            ),
                            "promptVersionId": (
                                prompt_version_id
                                if prompt_version_id is not None
                                else None
                            ),
                            "promptChainVersionId": (
                                prompt_chain_version_id
                                if prompt_chain_version_id is not None
                                else None
                            ),
                            "evaluatorConfig": [
                                evaluator.to_dict() for evaluator in evaluator_config
                            ],
                            "requiresLocalRun": requires_local_run,
                            "humanEvaluationConfig": (
                                human_evaluation_config.to_dict()
                                if human_evaluation_config
                                else None
                            ),
                        }.items()
                        if v is not None
                    }
                ),
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"])
            return TestRun.dict_to_class(json_response["data"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def attach_dataset_to_test_run(self, test_run_id: str, dataset_id: str) -> None:
        try:
            res = self.__make_network_call(
                method="POST",
                endpoint="/api/sdk/v1/test-run/attach-dataset",
                body=json.dumps({"testRunId": test_run_id, "datasetId": dataset_id}),
                headers={"Content-Type": "application/json"},
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def push_test_run_entry(
        self,
        test_run: Union[TestRun, TestRunWithDatasetEntry],
        entry: TestRunEntry,
        run_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        try:
            # making sure run_config has not null values
            if run_config is not None:
                run_config = {k: v for k, v in run_config.items() if v is not None}
            res = self.__make_network_call(
                method="POST",
                endpoint="/api/sdk/v1/test-run/push",
                body=json.dumps(
                    {
                        "testRun": test_run.to_dict(),
                        **({"runConfig": run_config} if run_config is not None else {}),
                        "entry": entry.to_dict(),
                    }
                ),
                headers={"Content-Type": "application/json"},
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def mark_test_run_processed(self, test_run_id: str) -> None:
        try:
            res = self.__make_network_call(
                method="POST",
                endpoint="/api/sdk/v1/test-run/mark-processed",
                body=json.dumps({"testRunId": test_run_id}),
                headers={"Content-Type": "application/json"},
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"]["message"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def mark_test_run_failed(self, test_run_id: str) -> None:
        try:
            res = self.__make_network_call(
                method="POST",
                endpoint="/api/sdk/v1/test-run/mark-failed",
                body=json.dumps({"testRunId": test_run_id}),
                headers={"Content-Type": "application/json"},
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"]["message"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def get_test_run_status(self, test_run_id: str) -> TestRunStatus:
        try:
            res = self.__make_network_call(
                method="GET",
                endpoint=f"/api/sdk/v1/test-run/status?testRunId={test_run_id}",
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"])
            status: Dict[str, Any] = {}
            status = json_response["data"]["entryStatus"]
            status["testRunStatus"] = json_response["data"]["testRunStatus"]
            return TestRunStatus.dict_to_class(status)
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def get_test_run_final_result(self, test_run_id: str) -> TestRunResult:
        try:
            res = self.__make_network_call(
                method="GET",
                endpoint=f"/api/sdk/v1/test-run/result?testRunId={test_run_id}",
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"])
            return TestRunResult.dict_to_class(json_response["data"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def execute_workflow_for_data(
        self,
        workflow_id: str,
        data_entry: Dict[str, Union[str, List[str], None]],
        context_to_evaluate: Optional[str] = None,
    ) -> ExecuteWorkflowForDataResponse:
        try:
            res = self.__make_network_call(
                method="POST",
                endpoint="/api/sdk/v1/test-run/execute/workflow",
                body=json.dumps(
                    {
                        "workflowId": workflow_id,
                        "dataEntry": data_entry,
                        "contextToEvaluate": context_to_evaluate,
                    }
                ),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"])
            return ExecuteWorkflowForDataResponse.dict_to_class(json_response["data"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def execute_prompt_for_data(
        self,
        prompt_version_id: str,
        input: str,
        data_entry: Dict[str, Union[str, List[str], None]],
        context_to_evaluate: Optional[str] = None,
    ) -> ExecutePromptForDataResponse:
        try:
            res = self.__make_network_call(
                method="POST",
                endpoint="/api/sdk/v1/test-run/execute/prompt",
                body=json.dumps(
                    {
                        "promptVersionId": prompt_version_id,
                        "input": input,
                        "dataEntry": data_entry,
                        "contextToEvaluate": context_to_evaluate,
                    }
                ),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"])
            return ExecutePromptForDataResponse.dict_to_class(json_response["data"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)

    def execute_prompt_chain_for_data(
        self,
        prompt_chain_version_id: str,
        input: str,
        data_entry: Dict[str, Union[str, List[str], None]],
        context_to_evaluate: Optional[str] = None,
    ) -> ExecutePromptForDataResponse:
        try:
            res = self.__make_network_call(
                method="POST",
                endpoint="/api/sdk/v1/test-run/execute/prompt-chain",
                body=json.dumps(
                    {
                        "promptChainVersionId": prompt_chain_version_id,
                        "input": input,
                        "dataEntry": data_entry,
                        "contextToEvaluate": context_to_evaluate,
                    }
                ),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            json_response = json.loads(res.decode())
            if "error" in json_response:
                raise Exception(json_response["error"])
            return ExecutePromptForDataResponse.dict_to_class(json_response["data"])
        except requests.HTTPError as e:
            if e.response is not None and e.response.json() is not None:
                error = e.response.json()
                raise Exception(error["error"]["message"])
            raise Exception(e)
        except Exception as e:
            raise Exception(e)
