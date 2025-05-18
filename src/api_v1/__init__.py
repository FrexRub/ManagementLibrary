from fastapi import APIRouter

from src.api_v1.users.views import router as users_router
from src.api_v1.books.views import router as books_router

router = APIRouter(prefix="/api")
router.include_router(router=users_router)
router.include_router(router=books_router)
