from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.error import ERROR_RESPONSES
from app.schemas.organization import OrganizationRead
from app.services.organization import OrganizationService

router = APIRouter(prefix="/organization", tags=["inbox"], responses=ERROR_RESPONSES)


@router.get("")
async def get_organization(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OrganizationRead:
    organization_service = OrganizationService(session)
    return await organization_service.get_current()
