from fastapi import APIRouter

from src.api_v1.users.views import router as users_router

router = APIRouter(prefix="/api")
router.include_router(router=users_router)
