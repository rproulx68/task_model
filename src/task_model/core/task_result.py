from typing import Dict, Any, Optional

class TaskResult:
    def __init__(self, success: bool, data: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error

    def __repr__(self) -> str:
        return f"TaskResult(success={self.success}, data={self.data}, error={self.error})"

    def __bool__(self) -> bool:
        return self.success

    @property
    def is_success(self) -> bool:
        return self.success

    @property
    def is_error(self) -> bool:
        return not self.success