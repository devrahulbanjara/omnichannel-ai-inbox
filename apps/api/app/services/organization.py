from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Organization


class OrganizationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_current(self) -> Organization:
        """The organization requests act for. No login exists, so it is the oldest organization."""
        org = await self.session.scalar(select(Organization).order_by(Organization.created_at))
        if org is None:
            raise NotFoundError("No organization exists. Run the seed script")
        return org
