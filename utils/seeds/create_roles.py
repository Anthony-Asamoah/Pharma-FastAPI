from db.session import SessionLocal
from domains.auth.models import Role

roles = [
    {'title': 'Admin'},
    {'title': 'Manager'},
    {'title': 'Supervisor'},
    {'title': 'User', 'default': True},
]

if __name__ == '__main__':
    with SessionLocal() as db:
        for role in roles:
            obj = Role(**role)
            db.add(obj)
        db.commit()
