from SiList import SiList
from SiRealList import SiRealList


def test_repr():
    testSiList = SiList(
        children=[SiRealList(data=[1], unit=[r"\one"]), SiRealList(data=[2], unit=[r"\one"])], label="foo"
    )
    assert repr(testSiList) == "SiList.SiList(_sorted=False, children=[SiRealList.SiRealList(unit=[1], _originType='si:realListXMLList', data=array([1])), SiRealList.SiRealList(unit=[1], _originType='si:realListXMLList', data=array([2]))], label='foo')"

def test_str():
    testSiList = SiList(
        children=[SiRealList(data=[1], unit = [r"\one"]), SiRealList(data=[2], unit = [r"\one"])], label="foo"
    )
    assert str(testSiList) ==  "\nSiList (_sorted: False, label: 'foo')\n[\n    [1] (unit: [1], _originType: si:realListXMLList)\n    [2] (unit: [1], _originType: si:realListXMLList)\n]\n"