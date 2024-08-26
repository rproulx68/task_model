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
        result = x * y
        return TaskResult(success=True, data={f"{self.task_id}.result": result})
    
@pytest.mark.asyncio
async def test_composite_task_with_parameter_connection():
    add_task = AddTask()
    multiply_task = MultiplyTask()
    composite_task = CompositeTask("composite", "Composite Task")
    composite_task.add_subtask(add_task)
    composite_task.add_subtask(multiply_task)
    composite_task.connect("add_task", "result", "multiply_task", "x")

    result = await composite_task.execute({
        "add_task.a": 2, 
        "add_task.b": 3, 
        "multiply_task.x": 4,
        "multiply_task.y": 4
    })
    assert result.success
    assert result.data["multiply_task.result"] == 20  # (2 + 3) * 4 = 20

@pytest.mark.asyncio
async def test_composite_task_with_multiple_connections():
    add_task1 = AddTask("add_task1")
    add_task2 = AddTask("add_task2")
    multiply_task = MultiplyTask()
    composite_task = CompositeTask("composite", "Composite Task")
    composite_task.add_subtask(add_task1)
    composite_task.add_subtask(add_task2)
    composite_task.add_subtask(multiply_task)
    composite_task.connect("add_task1", "result", "add_task2", "a")
    composite_task.connect("add_task2", "result", "multiply_task", "x")

    result = await composite_task.execute({
        "add_task1.a": 2, "add_task1.b": 3,
        "add_task2.a": 0, "add_task2.b": 4,
        "multiply_task.x": 1, "multiply_task.y": 5
    })
    assert result.success
    assert result.data["multiply_task.result"] == 45  # ((2 + 3) + 4) * 5 = 45

@pytest.mark.asyncio
async def test_composite_task_with_invalid_connection():
    add_task = AddTask()
    multiply_task = MultiplyTask()
    composite_task = CompositeTask("composite", "Composite Task")
    composite_task.add_subtask(add_task)
    composite_task.add_subtask(multiply_task)
    
    with pytest.raises(ValueError):
        composite_task.connect("add_task", "invalid_output", "multiply_task", "x")

@pytest.mark.asyncio
async def test_composite_task_with_missing_connection():
    add_task = AddTask()
    multiply_task = MultiplyTask()
    composite_task = CompositeTask("composite", "Composite Task")
    composite_task.add_subtask(add_task)
    composite_task.add_subtask(multiply_task)
    # Intentionally not connecting the tasks

    result = await composite_task.execute({
        "add_task.a": 2, "add_task.b": 3,
        "multiply_task.x": 4, "multiply_task.y": 5
    })
    assert result.success
    assert result.data["add_task.result"] == 5
    assert result.data["multiply_task.result"] == 20

@pytest.mark.asyncio
async def test_nested_composite_tasks():
    add_task = AddTask()
    multiply_task = MultiplyTask()
    inner_composite = CompositeTask("inner", "Inner Composite")
    inner_composite.add_subtask(add_task)
    inner_composite.add_subtask(multiply_task)
    inner_composite.connect("add_task", "result", "multiply_task", "x")

    outer_composite = CompositeTask("outer", "Outer Composite")
    outer_composite.add_subtask(inner_composite)
    outer_composite.add_subtask(AddTask("final_add"))
    outer_composite.connect("inner", "multiply_task.result", "final_add", "a")

    result = await outer_composite.execute({
        "inner.add_task.a": 2,
        "inner.add_task.b": 3,
        "inner.multiply_task.y": 4,
        "final_add.a": 0 , "final_add.b": 5
    })
    assert result.success
    assert result.data["final_add.result"] == 25  # ((2 + 3) * 4) + 5 = 25