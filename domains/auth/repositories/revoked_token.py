from crud.base_repository import BaseCRUDRepository
from domains.auth.models.revoked_token import RevokedToken
from domains.auth.schemas.revoked_token import (
    RevokedTokenCreate, RevokedTokenUpdate
)


class CRUDRevokedToken(BaseCRUDRepository[RevokedToken, RevokedTokenCreate, RevokedTokenUpdate]):
    pass


revoked_token_actions = CRUDRevokedToken(RevokedToken)
