from ...Application.DTO.Repository.model_user import User, Permissions, Scope
from abc import ABCMeta, abstractmethod


class BaseManagerContextFWDI(metaclass=ABCMeta):
     
     @abstractmethod
     def get_metadata_user(self) -> User:
          pass

     @abstractmethod
     def get_metadata_permission(self) -> Permissions:
          pass

     @abstractmethod
     def get_metadata_scopes(self) -> Scope:
          pass