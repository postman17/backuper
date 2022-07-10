from abc import ABC, abstractmethod


class AbstractClientManager(ABC):
    @property
    @abstractmethod
    def auth_type(self):
        pass

    @property
    @abstractmethod
    def client_name(self):
        pass

    @property
    @abstractmethod
    def create_client_action_method(self):
        pass

    @property
    @abstractmethod
    def create_client_action_method_fields(self):
        pass

    @property
    @abstractmethod
    def create_client_form(self):
        pass

    @abstractmethod
    def create_client_form_help_text(self):
        pass

    @property
    @abstractmethod
    def backup_method(self):
        pass

    @property
    @abstractmethod
    def backup_method_fields(self):
        pass

    @property
    @abstractmethod
    def is_local(self):
        pass
