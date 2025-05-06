from DccNoQuantity import DccNoQuantity

def test_repr():
    testNoQuantity = DccNoQuantity(data = 'abc', id = '123', refId= ['234', '345'], refType= ['@foo'], name={'en':'bar','de':'foo'})
    assert repr(testNoQuantity) == "DccNoQuantity.DccNoQuantity(_sorted=False, data='abc', id='123', refId=['234', '345'], refType=['@foo'], name=🇪🇳 bar)"
    shortNoQuantity = DccNoQuantity(data='abc')
    assert repr(shortNoQuantity) == 'DccNoQuantity.DccNoQuantity(_sorted=False, data=\'abc\')'

def test_str():
    testNoQuantity = DccNoQuantity(data = 'abc', id = '123', refId= ['234', '345'], refType= ['@foo'], name={'en':'bar','de':'foo'})
    assert str(testNoQuantity) == r"""abc (_sorted: False, id: 123, refId: ['234', '345'], refType: ['@foo'], name: {"en": "bar", "de": "foo"})"""
    shortNoQuantity = DccNoQuantity(data='abc')
    assert str(shortNoQuantity) == "abc (_sorted: False)"

def test_sorted():
    testNoQuantity = DccNoQuantity(data = 'abc', id = '123', refId= ['234', '345'], refType= ['@foo'], name={'en':'bar','de':'foo'})
    assert not testNoQuantity.sorted