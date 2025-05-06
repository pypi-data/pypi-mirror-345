import warnings
from AbstractQuantityTypeData import AbstractQuantityTypeData
from typing import Union #for python 3.8/3.9 compatibility

class DccCharsXMLList(AbstractQuantityTypeData):
    def __init__(self, data: list[str]) -> None:
        super().__init__()
        self.data = data

    def __len__(self) -> int:
        return len(self.data)

    def __str__(self) -> str:
        return self.data.__str__()

    def __repr__(self) -> str:
        params = {key: value for key, value in vars(self).items() if value is not None}
        paramStr = ", ".join(f"{key}={repr(value)}" for key, value in params.items())
        return f"DccCharsXMLList.DccCharsXMLList({paramStr})"

    def __add__(self, other):
        if isinstance(other, DccCharsXMLList):
            return DccCharsXMLList(data=self.data + other.data)
        elif isinstance(other, list):
            warnings.warn("Concatenating DccCharsXMLList and list!", RuntimeWarning)
            return DccCharsXMLList(data=self.data + other)
        else:
            raise TypeError(
                "unsupported operand for +: "
                f"'{type(self).__name__}' and '{type(other).__name__}'"
            )
        
    def __radd__(self, other):
        if isinstance(other, DccCharsXMLList):
            return DccCharsXMLList(data=other.data + self.data)
        elif isinstance(other, list):
            warnings.warn("Concatenating DccCharsXMLList and list!", RuntimeWarning)
            return DccCharsXMLList(data=other + self.data)
        else:
            raise TypeError(
                "unsupported operand for +: "
                f"'{type(other).__name__}' and '{type(self).__name__}'"
            )
        
    def toJsonDict(self) -> list:
        return {'dcc:charsXMLList': self.data}


    @property
    def sorted(self) -> bool:
        if self._sorted is None:
            self._sorted=all(self.data[i] <= self.data[i + 1] for i in range(len(self.data) - 1))
        """Check if the list of strings is sorted in ascending order."""
        return self._sorted


def parse(jsonDict: Union[dict, list]):
    if isinstance(jsonDict, list):
        return DccCharsXMLList(data=jsonDict)
    elif isinstance(jsonDict, dict):
        return NotImplemented

    return DccCharsXMLList(data=jsonDict)
