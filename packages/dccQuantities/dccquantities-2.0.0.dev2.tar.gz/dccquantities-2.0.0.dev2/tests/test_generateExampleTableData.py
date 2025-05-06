import numpy as np
from SiRealList import  SiRealList


def test_generateTestTable():
    primes1 = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29],dtype=np.float64)
    primes1Uncer = primes1 * 0.01
    primes2 = np.array([31, 37, 41, 43, 47, 53, 59, 61, 67, 71],dtype=np.float64)
    primes2Uncer = primes2 * 0.02
    # Repeat each element in primes1 10 times consecutively.
    longform1 = np.repeat(primes1, 10)
    longform1Uncer = np.repeat(primes1Uncer, 10)

    # For primes2, keeping the original behavior with np.tile.
    longform2 = np.tile(primes2, 10)
    longform2Uncer = np.tile(primes2Uncer, 10)
    XQunat=SiRealList(data={"value":longform1,'uncer':longform1Uncer},unit=r'\metre')
    YQunat=SiRealList(data={"value":longform2,'uncer':longform2Uncer},unit=r'\centi\metre')
    surfaceArrea=XQunat*YQunat
    surfaceArrea.reshape(10,10)
    assert surfaceArrea.values[2,1]==primes1[2]*0.01*primes2[1]
    assert np.isclose(surfaceArrea.values[5, 7],primes1[5] * 0.01 * primes2[7])