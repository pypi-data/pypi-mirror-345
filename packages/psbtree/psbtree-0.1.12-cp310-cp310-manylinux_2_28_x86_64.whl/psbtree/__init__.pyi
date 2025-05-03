from typing import Optional
import os
from psdec.verifier import Verifier

# 常量定义
AUTH_ERROR_MESSAGE: str
INVALID_CODE_MESSAGE: str
ENV_VAR_NAME: str

# 全局变量
SK_CODE: Optional[str]
verifier: Verifier
_is_authorized: Optional[bool]  # 缓存授权状态

def _load_from_env() -> Optional[str]: ...

def _save_to_env(code: str) -> None: ...

def set_sk_code(code: str) -> bool: ...

def check_authorization() -> None: ...

# 导出授权相关的功能
__all__: list[str] 