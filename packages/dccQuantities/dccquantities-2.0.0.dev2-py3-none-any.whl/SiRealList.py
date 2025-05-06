from __future__ import annotations  # for type annotation recursion
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
import math
import re
import warnings
from metas_unclib import *
import dsiUnits

from AbstractValueType import AbstractValueType
from helpers import *
from parseUncertainties import parseUncertainties, uncertaintyKeys
import numpy as np
from helpers import FieldSpec,ExplicitSerializerMixin

class SiRealList(ExplicitSerializerMixin,AbstractValueType):
    # 1) Specs for the single‐value form
    __single_specs__ = [
        # optional label first
        FieldSpec("label",    "si:label",
                  lambda s: s.label[0] if isinstance(s.label, list) else s.label),

        # raw value
        FieldSpec(None,       "si:value", "serialize_value", merge=False),

        # unit
        FieldSpec("unit",     "si:unit",
                  lambda s: str(s.unit[0])),

        # timestamp
        FieldSpec("dateTime", "si:dateTime",
                  lambda s: s.dateTime[0] if isinstance(s.dateTime, list) else s.dateTime),

        # then any measurementUncertainty…
        FieldSpec(None,       "si:measurementUncertaintyUnivariate",
                  "serialize_unc", merge=True),
    ]
    # For unkown reason the order of sireal and sireallist ist not consitent, WTF!

    # 2) Specs for the list‐value form
    __list_specs__ = [
        # optional label list
        FieldSpec("label",         "si:labelXMLList",    lambda s: s.label),

        # array of values
        FieldSpec(None,            "si:valueXMLList",    "serialize_value", merge=False),

        # list‐unit
        FieldSpec("unit", "si:unitXMLList", lambda s: [str(u) for u in s.unit]),

        # optional timestamp list
        FieldSpec("dateTime", "si:dateTimeXMLList", lambda s: s.dateTime),

        # then any list‐uncertainty
        FieldSpec(None,            "si:measurementUncertaintyUnivariateXMLList",
                  "serialize_unc", merge=True),
    ]

    def __init__(
        self,
        data: Union[
            list[ufloat],
            list[int],
            list[float],
            list[tuple],
            dict[list],
            tuple[list],
            list[list],
            np.ndarray,
        ],  # With uncertainty
        unit: list[dsiUnits.dsiUnit],
        label: list = None,
        dateTime: list[datetime] = None,
        _originType: str = "si:realListXMLList",
        _uncInfo: dict = None,
        # distribution: str = None,
    ) -> None:
        """Representation of si:reaListXMLList, SiRsi:real, si:constant

        Args:
            data (Union[ list[ufloat], list[int], list[float], list[tuple], dict[list], tuple[list], list[list], ]): Values with uncertainty, in one of the following formats:
                List of ufloat, list of float, list of int;
                list of tuples of the format [(value1, unc1), ...];
                tuple of two lists ([value1, ...],[unc1, ...]);
                dict with two keys value and unc {'value': [value1, ...], 'unc': [unc1, ...]};
                list of two lists [[value1, ...], [unc1, ...]].
                As an alternative to lists, numpy arrays are also supported. Array can also be already shaped but this is for internal use in tables only!
            unit (list[dsiUnits.dsiUnit], optional): Units of the values, must be length one or the same length as the values. Defaults to None.
            dateTime (list[datetime], optional): Timestamps of the values, must be length one or the same length as the values. Defaults to None.
            _originType (_type_, optional): Type to be used when generating XML from this object. Defaults to "si:realList".
        """
        super().__init__(label, unit, dateTime,_originType=_originType,_uncInfo=_uncInfo)
        self.data = _parseData(data)
        self._sorted = None
        # self.uncertainty = uncertainty
        # self.distribution = distribution
        if _originType in ["si:real", "si:constant"]:
            if len(self.data) != 1:
                warnings.warn(
                    f'Data of length {len(data)} can\'t have come from type {_originType}! Setting type to "si:realList"',
                    RuntimeWarning,
                )
                self._originType = "si:RealListXMLList"
        elif _originType in ["si:realListXMLList"]:
            pass
        else:
            warnings.warn(
                f"Type {_originType} not known - do expect xml export to fail.",
                RuntimeWarning,
            )
        if not len(self.unit) in [1, len(self.data)]:
            raise ValueError(
                "Length of unit list must be 1 or match length of data list!"
            )
        if self.label and not len(self.label) in [1, len(self.data)]:
            raise ValueError(
                "Length of label list must be 1 or match length of data list!"
            )
        if self.dateTime and not len(self.dateTime) in [1, len(self.data)]:
            raise ValueError(
                "Length of dateTime list must be 1 or match length of data list!"
            )

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        params = {key: value for key, value in vars(self).items() if value is not None}
        paramStr = ", ".join(f"{key}={repr(value)}" for key, value in params.items())
        return f"SiRealList.SiRealList({paramStr})"

    def __str__(self) -> str:
        params = {
            key: value
            for key, value in vars(self).items()
            if value is not None and key != "data"
        }
        paramStr = ", ".join(f"{key}: {str(value)}" for key, value in params.items())

        if len(paramStr) > 0:
            paramStr = " (" + paramStr + ")"
        return f"{str(self.data)}{paramStr}"

    def __eq__(self, value: object) -> bool:
        # TODO: implement comparison for non unc values
        warnings.warn(
            "Can't compare objects with uncertainty. If you need to know if the objects have the same value and deviation, use SiRealList.hasSameValue(list) or SiRealList.hasSameParameters(SiRealList).",
            RuntimeWarning,
        )
        return NotImplemented

    def hasSameValue(self, data: list[ufloat]) -> bool:
        result = True
        for value1, value2 in zip(self.data, data):
            result = result * (
                math.isclose(get_value(value1), get_value(value2))
                or (math.isnan(get_value(value1)) and math.isnan(get_value(value2)))
            )
            result = result * math.isclose(get_stdunc(value1), get_stdunc(value2))
        return bool(result)

    def hasSameParameters(self, other: SiRealList) -> bool:
        return (
            self.hasSameValue(other.data)
            and self.label == other.label
            and self.unit == other.unit
            and self.dateTime == other.dateTime
        )

    def toJsonDict(self):
        # 1) Choose which spec+root to use
        if self._originType in ("si:real", "si:constant"):
            # multi-value forces list form
            if any(
                isinstance(val, (list, np.ndarray)) and len(val) > 1
                for val in (self.data, self.label, self.unit, self.dateTime)
                if val is not None
            ):
                specs, root = self.__list_specs__, "si:realListXMLList"
            else:
                specs = self.__single_specs__
                root = "si:constant" if self._originType == "si:constant" else "si:real"
        else:
            specs, root = self.__list_specs__, "si:realListXMLList"

        # 2) Bind the chosen specs to the mixin, call to_dict(), then clean up
        self.__serialize_fields__ = specs
        ordered = self.to_dict()
        del self.__serialize_fields__

        # 3) Wrap under the correct root element
        return {root: ordered}

    # ————— helper methods for those specs —————

    def serialize_value(self):
        """
        Return just the flattened 'si:value' or 'si:valueXMLList' entry
        from serilizeDataToJSON().
        """
        if not hasattr(self,'_data'):
            self._data = self.serilizeDataToJSON()
        for key, val in self._data.items():
            if key.startswith("si:value"):
                return val
        return None

    def serialize_unc(self):
        """
        Return only the uncertainty sub-dict (everything *except* the 'si:value…'
        keys) from serilizeDataToJSON(), so it merges in the correct position.
        """
        # we dont need to copy since unc will allways call after the values ...
        if not hasattr(self, '_data'):
            self._data = self.serilizeDataToJSON()
        for key in list(self._data.keys()):
            if key.startswith("si:value"):
                self._data.pop(key)
        out=deepcopy(self._data)
        del self._data
        #we will delete '_data' since we don't need it anymore ... if we serialize again, we will create it again completely to prevent race conditions ...
        return out

    def __neg__(self):
        new_data = [-item for item in self.data]
        return SiRealList(
            data=new_data,
            label=["-" + item for item in self.label],
            unit=self.unit,
            dateTime=self.dateTime,
        )

    def __pos__(self):
        return deepcopy(self)

    def __add__(self, other) -> SiRealList:
        # single values
        if isinstance(other, int) or isinstance(other, float):
            return self + ufloat(other)
        elif isinstance(other, ufloat):
            result = deepcopy(self)
            result.data = [item + other for item in self.data]

        # lists
        elif isListOfTypes(other, [int, float]):
            return self + [ufloat(item) for item in other]
        elif isListOfTypes(other, [ufloat]):
            if len(other) == 1:
                return self + other[0]
            elif len(other) == len(self):
                result = deepcopy(self)
                result.data = [
                    summand1 + summand2 for summand1, summand2 in zip(self.data, other)
                ]
            else:
                raise AttributeError("Length of summands need to be equal or 1!")

        # SiRealList
        elif isinstance(other, SiRealList):
            if len(self.unit) == 1:
                scaleVector = [
                    self.unit[0].isScalablyEqualTo(otherUnit)
                    for otherUnit in other.unit
                ]
            elif len(other.unit) == 1:
                scaleVector = [
                    selfUnit.isScalablyEqualTo(other.unit[0]) for selfUnit in self.unit
                ]
            elif len(self.unit) == len(other.unit):
                scaleVector = [
                    selfUnit.isScalablyEqualTo(otherUnit)
                    for selfUnit, otherUnit in zip(self.unit, other.unit)
                ]
            else:
                raise AttributeError(
                    "Length of summands' units need to be equal or 1! Are the summands same length or one element?"
                )
            # unless someone manually changed the unit list, len(scaleVector) is either 1 or len(self)==len(other)!
            if None in [item[1] for item in scaleVector]:
                raise AttributeError(
                    "Units of summands are not scalably equal to each other!"
                )
            if len(scaleVector) == 1:
                scaleVector = scaleVector * len(self)
            result = deepcopy(other)
            if len(self) == 1:
                result.data = [
                    self.data[0] + scaleFactor * summand2
                    for summand2, (scaleFactor, unit) in zip(other.data, scaleVector)
                ]
            elif len(other) == 1:
                result.data = [
                    summand1 + scaleFactor * other.data[0]
                    for summand1, (scaleFactor, unit) in zip(self.data, scaleVector)
                ]
            elif len(self) == len(other):
                result.data = [
                    summand1 + scaleFactor * summand2
                    for summand1, summand2, (scaleFactor, unit) in zip(
                        self.data, other.data, scaleVector
                    )
                ]
            else:
                raise AttributeError("Length of summands need to be equal or 1!")
            result.label = joinLabels(self.label, other.label, "+")
            # originType
            if "si:realList" in [self._originType, other._originType]:
                result._originType = "si:realList"
            elif "si:realListXMLList" in [self._originType, other._originType]:
                result._originType = "si:realListXMLList"
            elif "si:real" in [self._originType, other._originType]:
                result._originType = "si:real"
            elif "si:constant" in [self._originType, other._originType]:
                result._originType = "si:constant"
        else:
            return NotImplemented
        result.dateTime = None
        return result

    def __radd__(self, other):
        if (
            isinstance(other, int)
            or isinstance(other, float)
            or isinstance(other, ufloat)
            or isListOfTypes(other, [int, float])
            or isListOfTypes(other, [ufloat])
        ):
            return self + other
        else:
            return NotImplemented

    def __sub__(self, other):
        if (
            isinstance(other, int)
            or isinstance(other, float)
            or isinstance(other, ufloat)
        ):
            return self + (-other)
        elif isListOfTypes(other, [int, float]) or isListOfTypes(other, [ufloat]):
            return self + [-item for item in other]
        elif isinstance(other, SiRealList):
            result = self + (-other)
            result.label = joinLabels(self.label, other.label, "-")
            return result
        else:
            return NotImplemented

    def __rsub__(self, other):
        if (
            isinstance(other, int)
            or isinstance(other, float)
            or isinstance(other, ufloat)
            or isListOfTypes(other, [int, float])
            or isListOfTypes(other, [ufloat])
        ):
            return (-self) + other
        else:
            return NotImplemented

    def __mul__(self, other):
        # single values
        if isinstance(other, int) or isinstance(other, float):
            return self * ufloat(other)
        elif isinstance(other, ufloat):
            result = deepcopy(self)
            result.data = [item * other for item in self.data]

        # lists
        elif isListOfTypes(other, [int, float]):
            return self * [ufloat(item) for item in other]
        elif isListOfTypes(other, [ufloat]):
            if len(other) == 1:
                return self * other[0]
            elif len(other) == len(self):
                result = deepcopy(self)
                result.data = [
                    factor1 * factor2 for factor1, factor2 in zip(self.data, other)
                ]
            else:
                raise AttributeError("Length of factors need to be equal or 1!")

        # SiRealList
        elif isinstance(other, SiRealList):
            # Require that both self.unit and other.unit are universal.
            if len(self.unit) != 1 or len(other.unit) != 1:
                raise NotImplementedError(
                    "Multiplication or Division for SiRealList with non-universal units is not implemented."
                )

            # Get the scaling factor so that other's unit is converted into self's unit.
            scale, scaledUnit = self.unit[0].isScalablyEqualTo(other.unit[0])
            result = deepcopy(self)
            if scaledUnit != None:
                result.unit = [self.unit[0] * scaledUnit]
            else:
                # the units are not scalable equal so scalfactor will be 1 since we now have new unit like 5 V *2 m= 10 Vm
                scale = 1.0
                result.unit = [self.unit[0] * other.unit[0]]
            # Determine the proper multiplication based on the length of data.
            if len(self) == 1:
                # self has a single value: multiply it with each scaled other.data element.
                result.data = [self.data[0] * (scale * d) for d in other.data]
                # The resulting unit is the product of the two universal units.
            elif len(other) == 1:
                # other has a single value: multiply it with each self.data element.
                result.data = [d * (scale * other.data[0]) for d in self.data]
            elif len(self) == len(other):
                # Both have the same number of data points: multiply elementwise.
                result.data = [
                    d1 * (scale * d2) for d1, d2 in zip(self.data, other.data)
                ]
            else:
                raise AttributeError(
                    "Data lengths must be equal or one must be a singleton!"
                )
            if self.label and other.label:
                result.label = joinLabels(self.label, other.label, "*")

            # originType
            if "si:realList" in [self._originType, other._originType]:
                result._originType = "si:realList"
            elif "si:realListXMLList" in [self._originType, other._originType]:
                result._originType = "si:realListXMLList"
            elif "si:real" in [self._originType, other._originType]:
                result._originType = "si:real"
            elif "si:constant" in [self._originType, other._originType]:
                result._originType = "si:constant"

        else:
            return NotImplemented
        result.dateTime = None
        return result

    def __rmul__(self, other):
        if (
            isinstance(other, int)
            or isinstance(other, float)
            or isinstance(other, ufloat)
            or isListOfTypes(other, [int, float])
            or isListOfTypes(other, [ufloat])
        ):
            return self * other
        else:
            return NotImplemented

    def __pow__(self, other) -> SiRealList:
        if isinstance(other, int) or isinstance(other, float):
            result = self ** ufloat(other)
            result.label = joinLabels(self.label, [str(other)], "^")
            result.unit = [item**other for item in self.unit]
        elif isinstance(other, ufloat):
            result = deepcopy(self)
            result.data = [item**other for item in self.data]
            result.label = joinLabels(self.label, [str(get_value(other))], "^")
            if get_stdunc(other) != 0:
                raise TypeError(
                    "If exponent is a ufloat object, uncertainty must be 0!"
                )
            else:
                exponent = get_value(other)
            result.unit = [item**exponent for item in self.unit]
        elif isListOfTypes(other, [int, float]):
            result = self ** [ufloat(item) for item in other]
            result.label = joinLabels(self.label, [str(item) for item in other], "^")
        elif isListOfTypes(other, [ufloat]):
            exponents = []
            for item in other:
                if get_stdunc(item) != 0:
                    raise TypeError(
                        "If exponent is a ufloat object, uncertainty must be 0!"
                    )
                else:
                    exponents.append(get_value(item))
            if len(other) == 1:
                result = deepcopy(self)
                result.data = [item ** other[0] for item in self.data]
                result.label = joinLabels(self.label, [str(other[0])], "^")
                result.unit = [base ** exponents[0] for base in self.unit]
            elif len(other) == len(self):
                result = deepcopy(self)
                result.data = [
                    base**exponent for base, exponent in zip(self.data, other)
                ]
                result.label = joinLabels(
                    self.label, [str(item) for item in other], "^"
                )
                result.unit = [
                    base**exponent for base, exponent in zip(self.unit, exponents)
                ]
            else:
                raise AttributeError(
                    "Length of exponent needs to be equal to length of base or 1!"
                )
        else:
            return NotImplemented

        result.dateTime = None
        return result

    def __truediv__(self, other):
        if (
            isinstance(other, int)
            or isinstance(other, float)
            or isinstance(other, ufloat)
        ):
            return self * other ** (-1)
        elif isListOfTypes(other, [int, float]) or isListOfTypes(other, [ufloat]):
            return self * [item ** (-1) for item in other]
        elif isinstance(other, SiRealList):
            result = self * other ** (-1)
            result.label = joinLabels(self.label, other.label, "/")
            return result
        else:
            return NotImplemented

    def __rtruediv__(self, other):
        if (
            isinstance(other, int)
            or isinstance(other, float)
            or isinstance(other, ufloat)
            or isListOfTypes(other, [int, float])
            or isListOfTypes(other, [ufloat])
        ):
            result = self ** (-1) * other
            result.label = [item + "^-1" for item in self.label]
            return result
        else:
            return NotImplemented

    def __getitem__(self, index) -> SiRealList:
        """
        Return a new SiRealList instance containing only the elements specified by `index`.
        Supports all nD indexing types including int, slice, list/array of indices, and boolean indexing.

        If an attribute (label, unit, dateTime) is stored as a list of length 1, it is assumed
        to be universal and is not sub‐indexed.
        """

        # Helper to subset an attribute (label/unit/dateTime)
        def subset_attr(attr):
            if attr is None:
                return None
            # If the attribute is universal, leave it as is.
            #TODO refactor this to handle reshapped attrs
            if len(attr) == 1:
                return attr
            try:
                arr = np.array(attr, dtype=object)
                sub = arr[index]
            except Exception as e:
                raise IndexError(f"Error indexing attribute {attr}: {e}")
            # If a single element is returned (e.g. when index is an int), wrap it in a list.
            if isinstance(sub, np.ndarray):
                return list(sub)
            else:
                return [sub]

        # Subset the main data list (which is a list of ufloat values)
        new_data = self.data[index]
        if not isinstance(new_data, np.ndarray):
            new_data= [new_data]
        # When index is an int, np.array returns a single element; we wrap it in a list.
        # Subset the optional attributes.
        new_label = subset_attr(self.label)
        new_unit = subset_attr(self.unit)
        new_dateTime = subset_attr(self.dateTime)

        return SiRealList(
            data=new_data,
            label=new_label,
            unit=new_unit,
            dateTime=new_dateTime,
            _originType=self._originType,
        )

    def __array__(self, dtype=None):
        # Convert self.data to a NumPy array
        return np.array(self.data, dtype=dtype)

    @property
    def values(self):
        """
        Returns a NumPy array of just the numerical values extracted from the data.
        """
        if np.issubdtype(self.data.dtype, np.number):
            # we have non uncer data so we directly return the data
            return self.data
        else:
            return get_valsFromUFloatArrays(self.data)

    @property
    def uncertainties(self):
        """
        Returns a NumPy array of just the uncertainties extracted from the data.
        """
        if np.issubdtype(self.data.dtype, np.number):
            # we have non uncer data so we directly return the data
            raise AttributeError("This siRealList doesn't has any uncer associated!")
        else:
            return get_uncerFromUFloatArrays(self.data)

    @property
    def shape(self) -> tuple:
        """Return the shape of the underlying data array."""
        return self.data.shape

    @property
    def sorted(self)-> bool:
        if self._sorted is None:
            try:
                self._sorted=all(self.values[i] <= self.values[i + 1] for i in range(len(self.values) - 1))
            except ValueError as e:
                warnings.warn(
                    f"sorted is only implemented for 1D data. Returning False: {e}", RuntimeWarning
                )
                self._sorted = False
        return self._sorted

    def reshape(self, *newshape) -> None:
        """
        Reshape the SiRealList in-place to the given new shape.
        Accepts newshape as separate integers or as a single tuple/list.
        """
        # Allow passing newshape as a tuple/list or separate arguments.
        if len(newshape) == 1 and isinstance(newshape[0], (tuple, list)):
            newshape = tuple(newshape[0])
        else:
            newshape = tuple(newshape)

        # Reshape the main data array in place.
        self.data = np.reshape(self.data, newshape)

        # Helper to reshape an attribute if it is not universal (length 1)
        def reshape_attr(attr):
            if attr is None or len(attr) == 1:
                return attr
            try:
                return list(np.reshape(np.array(attr, dtype=object), newshape))
            except Exception as e:
                warnings.warn(
                    f"Could not reshape attribute {attr}: {e}", RuntimeWarning
                )
                return attr

        # Reshape associated attributes.
        self.label = reshape_attr(self.label)
        self.unit = reshape_attr(self.unit)
        self.dateTime = reshape_attr(self.dateTime)

    def hasValidData(self):
        if self.label and not len(self.label) in [1, len(self)]:
            return False
        if self.unit and not len(self.unit) in [1, len(self)]:
            return False
        if self.dateTime and not len(self.dateTime) in [1, len(self)]:
            return False
        return True


def parseSingleValue(jsonDict: dict, relativeUncertainty: dict = None):
    siRealListArgs = {}

    siRealListArgs["_originType"] = "si:real"

    if "si:label" in jsonDict.keys():  # optional
        siRealListArgs["label"] = ensureList(jsonDict["si:label"])

    siRealListArgs["unit"] = ensureList(jsonDict["si:unit"])  # required

    if "si:dateTime" in jsonDict.keys():  # optional
        siRealListArgs["dateTime"] = ensureList(jsonDict["si:dateTime"])

    data = ensureList(jsonDict["si:value"])  # required
    siRealListArgs["data"],siRealListArgs["_uncInfo"] = parseUncertainties(
        jsonDict=jsonDict, data=data, relativeUncertainty=relativeUncertainty
    )

    for key in jsonDict.keys():
        if (
            key
            not in ["si:label", "si:value", "si:unit", "si:dateTime", "@_Comment"]
            + uncertaintyKeys
        ):
            warnings.warn(f"Unsupported key for si:real: {key}", RuntimeWarning)

    return SiRealList(**siRealListArgs)


def parseConst(jsonDict: dict, relativeUncertainty: dict = None):
    siRealListArgs = {}

    siRealListArgs["_originType"] = "si:constant"

    data = ensureList(jsonDict["si:value"])  # required
    siRealListArgs["data"],siRealListArgs["_uncInfo"] = parseUncertainties(
        jsonDict=jsonDict, data=data, relativeUncertainty=relativeUncertainty
    )
    siRealListArgs["unit"] = ensureList(jsonDict["si:unit"])  # required

    if "si:label" in jsonDict.keys():  # optional
        siRealListArgs["label"] = ensureList(jsonDict["si:label"])

    if "si:dateTime" in jsonDict.keys():  # optional
        siRealListArgs["dateTime"] = ensureList(jsonDict["si:dateTime"])

    #TODO refactor distribution Parsing
    if "si:distribution" in jsonDict.keys():
        siRealListArgs["distribution"] = ensureList(jsonDict["si:distribution"])

    for key in jsonDict.keys():
        if (
            key
            not in [
                "si:label",
                "si:value",
                "si:unit",
                "si:dateTime",
                "si:distribution",
                "@_Comment",
            ]
            + uncertaintyKeys
        ):
            warnings.warn(f"Unsupported key for si:constant: {key}", RuntimeWarning)

    return SiRealList(**siRealListArgs)


def parseXMLList(jsonDict: dict, relativeUncertainty: dict = None):
    siRealListArgs = {}

    siRealListArgs["_originType"] = "si:realListXMLList"

    siRealListArgs["unit"] = ensureList(jsonDict["si:unitXMLList"])

    if "si:labelXMLList" in jsonDict.keys():
        siRealListArgs["label"] = ensureList(jsonDict["si:labelXMLList"])

    if "si:dateTimeXMLList" in jsonDict.keys():  # optional
        siRealListArgs["dateTime"] = ensureList(jsonDict["si:dateTimeXMLList"])

    data = ensureList(jsonDict["si:valueXMLList"])
    siRealListArgs["data"],siRealListArgs["_uncInfo"] = parseUncertainties(
        jsonDict=jsonDict, data=data, relativeUncertainty=relativeUncertainty
    )

    for key in jsonDict.keys():
        if (
            key
            not in [
                "si:valueXMLList",
                "si:unitXMLList",
                "si:labelXMLList",
                "si:dateTimeXMLList",
                "@_Comment",
            ]
            + uncertaintyKeys
        ):
            warnings.warn(f"Unsupported key for si:realXMLList: {key}", RuntimeWarning)

    return SiRealList(**siRealListArgs)


def _parseData(data):
    if isinstance(data, list):
        if isListOfTypes(data, [tuple]):
            try:
                return np.array(
                    [ufloat(value=value, stdunc=unc) for value, unc in data]
                )
            except:
                raise ValueError(
                    f"List of tuples did not match expected format. Expecting tuples of form (value, unc). Data given was {data}"
                )
        else:
            try:
                shape = np.array(data).shape
            except ValueError:
                raise ValueError(
                    f"Can not parse data with inhomogeneous shape. Give data was {data}"
                )
            if len(shape) == 1:
                return np.array(data)
            elif len(shape) == 2 and shape[0] == 2:
                values = data[0]
                uncs = data[1]
                if (
                        (
                                (isinstance(values, list) and isinstance(uncs, list))
                                or (
                                        isinstance(values, np.ndarray)
                                        and isinstance(uncs, np.ndarray)
                                )
                        )
                        and len(values) == len(uncs)
                        and isListOfTypes(values, [int, float, np.integer, np.floating])
                        and isListOfTypes(uncs, [int, float, np.integer, np.floating])
                ):
                    return np.array(
                        [
                            ufloat(value=value, stdunc=unc)
                            for value, unc in zip(values, uncs)
                        ]
                    )
            elif len(shape) >= 2 and shape[0] == 2:
                raise NotImplementedError("Construction with list with 2 higher dimensional data  will not be supported! please convert manually to np.array of float or float. With correct shape.")
    elif isinstance(data, np.ndarray):
        # we had an array we return an array all fine :) 2D Array to store values and UNC is no longer a valide option
        # TODO remove from documentation!
        # TODO implement sanity check
        return data
    elif isinstance(data, tuple):
        if len(data) == 2:
            values, uncs = data
            if (
                (
                    (isinstance(values, list) and isinstance(uncs, list))
                    or (isinstance(values, np.ndarray) and isinstance(uncs, np.ndarray))
                )
                and len(values) == len(uncs)
                and isListOfTypes(values, [int, float, np.integer, np.floating])
                and isListOfTypes(uncs, [int, float, np.integer, np.floating])
            ):
                return np.array(
                    [
                        ufloat(value=value, stdunc=unc)
                        for value, unc in zip(values, uncs)
                    ]
                )
    elif isinstance(data, dict):
        valueKeys = [key for key in data.keys() if re.match(r"^value", key)]
        uncKeys = [key for key in data.keys() if re.match(r"^unc", key)]
        if len(valueKeys) == 1 and len(uncKeys) == 1:
            values = data[valueKeys[0]]
            uncs = data[uncKeys[0]]
            if (
                (
                    (isinstance(values, list) and isinstance(uncs, list))
                    or (isinstance(values, np.ndarray) and isinstance(uncs, np.ndarray))
                )
                and len(values) == len(uncs)
                and isListOfTypes(values, [int, float, np.integer, np.floating])
                and isListOfTypes(uncs, [int, float, np.integer, np.floating])
            ):
                result = []
                for value, unc in zip(values, uncs):
                    result.append(ufloat(value, unc))
                return np.array(result)
        else:
            raise ValueError(
                f"Could not parse data: Keys did not match. Keys found for values: {valueKeys}, keys found for uncertainties: {uncertaintyKeys}. Accepted keys must start with 'value' or 'unc'."
            )

    raise ValueError(
        "Could not parse data. Valid formats are 1-dimensional list (of unc objects or values without unc), list of tuples (value, unc), tuple of lists ([value1, ...], [unc1, ...]), dict {value: [...], unc: [...]}, and 2-dimensional array [[value1, ...], [unc1, ...]]"
    )
