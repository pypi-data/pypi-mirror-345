from pathlib import Path
from dccXMLJSONConv.dccConv import XMLToDict
# Define the root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent  # Resolve to the root folder

# File-wide variable for the absolute fallback path
ALTERNATIVE_ABS_PATH = Path("/builds/digitaldynamicmeasurement/dccQuantities/")  # Replace with your fallback path

def get_test_file(*path_parts,asDict=False):
    """
    Tries to fetch the test file, first relative to the current working directory.
    If it doesn't exist, it falls back to the absolute path specified by `ALTERNATIVE_ABS_PATH`.
    """
    # Try relative to the root directory
    test_file = ROOT_DIR / Path(*path_parts)
    if test_file.exists():
        if not asDict:
            return test_file
        else:
            with open(test_file, "r") as xml_file:
                xml_data = xml_file.read()
            return XMLToDict(str(xml_data))[0]
    else:
        # If not found, fall back to the absolute path
        test_file = ALTERNATIVE_ABS_PATH / Path(*path_parts)
        if test_file.exists():
            if not asDict:
                return test_file
            else:
                with open(test_file, "r") as xml_file:
                    xml_data = xml_file.read()
                return XMLToDict(str(xml_data))[0]
        else:
            raise FileNotFoundError(f"Test file not found at {test_file}")