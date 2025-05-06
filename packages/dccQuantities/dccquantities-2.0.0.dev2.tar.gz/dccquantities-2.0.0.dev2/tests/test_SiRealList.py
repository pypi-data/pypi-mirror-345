from SiRealList import SiRealList
import datetime
from metas_unclib import *
import warnings
import pytest
def test_hasSameValue():
    testSiRealList = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    assert testSiRealList.hasSameValue(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)]
    )


def test_sorted():
    testSiRealListSorted = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    testSiRealListSorted2 = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(1e-12), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    testSiRealListSorted3 = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    testSiRealListSortedUnc = SiRealList(
        data=[ufloat(-0.1,0.05), ufloat(0.0,0.05), ufloat(0.1,0.05), ufloat(0.2,0.05)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    testSiRealListNotSorted = SiRealList(
        data=[ufloat(0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    testSiRealListNotSortedUnc = SiRealList(
        data=[ufloat(0.1,0.05), ufloat(0.0,0.05), ufloat(0.1,0.05), ufloat(0.2,0.05)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    testSiRealListShapedSortedUnc = SiRealList(
        data=[ufloat(0.1,0.05), ufloat(0.0,0.05), ufloat(0.1,0.05), ufloat(0.2,0.05),ufloat(0.1,0.05), ufloat(0.0,0.05), ufloat(0.1,0.05), ufloat(0.2,0.05)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    testSiRealListShapedSortedUnc.reshape(2,4)
    assert testSiRealListSorted.sorted
    assert testSiRealListSorted2.sorted
    assert testSiRealListSorted3.sorted
    assert testSiRealListSortedUnc.sorted
    assert not testSiRealListNotSorted.sorted
    assert not testSiRealListNotSortedUnc.sorted
    # Catch the warning for reshaped data
    with pytest.warns(RuntimeWarning, match="sorted is only implemented for 1D data. Returning False"):
        assert not testSiRealListShapedSortedUnc.sorted

def test_hasSameParameters():
    now = datetime.datetime.now()
    testSiRealList1 = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[now],
    )
    testSiRealList2 = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[now],
    )
    assert testSiRealList1.hasSameParameters(testSiRealList2)
    testSiRealList2.label = ["foo"]
    assert not testSiRealList1.hasSameParameters(testSiRealList2)


def test_neg():
    testSiRealList = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    assert (-testSiRealList).hasSameValue(
        [ufloat(0.1), ufloat(0.0), ufloat(-0.1), ufloat(-0.2)]
    )
    assert (-testSiRealList).label == ["-test"]


def test_add_single_value():
    testSiRealList = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    b = 1
    assert (testSiRealList + b).hasSameValue(
        [ufloat(-0.1 + b), ufloat(0.0 + b), ufloat(0.1 + b), ufloat(0.2 + b)]
    )
    assert (testSiRealList + b).label == ["test"]
    b = 0.1
    testSiRealList.label = ["test1", "test2", "test3", "test4"]
    assert (testSiRealList + b).hasSameValue(
        [ufloat(-0.1 + b), ufloat(0.0 + b), ufloat(0.1 + b), ufloat(0.2 + b)]
    )
    assert (testSiRealList + b).label == ["test1", "test2", "test3", "test4"]
    b = ufloat(0.2)
    assert (testSiRealList + b).hasSameValue(
        [ufloat(-0.1) + b, ufloat(0.0) + b, ufloat(0.1) + b, ufloat(0.2) + b]
    )


def test_add_list():
    testSiRealList = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    b = [1]
    assert (testSiRealList + b).hasSameParameters(testSiRealList + b[0])
    assert (testSiRealList + b).label == ["test"]
    testSiRealList.label = ["test1", "test2", "test3", "test4"]
    assert (testSiRealList + b).label == ["test1", "test2", "test3", "test4"]
    b = [0.1, 0.2, 0.3, -2.5]
    assert (testSiRealList + b).hasSameValue(
        [
            ufloat(-0.1 + b[0]),
            ufloat(0.0 + b[1]),
            ufloat(0.1 + b[2]),
            ufloat(0.2 + b[3]),
        ]
    )
    b = [ufloat(0.2)]
    assert (testSiRealList + b).hasSameValue(
        [
            ufloat(-0.1) + b[0],
            ufloat(0.0) + b[0],
            ufloat(0.1) + b[0],
            ufloat(0.2) + b[0],
        ]
    )
    b = [ufloat(0.1), ufloat(0.3), ufloat(0.3), ufloat(0.7)]
    assert (testSiRealList + b).hasSameValue(
        [
            ufloat(-0.1) + b[0],
            ufloat(0.0) + b[1],
            ufloat(0.1) + b[2],
            ufloat(0.2) + b[3],
        ]
    )


def test_add_SiRealList():
    testSiRealList1 = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test1"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    testSiRealList2 = SiRealList(
        data=[ufloat(-10.0), ufloat(30.0), ufloat(30.0), ufloat(70.7)],
        label=["test2a", "test2b", "test2c", "test2d"],
        unit=[r"\milli\volt"],
        dateTime=[datetime.datetime.now()],
    )
    result = testSiRealList1 + testSiRealList2
    assert result.label == [
        "test1+test2a",
        "test1+test2b",
        "test1+test2c",
        "test1+test2d",
    ]
    assert result.hasSameValue(
        [ufloat(-0.11), ufloat(0.03), ufloat(0.13), ufloat(0.2707)]
    )



def test_sub_single_value():
    testSiRealList = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    b = 1
    assert (testSiRealList - b).hasSameValue(
        [ufloat(-0.1 - b), ufloat(0.0 - b), ufloat(0.1 - b), ufloat(0.2 - b)]
    )
    assert (testSiRealList - b).label == ["test"]
    testSiRealList.label = ["test2a", "test2b", "test2c", "test2d"]
    assert (testSiRealList - b).label == ["test2a", "test2b", "test2c", "test2d"]
    b = 0.1
    assert (testSiRealList - b).hasSameValue(
        [ufloat(-0.1 - b), ufloat(0.0 - b), ufloat(0.1 - b), ufloat(0.2 - b)]
    )
    b = ufloat(0.2)
    assert (testSiRealList - b).hasSameValue(
        [ufloat(-0.1) - b, ufloat(0.0) - b, ufloat(0.1) - b, ufloat(0.2) - b]
    )


def test_sub_list():
    testSiRealList = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    b = [1]
    assert (testSiRealList - b).hasSameParameters(testSiRealList - b[0])
    assert (testSiRealList - b).label == ["test"]
    testSiRealList.label = ["test2a", "test2b", "test2c", "test2d"]
    assert (testSiRealList - b).label == ["test2a", "test2b", "test2c", "test2d"]
    assert (b - testSiRealList).label == ["-test2a", "-test2b", "-test2c", "-test2d"]
    b = [0.1, 0.2, 0.3, -2.5]
    assert (testSiRealList - b).hasSameValue(
        [
            ufloat(-0.1 - b[0]),
            ufloat(0.0 - b[1]),
            ufloat(0.1 - b[2]),
            ufloat(0.2 - b[3]),
        ]
    )
    b = [ufloat(0.2)]
    assert (b - testSiRealList).hasSameValue(
        [
            b[0] - ufloat(-0.1),
            b[0] - ufloat(0.0),
            b[0] - ufloat(0.1),
            b[0] - ufloat(0.2),
        ]
    )
    b = [ufloat(0.1), ufloat(0.3), ufloat(0.3), ufloat(0.7)]
    assert (testSiRealList - b).hasSameValue(
        [
            ufloat(-0.1) - b[0],
            ufloat(0.0) - b[1],
            ufloat(0.1) - b[2],
            ufloat(0.2) - b[3],
        ]
    )


def test_sub_SiRealList():
    testSiRealList1 = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test1"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    testSiRealList2 = SiRealList(
        data=[ufloat(-10.0), ufloat(30.0), ufloat(30.0), ufloat(70.7)],
        label=["test2a", "test2b", "test2c", "test2d"],
        unit=[r"\milli\volt"],
        dateTime=[datetime.datetime.now()],
    )
    result = testSiRealList1 - testSiRealList2
    assert result.label == [
        "test1-test2a",
        "test1-test2b",
        "test1-test2c",
        "test1-test2d",
    ]
    assert result.hasSameValue(
        [ufloat(-0.09), ufloat(-0.03), ufloat(0.07), ufloat(0.1293)]
    )


def test_mul_single_value():
    testSiRealList = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    b = 7
    assert (testSiRealList * b).hasSameValue(
        [ufloat(-0.1 * b), ufloat(0.0 * b), ufloat(0.1 * b), ufloat(0.2 * b)]
    )
    assert (testSiRealList * b).label == ["test"]
    testSiRealList.label = ["test2a", "test2b", "test2c", "test2d"]
    assert (testSiRealList * b).label == ["test2a", "test2b", "test2c", "test2d"]
    b = 0.1
    assert (testSiRealList * b).hasSameValue(
        [ufloat(-0.1 * b), ufloat(0.0 * b), ufloat(0.1 * b), ufloat(0.2 * b)]
    )
    b = ufloat(0.2)
    assert (testSiRealList * b).hasSameValue(
        [ufloat(-0.1) * b, ufloat(0.0) * b, ufloat(0.1) * b, ufloat(0.2) * b]
    )
    assert (b * testSiRealList).hasSameValue(
        [ufloat(-0.1) * b, ufloat(0.0) * b, ufloat(0.1) * b, ufloat(0.2) * b]
    )


def test_mul_list():
    testSiRealList = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    b = [7]
    assert (testSiRealList * b).hasSameParameters(testSiRealList * b[0])
    assert (testSiRealList * b).label == ["test"]
    testSiRealList.label = ["test1", "test2", "test3", "test4"]
    assert (testSiRealList * b).label == ["test1", "test2", "test3", "test4"]
    b = [0.1, 0.2, 0.3, -2.5]
    assert (testSiRealList * b).hasSameValue(
        [
            ufloat(-0.1 * b[0]),
            ufloat(0.0 * b[1]),
            ufloat(0.1 * b[2]),
            ufloat(0.2 * b[3]),
        ]
    )
    b = [ufloat(0.2)]
    assert (b * testSiRealList).hasSameValue(
        [
            b[0] * ufloat(-0.1),
            b[0] * ufloat(0.0),
            b[0] * ufloat(0.1),
            b[0] * ufloat(0.2),
        ]
    )
    b = [ufloat(0.1), ufloat(0.3), ufloat(0.3), ufloat(0.7)]
    assert (testSiRealList * b).hasSameValue(
        [
            ufloat(-0.1) * b[0],
            ufloat(0.0) * b[1],
            ufloat(0.1) * b[2],
            ufloat(0.2) * b[3],
        ]
    )
    assert (b * testSiRealList).hasSameValue(
        [
            ufloat(-0.1) * b[0],
            ufloat(0.0) * b[1],
            ufloat(0.1) * b[2],
            ufloat(0.2) * b[3],
        ]
    )


def test_mul_SiRealList():
    testSiRealList1 = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test1"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    testSiRealList2 = SiRealList(
        data=[ufloat(-10.0), ufloat(30.0), ufloat(30.0), ufloat(70.7)],
        label=["test2a", "test2b", "test2c", "test2d"],
        unit=[r"\metre"],
        dateTime=[datetime.datetime.now()],
    )
    result = testSiRealList1 * testSiRealList2
    assert result.label == [
        "test1*test2a",
        "test1*test2b",
        "test1*test2c",
        "test1*test2d",
    ]
    assert result.hasSameValue([ufloat(1.0), ufloat(0.0), ufloat(3.0), ufloat(14.14)])

def test_mul_scalingSiRealList():
    testSiRealList1 = SiRealList(
        data=[ufloat(-0.1), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test1"],
        unit=[r"\metre"],
        dateTime=[datetime.datetime.now()],
    )
    testSiRealList2 = SiRealList(
        data=[ufloat(-10.0), ufloat(30.0), ufloat(30.0), ufloat(70.7)],
        label=["test2a", "test2b", "test2c", "test2d"],
        unit=[r"\kilo\metre"],
        dateTime=[datetime.datetime.now()],
    )
    result = testSiRealList1 * testSiRealList2
    assert result.label == [
        "test1*test2a",
        "test1*test2b",
        "test1*test2c",
        "test1*test2d",
    ]
    assert result.hasSameValue([ufloat(1000.0), ufloat(0.0), ufloat(3000.0), ufloat(14140.0)])
    assert result.unit[0].toUTF8()=='m²'


# def test_ufloat_pow():
#     a = ufloat(-1)
#     b = ufloat(3)
#     c = ufloat(3, 0)
#     test1 = a ** b
#     test2 = a ** c
#     assert get_value(test1) == -1
#     assert get_value(test2) == -1


def test_pow_single_value():
    testSiRealList = SiRealList(
        data=[ufloat(2), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    b = 7
    assert (testSiRealList**b).hasSameValue(
        [ufloat(2**b), ufloat(0.0**b), ufloat(0.1**b), ufloat(0.2**b)]
    )
    assert (testSiRealList**b).label == ["test^7"]
    testSiRealList.label = ["test1", "test2", "test3", "test4"]
    assert (testSiRealList**b).label == ["test1^7", "test2^7", "test3^7", "test4^7"]
    b = 0.1
    assert (testSiRealList**b).hasSameValue(
        [ufloat((2) ** b), ufloat(0.0**b), ufloat(0.1**b), ufloat(0.2**b)]
    )
    b = ufloat(0.2)
    assert (testSiRealList**b).hasSameValue(
        [ufloat(2) ** b, ufloat(0.0) ** b, ufloat(0.1) ** b, ufloat(0.2) ** b]
    )


def test_pow_list():
    testSiRealList = SiRealList(
        data=[ufloat(2), ufloat(0.0), ufloat(0.1), ufloat(0.2)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    b = [7]
    assert (testSiRealList**b).hasSameParameters(testSiRealList ** b[0])
    assert (testSiRealList**b).label == ["test^7"]
    testSiRealList.label = ["test1", "test2", "test3", "test4"]
    assert (testSiRealList**b).label == ["test1^7", "test2^7", "test3^7", "test4^7"]
    b = [2.0, 0.2, 0.3, 2.5]
    assert (testSiRealList**b).hasSameValue(
        [
            ufloat((2) ** b[0]),
            ufloat(0.0 ** b[1]),
            ufloat(0.1 ** b[2]),
            ufloat(0.2 ** b[3]),
        ]
    )
    assert (testSiRealList**b).label == [
        "test1^2.0",
        "test2^0.2",
        "test3^0.3",
        "test4^2.5",
    ]
    b = [ufloat(0.1), ufloat(0.3), ufloat(0.3), ufloat(0.7)]
    assert (testSiRealList**b).hasSameValue(
        [
            ufloat(2) ** b[0],
            ufloat(0.0) ** b[1],
            ufloat(0.1) ** b[2],
            ufloat(0.2) ** b[3],
        ]
    )


def test_div_single_value():
    testSiRealList = SiRealList(
        data=[ufloat(6), ufloat(8), ufloat(5), ufloat(3)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    b = 7
    assert (testSiRealList / b).hasSameValue(
        [ufloat(6 / b), ufloat(8 / b), ufloat(5 / b), ufloat(3 / b)]
    )
    assert (testSiRealList / b).label == ["test"]
    testSiRealList.label = ["test2a", "test2b", "test2c", "test2d"]
    assert (testSiRealList / b).label == ["test2a", "test2b", "test2c", "test2d"]
    b = 0.5
    assert (testSiRealList / b).hasSameValue(
        [ufloat(6 / b), ufloat(8 / b), ufloat(5 / b), ufloat(3 / b)]
    )
    b = ufloat(0.2)
    assert (testSiRealList / b).hasSameValue(
        [ufloat(6) / b, ufloat(8) / b, ufloat(5) / b, ufloat(3) / b]
    )
    assert (b / testSiRealList).hasSameValue(
        [b / ufloat(6), b / ufloat(8), b / ufloat(5), b / ufloat(3)]
    )
    assert (b / testSiRealList).label == [
        "test2a^-1",
        "test2b^-1",
        "test2c^-1",
        "test2d^-1",
    ]


def test_div_list():
    testSiRealList = SiRealList(
        data=[ufloat(6), ufloat(8), ufloat(5), ufloat(3)],
        label=["test"],
        unit=[r"\volt"],
        dateTime=[datetime.datetime.now()],
    )
    b = [7]
    assert (testSiRealList / b).hasSameParameters(testSiRealList / b[0])
    assert (testSiRealList / b).label == ["test"]
    testSiRealList.label = ["test1", "test2", "test3", "test4"]
    assert (testSiRealList / b).label == ["test1", "test2", "test3", "test4"]
    b = [0.1, 0.2, 0.3, -2.5]
    assert (testSiRealList / b).hasSameValue(
        [
            ufloat(6 / b[0]),
            ufloat(8 / b[1]),
            ufloat(5 / b[2]),
            ufloat(3 / b[3]),
        ]
    )
    b = [ufloat(0.2)]
    assert (b / testSiRealList).hasSameValue(
        [
            b[0] / ufloat(6),
            b[0] / ufloat(8),
            b[0] / ufloat(5),
            b[0] / ufloat(3),
        ]
    )
    assert (b / testSiRealList).label == [
        "test1^-1",
        "test2^-1",
        "test3^-1",
        "test4^-1",
    ]
    b = [ufloat(0.1), ufloat(0.3), ufloat(0.3), ufloat(0.7)]
    assert (testSiRealList / b).hasSameValue(
        [
            ufloat(6) / b[0],
            ufloat(8) / b[1],
            ufloat(5) / b[2],
            ufloat(3) / b[3],
        ]
    )
    assert (b / testSiRealList).hasSameValue(
        [
            b[0] / ufloat(6),
            b[1] / ufloat(8),
            b[2] / ufloat(5),
            b[3] / ufloat(3),
        ]
    )

def test_div_SiRealList():
    testSiRealList1 = SiRealList(
        data=[ufloat(4), ufloat(8.8), ufloat(55), ufloat(22)],
        label=["test1"],
        unit=[r"\volt\metre"],
        dateTime=[datetime.datetime.now()],
    )
    testSiRealList2 = SiRealList(
        data=[ufloat(200), ufloat(40), ufloat(50), ufloat(4)],
        label=["test2a", "test2b", "test2c", "test2d"],
        unit=[r"\milli\volt"],
        dateTime=[datetime.datetime.now()],
    )
    result = testSiRealList1 / testSiRealList2
    assert result.label == [
        "test1/test2a",
        "test1/test2b",
        "test1/test2c",
        "test1/test2d",
    ]
    assert result.hasSameValue([ufloat(0.02), ufloat(0.22), ufloat(1.1), ufloat(5.5)])

