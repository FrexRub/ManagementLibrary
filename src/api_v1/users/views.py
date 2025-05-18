from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import COOKIE_NAME
from src.core.database import get_async_session
from src.core.exceptions import (
    NotFindUser,
    EmailInUse,
    ErrorInData,
)
from src.core.jwt_utils import create_jwt, validate_password
from src.api_v1.users.crud import (
    get_user_from_db,
    create_user,
)
from src.models.user import User
from src.api_v1.users.depends import current_superuser_user
from src.api_v1.users.schemas import (
    LoginSchemas,
    AuthUserSchemas,
    OutUserSchemas,
    UserCreateSchemas,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/login", response_model=AuthUserSchemas, status_code=status.HTTP_202_ACCEPTED
)
async def user_login(
    response: Response,
    data_login: LoginSchemas,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        user: User = await get_user_from_db(session=session, email=data_login.email)
    except NotFindUser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The user with the username: {data_login.email} not found",
        )

    if await validate_password(
        password=data_login.password, hashed_password=user.hashed_password
    ):
        access_token: str = await create_jwt(str(user.id))

        response.set_cookie(
            key=COOKIE_NAME,
            value=access_token,
            httponly=True,
            samesite="lax",
            path="/",
        )
        return AuthUserSchemas(access_token=access_token, token_type="bearer")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error password for login: {data_login.email}",
        )


@router.get("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)


@router.post(
    "/create", response_model=OutUserSchemas, status_code=status.HTTP_201_CREATED
)
async def user_registration(
    user: UserCreateSchemas,
    session: AsyncSession = Depends(get_async_session),
    superuser_user: User = Depends(current_superuser_user),
):
    try:
        result: User = await create_user(session=session, user_data=user)
    except EmailInUse:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The email address is already in use",
        )
    except ErrorInData:
        pass
    else:
        return result


# @router.get(
#     "/list",
#     response_model=Page[OutUserSchemas],
#     status_code=status.HTTP_200_OK,
# )
# async def get_list_users(
#     session: AsyncSession = Depends(get_async_session),
#     user: User = Depends(current_superuser_user),
# ):
#     return paginate(await get_users(session=session))
#
#
# @router.get(
#     "/{id_user}/", response_model=OutUserSchemas, status_code=status.HTTP_200_OK
# )
# async def get_user(user: User = Depends(user_by_id)):
#     return user
#
#
# @router.put(
#     "/{id_user}/", response_model=OutUserSchemas, status_code=status.HTTP_200_OK
# )
# async def update_user(
#     user_update: UserUpdateSchemas,
#     user: User = Depends(user_by_id),
#     session: AsyncSession = Depends(get_async_session),
# ):
#     try:
#         res = await update_user_db(session=session, user=user, user_update=user_update)
#     except UniqueViolationError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Duplicate email",
#         )
#     else:
#         return res
#
#
# @router.patch(
#     "/{id_user}/", response_model=OutUserSchemas, status_code=status.HTTP_200_OK
# )
# async def update_user_partial(
#     user_update: UserUpdatePartialSchemas,
#     user: User = Depends(user_by_id),
#     session: AsyncSession = Depends(get_async_session),
# ):
#     try:
#         res = await update_user_db(
#             session=session, user=user, user_update=user_update, partial=True
#         )
#     except UniqueViolationError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Duplicate email",
#         )
#     else:
#         return res
#
#
# @router.delete("/{id_user}/", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(
#     user: User = Depends(user_by_id),
#     super_user: User = Depends(current_superuser_user),
#     session: AsyncSession = Depends(get_async_session),
# ) -> None:
#     await delete_user_db(session=session, user=user)
