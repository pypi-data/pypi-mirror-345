from datetime import datetime
from dsiUnits import dsiUnit
from numpy.core.defchararray import endswith

from AbstractQuantityTypeData import AbstractQuantityTypeData
from typing import Union #for python 3.8/3.9 compatibility
import numpy as np
from metas_unclib import *
from helpers import dccConfiguration

class AbstractValueType(AbstractQuantityTypeData):
    def __init__(
        self,
        label: list[str] = None,
        unit: list[Union[str , dsiUnit]] = None,
        dateTime: list[datetime] = None,
        _originType: str = None,
        _uncInfo: dict = None,
    ) -> None:
        super().__init__()
        self.label = label
        self.unit = []
        self._originType = _originType
        self._uncInfo = _uncInfo
        if isinstance(unit,str):
            unit=[unit]
        if unit:
            for item in unit:
                if isinstance(item, dsiUnit):
                    self.unit.append(item)
                elif isinstance(item, str):
                    self.unit.append(dsiUnit(item))
        self.dateTime = dateTime

    def serilizeDataToJSON(self):
        if isinstance(self.data, np.ndarray):
            dType = self.data.dtype
            length = self.data.size
            # check if data is a number so we will not have any uncer
            if np.issubdtype(dType, np.number):
                # we have number type so we defensively don't have any uncer
                if length > 1:
                    flattValues = list(self.data.flat)
                    flattUncs = None
                else:
                    flattValues = self.data.flat[0]
                    flattUncs = None
            # check if data is a object if yes check witch type of object
            if dType == object:
                flattarray = self.data.flat
                objType = type(flattarray[0])  # flatten the array so we can get an first element and inspect it's type
                if objType == ufloat:
                    # Define a vectorized function to extract the membervar.
                    vec_values = np.vectorize(lambda x: x.value)
                    vec_uncs = np.vectorize(lambda x: x.stdunc)
                    if length>1:
                        flattValues = list(vec_values(flattarray))
                        flattUncs = list(vec_uncs(flattarray))
                    else:
                        flattValues = vec_values(flattarray)[0]
                        flattUncs = vec_uncs(flattarray)[0]
            # okay now we can create the json
            suffix = "" if length ==1 and not self._originType.endswith('XMLList') else "XMLList"
            resultjson = {"si:value"+suffix: flattValues,}
            if flattUncs and self._uncInfo != None:
                kfactor=self._uncInfo['coverageFactor']
                covP = self._uncInfo['coverageProbability']
                distribution =self._uncInfo['distribution']
                lens=np.array([len(kfactor),len(covP),len(distribution)])
                if np.all(lens==1):
                    kfactor=kfactor[0]
                    covP=covP[0]
                    distribution=distribution[0]
                if not np.all(kfactor==1.0):
                    # we should create expanded uncs now

                    if not "originalUnc" in self._uncInfo:
                        # we had no original uncer so wie calculate expanded unc
                        uncValues=(np.array(flattUncs) * kfactor).tolist()
                        if suffix=='':
                            try:
                                uncValues=uncValues[0]
                            except TypeError:
                                # if we cant suscribe it it must be int or float
                                pass
                    else:
                        uncValues=self._uncInfo["originalUnc"]
                        if suffix=='':
                            try:
                                uncValues=uncValues[0]
                            except TypeError:
                                # if we cant suscribe it it must be int or float
                                pass

                    resultjson["si:measurementUncertaintyUnivariate"+suffix] = {
                        "si:expandedMU"+suffix:{
                            "si:valueExpandedMU" + suffix:uncValues,
                            "si:coverageFactor"+suffix:kfactor,
                            "si:coverageProbability"+suffix:covP,
                            "si:distribution"+suffix:distribution
                        }
                    }
                else:
                    resultjson["si:measurementUncertaintyUnivariate"+suffix] = {
                        "si:standardMU"+suffix:{
                            "si:valueStandardMU" + suffix: flattUncs,
                            "si:distribution"+suffix:distribution
                        }
                    }

            #TODO deal with coverra
            return resultjson
        else:
            raise ValueError("Data is not a numpy array")


