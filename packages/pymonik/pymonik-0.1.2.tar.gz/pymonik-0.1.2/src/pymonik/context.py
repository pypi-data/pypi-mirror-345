from logging import Logger

from .environment import RuntimeEnvironment
from armonik.worker import TaskHandler


# Tasks can create and upload data without it being a result, or launch new tasks
# They can also get low level information
# Being able to access the working_dir ata
class PymonikContext:
    def __init__(self, task_handler: TaskHandler, logger: Logger):
        self.task_handler = task_handler
        self.logger = logger
        self.live_reporter = None # TODO: Would be nice to support some live mechanism for tasks to report on their progress so you can make decisions mid-computation
        self.environment = RuntimeEnvironment(logger)
