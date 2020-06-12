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


class DataStoreFactory(DBClassFactory):
    def _name_class_pairs(self):
        return [("users", User), ("roles", Role), ("user_roles", UserRole)]