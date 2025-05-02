# type: ignore
from fleet_control.utils.utils import *
from functools import wraps
from balena.exceptions import RequestError

class BalenaAPIError(Exception):
    """Custom exception for Balena API errors."""
    def __init__(self, status_code, message="Balena API request failed"):
        self.status_code = status_code
        super().__init__(f"{message} (status code: {status_code})")

def handle_request_error(raise_exception=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RequestError as e:
                msg = f"Balena status code: {e.status_code}. Please try again in a few minutes."
                print(msg)
                print(f"{func.__name__} failed with status {e.status_code}: {e}")
                if raise_exception:
                    raise BalenaAPIError(e.status_code) from e
        return wrapper
    return decorator


def create_target(target_obj):
    """Factory function to create the appropriate target class."""
    if target_obj.get("device_name"):
        return Device(target_obj)
    else:
        return Application(target_obj)

class Device:
    """Class for handling operations on a device target."""

    def __init__(self, device: balena.types.models.TypeDevice):
        for k, v in device.items():
            setattr(self, k, v)
        self.device = device

    @handle_request_error()
    def get_variables(self, custom=False):
        """Get environment and service variables for the device."""
        return get_device_variables(self.device, custom)

    @handle_request_error()
    def set_env_var(self, var_name: str, value: str) -> None:
        """Set an environment variable on the device."""
        balena_sdk.models.device.env_var.set(self.id, var_name, str(value))

    @handle_request_error()
    def set_service_var(self, service: int, var_name: str, value: str) -> None:
        """Set a service variable on the device."""
        balena_sdk.models.device.service_var.set(self.id, service, var_name, str(value))

    @handle_request_error()
    def remove_env_var(self, var_name: str) -> None:
        """Remove an environment variable from the device."""
        balena_sdk.models.device.env_var.remove(self.id, var_name)

    @handle_request_error()
    def remove_service_var(self, service: int, var_name: str) -> None:
        """Remove a service variable from the device."""
        balena_sdk.models.device.service_var.remove(self.id, service, var_name)

    def get_identifier(self) -> str:
        """Get a string identifier for the device."""
        return f"device {self.device_name}"


class Application:
    """Class for handling operations on an application target."""

    def __init__(self, application: balena.types.models.TypeApplication):
        for k, v in application.items():
            setattr(self, k, v)

    @handle_request_error()
    def get_variables(self, custom=False):
        """Get environment and service variables for the application."""
        return get_fleet_variables(self.id)

    @handle_request_error()
    def set_env_var(self, var_name: str, value: str) -> None:
        """Set an environment variable on the application."""
        balena_sdk.models.application.env_var.set(self.id, var_name, str(value))

    @handle_request_error()
    def set_service_var(self, service: int, var_name: str, value: str) -> None:
        """Set a service variable on the application."""
        balena_sdk.models.service.var.set(service, var_name, str(value))

    @handle_request_error()
    def remove_env_var(self, var_name: str) -> None:
        """Remove an environment variable from the application."""
        balena_sdk.models.application.env_var.remove(self.id, var_name)

    @handle_request_error()
    def remove_service_var(self, service: int, var_name: str) -> None:
        """Remove a service variable from the application."""
        balena_sdk.models.service.var.remove(service, var_name)

    def get_identifier(self) -> str:
        """Get a string identifier for the application."""
        return f"application {self.app_name}"
    
class Service:
    pass