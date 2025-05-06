from functools import partial
from uuid import uuid4
import os, time
from metaflow.decorators import StepDecorator
from metaflow import current

from .nim_manager import NimManager
from .card import NimMetricsRefresher
from .utilities import get_storage_path, NIM_MONITOR_LOCAL_STORAGE_ROOT
from ..card_utilities.async_cards import AsyncPeriodicRefresher
from ..card_utilities.injector import CardDecoratorInjector


class NimDecorator(StepDecorator, CardDecoratorInjector):
    """
    This decorator is used to run NIM containers in Metaflow tasks as sidecars.

    User code call
    -----------
    @nim(
        models=['meta/llama3-8b-instruct', 'meta/llama3-70b-instruct'],
        backend='managed'
    )

    Valid backend options
    ---------------------
    - 'managed': Outerbounds selects a compute provider based on the model.

    Valid model options
    ----------------
        - 'meta/llama3-8b-instruct': 8B parameter model
        - 'meta/llama3-70b-instruct': 70B parameter model
        - any model here: https://nvcf.ngc.nvidia.com/functions?filter=nvidia-functions

    Parameters
    ----------
    models: list[NIM]
        List of NIM containers running models in sidecars.
    backend: str
        Compute provider to run the NIM container.
    queue_timeout : int
        Time to keep the job in NVCF's queue.
    """

    name = "nim"
    defaults = {
        "models": [],
        "backend": "managed",
        "monitor": True,
        "persist_db": False,
        "queue_timeout": 5 * 24 * 3600,  # Default 5 days in seconds
    }

    def step_init(
        self, flow, graph, step_name, decorators, environment, flow_datastore, logger
    ):

        if self.attributes["monitor"]:
            self.attach_card_decorator(
                flow,
                step_name,
                NimMetricsRefresher.CARD_ID,
                "blank",
                refresh_interval=4.0,
            )

        current._update_env(
            {
                "nim": NimManager(
                    models=self.attributes["models"],
                    backend=self.attributes["backend"],
                    flow=flow,
                    step_name=step_name,
                    monitor=self.attributes["monitor"],
                    queue_timeout=self.attributes["queue_timeout"],
                )
            }
        )

    def task_decorate(
        self, step_func, flow, graph, retry_count, max_user_code_retries, ubf_context
    ):
        if self.attributes["monitor"]:

            import sqlite3
            from metaflow import current

            file_path = get_storage_path(current.task_id)
            if os.path.exists(file_path):
                os.remove(file_path)
            os.makedirs(NIM_MONITOR_LOCAL_STORAGE_ROOT, exist_ok=True)
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE metrics (
                    error INTEGER,
                    success INTEGER,
                    status_code INTEGER,
                    prompt_tokens INTEGER,
                    completion_tokens INTEGER,
                    e2e_time NUMERIC,
                    model TEXT
                )
                """
            )

            def _wrapped_step_func(*args, **kwargs):
                async_refresher_metrics = AsyncPeriodicRefresher(
                    NimMetricsRefresher(),
                    updater_interval=4.0,
                    collector_interval=2.0,
                    file_name=file_path,
                )
                try:
                    async_refresher_metrics.start()
                    return step_func(*args, **kwargs)
                finally:
                    time.sleep(5.0)  # buffer for the last update to synchronize
                    async_refresher_metrics.stop()

            return _wrapped_step_func
        else:
            return step_func

    def task_post_step(
        self, step_name, flow, graph, retry_count, max_user_code_retries
    ):
        if not self.attributes["persist_db"]:
            import shutil

            file_path = get_storage_path(current.task_id)
            if os.path.exists(file_path):
                os.remove(file_path)
            # if this task is the last one, delete the whole enchilada.
            if not os.listdir(NIM_MONITOR_LOCAL_STORAGE_ROOT):
                shutil.rmtree(NIM_MONITOR_LOCAL_STORAGE_ROOT, ignore_errors=True)
