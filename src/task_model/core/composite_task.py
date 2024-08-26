import logging
from typing import List, Dict, Any, Tuple
from .base_task import BaseTask
from .task_result import TaskResult
from .parameter import ParameterValidationError, Parameter, ParameterSet

logger = logging.getLogger(__name__)

class CompositeTask(BaseTask):
    def __init__(self, task_id: str, name: str):
        super().__init__(task_id, name)
        self.subtasks: Dict[str, BaseTask] = {}  
        self.connections: List[Tuple[str, str, str, str]] = []
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{task_id}")

    def add_subtask(self, task: BaseTask):
        self.logger.debug(f"Adding subtask: {task.task_id}")
        self.subtasks[task.task_id] = task
        for param in task.input_params.parameters.values():
            full_param_name = f"{task.task_id}.{param.name}"
            self.input_params.add(Parameter(full_param_name, param.type, param.description, param.default, param.optional))
        for param in task.output_params.parameters.values():
            full_param_name = f"{task.task_id}.{param.name}"
            self.output_params.add(Parameter(full_param_name, param.type, param.description, param.default, True))
        self.logger.debug(f"Updated input params: {self.input_params.parameters}")
        self.logger.debug(f"Updated output params: {self.output_params.parameters}")

    def connect(self, from_task: str, from_param: str, to_task: str, to_param: str):
        self.logger.debug(f"Attempting to connect {from_task}.{from_param} to {to_task}.{to_param}")
        self.logger.debug(f"Current subtasks: {list(self.subtasks.keys())}")

        # Vérifier si les tâches existent
        if from_task not in self.subtasks or to_task not in self.subtasks:
            error_msg = f"Invalid task name: {from_task if from_task not in self.subtasks else to_task}"
            self.logger.error(error_msg)
            self.logger.debug(f"Available tasks: {list(self.subtasks.keys())}")
            raise ValueError(error_msg)
        
        # Vérifier si les paramètres existent
        from_full_param = f"{from_task}.{from_param}"
        to_full_param = f"{to_task}.{to_param}"
        
        self.logger.debug(f"Checking output parameters for {from_task}: {list(self.subtasks[from_task].output_params.parameters.keys())}")
        if from_param not in self.subtasks[from_task].output_params.parameters:
            error_msg = f"Invalid output parameter: {from_param} for task {from_task}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.logger.debug(f"Checking input parameters for {to_task}: {list(self.subtasks[to_task].input_params.parameters.keys())}")
        if to_param not in self.subtasks[to_task].input_params.parameters:
            error_msg = f"Invalid input parameter: {to_param} for task {to_task}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Ajouter la connexion
        self.connections.append((from_task, from_param, to_task, to_param))
        self.logger.info(f"Successfully connected {from_full_param} to {to_full_param}")
        
        # Rendre le paramètre cible optionnel
        self.logger.debug(f"Current input parameters: {list(self.input_params.parameters.keys())}")
        if to_full_param in self.input_params.parameters:
            self.input_params.parameters[to_full_param].optional = True
            self.logger.debug(f"Made {to_full_param} optional due to connection")
        else:
            self.logger.warning(f"{to_full_param} not found in input parameters, could not make it optional")
        
        # Vérifier les connexions circulaires
        if self._check_circular_connection(from_task, to_task):
            warning_msg = f"Potential circular connection detected between {from_task} and {to_task}"
            self.logger.warning(warning_msg)
        
        self.logger.debug(f"Current connections: {self.connections}")
        self.logger.debug(f"Updated input parameters: {list(self.input_params.parameters.keys())}")

    def _check_circular_connection(self, from_task: str, to_task: str) -> bool:
        visited = set()
        def dfs(task):
            visited.add(task)
            for _, _, next_task, _ in self.connections:
                if next_task == from_task:
                    return True
                if next_task not in visited:
                    if dfs(next_task):
                        return True
            return False
        return dfs(to_task)

    def _apply_connections(self, results: Dict[str, Any]) -> Dict[str, Any]:
        for from_task, from_param, to_task, to_param in self.connections:
            from_parts = from_task.split('.')
            to_parts = to_task.split('.')
            from_value = results
            for part in from_parts:
                from_value = from_value.get(part, {})
            if from_param in from_value:
                to_value = results
                for part in to_parts[:-1]:
                    if part not in to_value:
                        to_value[part] = {}
                    to_value = to_value[part]
                to_value[to_parts[-1]] = {to_param: from_value[from_param]}
        return results

    async def execute(self, input_data: Dict[str, Any]) -> TaskResult:
        self.logger.debug(f"Executing CompositeTask: {self.name}")
        self.logger.debug(f"Input data: {input_data}")

        try:
            validated_input = self.input_params.validate(input_data)
            self.logger.debug(f"Validated input: {validated_input}")
        except ParameterValidationError as e:
            self.logger.error(f"Input validation failed: {str(e)}")
            return TaskResult(success=False, error=str(e))

        results = {self.task_id: validated_input}
        for subtask in self.subtasks.values():
            subtask_input = {k.split('.')[-1]: v for k, v in validated_input.items() if k.startswith(f"{subtask.task_id}.")}
            
            # Appliquer les connexions avant d'exécuter la sous-tâche
            for from_task, from_param, to_task, to_param in self.connections:
                if to_task == subtask.task_id and from_task in results:
                    from_full_param = f"{from_task}.{from_param}"
                    if from_full_param in results[from_task]:
                        subtask_input[to_param] = results[from_task][from_full_param]
            
            self.logger.debug(f"Subtask {subtask.task_id} input: {subtask_input}")
            
            try:
                result = await subtask.execute(subtask_input)
                self.logger.debug(f"Subtask {subtask.task_id} result: {result}")
            except Exception as e:
                self.logger.error(f"Error executing subtask {subtask.task_id}: {str(e)}")
                return TaskResult(success=False, error=f"Error in subtask {subtask.task_id}: {str(e)}")
            
            if not result.success:
                return result
            
            results[subtask.task_id] = result.data
            self.logger.debug(f"Updated results after subtask {subtask.task_id}: {results}")

        final_results = self._apply_connections(results)
        self.logger.debug(f"Final results after applying all connections: {final_results}")

        output_data = {}
        for task_results in final_results.values():
            if isinstance(task_results, dict):
                output_data.update(task_results)

        self.logger.debug(f"Output data before validation: {output_data}")

        try:
            validated_output = self.output_params.validate(output_data)
            self.logger.debug(f"Validated output: {validated_output}")
            return TaskResult(success=True, data=validated_output)
        except ParameterValidationError as e:
            self.logger.error(f"Output validation failed: {str(e)}")
            return TaskResult(success=False, error=f"Output validation failed: {str(e)}")