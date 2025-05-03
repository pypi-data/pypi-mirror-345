"""
Utility functions for the ExcelJet API client.
"""

import time
from typing import Optional, TypeVar, Type, Dict, Any, List
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


def current_timestamp() -> int:
    """Get current Unix timestamp in seconds."""
    return int(time.time())


def model_to_dict(model: BaseModel) -> Dict[str, Any]:
    """Convert a Pydantic model to a dictionary."""
    return model.model_dump()


def models_to_list(models: List[BaseModel]) -> List[Dict[str, Any]]:
    """Convert a list of Pydantic models to a list of dictionaries."""
    return [model_to_dict(model) for model in models]


def dict_to_model(data: Dict[str, Any], model_class: Type[T]) -> T:
    """Convert a dictionary to a Pydantic model."""
    return model_class(**data)


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def format_api_path(path: str) -> str:
    """Ensure path starts with a slash and doesn't end with one."""
    if not path.startswith('/'):
        path = '/' + path
    return path.rstrip('/')


def format_content_type(content_type: Optional[str]) -> Optional[str]:
    """Normalize content type string."""
    if not content_type:
        return None
    return content_type.lower() 