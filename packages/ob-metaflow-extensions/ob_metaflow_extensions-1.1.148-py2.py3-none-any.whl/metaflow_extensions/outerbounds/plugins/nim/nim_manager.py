import os, sys, time, json, random, requests, sqlite3
from urllib.parse import urlparse
from metaflow.metaflow_config import SERVICE_URL
from metaflow.metaflow_config_funcs import init_config
from .utilities import get_storage_path
from ..nvcf.nvcf import retry_on_status


NVCF_URL = "https://api.nvcf.nvidia.com"
NVCF_SUBMIT_ENDPOINT = f"{NVCF_URL}/v2/nvcf/pexec/functions"
NVCF_RESULT_ENDPOINT = f"{NVCF_URL}/v2/nvcf/pexec/status"
NVCF_POLL_INTERVAL_SECONDS = 1
COMMON_HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "nvcf-feature-enable-gateway-timeout": "true",
}


class NimMetadata(object):
    def __init__(self):
        self._nvcf_chat_completion_models = []
        self._coreweave_chat_completion_models = []

        conf = init_config()

        if "OBP_AUTH_SERVER" in conf:
            auth_host = conf["OBP_AUTH_SERVER"]
        else:
            auth_host = "auth." + urlparse(SERVICE_URL).hostname.split(".", 1)[1]

        nim_info_url = "https://" + auth_host + "/generate/nim"

        if "METAFLOW_SERVICE_AUTH_KEY" in conf:
            headers = {"x-api-key": conf["METAFLOW_SERVICE_AUTH_KEY"]}
            res = requests.get(nim_info_url, headers=headers)
        else:
            headers = json.loads(os.environ.get("METAFLOW_SERVICE_HEADERS"))
            res = requests.get(nim_info_url, headers=headers)

        res.raise_for_status()
        self._ngc_api_key = res.json()["nvcf"]["api_key"]

        for model in res.json()["nvcf"]["functions"]:
            self._nvcf_chat_completion_models.append(
                {
                    "name": model["model_key"],
                    "function-id": model["id"],
                    "version-id": model["version"],
                }
            )
        for model in res.json()["coreweave"]["containers"]:
            self._coreweave_chat_completion_models.append(
                {"name": model["nim_name"], "ip-address": model["ip_addr"]}
            )

    def get_nvcf_chat_completion_models(self):
        return self._nvcf_chat_completion_models

    def get_headers_for_nvcf_request(self):
        return {**COMMON_HEADERS, "Authorization": f"Bearer {self._ngc_api_key}"}


class NimManager(object):
    def __init__(self, models, backend, flow, step_name, monitor, queue_timeout):

        nim_metadata = NimMetadata()
        if backend == "managed":
            nvcf_models = [
                m["name"] for m in nim_metadata.get_nvcf_chat_completion_models()
            ]

            self.models = {}
            for m in models:
                if m in nvcf_models:
                    self.models[m] = NimChatCompletion(
                        model=m,
                        provider="NVCF",
                        nim_metadata=nim_metadata,
                        monitor=monitor,
                        queue_timeout=queue_timeout,
                    )
                else:
                    raise ValueError(
                        f"Model {m} not supported by the Outerbounds @nim offering."
                        f"\nYou can choose from these options: {nvcf_models}\n\n"
                        "Reach out to Outerbounds if there are other models you'd like supported."
                    )
        else:
            raise ValueError(
                f"Backend {backend} not supported by the Outerbounds @nim offering. Please reach out to Outerbounds."
            )


class JobStatus(object):
    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"


class NimChatCompletion(object):
    def __init__(
        self,
        model="meta/llama3-8b-instruct",
        provider="NVCF",
        nim_metadata=None,
        monitor=False,
        queue_timeout=None,
        **kwargs,
    ):
        if nim_metadata is None:
            raise ValueError(
                "NimMetadata object is required to initialize NimChatCompletion object."
            )

        self._nim_metadata = nim_metadata
        self.compute_provider = provider
        self.invocations = []
        self.max_request_retries = int(
            os.environ.get("METAFLOW_EXT_HTTP_MAX_RETRIES", "10")
        )
        self.monitor = monitor

        if self.compute_provider == "NVCF":
            nvcf_model_names = [
                m["name"] for m in self._nim_metadata.get_nvcf_chat_completion_models()
            ]
            self.model = model
            self.function_id = self._nim_metadata.get_nvcf_chat_completion_models()[
                nvcf_model_names.index(model)
            ]["function-id"]
            self.version_id = self._nim_metadata.get_nvcf_chat_completion_models()[
                nvcf_model_names.index(model)
            ]["version-id"]
        else:
            raise ValueError(
                f"Backend compute provider {self.compute_provider} not yet supported for @nim."
            )

        # to know whether to set file_name
        self.first_request = True

        # TODO (Eddie) - this may make more sense in a base class.
        # @nim arch needs redesign if customers start using it in more creative ways.
        self._poll_seconds = "3600"
        self._queue_timeout = queue_timeout
        self._status = None
        self._result = {}

    @property
    def status(self):
        return self._status

    @property
    def has_failed(self):
        return self._status == JobStatus.FAILED

    @property
    def is_running(self):
        return self._status == JobStatus.SUBMITTED

    @property
    def result(self):
        return self._result

    def _log_stats(self, response, e2e_time):
        stats = {}
        if response.status_code == 200:
            stats["success"] = 1
            stats["error"] = 0
        else:
            stats["success"] = 0
            stats["error"] = 1
        stats["status_code"] = response.status_code
        try:
            stats["prompt_tokens"] = response.json()["usage"]["prompt_tokens"]
        except KeyError:
            stats["prompt_tokens"] = None
        try:
            stats["completion_tokens"] = response.json()["usage"]["completion_tokens"]
        except KeyError:
            stats["completion_tokens"] = None
        stats["e2e_time"] = e2e_time
        stats["provider"] = self.compute_provider
        stats["model"] = self.model

        conn = sqlite3.connect(self.file_name)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO metrics (error, success, status_code, prompt_tokens, completion_tokens, e2e_time, model)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    stats["error"],
                    stats["success"],
                    stats["status_code"],
                    stats["prompt_tokens"],
                    stats["completion_tokens"],
                    stats["e2e_time"],
                    stats["model"],
                ),
            )
            conn.commit()
        finally:
            conn.close()

    @retry_on_status(status_codes=[500], max_retries=3, delay=5)
    @retry_on_status(status_codes=[504])
    def __call__(self, **kwargs):

        if self.first_request:
            # Put here to guarantee self.file_name is set after task_id exists.
            from metaflow import current

            self.file_name = get_storage_path(current.task_id)

        request_data = {"model": self.model, **kwargs}
        request_url = f"{NVCF_SUBMIT_ENDPOINT}/{self.function_id}"
        retry_delay = 1
        attempts = 0
        t0 = time.time()
        while attempts < self.max_request_retries:
            try:
                attempts += 1
                response = requests.post(
                    request_url,
                    headers=self._nim_metadata.get_headers_for_nvcf_request(),
                    json=request_data,
                )
                if response.status_code == 202:
                    invocation_id = response.headers.get("NVCF-REQID")
                    self.invocations.append(invocation_id)
                    self._status = JobStatus.SUBMITTED
                elif response.status_code == 200:
                    tf = time.time()
                    if self.monitor:
                        self._log_stats(response, tf - t0)
                    self._status = JobStatus.SUCCESSFUL
                    self._result = response.json()
                    return self._result
                elif response.status_code == 400:
                    self._status = JobStatus.FAILED
                    msg = (
                        "[@nim ERROR] The OpenAI-compatible returned a 400 status code. "
                        + "Known causes include improper requests or prompts with too many tokens for the selected model. "
                        + "Please contact Outerbounds if you need assistance resolving the issue."
                    )
                    print(msg, file=sys.stderr)
                    self._result = {"ERROR": msg}
                    return self._result
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
            ) as e:
                # ConnectionErrors are generally temporary errors like DNS resolution failures,
                # timeouts etc.
                print(
                    "received error of type {}. Retrying...".format(type(e)),
                    e,
                    file=sys.stderr,
                )
                time.sleep(retry_delay)
                retry_delay *= 2  # Double the delay for the next attempt
                retry_delay += random.uniform(0, 1)  # Add jitter
                retry_delay = min(retry_delay, 10)

        def _poll():
            poll_request_url = f"{NVCF_RESULT_ENDPOINT}/{invocation_id}"
            attempts = 0
            retry_delay = 1
            while attempts < self.max_request_retries:
                try:
                    attempts += 1
                    poll_response = requests.get(
                        poll_request_url,
                        headers=self._nim_metadata.get_headers_for_nvcf_request(),
                    )
                    if poll_response.status_code == 200:
                        tf = time.time()
                        self._log_stats(response, tf - t0)
                        self._status = JobStatus.SUCCESSFUL
                        self._result = poll_response.json()
                        return self._result
                    elif poll_response.status_code == 202:
                        self._status = JobStatus.SUBMITTED
                        return 202
                    elif poll_response.status_code == 400:
                        self._status = JobStatus.FAILED
                        msg = (
                            "[@nim ERROR] The OpenAI-compatible API returned a 400 status code. "
                            + "Known causes include improper requests or prompts with too many tokens for the selected model. "
                            + "Please contact Outerbounds if you need assistance resolving the issue."
                        )
                        print(msg, file=sys.stderr)
                        self._result = {"@nim ERROR": msg}
                        return self._result
                except (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.ReadTimeout,
                ) as e:
                    print(
                        "received error of type {}. Retrying...".format(type(e)),
                        e,
                        file=sys.stderr,
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Double the delay for the next attempt
                    retry_delay += random.uniform(0, 1)  # Add jitter
                    retry_delay = min(retry_delay, 10)

        while True:
            data = _poll()
            if data and data != 202:
                return data
            time.sleep(NVCF_POLL_INTERVAL_SECONDS)
