from .Usecase.user_repository import UserRepositoryFWDI

from ..Application.TaskManager.task_queue_manager import TaskQueueManager
from ..Application.TaskCallback.task_callback_handler import TaskCallbackHandler

from ..Application.Abstractions.base_task_callback_handler import BaseTaskCallbackHandler
from ..Application.Abstractions.base_task_queue_manager import BaseTaskQueueManager
from ..Application.Abstractions.base_user_repository import BaseUserRepositoryFWDI
from ..Application.Abstractions.base_service_collection import BaseServiceCollectionFWDI

class DependencyInjection():

    @staticmethod
    def AddApplication(services:BaseServiceCollectionFWDI)->None:
        services.AddTransient(BaseUserRepositoryFWDI, UserRepositoryFWDI)
        services.AddSingleton(BaseTaskQueueManager, TaskQueueManager)
        services.AddTransient(BaseTaskCallbackHandler, TaskCallbackHandler)