from typing import List, Optional

from pydantic import UUID4
from sqlalchemy.orm import Session

from domains.auth.repositories.revoked_token import revoked_token_actions as revoked_token_repo
from domains.auth.schemas.revoked_token import RevokedTokenSchema, RevokedTokenUpdate, RevokedTokenCreate


class RevokedTokenService:

    def __init__(self):
        self.repo = revoked_token_repo

    async def list_revoked_tokens(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
    ) -> List[RevokedTokenSchema]:
        revoked_tokens = await self.repo.get_all(
            db=db, skip=skip, limit=limit, order_by=order_by
        )
        return revoked_tokens

    async def create_revoked_token(self, db: Session, *, revoked_token_in: RevokedTokenCreate) -> RevokedTokenSchema:
        revoked_token = await self.repo.create(db=db, data=revoked_token_in)
        return revoked_token

    async def update_revoked_token(
            self, db: Session, *, id: UUID4, revoked_token_in: RevokedTokenUpdate
    ) -> RevokedTokenSchema:
        revoked_token = await self.repo.get_by_id(db=db, id=id)
        revoked_token = await self.repo.update(db=db, db_obj=revoked_token, data=revoked_token_in)
        return revoked_token

    async def get_revoked_token_by_jti(self, db: Session, jti: str) -> Optional[RevokedTokenSchema]:
        return await self.repo.get_by_filters(db=db, jti=jti, limit=1)

    async def get_revoked_token_by_id(self, db: Session, *, id: UUID4) -> RevokedTokenSchema:
        revoked_token = await self.repo.get_by_id(db=db, id=id)
        return revoked_token

    async def delete_revoked_token(self, db: Session, *, id: UUID4) -> None:
        await self.repo.delete(db=db, id=id, soft=False)

    async def get_revoked_token_by_keywords(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            **kwargs
    ) -> List[RevokedTokenSchema]:
        revoked_tokens = await self.repo.get_by_filters(
            db=db, skip=skip, limit=limit, order_by=order_by, **kwargs
        )
        return revoked_tokens

    async def search_revoked_tokens(
            self, db: Session, *,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[List[str]] = None,
            **kwargs
    ) -> List[RevokedTokenSchema]:
        revoked_tokens = await self.repo.get_by_pattern(
            db=db, skip=skip, limit=limit, order_by=order_by, **kwargs
        )
        return revoked_tokens


revoked_token_service = RevokedTokenService()
