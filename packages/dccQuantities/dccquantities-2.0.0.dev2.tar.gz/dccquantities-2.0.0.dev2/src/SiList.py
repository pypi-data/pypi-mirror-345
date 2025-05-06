from __future__ import annotations  # for type annotation recursion
from datetime import datetime
from typing import Union

from AbstractListType import AbstractListType
from AbstractValueType import AbstractValueType


class SiList(AbstractListType):
    def __init__(
        self,
        children: list[Union[AbstractValueType, SiList]],
        label: str = None,
        dateTime: datetime = None,
    ) -> None:
        super().__init__(children)
        self.label = label
        self.dateTime = dateTime
        self._sorted = False #siList is not guaranteed to be sortable in the first palace what's with values with different units ? How to sort them ?


    def toJsonDict(self):
        keyMapping = {
            'label': 'si:label',
            'dateTime': 'si:dateTime',
        }
        attributes = super().toJsonDict() # converts all the data in 'children'
        for key, value in self.__dict__.items():
            if value is not None:
                if key in keyMapping:
                    attributes[keyMapping[key]] = value
                elif key == 'children':
                    pass
                else:
                    attributes[key] = value
                    # TODO: This should not happen, maybe add a warning?

        return {'si:list': attributes}
    
    def __repr__(self) -> str:
        params = {key: value for key, value in vars(self).items() if value is not None}
        paramStr = ', '.join(f'{key}={repr(value)}' for key, value in params.items())
        return f'SiList.SiList({paramStr})'
    
    def __str__(self) -> str:
        params = {key: value for key, value in vars(self).items() if value is not None and key is not 'children'}
        paramStr = ', '.join(f'{key}: {repr(value)}' for key, value in params.items())
        if len(paramStr) > 0:
            paramStr = f'({paramStr})'
        childrenStr = "\n    ".join(str(child) for child in self.children)
        childrenStr = f"[\n    {childrenStr}\n]\n"
        return f"\nSiList {paramStr}\n{childrenStr}"

    @property
    def sorted(self) -> bool:
        return self._sorted

def parse(jsonDict: dict, relativeUncertainty: dict = None):
    return None