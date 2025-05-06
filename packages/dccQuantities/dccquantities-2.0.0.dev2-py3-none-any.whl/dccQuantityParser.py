from SiRealList import parseSingleValue as parseSiRealValue
from SiRealList import parseXMLList as parseRealListXMLList
from SiRealList import parseConst as parseConst
from SiList import parse as parseList
from DccNoQuantity import parse as parseDccNoQuantity
from DccCharsXMLList import parse as parseCharsXMLList
from SiHybrid import parse as parseSiHybrid
from dccXMLJSONConv.dccConv import XMLToDict
from helpers import dccTypeCollector, replaceQuantitiesInDict, parseAttributes,ensureList
from DccQuantityType import DccQuantityType

import warnings


def parse(xmlStr: str):
    # parse XML to Json
    jsonDict,errors = XMLToDict(xmlStr)

    # get dccQuantities
    quantityDict = dccTypeCollector(jsonDict)

    # parse content to DccQuantityType objects
    dccQuantityTypeObjects = []
    for path, item in quantityDict:
        dccQuantityTypeObjects.append(parseItemFromJsonDict(item))
    return dccQuantityTypeObjects


def parseItemFromJsonDict(itemJsonDict: dict):
    for key, element in itemJsonDict.items():
        if isinstance(element, list) and len(element) == 1:
            itemJsonDict[key] = element[0]

    quantityArgs = {}
    keys = itemJsonDict.keys()

    # Attributes
    quantityArgs = parseAttributes(itemJsonDict)

    # Name
    try:
        if "dcc:name" in keys:
            quantityArgs["name"] = {
                d["@lang"]: d["$"] for d in itemJsonDict["dcc:name"]["dcc:content"]
            }
    except:
        pass
    # Description
    # TODO: dcc:file und dcc:formula
    if "dcc:description" in keys:
        # quantityArgs["description"] = {
        #     d["@lang"]: d["$"]
        #     for d in itemJsonDict["dcc:description"]["dcc:content"]
        # }
        quantityArgs["description"] = itemJsonDict["dcc:description"]

    # relative Uncertainty
    relativeUncertainty = None
    if "dcc:relativeUncertainty" in keys:
        relativeUncertainty = {}
        relUncerJsonDict = itemJsonDict["dcc:relativeUncertainty"]
        if "dcc:relativeUncertaintyXmlList" in relUncerJsonDict.keys():
            # currently not looking at any of the optional parameters
            relativeUncertainty["uncertainty"] = ensureList(relUncerJsonDict[
                "dcc:relativeUncertaintyXmlList"
            ]["si:valueXMLList"])
            relativeUncertainty["unit"] = ensureList(relUncerJsonDict[
                "dcc:relativeUncertaintyXmlList"
            ]["si:unitXMLList"])
        elif "dcc:relativeUncertaintySingle" in relUncerJsonDict.keys():
            # Note: untested as we do not have a single dcc that uses this
            # currently not looking at any of the optional parameters
            relativeUncertainty["uncertainty"] = [
                relUncerJsonDict["dcc:relativeUncertaintySingle"]["si:value"]["$"]
            ]
            relativeUncertainty["unit"] = [
                relUncerJsonDict["dcc:relativeUncertaintySingle"]["si:unit"]["$"]
            ]

    # Data
    if "si:real" in keys:
        quantityArgs["data"] = parseSiRealValue(
            jsonDict=itemJsonDict["si:real"], relativeUncertainty=relativeUncertainty
        )
    elif "dcc:noQuantity" in keys:
        quantityArgs["data"] = parseDccNoQuantity(
            jsonDict=itemJsonDict["dcc:noQuantity"]
        )
    elif "si:realListXMLList" in keys:
        quantityArgs["data"] = parseRealListXMLList(
            jsonDict=itemJsonDict["si:realListXMLList"],
            relativeUncertainty=relativeUncertainty,
        )
    elif "dcc:charsXMLList" in keys:
        quantityArgs["data"] = parseCharsXMLList(
            jsonDict=itemJsonDict["dcc:charsXMLList"]
        )
    elif "si:hybrid" in keys:
        quantityArgs["data"] = parseSiHybrid(
            jsonDict=itemJsonDict["si:hybrid"], relativeUncertainty=relativeUncertainty
        )
    elif "si:constant" in keys:
        quantityArgs["data"] = parseConst(
            jsonDict=itemJsonDict["si:constant"],
            relativeUncertainty=relativeUncertainty,
        )
    elif "si:list" in keys:
        quantityArgs["data"] = parseList(
            jsonDict=itemJsonDict["si:list"], relativeUncertainty=relativeUncertainty
        )

    # Measurement Environment
    if "dcc:usedMethods" in keys:
        quantityArgs["usedMethods"] = replaceQuantitiesInDict(
            jsonDict=itemJsonDict["dcc:usedMethods"], parser=parseItemFromJsonDict
        )  # TODO: Test
    if "dcc:usedSoftware" in keys:
        quantityArgs["usedSoftware"] = replaceQuantitiesInDict(
            jsonDict=itemJsonDict["dcc:usedSoftware"], parser=parseItemFromJsonDict
        )  # TODO: Test
    if "dcc:measuringEquipments" in keys:
        quantityArgs["measuringEquipments"] = replaceQuantitiesInDict(
            jsonDict=itemJsonDict["dcc:measuringEquipments"],
            parser=parseItemFromJsonDict,
        )  # TODO: Test
    if "dcc:influenceConditions" in keys:
        quantityArgs["measuringEquipments"] = replaceQuantitiesInDict(
            jsonDict=itemJsonDict["dcc:influenceConditions"],
            parser=parseItemFromJsonDict,
        )  # TODO: Test

    # Meta Data
    if "dcc:measurementMetaData" in keys:
        quantityArgs["measurementMetaData"] = replaceQuantitiesInDict(
            jsonDict=itemJsonDict["dcc:measurementMetaData"],
            parser=parseItemFromJsonDict,
        )

    for key in keys:
        if key not in [
            "@id",
            "@refId",
            "@refType",
            "dcc:name",
            "dcc:description",
            "dcc:relativeUncertainty",
            "si:real",
            "dcc:noQuantity",
            "si:realListXMLList",
            "dcc:charsXMLList",
            "si:hybrid",
            "si:constant",
            "si:list",
            "dcc:usedMethods",
            "dcc:usedSoftware",
            "dcc:measuringEquipments",
            "dcc:influenceConditions",
            "dcc:measurementMetaData",
            "@_Comment",
        ]:
            warnings.warn(f"Unsupported key for dcc:quantity: {key}", RuntimeWarning)

    return DccQuantityType(**quantityArgs)
