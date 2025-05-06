import uuid
import warnings
import numpy as np
from typing import Union
from helpers import FieldSpec, ExplicitSerializerMixin, ensureList, format_slice
from DccName import DccName
from AbstractQuantityTypeData import AbstractQuantityTypeData

class DccQuantityType(ExplicitSerializerMixin):
    """
       Represents the <dcc:quantity> element, serialized in the exact order required
       by the XSD <quantityType> sequence.
       """
    # -------------------------------------------------------------------------
    # 1) Declare every element/attribute in the XSD order:
    #    1. name
    #    2. description
    #    3. choice → data (one of si:real, si:list, etc.)
    #    4. relativeUncertainty
    #    5. usedMethods
    #    6. usedSoftware
    #    7. measuringEquipments
    #    8. measurementMetaData
    #    then attributes: @id, @refId, @refType
    # -------------------------------------------------------------------------
    __serialize_fields__ = [
        # 1. name → merge the DccName dict under 'dcc:name'
        FieldSpec(
            name=None,
            tag="dcc:name",
            serializer=lambda s: s.name.to_json_dict()["dcc:name"]
        ),

        # 2. description (raw dict under 'dcc:description')
        FieldSpec("description", "dcc:description"),

        # 3. data choice → merge whatever data.toJsonDict() returns (e.g. 'si:real', ...)
        FieldSpec(
            name=None,
            tag=None,
            serializer=lambda s: s.data.toJsonDict(),
            merge=True
        ),

        # 4. relativeUncertainty
        FieldSpec("relativeUncertainty", "dcc:relativeUncertainty"),

        # 5. usedMethods
        FieldSpec("usedMethods", "dcc:usedMethods"),

        # 6. usedSoftware
        FieldSpec("usedSoftware", "dcc:usedSoftware"),

        # 7. measuringEquipments
        FieldSpec("measuringEquipments", "dcc:measuringEquipments"),

        # 8. measurementMetaData
        FieldSpec("measurementMetaData", "dcc:measurementMetaData"),

        # Finally, attributes (order doesn't matter in XML, but we keep them last)
        FieldSpec("id", "@id"),
        FieldSpec("refId", "@refId"),
        FieldSpec("refType", "@refType"),
    ]

    def __init__(
            self,
            data: AbstractQuantityTypeData,
            id: str = None,
            refId: list[str] = None,
            refType: list[str] = None,
            name: Union[dict, DccName] = None,
            description: dict = None,
            relativeUncertainty: str = None,
            usedMethods: dict = None,
            usedSoftware: dict = None,
            measuringEquipments: dict = None,
            measurementMetaData: dict = None,
    ) -> None:
        # Core fields
        self.data = data
        self.name = DccName(name) if name is not None else None
        self.description = description
        self.relativeUncertainty = relativeUncertainty
        self.usedMethods = usedMethods
        self.usedSoftware = usedSoftware
        self.measuringEquipments = measuringEquipments
        self.measurementMetaData = measurementMetaData

        # IDs/refs
        self.id = id or f"U{uuid.uuid4()}"
        self.refId = ensureList(refId)
        self.refType = ensureList(refType)

    def __repr__(self) -> str:
        params = {key: value for key, value in vars(self).items() if value is not None}
        paramStr = ", ".join(f"{key}={repr(value)}" for key, value in params.items())
        return f"DccQuantityType({paramStr})"#{hex(id(self))}

    def __str__(self) -> str:
        params = {key: value for key, value in vars(self).items() if value is not None}
        paramStr = "\n".join(f"{key}: {value}" for key, value in params.items())
        return f"\nDccQuantityType\n\n{paramStr}"

    def _new_instance(self, new_data: AbstractQuantityTypeData, names: Union[str, dict] = None):
        """
        Create a new instance of DccQuantityType using the new_data and
        the provided names (which is generated entirely by mergeNames).
        """
        return DccQuantityType(
            data=new_data,
            id='U'+str(uuid.uuid4()),
            refId=self.refId,
            refType=self.refType,
            name=names
            # You can uncomment or add additional attributes as needed.
            # description=self.description,
            # relativeUncertainty=self.relativeUncertainty,
            # usedMethods=self.usedMethods,
            # usedSoftware=self.usedSoftware,
            # measuringEquipments=self.measuringEquipments,
            # measurementMetaData=self.measurementMetaData
        )

    def __getitem__(self, index):
        new_data = self.data.__getitem__(index)
        if len(new_data)==0:
            if isinstance(index, (list, tuple)) and all(isinstance(item, bool) for item in index):
                #okay we got a bool list or tuple as index but numpy cant handle that directly so we will cast and then get the data
                new_data=self.data.__getitem__(np.array(index))
            else:
                # okay somthing else we try cast to np.array anyway lets see
                try:
                    new_data = self.data.__getitem__(np.array(index))
                    if len(new_data)==0:
                        warnings.warn("tryed backup indexing "+str(self)+" with index casted to np.array "+str(np.array(index))+" but still got nothing back. Maybe indexing is wrong")
                except Exception as e:
                    raise e

        if isinstance(index, slice):
            index_str = format_slice(index)
        else:
            index_str = f"[{index}]"

        #TODO move into DccName
        if self.name is not None:
            if isinstance(self.name, dict):
                new_name = {lang: f"{name_val}{index_str}" for lang, name_val in self.name.items()}
            else:
                new_name = f"{self.name}{index_str}"
        else:
            new_name = None

        return self._new_instance(new_data, names=new_name)

    def __len__(self):
        return len(self.data)

    def __neg__(self):
        return self._new_instance(-self.data, names=-self.name)

    def __pos__(self):
        return self._new_instance(+self.data, names=+self.name)

    def __add__(self, other):
        new_data = self.data + (other.data if isinstance(other, DccQuantityType) else other)
        new_name = self.name + (other.name if isinstance(other, DccQuantityType) else DccName(str(other)))
        return self._new_instance(new_data, names=new_name)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        new_data = self.data - (other.data if isinstance(other, DccQuantityType) else other)
        new_name = self.name - (other.name if isinstance(other, DccQuantityType) else DccName(str(other)))
        return self._new_instance(new_data, names=new_name)

    def __rsub__(self, other):
        new_data = (other.data if isinstance(other, DccQuantityType) else other) - self.data
        new_name = (other.name if isinstance(other, DccQuantityType) else str(other)) - self.name
        return self._new_instance(new_data, names=new_name)

    def __mul__(self, other):
        new_data = self.data * (other.data if isinstance(other, DccQuantityType) else other)
        new_name = self.name * (other.name if isinstance(other, DccQuantityType) else str(other))
        return self._new_instance(new_data, names=new_name)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        new_data = self.data / (other.data if isinstance(other, DccQuantityType) else other)
        new_name = self.name / (other.name if isinstance(other, DccQuantityType) else str(other))
        return self._new_instance(new_data, names=new_name)

    def __rtruediv__(self, other):
        new_data = (other.data if isinstance(other, DccQuantityType) else other) / self.data
        new_name = (other.name if isinstance(other, DccQuantityType) else str(other)) / self.name
        return self._new_instance(new_data, names=new_name)

    def __array__(self, dtype=None):
        return np.array(self.data, dtype=dtype)

    @property
    def values(self):
        return self.data.values

    @property
    def uncertainties(self):
        return self.data.uncertainties

    @property
    def sorted(self):
        return self.data.sorted

    def shape(self) -> tuple:
        return self.data.shape

    def reshape(self, *newshape) -> None:
        self.data.reshape(newshape)

    def to_json_dict(self) -> dict:
        """
        Wrap the ordered fields under the <dcc:quantity> root.
        """
        return self.to_dict()
