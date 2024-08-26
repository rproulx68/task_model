from typing import Any, Dict, Optional, Type

class ParameterValidationError(Exception):
    pass

class Parameter:
    def __init__(self, name: str, type: Type, description: str = "", default: Any = None, optional: bool = False, task_id: Optional[str] = None):
        self.name = name
        self.type = type
        self.description = description
        self.default = default
        self.optional = optional
        self.task_id = task_id

    def get_full_name(self) -> str:
        return f"{self.task_id}.{self.name}" if self.task_id else self.name

    @classmethod
    def create(cls, name: str, type: Type, description: str = "", default: Any = None, optional: bool = False, task_id: Optional[str] = None):
        return cls(name=name, type=type, description=description, default=default, optional=optional, task_id=task_id)

class ParameterSet:
    def __init__(self, parameters: Dict[str, Parameter] = None):
        self.parameters: Dict[str, Parameter] = {}
        if parameters:
            for param in parameters.values():
                self.add(param)

    def add(self, param: Parameter):
        self.parameters[param.get_full_name()] = param

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        validated_data = {}
        for full_name, param in self.parameters.items():
            name = full_name.split('.')[-1]  # Obtenir le nom du paramètre sans préfixe
            if full_name in data:
                value = data[full_name]
            elif name in data:
                value = data[name]
            elif not param.optional:
                if param.default is not None:
                    validated_data[full_name] = param.default
                    continue
                else:
                    raise ParameterValidationError(f"Missing required input parameter: {full_name}")
            else:
                continue

            if not isinstance(value, param.type):
                raise ParameterValidationError(f"Invalid type for {full_name}. Expected {param.type}, got {type(value)}")
            validated_data[full_name] = value
        return validated_data

    def merge(self, other: 'ParameterSet'):
        for param in other.parameters.values():
            self.add(Parameter.create(
                name=param.name,
                type=param.type,
                description=param.description,
                default=param.default,
                optional=param.optional,
                task_id=param.task_id
            ))

    def keys(self):
        return self.parameters.keys()

    def get_parameter(self, name: str) -> Optional[Parameter]:
        return next((p for p in self.parameters.values() if p.name == name or p.get_full_name() == name), None)

    def __getitem__(self, key: str) -> Parameter:
        param = self.get_parameter(key)
        if param is None:
            raise KeyError(f"Parameter '{key}' not found")
        return param

    def __contains__(self, key: str) -> bool:
        return self.get_parameter(key) is not None

    def __iter__(self):
        return iter(self.parameters.values())

    def __len__(self):
        return len(self.parameters)