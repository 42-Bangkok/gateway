from ninja import ModelSchema

from appdata.models.cadetmetas import CadetMeta


class CadetmetaGetOut(ModelSchema):
    class Meta:
        model = CadetMeta
        fields = "__all__"


class CadetmetaPatchOut(CadetmetaGetOut): ...


class CadetmetaPatchIn(ModelSchema):
    class Meta:
        model = CadetMeta
        fields = ["note"]
