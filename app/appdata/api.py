from ninja import Router
from appcore.services.auths import ServiceBearerTokenAuth
from appdata.routes.cadetmeta import router as cadetmeta_router
from appdata.routes.intra import router as intra_router


router = Router()
router.add_router("/cadetmeta", cadetmeta_router, auth=ServiceBearerTokenAuth())
router.add_router("/intra", intra_router, auth=ServiceBearerTokenAuth())
