from pathlib import Path
import warnings
import json
import pytest
import os
import traceback
from dccQuantityParser import parse
import numpy as np
print("TESTING test_parser.py")
print(os.getcwd())  # Print current working directory
from testHelpers import get_test_file
from helpers import replaceQuantitiesInDict,DCCJSONEncoder
from dccXMLJSONConv.dccConv import XMLToDict,DictToXML
from dccQuantityParser import parseItemFromJsonDict
from xmlschema import XMLSchemaValidationError
import copy

@pytest.mark.filterwarnings("ignore:Parsing a correctly marked non D-SI unit")
@pytest.mark.filterwarnings("ignore:The identifier .* does not match any D-SI units!")
def test_allFilesBackAndForthSer():
    # load our list of known-invalid files
    filePath = get_test_file(
        "tests", "data", "private", "1_7calibrationanddccsampledata",
        "AndereScheine", "grabbedFiles", "validation_results.json"
    )
    dirPath = get_test_file(
        "tests", "data", "private", "1_7calibrationanddccsampledata",
        "AndereScheine", "grabbedFiles")
    with open(filePath, "r") as validationFile:
        validationDict = json.load(validationFile)
    invalidFileNames = [
        "dcc-2019-75056_mod.xml",
        "DCCTableXMLStub.xml",
        "test_xmlDumpingSingleQuantNoUncer.xml",
        "test_dccQuantTabXMLDumping.xml",
        "CalSchein_20220708_8305_SN1842876.xml",
        "dcc-vacuumlab-CDG.xml",
        "acoustics_refTypeDefinition.xml"
    ]
    # add any others flagged in the validation results
    invalidFileNames += [
        entry["Invalid File"] for entry in validationDict.values()
    ]
    allowed_reason = "value doesn't match any pattern of ['3\\\\.3\\\\.0']"
    # iterate every XML that isn't already known-bad
    #TODO test all files and fix things like quants WO a name
    for fileCount,xmlFile in enumerate(dirPath.rglob("*.xml")):
    #for xmlFile in [get_test_file( "tests", "data", "private", "1_7calibrationanddccsampledata","sinCal","sin_acceleration_example_dcc","sin_acceleration_example_dcc_WithExampleConformatyStatment.xml")]:
        if xmlFile.name in invalidFileNames:
            continue
        with open(xmlFile, "r") as f:
            xml_text = f.read()
        xmlDict, errors = XMLToDict(xml_text)
        # update schema Version brutaly to 3.3.0
        xmlDict['@xsi:schemaLocation']=r'https://ptb.de/dcc https://ptb.de/dcc/v3.3.0/dcc.xsd'
        xmlDict['@schemaVersion'] = '3.3.0'

        xmlDictcopy=copy.deepcopy(xmlDict)

        serDict, quantList = replaceQuantitiesInDict(xmlDictcopy, parser=parseItemFromJsonDict,returnQuantityList=True)
        assert len(quantList) > 0
        json_text = json.dumps(serDict, cls=DCCJSONEncoder)
        dictForConversion=json.loads(json_text)
        xml_out, root_elem, errors = DictToXML(dictForConversion)
        assert xml_out, f"No XML produced for {xmlFile.name}"
        # Filter out the one allowed schema‐validation complaint
        remaining = [
            err for err in errors
            if not (
                isinstance(err, XMLSchemaValidationError)
                and err.reason.startswith("value doesn't match any pattern of ")
            )
        ]
        # If anything unexpected remains, fail
        assert not remaining, (
            f"Unexpected validation errors in {xmlFile.name}:\n"
            + "\n".join(f"  • {type(err).__name__}: {getattr(err, 'reason', err)}"
                        for err in remaining)
        )


def test_parsedQuantValuesAndFunctions():    # Use the correct relative paths
    try:
        test_file = get_test_file("tests", "data", "simpleSineCalibration.xml")
        with open(test_file, "r") as xml_file:
            xml_data = xml_file.read()
    except FileNotFoundError as e:
        warnings.warn(str(e))
    parsedQuants = parse(xml_data)
    Amplitude = parsedQuants[11]
    Frequenz = parsedQuants[10]
    Frequenz10Times10 = Frequenz[10] * 10
    assert Frequenz10Times10.data.data[0].value == 1000
    assert str(Frequenz10Times10.data.unit[0]) == r'\hertz'
    assert Frequenz.id != Frequenz10Times10.id
    Frequenz10Div10 = Frequenz[10] / 10
    assert Frequenz10Div10.data.data[0].value == 10
    freqSquared = Frequenz[10:15] * Frequenz[5:10]
    assert str(freqSquared.data.unit[0]) == r'\hertz\tothe{2}'
    first5Freqs = Frequenz[:5]
    assert first5Freqs.id != Frequenz.id
    outOfrangeFreqs = Frequenz[20:100]
    assert len(outOfrangeFreqs)==11
    boolIndexdFreqs = first5Freqs[np.array([True, False, True, False, False])]
    assert len(boolIndexdFreqs)==2
    boolIndexdFreqs = first5Freqs[True, False, True, False, False]
    assert len(boolIndexdFreqs)==2


def test_321AbsUncerParsing():
    # Use the correct relative paths
    try:
        test_file = get_test_file("tests", "data", "simpleSineCalibration.xml")
        with open(test_file, "r") as xml_file:
            xml_data = xml_file.read()
    except FileNotFoundError as e:
        warnings.warn(str(e))


def test_basic():
    # Use the correct relative paths
    try:
        test_file = get_test_file("tests", "data", "simpleSineCalibration.xml")
        with open(test_file, "r") as xml_file:
            xml_data = xml_file.read()
        parse(xml_data)
    except FileNotFoundError as e:
        warnings.warn(str(e))

    # test remove since 3.3.0.rc1 dosnt use correct dsi 2.2 syntax :(
    # Test with the private test data file (1st example)
    #try:
    #       test_file = get_test_file(
    #        "tests", "data", "private", "1_7calibrationanddccsampledata",
    #        "AndereScheine", "example-ISO376.xml"
    #    )
    #    with open(test_file) as xml_file:
    #        xml_data = xml_file.read()
    #    parse(xml_data)
    #except FileNotFoundError as e:
    #    warnings.warn(str(e))

    # Test with the private test data file (2nd example)
    try:
        test_file = get_test_file(
            "tests", "data", "private", "1_7calibrationanddccsampledata",
            "AndereScheine", "grabbedFiles", "downloads",
            "DKD-Akustik-DCC", "4180_2583081_XMLList_GP.xml"
        )
        with open(test_file) as xml_file:
            xml_data = xml_file.read()
        parse(xml_data)
    except FileNotFoundError as e:
        warnings.warn(str(e))

    # Test with the private test data file (3rd example)
    try:
        test_file = get_test_file(
            "tests", "data", "private", "1_7calibrationanddccsampledata",
            "AndereScheine", "grabbedFiles", "downloads", "vl-dcc",
            "Keithley_DAQ6510_4427944.xml"
        )
        with open(test_file) as xml_file:
            xml_data = xml_file.read()
        parse(xml_data)
    except FileNotFoundError as e:
        warnings.warn(str(e))


def test_bamSchein():
    try:
        test_file = get_test_file(
            "tests", "data", "private", "qi-digital-dcc",
            "BAM_Pt100-DCC_8.1I1496A-V6.1a-SEALED.xml"
        )
        with open(test_file) as xml_file:
            xml_data = xml_file.read()
        parse(xml_data)
    except FileNotFoundError as e:
        warnings.warn(str(e))


@pytest.mark.filterwarnings("ignore:Parsing a correctly marked non D-SI unit")
@pytest.mark.filterwarnings("ignore:The identifier .* does not match any D-SI units!")
def test_allFiles():
    try:
        filePath = get_test_file(
            "tests", "data", "private", "1_7calibrationanddccsampledata",
            "AndereScheine", "grabbedFiles", "validation_results.json"
        )
        dirPath = get_test_file(
            "tests", "data", "private", "1_7calibrationanddccsampledata",
            "AndereScheine", "grabbedFiles")
        with open(filePath, "r") as validationFile:
            validationDict = json.load(validationFile)
    except FileNotFoundError as e:
        warnings.warn(str(e))

    invalidFileNames = [
        "dcc-2019-75056_mod.xml",
        "DCCTableXMLStub.xml",
        "test_xmlDumpingSingleQuantNoUncer.xml",
        "test_dccQuantTabXMLDumping.xml",
        "CalSchein_20220708_8305_SN1842876.xml",
        "dcc-vacuumlab-CDG.xml",
        "acoustics_refTypeDefinition.xml"
    ]  # Invalid files that don't appear in the validation result json
    for item in validationDict.items():
        invalidFileNames.append(item[1]["Invalid File"])

    dccFiles = dirPath.rglob("*.xml")
    for dccFile in dccFiles:
        if dccFile.name not in invalidFileNames:
            with open(dccFile, "r") as file:
                try:
                    quantTypeObjects=parse(file.read())
                except Exception as e:
                    raise e

