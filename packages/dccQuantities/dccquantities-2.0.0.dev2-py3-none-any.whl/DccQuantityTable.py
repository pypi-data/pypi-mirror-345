from __future__ import annotations
from typing import Dict, Union# for type annotation recursion
import warnings

import numpy as np
import uuid
import DccQuantityType
from helpers import replaceQuantitiesInDict, slice_AND, ints_to_slice,ensureList, dccTypeCollector
from dccQuantityParser import parseItemFromJsonDict
import re
from dsiUnits import dsiUnit
from DccName import DccName
from helpers import get_nearest_slice,get_conditional_slice,get_exact_slice,evaluate_query
from collections import OrderedDict
from helpers import FieldSpec,ExplicitSerializerMixin
import datetime
def getBasicIndexDimensionFromRefTypes(ref_types):
    """
    Given a list of refType strings, this function searches for those that match
    the pattern 'basic_tableIndex([0-9])' (with or without parentheses).

    Returns:
        The numeric dimension as an integer if exactly one match is found.
        None if no match is found.

    Raises:
        ValueError: If more than one string in the list matches the pattern.
    """
    if ref_types is None or ref_types ==[None]:
        return None
    if isinstance(ref_types,str):
        warnings.warn("refTypes was not a List Fix this !!!")
        ref_types=ref_types.split()
    pattern = re.compile(r'^basic_(?:Flat)?tableindex(?:\((\d+)\)|(\d+))$', re.IGNORECASE)
    matches = []
    for s in ref_types:
        match = pattern.match(s)
        if match:
            matches.append(match)
    if len(matches) == 0:
        return None
    elif len(matches) > 1:
        raise ValueError("More than one refType matches the pattern ^basic_(\\d+)IndexTable$.")
    else:
        m = matches[0]
        # Use group(1) if available; otherwise, use group(2)
        index_str = m.group(1) if m.group(1) is not None else m.group(2)
        return int(index_str)

def getBasicDimensionAndTypeFromRefTypes(ref_types):
    """
    Given a list of refType strings, this function looks for those that match the
    'basic_<number>IndexTable' pattern.

    Returns:
        The numeric index as an integer if exactly one match is found.
        None if no match is found.

    Raises:
        ValueError: If more than one string in the list matches the pattern.
    """
    if isinstance(ref_types,str):
        warnings.warn("refTypes was not a List Fix this !!!")
        ref_types=ref_types.split()
    patternLong = re.compile(r'^basic_(\d+)IndexTable$')
    longMatches = []
    for s in ref_types:
        match = patternLong.match(s)
        if match:
            longMatches.append(match)
    patternFlat = re.compile(r'^basic_(\d+)IndexFlatTable$')
    flatMatches = []
    for s in ref_types:
        match = patternFlat.match(s)
        if match:
            flatMatches.append(match)

    if len(longMatches) == 0 and len(flatMatches)==0:
        return None,None
    elif len(longMatches) > 1 or len(flatMatches)>1:
        raise ValueError("More than one refType matches the pattern ^basic_(\d+)IndexTable$. Or ^basic_(\d+)IndexFlatTable$")
    elif (len(longMatches)+len(flatMatches))>1:
        raise ValueError(
            "Found both refTypes for Flat and LongTable")
    elif len(longMatches) == 1:
        return 'long', int(longMatches[0].group(1))
    elif len(flatMatches) == 1:
        return 'flat', int(flatMatches[0].group(1))

def matchesFlatTableIndex(ref_types, dim):
    """
    Check if any of the ref_types matches 'basic_FlatTableIndex<dim>' with optional leading zeros.
    """
    if ref_types is None or ref_types == [None]:
        return None
    pattern = re.compile(rf'^basic_FlatTableIndex0*{dim}$', re.IGNORECASE)
    return any(pattern.fullmatch(ref) for ref in ref_types)

def matchesFlatTable(dim, ref_types):
    """
    Check if ref_types includes 'basic_<dim>IndexFlatTable' with optional leading zeros.
    """
    if ref_types is None or ref_types == [None]:
        return None
    pattern = re.compile(rf'^basic_0*{dim}IndexFlatTable$', re.IGNORECASE)
    return any(pattern.fullmatch(ref) for ref in ref_types)

def matchesLongTable(ref_types, dim):
    """
    Check if any of the ref_types matches 'basic_<dim>IndexTable' with optional leading zeros.
    """
    if ref_types is None or ref_types == [None]:
        return None
    pattern = re.compile(rf'^basic_0*{dim}IndexTable$', re.IGNORECASE)
    return any(pattern.fullmatch(ref) for ref in ref_types)

def matchesTableIndex(ref_types, dim):
    """
    Check if any of the ref_types matches 'basic_tableIndex<dim>' with optional leading zeros and optional parentheses.
    """
    if ref_types is None or ref_types == [None]:
        return None
    pattern = re.compile(rf'^basic_tableIndex(?:\({dim}\)|0*{dim})$', re.IGNORECASE)
    return any(pattern.fullmatch(ref) for ref in ref_types)

class DccQuantityTable(ExplicitSerializerMixin):
    def __init__(self,
                 idxQuants: dict[DccQuantityType],
                 valueQuants: list[DccQuantityType],#keyed by index dimension
                 _dimensionLen: int = None,
                 id: str = None,
                 refId: list[str] = None,
                 refType: list[str] = None,
                 name: Union[dict, DccName] = None,
                 dateTime: Union[datetime.datetime,list[datetime.datetime]]=None,
                 description: dict = None,
                 usedMethods: dict = None,
                 usedSoftware: dict = None,
                 measuringEquipments: dict = None,
                 influenceConditions: dict = None,
                 measurementMetaData: dict = None,
                 ):

        if id is None:
            id = 'U'+str(uuid.uuid4())
        self.id = id
        self.refId = refId
        self.refType = ensureList(refType)
        self.name = DccName(name)
        self.description = description
        self.dateTime=dateTime
        self.usedMethods = usedMethods
        self.usedSoftware = usedSoftware
        self.measuringEquipments = measuringEquipments
        self.measurementMetaData = measurementMetaData
        self.influenceConditions = influenceConditions
        self._idxQuantities = idxQuants
        self._valueQuantities = valueQuants
        self._allQuantities = []
        self._quntsByID={}
        self._dimensionLen= _dimensionLen
        for key,quant in self._idxQuantities.items():
            self._allQuantities.append(quant)
            self._quntsByID[quant.id]=quant
        if self._dimensionLen is None:
            warnings.warn("Dimension len was not specified for DccQuantityTable taking num of given index quantities")
            self._dimensionLen=len(self._idxQuantities)
            for i in range(self._dimensionLen):
                if i not in self._idxQuantities:
                    raise ValueError("Index "+str(i)+" is missing table is incomplete.")

        for quant in self._valueQuantities:
            self._allQuantities.append(quant)
            self._quntsByID[quant.id] = quant

    @property
    def shape(self):
        # Compute and return the shape as a tuple, e.g. (10, 10)
        dims = []
        for key in sorted(self._idxQuantities.keys()):
            dims.append(len(self._idxQuantities[key]))
        return tuple(dims)

    @property
    def units(self):
        units = []
        for qunat in self._allQuantities:
            try:
                unitList=qunat.data.unit
                for unit in unitList:
                    units.append(unit)
            except AttributeError:
                pass
        return set(units)

    def __getitem__(self, index):
        raise NotImplementedError("Subclasses must implement __getitem__.")

    @classmethod
    def fromDict(cls, dccDict):
        """
        Generic constructor that chooses the correct subclass based on the parsed table type.
        """
        # First, extract the table type using your helper function.
        dccDict=replaceQuantitiesInDict(dccDict,parser=parseItemFromJsonDict)
        tableType, dimensionLen = getBasicDimensionAndTypeFromRefTypes(dccDict.get('@refType', ''))
        #TODO refactor
        args={
        'refType' : dccDict.get('@refType', None),
        'id' : dccDict.get('@id', None),
        'refId' : dccDict.get('@refId', None),
        'name' : dccDict.get('dcc:name', None),
        'description' : dccDict.get('dcc:description', None),
        'usedMethods' : dccDict.get('dcc:usedMethods', None),
        'usedSoftware' : dccDict.get('dcc:usedSoftware', None),
        'measuringEquipments' : dccDict.get('dcc:measuringEquipments', None),
        'measurementMetaData' : dccDict.get('dcc:measurementMetaData', None),
        'influenceConditions' : dccDict.get('dcc:influenceConditions', None),
        'idxQuants': {},
        'valueQuants': [],
        '_dimensionLen': dimensionLen,
        }
        #pasring the data
        allQuantsAndPathes = dccTypeCollector(jsonDict=dccDict, searchKeys=["dcc:quantity"])
        for quantAndPath in allQuantsAndPathes:
            quantPath = quantAndPath[0]
            quant = quantAndPath[1]
            # get the index dimension
            idx = getBasicIndexDimensionFromRefTypes(quant.refType)
            if idx is not None:
                # add to the index quantities
                args['idxQuants'][idx] = quant
            else:
                # add to the value quantities
                args['valueQuants'].append(quant)

        if tableType == 'long':
            return DccLongTable(**args)
        elif tableType == 'flat':
            return DccFlatTable(**args)
        else:
            raise ValueError("Unknown table type encountered: {}".format(tableType))

    def getQunatitysIDsByName(self,name:Union[str,DccName]):
        qunatites=[]
        for quant in self._allQuantities:
            if quant.name.matches(name):
                qunatites.append(quant.id)
        if qunatites==[]:
            return None
        if len(qunatites)==1:
            return qunatites[0]
        if len(qunatites)>1:
            warnings.warn("More Than one Quantity found matching "+str(name))
            return qunatites

    def getQunatitysIDsByrefType(self, refType:str):
        qunatites = []
        for quant in self._allQuantities:
            # Check if the given refType is in the quantity's refType list.
            if refType in quant.refType:
                qunatites.append(quant.id)
        if not qunatites:
            return None
        if len(qunatites) == 1:
            return qunatites[0]
        if len(qunatites) > 1:
            warnings.warn("More than one Quantity found matching " + str(refType))
            return qunatites

    def getQunatitysIDsByUnit(self, unit:Union[str,dsiUnit]):
        unit=dsiUnit(unit)
        qunatites = []
        for quant in self._allQuantities:
            # Check if the given refType is in the quantity's refType list.
            try:
                units=quant.data.unit
                if len(units)>1:
                    warnings.warn("The Qunatity"+(quant.__repr__())+" has more than one Unit skipping unit matching")
                elif len(units)==1:
                    if units[0]==unit:
                        qunatites.append(quant.id)
            except AttributeError:
                pass
        if not qunatites:
            return None
        if len(qunatites) == 1:
            return qunatites[0]
        if len(qunatites) > 1:
            warnings.warn("More than one Quantity found matching " + str(unit))
            return qunatites

    def __getitem__(self, index):
        if isinstance(index, str):
            try:
                return self._quntsByID[index]
            except KeyError:
                raise KeyError(
                    f"{index} is type str but  not an id of an Quantity in this table.\n"
                    "The member functions :meth:`getQunatitysIDsByUnit`, :meth:`getQunatitysIDsByrefType`, "
                    "or :meth:`getQunatitysIDsByName` can be used to get the id of the quantity."
                )

    def getTableByCondition(self,*queries):
        """
        Get the index Table for the given query.
        Args:
            querrys: query strings or a list of such to match against the index quantities.
            This are the operators supported ['==','<','<=','>','>=','!=']
            a querry lookslike this ('>=',10.0)
        Returns:
            A DCCFalteTable with subindexd data according matched index quantities.
        """
        # If a single list or tuple is passed, unpack it.
        slices = self.getIndexSlicesByCondition(*queries)
        return self[slices]

    def getTableByNearest(self, *nearestValues, mode='absolute'):
        """
        Get the index Table for the given query.
        Args:
            nearestValues: Either a single list/tuple/array of floats to match against the index quantities,
                           or multiple float arguments.
            Modes:
                - 'lower': nearest index with value <= query.
                - 'higher': nearest index with value >= query.
                - 'absolute': index with smallest absolute difference.
        Returns:
            A DCCFalteTable with subindexd data according matched index quantities.
        """
        # If a single list/tuple is passed, unpack it.
        slices = self.getNearestIndex(*nearestValues, mode=mode)
        return self[slices]

    def getTableFromValues(self, *values):
        """
        Get the index Table for the given query.
        Args:
            values: Either a list with an list/tuple/array of floats for each dimension to match against the index quantities,
                    or multiple  arguments.
        Returns:
            A DCCFalteTable with subindexd data according matched index quantities.
        """
        # If a single list/tuple is passed, unpack it.
        slices = self.getIndexFromValues(*values)
        return self[slices]

    def getIndexSlicesByCondition(self, *queries):
        """
        Get the slices (as lists of indices) for the given query per index dimension.

        The query for each dimension can be:
          - None (unconstrained),
          - A simple condition tuple like ('>=', 10.0),
          - Or a nested query expression combining multiple conditions (using AND, OR, XOR).

        Nested queries are recursively evaluated, and the final result per dimension
        is a sorted list of indices.

        Raises:
          ValueError: if the number of query conditions does not match the table dimension.
        """
        # Unpack if a single list or tuple is passed.
        if len(queries) == 1 and isinstance(queries[0], (list, tuple)):
            if len(self._idxQuantities) != 1:
                queries = queries[0]
            if len(self._idxQuantities) == 1:
                queries = [queries[0]]
        if len(queries) != len(self._idxQuantities):
            raise ValueError("Number of query conditions does not match the table dimension.")

        consolidatedSlices = []
        for i, query in enumerate(queries):
            if query is None:
                # If the query is None, select all indices for that dimension.
                idx_len = len(self._idxQuantities[i].values)
                consolidatedSlices.append(list(range(idx_len)))
                continue
            if not self._idxQuantities[i].sorted:
                raise ValueError("Index Quantities must be sorted to use this function.")

            # Evaluate the (possibly nested) query to get a set of indices.
            indices_set = evaluate_query(query, self._idxQuantities[i].values)
            consolidatedSlices.append(ints_to_slice(sorted(indices_set)))

        return consolidatedSlices

    def getNearestIndex(self, *nearestValues, mode='absolute'):
        """
        Get the slices with the nearest values for the given query.
        Args:
            nearestValues: Either a single list/tuple/array of floats to match against the index quantities,
                           or multiple float arguments.
        Modes:
            - 'lower': nearest index with value <= query.
            - 'higher': nearest index with value >= query.
            - 'absolute': index with smallest absolute difference.
        Returns:
            A list of slices corresponding to the matched index quantities.
        """
        # If a single list/tuple is passed, unpack it.
        if len(nearestValues) == 1 and isinstance(nearestValues[0], (list, tuple)):
            nearestValues = nearestValues[0]

        if len(nearestValues) != len(self._idxQuantities):
            raise ValueError("Number of query quantities does not match the table dimension.")

        slices = []
        for i, value in enumerate(nearestValues):
            if not self._idxQuantities[i].sorted:
                raise ValueError("Index Quantities must be sorted to use this function.")
            if value is None:
                # If the query is None, we can skip this dimension. and add a none Slice witch will select all
                slices.append(slice(None))
                continue
            slice_obj = get_nearest_slice(self._idxQuantities[i].values, value, mode=mode)
            slices.append(slice_obj)
        return slices

    def getIndexFromValues(self, *values):
        """
        Get the slices for the given query.
        Args:
            values: Either a single list/tuple/array of floats to match against the index quantities,
                    or multiple float arguments.
        Returns:
            A list of slices corresponding to the matched index quantities.
        """
        # If a single list/tuple is passed, unpack it.
        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            values = values[0]

        if len(values) != len(self._idxQuantities):
            raise ValueError("Number of query quantities does not match the table dimension.")

        slices = []
        for i, value in enumerate(values):
            if not self._idxQuantities[i].sorted:
                raise ValueError("Index Quantities must be sorted to use this function.")
            slice_obj = get_exact_slice(self._idxQuantities[i].values, value)
            slices.append(slice_obj)
        return slices


class DccLongTable(DccQuantityTable):
    """
       Serializes as a <dcc:list> without sub‑lists, emitting:
         1) dcc:name
         2) dcc:description
         3) dcc:dateTime
         4) repeated <dcc:quantity> entries (all idx + value quantities in order)
         5) dcc:usedMethods, dcc:usedSoftware, dcc:measuringEquipments,
            dcc:influenceConditions, dcc:measurementMetaData
         6) @id, @refId, @refType
       """

    __serialize_fields__ = [
        # 1. name
        FieldSpec(
            name=None,
            tag="dcc:name",
            serializer=lambda s: s.name.to_json_dict()["dcc:name"] if s.name else None
        ),

        # 2. description
        FieldSpec("description", "dcc:description"),

        # 3. dateTime
        FieldSpec("dateTime", "dcc:dateTime"),

        # 4. all quantities as repeated <dcc:quantity>
        FieldSpec(
            name=None,
            tag="dcc:quantity",
            serializer="_build_quantity_list",
            merge=False
        ),

        # 5. optional tail elements
        FieldSpec("usedMethods", "dcc:usedMethods"),
        FieldSpec("usedSoftware", "dcc:usedSoftware"),
        FieldSpec("measuringEquipments", "dcc:measuringEquipments"),
        FieldSpec("influenceConditions", "dcc:influenceConditions"),
        FieldSpec("measurementMetaData", "dcc:measurementMetaData"),

        # 6. attributes
        FieldSpec("id", "@id"),
        FieldSpec("refId", "@refId"),
        FieldSpec("refType", "@refType"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # check refTypes

        expectedRefType = f"basic_{self._dimensionLen}IndexTable"
        if not matchesLongTable(self.refType, self._dimensionLen):
            if getBasicIndexDimensionFromRefTypes(self.refType) is None:
                warnings.warn(f"Table Dimension refType {expectedRefType} missing, added it")
                self.refType.append(expectedRefType)
            else:
                raise ValueError(
                    f"Table Dimension refType {expectedRefType} missing but another one was found: {self.refType}")

        for idx, idxQuant in self._idxQuantities.items():
            expectedRefType = f"basic_tableIndex{idx}"
            if not matchesTableIndex(idxQuant.refType, idx):
                if getBasicIndexDimensionFromRefTypes(idxQuant.refType) is not None:
                    raise ValueError(
                        f"Table Dimension refType {expectedRefType} missing but another one was found: {idxQuant.refType}")
                else:
                    warnings.warn(f"Table Dimension refType {expectedRefType} missing, added it")
                    idxQuant.refType.append(expectedRefType)




    def __getitem__(self, index):
        if isinstance(index, str):
            # Try the general case as implemented in the parent class.
            return super().__getitem__(index)
        elif isinstance(index, int) or isinstance(index, slice) or isinstance(index, list) or isinstance(index, np.ndarray):
            idxQuants=[]
            valueQuants=[]
            for key,idxQuant in self._idxQuantities.items():
                idxQuants.append(idxQuant[index])
            for vQuant in self._valueQuantities:
                valueQuants.append(vQuant[index])
            return(idxQuants, valueQuants)
        elif isinstance(index, tuple):
            if all(isinstance(x, slice) or isinstance(x, int) for x in index):
                # okay we had a tuple of slices user wants acces nd Data
                if len(index) > 1:
                    if len(self._idxQuantities)>1:
                        raise IndexError("DccLongTable does not support multi dimensional slices. Use the indexing methods to get the 1D indexes for your higher dimensional data.")
                    else:
                        raise IndexError(
                            "DccLongTable does not support multi dimensional slices. Use the indexing methods to get the 1D indexes for your higher dimensional data.\n But this instance is 1D anyways.")

    def getIndexSlicesByCondition(self, *queries):
        """
        Get the slices (as lists of indices) for the given query per index dimension.

        The query for each dimension can be:
          - None (unconstrained),
          - A simple condition tuple like ('>=', 10.0),
          - Or a nested query expression combining multiple conditions (using AND, OR, XOR).

        Nested queries are recursively evaluated, and the final result per dimension
        is a sorted list of indices.

        Raises:
          ValueError: if the number of query conditions does not match the table dimension.
        """
        # Unpack if a single list or tuple is passed.
        slices=super().getIndexSlicesByCondition(*queries)
        if len(slices) == 1:
            return slices[0]
        else:
            return slice_AND(*slices)

    def getNearestIndex(self, *nearestValues, mode='absolute'):
        """
        Get the slices with the nearest values for the given query.
        Args:
            nearestValues: Either a single list/tuple/array of floats to match against the index quantities,
                           or multiple float arguments.
        Modes:
            - 'lower': nearest index with value <= query.
            - 'higher': nearest index with value >= query.
            - 'absolute': index with smallest absolute difference.
        Returns:
            A list of slices corresponding to the matched index quantities.
        """
        # If a single list/tuple is passed, unpack it.
        slices=super().getNearestIndex(*nearestValues,mode)
        if len(slices) == 1:
            return slices[0]
        else:
            return slice_AND(*slices)

    def getIndexFromValues(self, *values):
        """
        Get the slices for the given query.
        Args:
            values: Either a single list/tuple/array of floats to match against the index quantities,
                    or multiple float arguments.
        Returns:
            A list of slices corresponding to the matched index quantities.
        """
        # If a single list/tuple is passed, unpack it.
        slices = super().getIndexFromValues(*values)
        if len(slices) == 1:
            return slices[0]
        else:
            return slice_AND(*slices)

    def _build_quantity_list(self) -> list[dict]:
        """
        Return a flat list of each quantity's inner dict, in index-order
        followed by value-order.
        """
        # index quantities in numeric key order
        idxs = [self._idxQuantities[i] for i in sorted(self._idxQuantities)]
        vals = self._valueQuantities
        all_quants = idxs + vals

        return [
            q.to_json_dict()
            for q in all_quants
        ]

    def to_json_dict(self) -> dict:
        """
        Wrap the ordered fields under a single 'dcc:list' element.
        """
        return {"dcc:list": self.to_dict()}

    # alias for existing callers
    toJsonDict = to_json_dict


class DccFlatTable(DccQuantityTable):
    """
    Serializes as a <dcc:list> with:
      1) dcc:name
      2) dcc:description
      3) dcc:dateTime
      4) two recursive <dcc:list> wrappers (indices & data)
      5) dcc:usedMethods, dcc:usedSoftware, dcc:measuringEquipments,
         dcc:influenceConditions, dcc:measurementMetaData
      6) @id, @refId, @refType
    """

    __serialize_fields__ = [
        # 1. name
        FieldSpec(
            name=None,
            tag="dcc:name",
            serializer=lambda s: s.name.to_json_dict()["dcc:name"] if s.name else None
        ),

        # 2. description
        FieldSpec("description", "dcc:description"),

        # 3. dateTime
        FieldSpec("dateTime", "dcc:dateTime"),

        # 4. the two inner <dcc:list> wrappers
        FieldSpec(
            name=None,
            tag="dcc:list",
            serializer="_build_list_wrappers",
            merge=False
        ),

        # 5. optional tail elements
        FieldSpec("usedMethods",          "dcc:usedMethods"),
        FieldSpec("usedSoftware",         "dcc:usedSoftware"),
        FieldSpec("measuringEquipments",  "dcc:measuringEquipments"),
        FieldSpec("influenceConditions",  "dcc:influenceConditions"),
        FieldSpec("measurementMetaData",  "dcc:measurementMetaData"),

        # 6. attributes
        FieldSpec("id",      "@id"),
        FieldSpec("refId",   "@refId"),
        FieldSpec("refType", "@refType"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Additional parsing specific to flat tables can be added here.
        # okay we will reshape the data to the correct shape now
        for valueQuant in self._valueQuantities:
            # Check if the quantity is a DccQuantityType
            if valueQuant.shape != self.shape:
                valueQuant.data.reshape(self.shape)

        expectedRefType = f"basic_{self._dimensionLen}IndexFlatTable"
        if not matchesFlatTable(self._dimensionLen, self.refType):
            if getBasicIndexDimensionFromRefTypes(self.refType) is None:
                warnings.warn(f"Table Dimension refType {expectedRefType} missing, added it")
                self.refType.append(expectedRefType)
            else:
                raise ValueError(
                    f"Table Dimension refType {expectedRefType} missing, but a different one was found: {self.refType}")

        for idx, idxQuant in self._idxQuantities.items():
            expectedIdxRefType = f"basic_FlatTableIndex{idx}"
            if not matchesFlatTableIndex(idxQuant.refType, idx):
                if getBasicIndexDimensionFromRefTypes(idxQuant.refType) is not None:
                    raise ValueError(
                        f"Table Dimension refType {expectedIdxRefType} missing, but a different one was found: {idxQuant.refType}")
                else:
                    warnings.warn(f"Table Dimension refType {expectedIdxRefType} missing, added it")
                    idxQuant.refType.append(expectedIdxRefType)
    def __getitem__(self, index):
        if isinstance(index, str):
            # Try the general case as implemented in the parent class.
            return super().__getitem__(index)
        elif isinstance(index, list):
            # okay we had a list of slices user wants acces nd Data
            if len(index) != len(self._idxQuantities):
                raise IndexError("Number of index quantities does not match the table dimension. if you dont want to index a dimension use \":\" or None")
            else:
                idxQuants = []
                valueQuants = []
                for i,slice in enumerate(index):
                    idxQuants.append(self._idxQuantities[i][slice])
                # Unpack the list by converting it to a tuple.
                index_tuple = tuple(index)
                for vQuant in self._valueQuantities:
                    valueQuants.append(vQuant[index_tuple])
                return (idxQuants, valueQuants)
        elif isinstance(index, tuple):
            # here we go correct type now we check if we have an entry for each dimension
            if len(index) != len(self._idxQuantities):
                raise IndexError("Number of index quantities ("+str(len(index))+") does not match the table dimension ("+str(len(self._idxQuantities))+").")
            else:
                idxQuants = []
                valueQuants = []
                for i in range(len(self._idxQuantities)):
                    idxQuants.append(self._idxQuantities[i][index[i]])
                for vQuant in self._valueQuantities:
                    valueQuants.append(vQuant[index])
                return (idxQuants, valueQuants)
        elif isinstance(index, int) or isinstance(index, slice):
            if len(self._idxQuantities) != 1:
                raise IndexError("Integer/1D Slice indexing not supported for nD DccFlatTable. Use proper slice indexing.\n Hint this table is "+str(len(self._idxQuantities))+" dimensional.")
            else:
                raise RuntimeWarning("Indexing an 1D DccFlatTable with an integer or slice, this will work but 1D DccFlatTable should always be a DccLongTable in the first place!")
                idxQuants = []
                valueQuants = []
                for key, idxQuant in self._idxQuantities.items():
                    idxQuants.append(idxQuant[index])
                for vQuant in self._valueQuantities:
                    valueQuants.append(vQuant[index])
                return (idxQuants, valueQuants)

    def _build_list_wrappers(self) -> list[dict]:
        """
        Build the two <dcc:list> wrappers on the fly:
          - first: index quantities
          - second: data (value) quantities
        """
        # helper to build one wrapper
        def make_wrapper(title: dict, ref_type: list[str], quants: list):
            wrapper = DccName(title).to_json_dict()  # yields {'dcc:name': ...}
            wrapper["@refType"] = ref_type
            # each quant.toJsonDict() returns {'dcc:quantity': {...}}
            # we pull out that inner dict
            wrapper["dcc:quantity"] = [
                q.to_json_dict() for q in quants
            ]
            return wrapper

        # preserve numeric index order
        idx_quants = [self._idxQuantities[i] for i in sorted(self._idxQuantities)]
        val_quants = self._valueQuantities

        index_wrapper = make_wrapper(
            title={"en": "Index Quantities", "de": "Indexquantities"},
            ref_type=["basic_FlatTableIndices"],
            quants=idx_quants
        )
        value_wrapper = make_wrapper(
            title={"en": "Data Quantities",  "de": "Datenquantities"},
            ref_type=["basic_FlatTableData"],
            quants=val_quants
        )

        return [index_wrapper, value_wrapper]

    def to_json_dict(self) -> dict:
        """
        Top‑level wrapper: emit a single 'dcc:list' element
        containing the ordered children from to_dict().
        """
        return {"dcc:list": self.to_dict()}

    # keep old name if anything still calls it
    toJsonDict = to_json_dict

