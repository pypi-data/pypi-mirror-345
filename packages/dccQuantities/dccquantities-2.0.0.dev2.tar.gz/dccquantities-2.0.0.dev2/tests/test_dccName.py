import pytest
from DccName import DccName

def test_to_json_dict():
    jsonDict = {'dcc:name':{'dcc:content': [{'@lang': 'en', '$': 'Room temperature during calibration'}, {'@lang': 'de', '$': 'Raumtemperatur währenden der Kalibration'}]}}
    parsedDict = {'en': 'Room temperature during calibration', 'de': 'Raumtemperatur währenden der Kalibration'}
    nameInstance = DccName(parsedDict)
    generatedJsonDict = nameInstance.to_json_dict()
    assert jsonDict == generatedJsonDict

def test_matches_with_subset_dict():
    content = {'en': 'Frequency', 'de': 'Frequenz', 'fr': 'Fréquence'}
    name_instance = DccName(content)
    subset = {'en': 'Frequency', 'de': 'Frequenz'}
    # Should return True if the subset's key/value pairs exist in name_instance
    assert name_instance.matches(subset) is True

def test_matches_with_exact_dict():
    content = {'en': 'Frequency', 'de': 'Frequenz'}
    name_instance = DccName(content)
    # Exact match should succeed
    assert name_instance.matches(content) is True

def test_matches_with_non_subset_dict():
    content = {'en': 'Frequency', 'de': 'Frequenz'}
    name_instance = DccName(content)
    non_subset = {'en': 'Frequency', 'it': 'Frequenza'}
    # 'it' key is missing in name_instance, so should return False
    assert name_instance.matches(non_subset) is False

def test_matches_with_non_matching_value_dict():
    content = {'en': 'Frequency', 'de': 'Frequenz'}
    name_instance = DccName(content)
    mismatch = {'en': 'Frequency', 'de': 'Speed'}  # Value for 'de' does not match
    assert name_instance.matches(mismatch) is False

def test_matches_with_dccname_argument():
    content = {'en': 'Frequency', 'de': 'Frequenz'}
    name_instance = DccName(content)
    other = DccName({'en': 'Frequency'})
    # A DccName instance is acceptable as argument
    assert name_instance.matches(other) is True

def test_matches_with_string_found():
    content = {'en': 'Frequency', 'de': 'Frequenz'}
    name_instance = DccName(content)
    # Should return True because 'Frequency' is a value in name_instance
    assert name_instance.matches('Frequency') is True

def test_matches_with_string_not_found():
    content = {'en': 'Frequency', 'de': 'Frequenz'}
    name_instance = DccName(content)
    # 'Speed' is not a value in name_instance, so should return False
    assert name_instance.matches('Speed') is False

def test_matches_with_invalid_type():
    content = {'en': 'Frequency', 'de': 'Frequenz'}
    name_instance = DccName(content)
    # Passing an int should raise a TypeError
    with pytest.raises(TypeError):
        name_instance.matches(123)