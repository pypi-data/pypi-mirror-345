import json
from dataclasses import dataclass, field, asdict
from typing import Dict, Any


@dataclass
class RabbitMQData:
    table_name: str = None
    old: Dict[str, Any] = field(default_factory=dict)
    new: Dict[str, Any] = field(default_factory=dict)
    id: str = None
    action: str = None
    diff: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the RabbitMQData instance to a dictionary
        """
        return asdict(self)

    def to_json(self) -> str:
        """
        Convert the RabbitMQData instance to a JSON string
        """
        return json.dumps(self.to_dict())
