from pathlib import Path
import warnings
import os
import pytest
from dccQuantityParser import parse

# Define the root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent  # Resolves to the root folder

# File-wide variable for the absolute fallback path
ALTERNATIVE_ABS_PATH = Path("/builds/digitaldynamicmeasurement/dccQuantities/")  # Replace with your fallback path

def get_test_file(*path_parts):
    """
    Tries to fetch the test file, first relative to the current working directory.
    If it doesn't exist, it falls back to the absolute path specified by ALTERNATIVE_ABS_PATH.
    """
    # Try relative to the root directory
    test_file = ROOT_DIR / Path(*path_parts)
    if test_file.exists():
        return test_file
    else:
        # If not found, fall back to the absolute path
        test_file = ALTERNATIVE_ABS_PATH / Path(*path_parts)
        if test_file.exists():
            return test_file
        else:
            raise FileNotFoundError(f"Test file not found at {test_file}")

# Define a fixture with module scope so that the XML file is parsed once per test module.
@pytest.fixture(scope="module")
def parsed_quantities():
    """
    Parse the XML file once and return the parsed quantities.
    Any test that accepts the 'parsed_quantities' fixture will reuse this parsed instance.
    """
    test_file = get_test_file("tests", "data", "simpleSineCalibration.xml")
    with open(test_file, "r") as xml_file:
        xml_data = xml_file.read()
    parsed_quants = parse(xml_data)
    return parsed_quants

def test_vlauesAndUncerMethodes(parsed_quantities):
    #Simple non Uncer Data
    freqs=parsed_quantities[10]
    values=freqs.values
    with pytest.raises(AttributeError, match="This siRealList doesn't has any uncer associated!"):
        uncer=freqs.uncertainties
    chargSens=parsed_quantities[12]
    chargSensValues=chargSens.values
    chargSensUncers=chargSens.uncertainties
    assert parsed_quantities is not None
    # You can now run several tests using parsed_quantities without re-parsing.
    # For example:
    # assert parsed_quantities.someValue == expected_value
    # assert parsed_quantities.someFunction() == expected_result
