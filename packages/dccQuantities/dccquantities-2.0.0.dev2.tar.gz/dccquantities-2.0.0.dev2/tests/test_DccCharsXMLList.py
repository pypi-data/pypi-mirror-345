from DccCharsXMLList import DccCharsXMLList
import pytest


def test_repr():
    testList = DccCharsXMLList(["a", "b", "c"])
    assert repr(testList) == "DccCharsXMLList.DccCharsXMLList(data=['a', 'b', 'c'])"


def test_str():
    testList = DccCharsXMLList(["a", "b", "c"])
    assert str(testList) == "['a', 'b', 'c']"


def test_add():
    testList1 = DccCharsXMLList(["a", "b", "c"])
    testList2 = DccCharsXMLList(["d", "e", "f"])
    result = testList1 + testList2
    assert result.data == ["a", "b", "c", "d", "e", "f"]
    with pytest.warns(RuntimeWarning, match=r'Concatenating DccCharsXMLList and list!'):
        result = testList1 + [1, 2, 3]
        assert result.data == ["a", "b", "c", 1, 2, 3]
    with pytest.warns(RuntimeWarning, match=r'Concatenating DccCharsXMLList and list!'):
        result = [1, 2, 3] + testList2
        assert result.data == [1, 2, 3, "d", "e", "f"]

def test_sorted():
    sortedList1 = DccCharsXMLList(["a", "b", "c"])
    sortedList2 = DccCharsXMLList(["0001", "AA", "FE"])
    unsortedList1 = DccCharsXMLList(["CDE", "AA", "FE"])
    unsortedList2 = DccCharsXMLList(["Qsafdadsf", "Adsafas A", "FE"])
    assert sortedList1.sorted
    assert sortedList2.sorted
    assert not unsortedList1.sorted
    assert not unsortedList2.sorted