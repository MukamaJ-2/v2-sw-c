from e_voting.models.admin import Admin


class AdminService:
    """Business logic for admin account management."""

    def __init__(self, store):
        self._store = store

    def is_username_unique(self, username):
        return all(
            a.username != username for a in self._store.admins.values()
        )

    def create(self, username, full_name, email, password_hash, role,
               created_by):
        admin_id = self._store.next_id("admin")
        admin = Admin(
            admin_id=admin_id,
            username=username,
            password=password_hash,
            full_name=full_name,
            email=email,
            role=role,
        )
        self._store.admins[admin_id] = admin
        self._store.log_action(
            "CREATE_ADMIN", created_by,
            f"Created admin: {username} (Role: {role})"
        )
        self._store.save()
        return admin

    def get_all(self):
        return self._store.admins

    def deactivate(self, admin_id, deactivated_by):
        admin = self._store.admins.get(admin_id)
        if not admin:
            return False, "Admin not found."
        admin.deactivate()
        self._store.log_action(
            "DEACTIVATE_ADMIN", deactivated_by,
            f"Deactivated admin: {admin.username}"
        )
        self._store.save()
        return True, None
