from abc import ABC, abstractmethod


class AbstractClientManager(ABC):
    """Abstract manager class.
    Implements required attributes
    """
    @property
    @abstractmethod
    # Client name (Enum)
    def client_name(self):
        pass

    @property
    @abstractmethod
    # Manager action method in creating client
    def create_client_action_method(self):
        pass

    @property
    @abstractmethod
    # Form for creating a client
    def create_client_action_method_fields(self):
        pass

    @property
    @abstractmethod
    # Form for creating a client
    def create_client_form(self):
        pass

    @abstractmethod
    # Create client help text
    def create_client_form_help_text(self):
        pass

    @property
    @abstractmethod
    # Backup method name
    def backup_method(self):
        pass

    @property
    @abstractmethod
    # Fields for passing in backup method
    def backup_method_fields(self):
        pass

    @property
    @abstractmethod
    # Run create container before or after backup manager method
    def create_container_handle(self):
        pass

    @property
    @abstractmethod
    # After backup do action method name
    def after_action_method_name(self):
        pass

    @property
    @abstractmethod
    # Delete file method name
    def delete_file_method_name(self):
        pass
