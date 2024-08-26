
from abc import ABC, abstractmethod
from typing import Dict, Any
from .parameter import ParameterSet
from .task_result import TaskResult

class BaseTask(ABC):
    def __init__(self, task_id: str, name: str):
        self.task_id = task_id
        self.name = name
        self.input_params = ParameterSet()
        self.output_params = ParameterSet()

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> TaskResult:
        pass

    async def _validate_and_execute(self, input_data: Dict[str, Any]) -> TaskResult:
        try:
            validated_input = self.input_params.validate(input_data)
            result = await self.execute(validated_input)
            validated_output = self.output_params.validate(result.data)
            return TaskResult(success=True, data=validated_output)
        except Exception as e:
            return TaskResult(success=False, error=str(e))
