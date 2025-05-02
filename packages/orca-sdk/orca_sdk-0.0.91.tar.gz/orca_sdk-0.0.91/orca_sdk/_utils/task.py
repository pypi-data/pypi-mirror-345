import time

from tqdm.auto import tqdm

from .._generated_api_client.api import abort_task as _abort_task
from .._generated_api_client.api import get_task_status_task
from .._generated_api_client.api import list_tasks as _list_tasks
from .._generated_api_client.models import Task, TaskStatus, TaskStatusInfo

task_config = {
    "retry_interval": 3,
    "show_progress": True,
    "max_wait": 60 * 60,
}


def set_task_config(
    retry_interval: int | None = None,
    show_progress: bool | None = None,
    max_wait: int | None = None,
) -> None:
    if retry_interval is not None:
        task_config["retry_interval"] = retry_interval
    if show_progress is not None:
        task_config["show_progress"] = show_progress
    if max_wait is not None:
        task_config["max_wait"] = max_wait


def wait_for_task(task_id: str, description: str | None = None, show_progress: bool = True) -> None:
    start_time = time.time()
    pbar = None
    steps_total = None
    show_progress = show_progress and task_config["show_progress"]
    while True:
        task_status = get_task_status_task(task_id)

        # setup progress bar if steps total is known
        if task_status.steps_total is not None and steps_total is None:
            steps_total = task_status.steps_total
        if not pbar and steps_total is not None and show_progress:
            pbar = tqdm(total=steps_total, desc=description)

        # return if task is complete
        if task_status.status == TaskStatus.COMPLETED:
            if pbar:
                pbar.update(steps_total - pbar.n)
                pbar.close()
            return

        # raise error if task failed
        if task_status.status == TaskStatus.FAILED:
            raise RuntimeError(f"Task failed with: {task_status.exception}")

        # raise error if task timed out
        if (time.time() - start_time) > task_config["max_wait"]:
            raise RuntimeError(f"Task {task_id} timed out after {task_config['max_wait']}s")

        # update progress bar
        if pbar and task_status.steps_completed is not None:
            pbar.update(task_status.steps_completed - pbar.n)

        # sleep before retrying
        time.sleep(task_config["retry_interval"])


def abort_task(task_id: str) -> TaskStatusInfo:
    _abort_task(task_id)
    return get_task_status_task(task_id)


def list_tasks() -> list[Task]:
    return _list_tasks()
