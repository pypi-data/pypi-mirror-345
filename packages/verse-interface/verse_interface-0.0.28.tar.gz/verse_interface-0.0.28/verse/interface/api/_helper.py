import inspect
from typing import Any

from verse.core import Component

from ._models import APIAuth
from .component import API


def get_operations(component: Component) -> dict[str, Any]:
    """
    Get operations from component
    """
    operations: dict = {}
    for method_name, method in inspect.getmembers(
        component, predicate=inspect.ismethod
    ):
        if callable(method) and hasattr(method, "operation"):
            operations[method_name] = method
    return operations


def get_return_type(method: Any) -> Any:
    """
    Get return type of operation
    """
    sig = inspect.signature(method)
    if sig.return_annotation != inspect.Signature.empty:
        return sig.return_annotation
    return None


def get_api_auth(
    api_component: API,
    component_name: str,
    operation_name: str,
) -> APIAuth | None:
    pass
