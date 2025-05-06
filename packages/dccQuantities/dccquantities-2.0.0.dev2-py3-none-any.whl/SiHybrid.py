import warnings
from AbstractListType import AbstractListType
from AbstractValueType import AbstractValueType
from SiList import SiList
from SiRealList import parseSingleValue as parseSiReal
from SiRealList import parseXMLList as parseRealListXMLList
from SiRealList import parseConst
from typing import Union

class SiHybrid(AbstractListType):
    def __init__(self, children: list[Union[AbstractValueType, SiList]]) -> None:
        super().__init__(children)

    def getUnits(self):
        pass

    def toJsonDict(self):
        return {'si:hybrid': super().toJsonDict()}

    def __repr__(self) -> str:
        params = {key: value for key, value in vars(self).items() if value is not None}
        paramStr = ", ".join(f"{key}={repr(value)}" for key, value in params.items())
        return f"SiHybrid.SiHybrid({paramStr})"

    def __str__(self) -> str:
        return (
            "\n[\n    " + "\n    ".join(str(child) for child in self.children) + "\n]\n"
        )

    @property
    def sorted(self) -> bool:
        return self.children[0].sorted


def parse(jsonDict: dict, relativeUncertainty: dict = None):
    keyParserMapping = {
        "si:real": parseSiReal,
        "si:complex": __placeholder,
        "si:list": __placeholder,
        "si:realList": __placeholder,
        "si:realListXMLList": parseRealListXMLList,
        "si:complexList": __placeholder,
        "si:constant": parseConst,
    }
    children = []
    for key in keyParserMapping.keys():
        if key in jsonDict.keys():
            if isinstance(jsonDict[key], list):
                for item in jsonDict[key]:
                    children.append(keyParserMapping[key](item, relativeUncertainty=relativeUncertainty))
            else:
                children.append(keyParserMapping[key](item, relativeUncertainty=relativeUncertainty))

    for key in jsonDict.keys():
        if key not in keyParserMapping.keys():
            warnings.warn(f"Unsupported key for si:hybrid: {key}", RuntimeWarning)

    return SiHybrid(children=children)


def __placeholder(argument=None):
    """
    THIS IS A PLACEHOLDER FOR PARSER FUNCTIONS THAT ARE NOT IMPLEMENTED YET
    IT SHOULD NO LONGER EXIST IN PROD
    """
    return "TODO"
