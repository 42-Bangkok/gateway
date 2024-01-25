from appaccount.serializers.users import MeGetOut, MePatchIn, MePatchOut
from ninja import Router

router = Router(tags=["user", "account"])


@router.get(
    "/me/",
    response={200: MeGetOut},
)
def get_me(request):
    """
    Get current user profile
    """
    user = request.auth.user

    return {**user.userprofile.__dict__, "username": user.username}


@router.patch(
    "/me/",
    response={200: MePatchOut},
)
def patch_me(request, payload: MePatchIn):
    """
    Patch current user profile
    """
    user = request.auth.user

    for k, v in payload.dict(exclude_none=True).items():
        if k == "username":
            user.username = v
            user.save()
            continue
        setattr(user.userprofile, k, v)

    user.userprofile.save()

    return {**user.userprofile.__dict__, "username": user.username}


@router.delete(
    "/me/",
    response={200: None},
)
def delete_me(request):
    """
    Delete current user profile
    """
    user = request.auth.user

    user.delete()

    return None
