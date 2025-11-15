from fastapi import APIRouter

from app.api.v1.profile import user_profile

router = APIRouter()
router.include_router(user_profile.router)
