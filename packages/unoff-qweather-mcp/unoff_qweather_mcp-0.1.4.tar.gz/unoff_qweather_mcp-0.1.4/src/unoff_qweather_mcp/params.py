from typing import Optional, Union, Any
from pydantic import BaseModel, field_validator

class NumberParam(BaseModel):
    number: Optional[Union[int, float, str]] = None
    
    @field_validator('number', mode='before')
    @classmethod
    def validate_number(cls, v: Any) -> Optional[int]:
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return int(v)
        if isinstance(v, str):
            try:
                return int(float(v))
            except ValueError:
                raise ValueError(
                    f"Invalid number value: '{v}'. Number parameter must be a valid integer, "
                    f"convertible float, or a string that can be converted to an integer."
                )
        raise TypeError(
            f"Number parameter must be an integer, float, or string, not {type(v).__name__}. "
            f"Received: {v}"
        )

class DaysParam(BaseModel):
    days: Union[int, float, str] = 1
    
    @field_validator('days', mode='before')
    @classmethod
    def validate_days(cls, v: Any) -> int:
        if v is None:
            return 1
        if isinstance(v, (int, float)):
            return int(v)
        if isinstance(v, str):
            try:
                return int(float(v))
            except ValueError:
                raise ValueError(
                    f"Invalid days value: '{v}'. Days parameter must be a valid integer, "
                    f"convertible float, or a string that can be converted to an integer."
                )
        raise TypeError(
            f"Days parameter must be an integer, float, or string, not {type(v).__name__}. "
            f"Received: {v}"
        )

class HoursParam(BaseModel):
    hours: Union[int, float, str] = 24
    
    @field_validator('hours', mode='before')
    @classmethod
    def validate_hours(cls, v: Any) -> int:
        if v is None:
            return 24
        if isinstance(v, (int, float)):
            return int(v)
        if isinstance(v, str):
            try:
                return int(float(v))
            except ValueError:
                raise ValueError(
                    f"Invalid hours value: '{v}'. Hours parameter must be a valid integer, "
                    f"convertible float, or a string that can be converted to an integer."
                )
        raise TypeError(
            f"Hours parameter must be an integer, float, or string, not {type(v).__name__}. "
            f"Received: {v}"
        )

class CoordinatesParams(BaseModel):
    latitude: Union[float, int, str]
    longitude: Union[float, int, str]
    
    @field_validator('latitude', 'longitude', mode='before')
    @classmethod
    def validate_coordinates(cls, v: Any) -> float:
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                raise ValueError(
                    f"Invalid coordinate value: '{v}'. Coordinate must be a valid decimal number, " 
                    f"or a string that can be converted to a decimal number."
                )
        raise TypeError(
            f"Coordinate must be a float, integer, or string, not {type(v).__name__}. "
            f"Received: {v}"
        ) 