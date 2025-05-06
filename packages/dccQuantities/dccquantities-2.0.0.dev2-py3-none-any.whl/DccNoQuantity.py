import warnings
from AbstractQuantityTypeData import AbstractQuantityTypeData
from helpers import dccTypeCollector, parseAttributes, unexpected_key_serialization_handler
from DccRichContentType import (
    DccContent,
    DccFile,
    DccFormula,
    parseDccContent,
    parseDccFile,
    parseDccFormula,
)
from DccName import DccName

class DccNoQuantity(AbstractQuantityTypeData):
    def __init__(
        self,
        data: dict[list],  # contains list of content/file/formula
        id: str = None,
        refId: list[str] = None,
        refType: list[str] = None,
        name: dict = None
    ) -> None:
        super().__init__()
        self.data = data
        self.id = id
        self.refId = refId
        self.refType = refType
        self.name = DccName(name)
        self._sorted=False #noQuantitys can't be sorted in numeric or alphanumeric ways....

    def __len__(self) -> int:
        return len(self.data['content'])+len(self.data['file'])+len(self.data['formula'])

    def __repr__(self) -> str:
        params = {key: value for key, value in vars(self).items() if value is not None}
        paramStr = ", ".join(f"{key}={repr(value)}" for key, value in params.items())
        return f"DccNoQuantity.DccNoQuantity({paramStr})"

    def __str__(self) -> str:
        params = {
            key: value
            for key, value in vars(self).items()
            if value is not None and key is not "data"
        }
        paramStr = ", ".join(f"{key}: {str(value)}" for key, value in params.items())

        if len(paramStr) > 0:
            paramStr = " (" + paramStr + ")"
        return f"{str(self.data)}{paramStr}"

    def toJsonDict(self) -> dict:
        privateKeys=['_sorted']
        keyMapping = {
            'id': '@id',
            'refId': '@refId',
            'refType': '@refType'
        }
        dataKeyMapping = {
            'content': 'dcc:content',
            'file': 'dcc:file',
            'formula': 'dcc:formula'
        }
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                if key in keyMapping:
                    result[keyMapping[key]] = value
                elif key == 'data':
                    for key, value in self.data.items():
                        if value is not None:
                            if isinstance(value,list):
                                if len(value) >0: #skip empty lists
                                    result[dataKeyMapping[key]] = []
                                    for item in value:
                                        result[dataKeyMapping[key]].append(item.toJSONDict())
                    if set(self.data.keys()) - set(dataKeyMapping.keys()):
                        pass # TODO: This should not happen, maybe add a warning?
                elif key in privateKeys:
                    pass
                else:
                    # Use the fallback handler for unexpected keys.
                    unexpected_key_serialization_handler(result, key, value, self.__class__.__name__)
        return {'dcc:noQuantity': result}

    @property
    def sorted(self) -> bool:
        return self._sorted

def parse(jsonDict) -> DccNoQuantity:
    dccNoQuantityArgs = parseAttributes(jsonDict=jsonDict)

    if "dcc:name" in jsonDict.keys():
        dccNoQuantityArgs["name"] = jsonDict["dcc:name"]

    dccNoQuantityData = {}

    dccContentResults = []
    # TODO: All the quantityTypeCollector is doing here is handle the lists. Maybe there's a better way?
    #
    for result in dccTypeCollector(jsonDict=jsonDict, searchKeys=["dcc:content"]):
        dccContentResults.append(parseDccContent(result[1]))
    dccNoQuantityData["content"] = dccContentResults

    dccFileResults = []
    for result in dccTypeCollector(jsonDict=jsonDict, searchKeys=["dcc:file"]):
        dccFileResults.append(parseDccFile(result[1]))
    dccNoQuantityData["file"] = dccFileResults

    dccFormulaResults = []
    for result in dccTypeCollector(jsonDict=jsonDict, searchKeys=["dcc:formula"]):
        dccFormulaResults.append(parseDccFormula(result[1]))
    dccNoQuantityData["formula"] = dccFormulaResults

    dccNoQuantityArgs["data"] = dccNoQuantityData

    for key in jsonDict.keys():
        if key not in [
            "dcc:name",
            "dcc:content",
            "dcc:file",
            "dcc:formula",
            "@_Comment",
        ]:
            warnings.warn(f"Unsupported key for dcc:noQuantity: {key}", RuntimeWarning)

    return DccNoQuantity(**dccNoQuantityArgs)
