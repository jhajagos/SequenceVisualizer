from .db_classes import DBClass, DBClassFactory


class User(DBClass):
    def _table_name(self):
        return "users"


class Role(DBClass):
    def _table_name(self):
        return "roles"


class UserRole(DBClass):
    def _table_name(self):
        return "user_roles"


class UserInternalAuthLogin(DBClass):
    def _table_name(self):
        return "user_internal_auth_login"


class UserAuthInternalAudit(DBClass):
    def _table_name(self):
        return "user_auth_internal_audit"


class UserAuthInternal(DBClass):
    def _table_name(self):
        return "user_auth_internal"


class DataStoreFactory(DBClassFactory):
    def _name_class_pairs(self):
        return [("users", User), ("roles", Role), ("user_roles", UserRole),
                ("user_internal_auth_login", UserInternalAuthLogin),
                ("user_auth_internal", UserAuthInternal),
                ("user_auth_internal_audit", UserAuthInternalAudit)]