import datetime


class Admin:
    def __init__(self, admin_id, username, password, full_name, email, role,
                 created_at=None, is_active=True):
        self.id = admin_id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.email = email
        self.role = role
        self.created_at = created_at or str(datetime.datetime.now())
        self.is_active = is_active

    def is_super_admin(self):
        return self.role == "super_admin"

    def deactivate(self):
        self.is_active = False

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            admin_id=data["id"],
            username=data["username"],
            password=data["password"],
            full_name=data["full_name"],
            email=data["email"],
            role=data["role"],
            created_at=data.get("created_at"),
            is_active=data.get("is_active", True),
        )
