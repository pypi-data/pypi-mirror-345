import warnings
from DccFormulaType import DccMathml, parseDccMathml
from helpers import parseAttributes,unexpected_key_serialization_handler
from typing import Union #for python 3.8/3.9 compatibility

class DccContent:
    def __init__(self, string, lang=None, id=None, refId=None, refType=None) -> None:
        self.string = string
        self.lang = lang
        self.id = id
        self.refId = refId
        self.refType = refType

    def toJSONDict(self) -> dict:
        # Mapping of attribute names to their corresponding JSON keys.
        keyMapping = {
            'lang': '@lang',
            'id': '@id',
            'refId': '@refId',
            'refType': '@refType'
        }

        # Start with the required attribute.
        result = {'$': self.string}

        # Iterate over all instance attributes.
        for key, value in self.__dict__.items():
            # Skip the already processed "string" attribute.
            if key == 'string':
                continue
            # Only process attributes with a meaningful value.
            if value not in [None, [None]]:
                if key in keyMapping:
                    result[keyMapping[key]] = value
                else:
                    # Use the fallback handler for unexpected keys.
                    unexpected_key_serialization_handler(result, key, value, self.__class__.__name__)

        return result


def parseDccContent(jsonDict):
    if isinstance(jsonDict,dict):
        dccContentArgs = parseAttributes(jsonDict=jsonDict)
        dccContentArgs["string"] = jsonDict["$"]
    elif isinstance(jsonDict,str):
        dccContentArgs={"string" : jsonDict}


    return DccContent(**dccContentArgs)


# TODO: File Object API
class DccFile:
    def __init__(
        self,
        fileName,
        mimeType,
        dataBase64,
        description=None,
        name=None,
        id=None,
        refId=None,
        refType=None,
    ) -> None:
        self.fileName = fileName
        self.mimeType = mimeType
        self.dataBase64 = dataBase64
        self.description = description
        self.name = name
        self.id = id
        self.refId = refId
        self.refType = refType


def parseDccFile(jsonDict):
    dccFileArgs = parseAttributes(jsonDict=jsonDict)
    if "name" in jsonDict.keys():
        dccFileArgs["name"] = jsonDict["name"]
    if "description" in jsonDict.keys():
        dccFileArgs["description"] = jsonDict["description"]

    dccFileArgs["fileName"] = jsonDict["fileName"]
    dccFileArgs["mimeType"] = jsonDict["mimeType"]
    dccFileArgs["dataBase64"] = jsonDict["dataBase64"]

    return DccFile(**dccFileArgs)


class DccFormula:
    def __init__(
        self, formula: Union[str, DccMathml], id=None, refId=None, refType=None
    ) -> None:
        self.formula = formula
        self.formulaType = "mathml" if isinstance(formula, DccMathml) else "latex"
        self.id = id
        self.refId = refId
        self.refType = refType


def parseDccFormula(jsonDict: dict):
    dccFormulaArgs = parseAttributes(jsonDict=jsonDict)
    if "dcc:latex" in jsonDict.keys():
        dccFormulaArgs["formula"] = jsonDict["dcc:latex"]
    else:  # mathml must be given
        dccFormulaArgs["formula"] = parseDccMathml(jsonDict=jsonDict["dcc:mathml"])

    for key in jsonDict.keys():
        if key not in ["dcc:latex", "dcc:mathml", "@_Comment"]:
            warnings.warn(f"Unsupported key for dcc:formula: {key}", RuntimeWarning)

    return DccFormula(**dccFormulaArgs)
