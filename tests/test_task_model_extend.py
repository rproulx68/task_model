import pytest
from task_model.core.base_task import BaseTask
from task_model.core.composite_task import CompositeTask
from task_model.core.parameter import Parameter, ParameterSet
from task_model.core.task_result import TaskResult

class AddTask(BaseTask):
    def __init__(self, task_id="add_task"):
        super().__init__(task_id, "Add two numbers")
        self.input_params.add(Parameter("a", int, "First number"))
        self.input_params.add(Parameter("b", int, "Second number"))
        self.output_params.add(Parameter("result", int, "Sum of a and b"))

    async def execute(self, input_data):
        a = input_data["a"]
        b = input_data["b"]
        result = a + b
        return TaskResult(success=True, data={f"{self.task_id}.result": result})

class MultiplyTask(BaseTask):
    def __init__(self, task_id="multiply_task"):
        super().__init__(task_id, "Multiply two numbers")
        self.input_params.add(Parameter("x", int, "First number"))
        self.input_params.add(Parameter("y", int, "Second number"))
        self.output_params.add(Parameter("result", int, "Product of x and y"))

    async def execute(self, input_data):
        x = input_data["x"]
        y = input_data["y"]
        return TaskResult(success=True, data={"result": x * y})
    async def execute(self, input_data):
        x = input_data["x"]
        y = input_data["y"]
        result = a * b
        return TaskResult(success=True, data={f"{self.task_id}.result": result})

class StringLengthTask(BaseTask):
    def __init__(self, task_id="string_length_task"):
        super().__init__(task_id, "Get string length")
        self.input_params.add(Parameter("text", str, "Input text"))
        self.output_params.add(Parameter("length", int, "Length of text"))

    async def execute(self, input_data):
        text = input_data["text"]
        return TaskResult(success=True, data={"length": len(text)})

@pytest.mark.asyncio
async def test_complex_composite_task():
    # Créer les tâches de base
    add_task1 = AddTask("add_task1")
    add_task2 = AddTask("add_task2")
    multiply_task = MultiplyTask("multiply_task")
    string_length_task = StringLengthTask("string_length_task")

    # Créer une tâche composite interne
    inner_composite = CompositeTask("inner_composite", "Inner Composite Task")
    inner_composite.add_subtask(add_task1)
    inner_composite.add_subtask(multiply_task)
    inner_composite.connect("add_task1", "result", "multiply_task", "x")

    # Créer la tâche composite principale
    main_composite = CompositeTask("main_composite", "Main Composite Task")
    main_composite.add_subtask(inner_composite)
    main_composite.add_subtask(add_task2)
    main_composite.add_subtask(string_length_task)

    # Connecter les tâches
    main_composite.connect("multiply_task", "result", "add_task2", "a")
    main_composite.connect("add_task2", "result", "string_length_task", "text")

    # Exécuter la tâche composite principale
    result = await main_composite.execute({
        "add_task1.a": 5,
        "add_task1.b": 3,
        "multiply_task.x": 1,
        "multiply_task.y": 2,
        "add_task2.a": 0,
        "add_task2.b": 10
    })

    # Vérifier les résultats
    assert result.success, f"Task failed with error: {result.error}"
    
    # Vérifier les résultats intermédiaires
    assert result.data["add_task1.result"] == 8  # 5 + 3
    assert result.data["multiply_task.result"] == 16  # 8 * 2
    assert result.data["add_task2.result"] == 26  # 16 + 10
    
    # Vérifier le résultat final
    assert result.data["string_length_task.length"] == 26  # Longueur de "26"

    print("Complex composite task test passed successfully!")