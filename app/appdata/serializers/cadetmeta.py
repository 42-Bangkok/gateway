from ninja import ModelSchema

from appdata.models.cadetmetas import CadetMeta
from appdata.models.intras import HistIntraProfileData


class CadetmetaGetOut(ModelSchema):
    class Meta:
        model = CadetMeta
        fields = "__all__"


class CadetmetaPatchOut(CadetmetaGetOut): ...


class CadetmetaPatchIn(ModelSchema):
    class Meta:
        model = CadetMeta
        fields = ["note"]


class GetLastestCadetMetaOut(ModelSchema):
    class Meta:
        model = HistIntraProfileData
        fields = "__all__"
