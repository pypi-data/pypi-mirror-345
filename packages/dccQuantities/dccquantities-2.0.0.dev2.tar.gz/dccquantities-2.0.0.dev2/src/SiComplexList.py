from datetime import datetime
from AbstractValueType import AbstractValueType


class SiComplexList(AbstractValueType):
    def __init__(
        self,
        data: list,
        label: str = None,
        unit: str = None,
        dateTime: datetime = None,
        phase: str = None,
        uncertainty: str = None,
    ) -> None:
        super().__init__(label, unit, dateTime)
        self.data = data
        self.phase = phase
        self.uncertainty = uncertainty
        self._sorted=False #noQuantitys can't be sorted in numeric or alphanumeric ways....

    def toJsonDict(self):
        return NotImplemented

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        params = {key: value for key, value in vars(self).items() if value is not None}
        paramStr = ", ".join(f"{key}={repr(value)}" for key, value in params.items())
        return f"SiComplexList.SiComplexList({paramStr})"
    
    def __str__(self) -> str:
        params = {key: value for key, value in vars(self).items() if value is not None and key is not 'data'}
        paramStr = ", ".join(f"{key}: {str(value)}" for key, value in params.items())
        
        if len(paramStr) > 0:
            paramStr = " (" + paramStr + ")"
        return f"{str(self.data)}{paramStr}"

    @property
    def sorted(self) -> bool:
        return self._sorted
