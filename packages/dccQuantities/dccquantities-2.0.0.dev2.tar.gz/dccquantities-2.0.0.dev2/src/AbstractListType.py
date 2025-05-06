from __future__ import annotations
from collections import defaultdict # for type annotation recursion

from AbstractQuantityTypeData import AbstractQuantityTypeData
from AbstractValueType import AbstractValueType
from typing import Union #for python 3.8/3.9 compatibility


class AbstractListType(AbstractQuantityTypeData):
    def __init__(self, children: list[Union[AbstractListType,AbstractValueType]]) -> None:
        super().__init__()
        self.children = children

    def toJsonDict(self):
        result = defaultdict(list)
        for child in self.children:
            childJson = child.toJsonDict()
            for key, value in childJson.items():
                result[key].append(value)
        return dict(result)


    def flatten(self):
        pass

    def __len__(self):
        return len(self.children)
