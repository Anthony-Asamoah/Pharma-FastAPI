from sqlalchemy import inspect

from db.session import SessionLocal, engine
from domains.auth.models import Role, Permission

roles = [
    {'title': 'Admin'},
    {'title': 'Manager'},
    {'title': 'Supervisor'},
    {'title': 'User', 'default': True},
]
permissions = ['CREATE', 'READ', 'UPDATE', 'DELETE']


def create_roles() -> None:
    with SessionLocal() as db:
        for role in roles:
            obj = Role(**role)
            db.add(obj)
        db.commit()


def create_permissions() -> None:
    permissions_list = _get_app_permissions()
    with SessionLocal() as db:
        permission_objects = [Permission(title=perm) for perm in permissions_list]
        db.bulk_save_objects(permission_objects)
        db.commit()


def _get_app_permissions() -> list[str]:
    models = _get_app_models()
    models_permissions = [f"{perm}_{model.upper()}" for model in models for perm in permissions]
    return models_permissions


def _get_app_models() -> list[str]:
    inspector = inspect(engine)
    models = [name for name in inspector.get_table_names()]
    models.remove('alembic_version')  # remove alembic version table
    return models


if __name__ == '__main__':
    create_roles()
    create_permissions()
