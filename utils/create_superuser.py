from db.session import SessionLocal
from domains.auth.repositories.user import user_actions
from domains.auth.schemas.role import RoleCreate
from domains.auth.schemas.user import UserCreate
from domains.auth.services.user import user_service


class SuperAdminInfo:
    username: str = "AdministratorAccount"
    password: str = "openforme"
    first_name: str = "Administrator"
    last_name: str = "Account"


class SuperAdminRoleInfo:
    title: str = "SuperAdmin"


async def create_system_admin():
    db = SessionLocal()
    from domains.auth.services.role import role_service

    system_admin_role = await role_service.repo.get_or_create(
        db=db, unique_field="title", data=RoleCreate(title=SuperAdminRoleInfo.title)
    )

    # Check if Super Admin already exists
    system_admin = await user_service.get_user_by_username(db=db, username=SuperAdminInfo.username, silent=True)
    if system_admin: return

    # create user
    system_admin = await user_service.create_user(db=db, data=UserCreate(
        first_name=SuperAdminInfo.first_name,
        last_name=SuperAdminInfo.last_name,
        username=SuperAdminInfo.username,
        password=SuperAdminInfo.password,
    ))

    # assign role
    await user_service.add_roles(db=db, user_id=system_admin.id, role_ids=[system_admin_role.id])
