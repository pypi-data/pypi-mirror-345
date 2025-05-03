from functools import wraps
from typing import Callable, TypeVar, Any
from psbtree import check_authorization

T = TypeVar('T')

def require_authorization(func: Callable[..., T]) -> Callable[..., T]: ... 