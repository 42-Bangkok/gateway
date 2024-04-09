from ninja import Router

from ninja.pagination import paginate
from appcore.services.paginate_queryset import PageNumberPaginationExt
from appdata.models.cadetmetas import CadetMeta
from appdata.querysets.cadetmeta import query_latest_hist_intra_profile_data
from appdata.serializers.cadetmeta import (
    CadetmetaGetOut,
    CadetmetaPatchIn,
    CadetmetaPatchOut,
    GetLastestCadetMetaOut,
)

router = Router(tags=["cadet-meta"])


@router.get(
    "/latest/",
    response={
        200: list[GetLastestCadetMetaOut],
    },
)
@paginate(PageNumberPaginationExt, page_size=100)
def get_latest_cadetmeta(request):
    """
    Get the latest cadetmeta of all users
    """
    return query_latest_hist_intra_profile_data()


@router.get(
    "/{login}/",
    response={
        200: CadetmetaGetOut,
    },
)
def get_cadetmeta(request, login: str):
    """
    Get the cadetmeta of a user for the given login
    If meta does not exist it creates one regardless of it being on intra or not.
    """
    cadetmeta, _ = CadetMeta.objects.get_or_create(login=login)
    return cadetmeta


@router.patch(
    "/{login}/",
    response={
        200: CadetmetaPatchOut,
    },
)
def patch_cadetmeta(request, login: str, payload: CadetmetaPatchIn):
    """
    Patch the cadetmeta of a user for the given login
    If meta does not exist it creates one regardless of it being on intra or not.
    """
    cadetmeta, _ = CadetMeta.objects.get_or_create(login=login)
    for key, value in payload.dict().items():
        setattr(cadetmeta, key, value)
    cadetmeta.save()
    return cadetmeta
