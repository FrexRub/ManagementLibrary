from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_session
from src.core.exceptions import (
    ErrorInData,
    ExceptDB,
)
from src.api_v1.library.crud import (
    create_receiving,
    return_receiving,
    get_books,
)
from src.api_v1.users.depends import current_superuser_user, user_by_id

from src.models.user import User
from src.models.book import Book
from src.models.library import ReceivingBook
from src.api_v1.library.schemas import (
    ReceivingCreateSchemas,
    OutReceivingSchemas,
    ReceivingResultSchemas,
    RecevingBookUserSchemas,
)

router = APIRouter(prefix="/library", tags=["Library"])


@router.post(
    "/borrow",
    response_model=OutReceivingSchemas,
    status_code=status.HTTP_201_CREATED,
)
async def borrow_book(
        borrow: ReceivingCreateSchemas,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_superuser_user),
):
    try:
        result: ReceivingBook = await create_receiving(session=session, borrow=borrow)
    except ExceptDB as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    except ErrorInData as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    else:
        return result


@router.post(
    "/return",
    response_model=ReceivingResultSchemas,
    status_code=status.HTTP_201_CREATED,
)
async def return_book(
        receiving: ReceivingCreateSchemas,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_superuser_user),
):
    try:
        result: str = await return_receiving(
            session=session, receiving=receiving
        )
    except ExceptDB as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    except ErrorInData as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )
    else:
        return ReceivingResultSchemas(result=result)


@router.get("/{user_id}/", response_model=list[RecevingBookUserSchemas])
async def get_book_user_by_id(
    user: User = Depends(user_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        result: list[Book] = await get_books(session=session, user_id=user.id)
    except ExceptDB as exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{exp}",
        )

    return result
