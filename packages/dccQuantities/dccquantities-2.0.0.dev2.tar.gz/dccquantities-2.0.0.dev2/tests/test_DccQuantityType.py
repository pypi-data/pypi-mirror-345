from DccQuantityType import DccQuantityType
from DccNoQuantity import DccNoQuantity


def test_repr():
    testQuantity = DccQuantityType(
        data=DccNoQuantity(data="abc"), id="123", refType=["foo"]
    )
    assert (
        repr(testQuantity)
        == "DccQuantityType(data=DccNoQuantity.DccNoQuantity(_sorted=False, data='abc'), id='123', refId=[], refType=['foo'])"
    )
