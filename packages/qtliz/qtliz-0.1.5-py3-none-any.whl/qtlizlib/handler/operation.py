import time
from abc import abstractmethod
from enum import Enum
from typing import Protocol, TypeVar, Callable

from PySide6.QtCore import QThreadPool, QRunnable
from pylizlib.data import datautils
from pylizlib.domain.queueProgress import QueueProgress, QueueProgressMode

from qtlizlib.util.qtlizLogger import logger

T = TypeVar("T")


class OperationStatus(Enum):
    Pending = "Pending"
    InProgress = "In Progress"
    Completed = "Completed"
    Failed = "Failed"


class OperationType(Enum):
    DownloadRequest = "Download Request"
    DevDebug = "Dev Debug"
    Test = "Test"


class RunnerInteraction(Protocol):
    def on_runner_start(self): ...
    def on_runner_finish(self): ...
    def on_runner_stop(self): ...
    def on_runner_update_progress(self, progress: int): ...

    def on_op_start(self): ...
    def on_op_update_status(self, status: OperationStatus): ...
    def on_op_update_progress(self, progress: int): ...
    def on_op_finished(self): ...

    def on_task_start(self, task_name: str): ...
    def on_task_update_status(self, task_name: str, status: OperationStatus): ...
    def on_task_update_progress(self, task_name: str, progress: int): ...
    def on_task_finished(self, task_name: str): ...


class Task:

    def __init__(
            self,
            name: str,
            on_progress_changed: Callable[[str, int], None],
            abort_all_on_error: bool = True,
            interaction: RunnerInteraction | None = None
    ):
        self.interaction = interaction
        self.name = name
        self.abort_all_on_error = abort_all_on_error
        self.status = OperationStatus.Pending
        self.on_progress_changed = on_progress_changed

        self.progress = 0

    def execute(self):
        pass

    def update_task_status(self, status: OperationStatus):
        logger.debug("Updating task \"%s\" status: %s", self.name, status)
        self.status = status
        self.interaction.on_task_update_status(self.name, status) if self.interaction else None

    def update_task_progress(self, progress: int):
        logger.debug("Updating task \"%s\" progress: %s", self.name, progress)
        self.progress = progress
        self.interaction.on_task_update_progress(self.name, progress) if self.interaction else None
        self.on_progress_changed(self.name, progress)


class Operation(QRunnable):

    def __init__(
            self,
            tasks: list[Task],
            op_type: OperationType,
            interaction: RunnerInteraction | None = None
    ):
        super().__init__()
        self.id = datautils.gen_random_string(10)
        self.type = op_type
        self.status = OperationStatus.Pending

        self.tasks = tasks
        self.progress = 0
        self.progress_obj = QueueProgress(QueueProgressMode.SINGLE, len(tasks))
        self.interaction = interaction
        self.finished_callback: Callable | None = None
        self.op_progress_update_callback: Callable | None = None

        for task in tasks:
            self.progress_obj.add_single(task.name)


    def execute_tasks(self):
        for task in self.tasks:
            try:
                task.update_task_status(OperationStatus.InProgress)
                logger.debug("Executing task: %s", task.name)
                task.execute()
                task.update_task_status(OperationStatus.Completed)
            except Exception as e:
                task.update_task_status(OperationStatus.Failed)
                logger.error("Error in task %s: %s", task.name, e)
                if task.abort_all_on_error:
                    raise RuntimeError(f"Task {task.name} failed: {e}")
            finally:
                pass


    def execute(self):
        try:
            self.set_operation_started()
            self.update_op_status(OperationStatus.InProgress)
            self.execute_tasks()
            self.update_op_status(OperationStatus.Completed)
        except Exception as e:
            self.update_op_status(OperationStatus.Failed)
            logger.error("Error in operation: %s", e)
        finally:
            self.set_operation_finished()


    def on_task_progress_update(self, task_name: str, progress: int):
        self.progress_obj.set_single_progress(task_name, progress)
        self.update_op_progress(self.progress_obj.get_total_progress())


    @abstractmethod
    def stop(self):
        pass

    def get_tasks_ids(self) -> list[str]:
        return [task.name for task in self.tasks]

    def update_op_status(self, status: OperationStatus):
        logger.debug("Updating operation status: %s", status)
        self.status = status
        self.interaction.on_op_update_status(status) if self.interaction else None

    def update_op_progress(self, progress: int):
        logger.debug("Updating operation progress: %s", progress)
        self.progress = progress
        self.interaction.on_op_update_progress(progress) if self.interaction else None
        self.op_progress_update_callback(self.id, self.progress) if self.op_progress_update_callback else None

    def set_finished_callback(self, callback: Callable):
        self.finished_callback = callback

    def set_op_progress_callback(self, callback: Callable):
        self.op_progress_update_callback = callback

    def set_operation_started(self):
        logger.info("Starting operation %s", self.id)
        self.interaction.on_op_start() if self.interaction else None

    def set_operation_finished(self):
        logger.info("Finishing operation %s", self.id)
        if self.finished_callback:
            self.finished_callback()
        self.interaction.on_op_finished() if self.interaction else None





class OperationRunner:

    def __init__(
            self,
            interaction: RunnerInteraction,
            max_threads: int = 1,
    ):
        self.interaction = interaction
        self.max_threads = max_threads
        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(self.max_threads)
        self.operation_pool: list[Operation] = []
        self.active_operations = 0
        self.progress_obj: QueueProgress | None = None


    def add(self, operation: Operation):
        self.operation_pool.append(operation)

    def start(self):
        self.interaction.on_runner_start()
        self.progress_obj = QueueProgress(QueueProgressMode.SINGLE, len(self.operation_pool))
        for op in self.operation_pool:
            self.progress_obj.add_single(op.id)
        for op in self.operation_pool:
            self.__start_next_operation()

    def stop(self):
        self.interaction.on_runner_stop()
        self.thread_pool.waitForDone()
        self.active_operations = 0
        self.operation_pool.clear()

    def __start_next_operation(self):
        can_start = self.active_operations < self.thread_pool.maxThreadCount()
        if can_start and self.operation_pool:
            op = self.operation_pool.pop(0)
            op.set_finished_callback(lambda: self.on_operation_finished(op))
            op.set_op_progress_callback(self.on_op_progress_update)
            self.thread_pool.start(op)
            self.active_operations += 1

    def on_operation_finished(self, item):
        self.active_operations -= 1
        self.__start_next_operation()
        if self.active_operations == 0 and not self.operation_pool:
            time.sleep(1)
            self.interaction.on_runner_finish()

    def on_op_progress_update(self, op_id: str, op_progress: int):
        self.progress_obj.set_single_progress(op_id, op_progress)
        self.interaction.on_runner_update_progress(self.progress_obj.get_total_progress())
