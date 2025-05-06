from helpers import findTables
import numpy as np
import random
import pytest
from DccQuantityTable import DccQuantityTable
from testHelpers import get_test_file
from dsiUnits import dsiUnit

def test_tableFinder():
    test_file = get_test_file("tests", "data", "simpleSineCalibration.xml",asDict=True)

    tableDicts= findTables(test_file)
    assert len(tableDicts)==1
    test_file = get_test_file("tests", "data", "private","1_7calibrationanddccsampledata", "AndereScheine", "example-ISO376.xml",asDict=True)

    tableDicts= findTables(test_file)
    for i,tablePathesAndData in enumerate(tableDicts):
        try:
            table = DccQuantityTable.fromDict(tablePathesAndData[1])
        except Exception as e:
            print(tablePathesAndData[0])
            raise e

# Fixture to load the simple sine calibration file once per module.
@pytest.fixture(scope="module")
def simple_sine_calibration_file():
    return get_test_file("tests", "data", "simpleSineCalibration.xml", asDict=True)

@pytest.fixture(scope="module")
def simple_sine_calibration_2D_file():
    return get_test_file("tests", "data", "simpleSineCalibration2DTable.xml", asDict=True)

# Fixture to load the sample flat table file once per module.
@pytest.fixture(scope="module")
def sample_flat_table_file():
    return get_test_file("tests", "data", "sample_flat_table.xml", asDict=True)

# Fixture to parse and return the DccQuantityTable from the simple sine calibration file.
@pytest.fixture(scope="module")
def simple_sine_table(simple_sine_calibration_file):
    table_dicts = findTables(simple_sine_calibration_file)
    return DccQuantityTable.fromDict(table_dicts[0][1])

# Fixture to parse and return the DccQuantityTable from the sample flat table file.
@pytest.fixture(scope="module")
def sample_flat_table(sample_flat_table_file):
    table_dicts = findTables(sample_flat_table_file)
    return DccQuantityTable.fromDict(table_dicts[0][1])

# Fixture to parse and return the DccQuantityTable from the simple sine calibration file.
@pytest.fixture(scope="module")
def simple_sine_table2D(simple_sine_calibration_2D_file):
    table_dicts = findTables(simple_sine_calibration_2D_file)
    return DccQuantityTable.fromDict(table_dicts[0][1])

def test_flat_table_shape(sample_flat_table):
    # Test that the flat table is correctly parsed.
    assert sample_flat_table is not None
    assert sample_flat_table.shape == (10, 10)


def test_getQuantityByName(simple_sine_table):
    # Test that the simple sine table is properly parsed.
    amplitudeQuantityID_EN = simple_sine_table.getQunatitysIDsByName('Acceleration Amplitude')
    amplitudeQuantityID_DE = simple_sine_table.getQunatitysIDsByName('Beschleunigungsamplitude')
    amplitudeQuantityID_DE2 = simple_sine_table.getQunatitysIDsByName({'de': 'Beschleunigungsamplitude'})
    assert amplitudeQuantityID_EN == amplitudeQuantityID_DE == amplitudeQuantityID_DE2
    wrongQuantityID = simple_sine_table.getQunatitysIDsByName('Acceleration Amplidsad dysafdsa fas fatude')
    assert wrongQuantityID is None


def test_getQuantityByRefType(simple_sine_table):
    # Test that the simple sine table is properly parsed.
    frequencyQuantityID_fromName = simple_sine_table.getQunatitysIDsByName('Frequenz')
    frequencyQuantityID_fromRefType1 = simple_sine_table.getQunatitysIDsByrefType('vib_frequency')
    frequencyQuantityID_fromRefType2 = simple_sine_table.getQunatitysIDsByrefType('vib_nominalFrequency')
    frequencyQuantityID_fromRefType3 = simple_sine_table.getQunatitysIDsByrefType('basic_TableIndex0')
    assert frequencyQuantityID_fromName == frequencyQuantityID_fromRefType1 == frequencyQuantityID_fromRefType2 == frequencyQuantityID_fromRefType3
    phaseQuantityIDs = simple_sine_table.getQunatitysIDsByrefType('vib_phase')
    assert len(phaseQuantityIDs) == 2
    wrongQuantityID = simple_sine_table.getQunatitysIDsByrefType('foo')
    assert wrongQuantityID is None

def test_logTableTOJSON(simple_sine_table):
    jsondict=simple_sine_table.toJsonDict()
    #TODO improve this test to test somthing meaning full and not just no errors risen
    assert jsondict is not None
    assert jsondict['dcc:list'] is not None

def test_flatTableTOJSON(sample_flat_table):
    jsondict=sample_flat_table.toJsonDict()
    # TODO improve this test to test somthing meaning full and not just no errors risen
    assert jsondict is not None
    assert jsondict['dcc:list'] is not None

def test_tablegetIdByUnits(simple_sine_table):
    frequencyQuantityID_fromUnitStr = simple_sine_table.getQunatitysIDsByUnit(r'\hertz')
    frequencyQuantityID_fromUnitUnit = simple_sine_table.getQunatitysIDsByUnit(dsiUnit(r'\hertz'))
    assert frequencyQuantityID_fromUnitStr == frequencyQuantityID_fromUnitUnit
    radQuantityIDs = simple_sine_table.getQunatitysIDsByUnit(dsiUnit(r'\radian'))
    assert len(radQuantityIDs) == 2

def test_longTableGetQuantity(simple_sine_table):
    # First, get a valid quantity by ID (this should not raise an error)
    frequencyQuantityID = simple_sine_table.getQunatitysIDsByUnit(r'\hertz')
    frequencyQuant = simple_sine_table[frequencyQuantityID]
    assert frequencyQuant is not None

    # Now, access by string keys that will trigger a KeyError.
    # We expect the error message to include links to the helper member functions.
    with pytest.raises(KeyError) as excinfo:
        _ = simple_sine_table['Frequenz']
    error_msg = str(excinfo.value)
    assert "is type str but  not an id of an Quantity in this table." in error_msg
    # Check that the error message contains a “link” to the member functions.
    # Use Sphinx-style linking if desired.
    assert (":meth:`getQunatitysIDsByUnit`" in error_msg or ".getQunatitysIDsByUnit" in error_msg)
    assert (":meth:`getQunatitysIDsByrefType`" in error_msg or ".getQunatitysIDsByrefType" in error_msg)
    assert (":meth:`getQunatitysIDsByName`" in error_msg or ".getQunatitysIDsByName" in error_msg)

    with pytest.raises(KeyError) as excinfo:
        _ = simple_sine_table['vib_frequency']
    error_msg = str(excinfo.value)
    assert "is type str but  not an id of an Quantity in this table." in error_msg

def test_1DlongTableIndexing(simple_sine_table):
    singleRow=simple_sine_table[10]
    sliced=simple_sine_table[10:15]
    everythirStartingWithSecond=simple_sine_table[1::3]
    with pytest.raises(IndexError) as excinfo:
        idxErrorIndexing = simple_sine_table[1::3,2]
    error_msg = str(excinfo.value)
    assert "DccLongTable does not support multi dimensional slices." in error_msg

def test_flat_table_getQuantity(sample_flat_table):
    # Test that the flat table is correctly parsed.
    dataID = sample_flat_table.getQunatitysIDsByName({'en': 'Flattened Data: Surface Area'})
    dataQuantity = sample_flat_table[dataID]
    assert dataQuantity is not None

    # Attempt to access by string key to trigger the KeyError.
    with pytest.raises(KeyError) as excinfo:
        _ = sample_flat_table['Flattened Data: Surface Area']
    error_msg = str(excinfo.value)
    assert "is type str but  not an id of an Quantity in this table." in error_msg
    # Verify that the error message links to the member functions.
    assert (":meth:`getQunatitysIDsByUnit`" in error_msg or ".getQunatitysIDsByUnit" in error_msg)
    assert (":meth:`getQunatitysIDsByrefType`" in error_msg or ".getQunatitysIDsByrefType" in error_msg)
    assert (":meth:`getQunatitysIDsByName`" in error_msg or ".getQunatitysIDsByName" in error_msg)

def test_flat_table_IndexLookUp(sample_flat_table):
    # TODO improve testing here but table construction is still ongoing
    slices = sample_flat_table.getIndexSlicesByCondition([('<',5.0),('>',13.0)])
    data = sample_flat_table[slices]
    slices2 = sample_flat_table.getIndexSlicesByCondition(('<',5.0),('>',13.0))
    data2 = sample_flat_table[slices2]

    slices3 = sample_flat_table.getNearestIndex(2.0,0.31)
    slices4 = sample_flat_table.getNearestIndex(2.05, 0.32)
    slices5 = sample_flat_table.getNearestIndex([2.05,2.99], [0.32,41.0,47.1])

    slices32 = sample_flat_table.getIndexFromValues(2.0,31.0)
    slices62 = sample_flat_table.getIndexFromValues([2.0, 3.0], [31.0, 41, 43])
    # catch error
    with pytest.raises(ValueError) as excinfo:
        _ = sample_flat_table.getIndexFromValues(2.05, 0.32)
    error_msg = str(excinfo.value)
    assert ("No match found" in error_msg)

def test_longTable_IndexLookUp(simple_sine_table,simple_sine_table2D):
    slice=simple_sine_table.getIndexSlicesByCondition(('>',100.0))
    assert slice.start==11
    assert  slice.stop==31
    assert slice.step==1

    idxs2=simple_sine_table2D.getIndexSlicesByCondition(('>',100.0),('<',100.0))
    idxs3 = simple_sine_table2D.getIndexSlicesByCondition(('<', 100.0), ('<', 10.0))
    data=simple_sine_table2D[idxs3]


    assert len(data)>0
    assert np.all(data[0][0].data.values<100.0)
    assert np.all(data[0][1].data.values < 10.0)
    idx4 = simple_sine_table2D.getIndexFromValues(20.0, 10.0)
    data2 = simple_sine_table2D[idx4]
    assert data2[0][0].data.values==20.0
    assert data2[0][1].data.values==10.0

def test_longTable_nestedConditionIndexLookUp(simple_sine_table2D):
    idxs = simple_sine_table2D.getIndexSlicesByCondition([('>',50),'AND',('<', 100.0)], ('>', 10.0))
    data=simple_sine_table2D[idxs]
    assert np.all(data[0][0].data.values<100.0)
    assert np.all(data[0][0].data.values > 50.0)
    assert np.all(data[0][1].data.values > 10.0)
    idxs2 = simple_sine_table2D.getIndexSlicesByCondition([[('>',50),'AND',('<', 100.0)],'OR',('<',15.0)], ('<', 10.0))
    print(idxs2)
    data=simple_sine_table2D[idxs2]
    assert np.all(data[0][0].data.values<100.0)
    assert np.all(data[0][0].data.values > 50.0) | np.all(data[0][0].data.values < 15.0)
    assert np.all(data[0][1].data.values < 10.0)

def test_flat_table_Indexing(sample_flat_table):
    # TODO improve testing here but table construction is still ongoing
    sliced=sample_flat_table[1:9,5:7]
    # Test that the flat table is correctly parsed.
    intIndexing=sample_flat_table[9,5]
    mixedIndexing=sample_flat_table[1:9,6]
    assert len(sliced)>0
    assert len(intIndexing)>0
    assert len(mixedIndexing)>0


def test_flatTableShort():
    test_file = get_test_file("tests", "data", "5DFlatTableParsingTest.xml",asDict=True)
    tableDicts= findTables(test_file)
    table = DccQuantityTable.fromDict(tableDicts[0][1])
    assert len(tableDicts)>0
    assert table.shape == (2, 3, 5, 7, 11)

def test_flatTableLong():
    test_file = get_test_file("tests", "data", "6DFlatTableParsingTest.xml",asDict=True)
    tableDicts= findTables(test_file)
    table = DccQuantityTable.fromDict(tableDicts[0][1])
    assert len(tableDicts)>0
    assert table.shape == (2, 3, 5, 7, 11, 13)

def prime_factors(n):
    """
    Return the prime factor decomposition of n as a list of factors.
    Assumes n is a positive integer.
    """
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def check_random_and_edge_flat_table_prime_factors(fileName):
    """
    Parse the flat table XML file and then:
      - Verify that the first element (at index (0,0,...,0)) equals the product
        of the first values of each index quantity.
      - Verify that the last element (at index (dim0-1,dim1-1,...,dimN-1)) equals the product
        of the last values of each index quantity.
      - Randomly pick 1000 entries and for each, verify that the value equals the product
        of the corresponding prime values from the index quantities.

      For every 100th random sample (as well as the first and last entries) a message is printed:
         data[indexes] = <actual value>;
         expected prime factors = <expected factors>;
         actual prime factors = <actual factors>;
         expected product = <expected product>

      All multiplications use np.int64 to avoid quantization issues.

      Additionally, the actual prime factor decomposition (via prime_factors) is checked against
      the expected prime factors.

      If any computed product exceeds 2**24, a flag is set and a statement is printed.

      Returns:
          A boolean flag indicating whether any expected product exceeded 2**24.
    """
    # Load the test XML file.
    test_file = get_test_file("tests", "data", fileName, asDict=True)
    tableDicts = findTables(test_file)
    assert len(tableDicts) > 0, "No table found in the provided XML file"

    # Construct the table object from the XML dictionary.
    table = DccQuantityTable.fromDict(tableDicts[0][1])
    dataQuantID=table.getQunatitysIDsByName({'en':'Flattened Data: Product'})
    # Get the reassembled n-D data array from the table (assumed to be in table[0].values).
    data_array = table[dataQuantID].values
    shape = table.shape  # e.g., (2,3,5,7,11) or (2,3,5,7,11,13)
    ndim = len(shape)
    assert data_array.shape == shape, f"Data array shape {data_array.shape} does not match table shape {shape}"

    # Flag to check if any computed product exceeds 2**24.
    large_numbers_processed = False

    # Helper to compute the expected product using int64 arithmetic.
    # Also returns the expected prime factors (as a list) in the order of the dimensions.
    def compute_product(idx):
        nonlocal large_numbers_processed
        prod = np.int64(1)
        expected_pf = []
        for dim, pos in enumerate(idx):
            val = np.int64(table._idxQuantities[dim].values[pos])
            expected_pf.append(val)
            prod *= val
        if prod > (2 ** 24):
            large_numbers_processed = True
        return prod, expected_pf

    # --- Edge Check: First Element ---
    first_index = (0,) * ndim
    expected_first, expected_pf_first = compute_product(first_index)
    actual_first = np.int64(data_array[first_index])
    # Compute actual prime factors from the actual value using our prime_factors function.
    actual_pf_first = prime_factors(int(actual_first))
    print(f"Edge check (first): data{first_index} = {actual_first}; "
          f"expected prime factors = {[int(x) for x in expected_pf_first]}; "
          f"actual prime factors = {actual_pf_first}; "
          f"expected product = {expected_first}")
    assert actual_first == expected_first, (
        f"Mismatch at first index {first_index}: expected {expected_first}, got {actual_first}"
    )
    assert actual_pf_first == [int(x) for x in expected_pf_first], (
        f"Prime factor mismatch at first index {first_index}: expected {[int(x) for x in expected_pf_first]}, got {actual_pf_first}"
    )

    # --- Edge Check: Last Element ---
    last_index = tuple(dim - 1 for dim in shape)
    expected_last, expected_pf_last = compute_product(last_index)
    actual_last = np.int64(data_array[last_index])
    actual_pf_last = prime_factors(int(actual_last))
    print(f"Edge check (last): data{last_index} = {actual_last}; "
          f"expected prime factors = {[int(x) for x in expected_pf_last]}; "
          f"actual prime factors = {actual_pf_last}; "
          f"expected product = {expected_last}")
    assert actual_last == expected_last, (
        f"Mismatch at last index {last_index}: expected {expected_last}, got {actual_last}"
    )
    assert actual_pf_last == [int(x) for x in expected_pf_last], (
        f"Prime factor mismatch at last index {last_index}: expected {[int(x) for x in expected_pf_last]}, got {actual_pf_last}"
    )

    # --- Random Sampling: 1000 Random Multi-Indices ---
    for i in range(1000):
        idx = tuple(random.randint(0, dim - 1) for dim in shape)
        expected_value, expected_pf = compute_product(idx)
        actual_value = np.int64(data_array[idx])
        actual_pf = prime_factors(int(actual_value))
        if i % 100 == 0:
            print(f"Random check {i:04d}: data{idx} = {actual_value}; "
                  f"expected prime factors = {[int(x) for x in expected_pf]}; "
                  f"actual prime factors = {actual_pf}; "
                  f"expected product = {expected_value}")
        assert actual_value == expected_value, (
            f"Mismatch at index {idx}: expected {expected_value}, got {actual_value}"
        )
        assert actual_pf == [int(x) for x in expected_pf], (
            f"Prime factor mismatch at index {idx}: expected {[int(x) for x in expected_pf]}, got {actual_pf}"
        )

    if large_numbers_processed:
        print("FlattArray Test performed, numbers larger than 2^24 have been processed.")
    return large_numbers_processed


def test_primeFactoredFlatTables():
    # For the 5D table, we don't necessarily require large numbers.
    flag_5d = check_random_and_edge_flat_table_prime_factors('5DFlatTableParsingTest.xml')
    # For the 6D table, we expect large products.
    flag_6d = check_random_and_edge_flat_table_prime_factors('6DFlatTableParsingTest.xml')
    # Assert that the 6D table test did process numbers larger than 2^24.
    assert flag_6d, "6D table test did not process numbers larger than 2^24 as expected."

