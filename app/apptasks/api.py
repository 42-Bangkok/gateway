from ninja import Router
from appcore.services.auths import ServiceBearerTokenAuth
from apptasks.routes.tasks import router as snappy_router


router = Router()
router.add_router("/tasks", snappy_router)
