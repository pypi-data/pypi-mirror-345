from helpers import *
import numpy as np
import pytest

def test_isListOfTypes():
    assert isListOfTypes([1, 2, 3], [int])
    assert not isListOfTypes([1, 2, 3.0], [int])
    assert isListOfTypes([1, 2, 3.3], [int, float])
    assert isListOfTypes(np.array([1, 2, 3]), [np.integer])


def test_get_exact_slice_single():
    index_vector = [0.0, 0.5, 1.0, 1.5, 2.0]
    s = get_exact_slice(index_vector, 1.0)
    # 1.0 is at index 2 → expected slice(2, 3)
    assert s==2

def test_get_exact_slice_multiple_matches():
    index_vector = np.array([1.0, 1.0, 2.0, 3.0])
    s = get_exact_slice(index_vector, 1.0)
    # Expected unique indices: [0, 1] → slice(0, 2)
    assert s.start==0
    assert s.stop==2
    assert s.step==1

def test_get_exact_slice_no_match():
    index_vector = np.array([0.0, 0.5, 1.0, 1.5, 2.0])
    with pytest.raises(ValueError, match="No match found for query"):
        get_exact_slice(index_vector, 3.0)

def test_get_exact_slice_list_query():
    index_vector = [0.0, 0.5, 1.0, 1.5, 2.0]
    # Querying two values: 0.5 and 1.5 → expected unique indices: [1, 3] → slice(1, 4)
    s = get_exact_slice(index_vector, [0.5, 1.5])
    assert s.start==1
    assert s.stop==5
    assert s.step==2

# Tests for get_conditional_slice

def test_get_conditional_slice_le():
    index_vector = [0.0, 0.5, 1.0, 1.5, 2.0]
    # Condition ('<=', 1.0) → indices [0,1,2] → slice(0,3)
    s = get_conditional_slice(index_vector, ('<=', 1.0))
    assert s.start == 0 and s.stop == 3

def test_get_conditional_slice_gt():
    index_vector = [0.0, 0.5, 1.0, 1.5, 2.0]
    # Condition ('>', 1.0) → indices [3,4] → slice(3,5)
    s = get_conditional_slice(index_vector, ('>', 1.0))
    assert s.start == 3 and s.stop == 5

def test_get_conditional_slice_equal():
    index_vector = [0.0, 0.5, 1.0, 1.5, 2.0]
    s = get_conditional_slice(index_vector, ('==', 1.5))
    assert s.start == 3 and s.stop == 4

def test_get_conditional_slice_no_match():
    index_vector = [0.0, 0.5, 1.0, 1.5, 2.0]
    with pytest.raises(ValueError, match="No indices satisfy condition"):
        get_conditional_slice(index_vector, ('<', -1.0))

def test_get_conditional_slice_unsupported_operator():
    index_vector = [0.0, 0.5, 1.0, 1.5, 2.0]
    with pytest.raises(ValueError, match="Unsupported operator"):
        get_conditional_slice(index_vector, ('**', 1.0))

# Tests for get_nearest_slice

def test_get_nearest_slice_exact_match():
    index_vector = [0.0, 0.5, 1.0, 1.5, 2.0]
    # Query 1.5 exists exactly (index 3)
    s = get_nearest_slice(index_vector, 1.5, mode='absolute')
    assert s==3

def test_get_nearest_slice_lower():
    index_vector = [0.0, 0.5, 1.0, 1.5, 2.0]
    # Query 1.2, mode 'lower' → candidates: indices [0,1,2] → max is index 2
    s = get_nearest_slice(index_vector, 1.2, mode='lower')
    assert s==2

def test_get_nearest_slice_higher():
    index_vector = [0.0, 0.5, 1.0, 1.5, 2.0]
    # Query 1.2, mode 'higher' → candidates: indices [3,4] → min is index 3
    s = get_nearest_slice(index_vector, 1.2, mode='higher')
    assert s ==3

def test_get_nearest_slice_absolute():
    index_vector = [0.0, 0.5, 1.0, 1.5, 2.0]
    # Query 1.2, mode 'absolute' → diff: [1.2,0.7,0.2,0.3,0.8] → closest index is 2
    s = get_nearest_slice(index_vector, 1.2, mode='absolute')
    assert s == 2

def test_get_nearest_slice_tie():
    # Create a tie: index_vector with two equally near values.
    index_vector = [1.0, 1.5, 2.0, 10.0, 1.5]
    # Query 1.75 → diffs: [0.75, 0.25, 0.25] → tie between indices 1 and 2.
    with pytest.warns(UserWarning, match="Multiple indices equally near"):
        s = get_nearest_slice(index_vector, 1.75, mode='absolute')
    # Expected unique indices: [1,2] → slice(1, 3)
    assert np.all(s == np.array([1,2,4]))

def test_get_nearest_slice_no_lower():
    index_vector = [1.0, 1.5, 2.0]
    with pytest.raises(ValueError, match="No index found lower than or equal to"):
        get_nearest_slice(index_vector, 0.5, mode='lower')

def test_get_nearest_slice_no_higher():
    index_vector = [1.0, 1.5, 2.0]
    with pytest.raises(ValueError, match="No index found higher than or equal to"):
        get_nearest_slice(index_vector, 2.5, mode='higher')


def test_slice_AND():
    # Test 1: Intersection of two slices.
    result1 = slice_AND(slice(1, 10), slice(5, 15))
    expected1 = [5, 6, 7, 8, 9]
    assert result1 == expected1, f"Test 1 Failed: expected {expected1}, got {result1}"

    # Test 2: Intersection of a slice and a list.
    result2 = slice_AND(slice(0, 10, 2), [2, 3, 4, 6, 8])
    expected2 = [2,4, 6, 8]
    assert result2 == expected2, f"Test 2 Failed: expected {expected2}, got {result2}"

    # Test 3: Intersection of multiple iterables.
    result3 = slice_AND([1, 2, 3, 4, 5], [3, 4, 5, 6, 7], [0, 4, 5, 3])
    expected3 = [3, 4, 5]
    assert result3 == expected3, f"Test 3 Failed: expected {expected3}, got {result3}"

    # Test 4: Mixed types with one unconstraining input.
    inputs = [None, slice(0, 5), [2, 3, 4, 5, 6]]
    result4 = slice_AND(inputs)
    expected4 = [2, 3, 4]  # Intersection of slice(0,5) -> {0,1,2,3,4} and [2,3,4,5,6] -> {2,3,4,5,6} is {2,3,4}
    assert result4 == expected4, f"Test 4 Failed: expected {expected4}, got {result4}"

    # Test 5: Only unconstrained inputs (should raise ValueError).
    try:
        _ = slice_AND(None, slice(None))
    except ValueError as e:
        pass
    else:
        assert False, "Test 5 Failed: Expected ValueError for all unconstrained inputs."

    print("All tests passed.")