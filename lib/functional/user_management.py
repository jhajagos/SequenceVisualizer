from data_access.db_tables import DataStoreFactory

import datetime
import hashlib
import random


class UserManagement(object):
    """Parent class which defines interface for user management and authentication"""

    def __init__(self):
        pass

    def log_event(self, username, status, message):
        return self.log_event(username, status, message)

    def login_with_password(self, username, password):
        """Validate that the username exists and the password is correct"""

        if self.check_user(username):
            pass
        else:
            return False, "User does not exist"

        if self.check_if_account_is_validated(username):
            pass
        else:
            return False, "User is not validated"

        if self.check_if_account_is_locked(username):
            return False, "Account is locked"
        else:
            pass

        if self.validate_password(username, password):
            return True, "Password is correct"
        else:
            return False, "Password is incorrect"

    def check_if_account_is_validated(self, username):
        return self._check_if_account_is_validated(username)

    def validate_user_account(self, username, validation_code):
        return self._validate_user_account(username, validation_code)

    def check_if_account_is_locked(self, username):
        return self._check_if_is_locked(username)

    def check_user(self, username):
        """Validate that the username exists"""
        return self._validate_user(username)

    def validate_password(self, username, password):
        return self._validate_password(username, password)

    def update_password(self, username, password):
        return self._update_password(username, password)

    def create_user(self, username, **kwargs):
        if self.check_user(username):
            return False, "User exists"
        else:
            pass

        return self._create_user(username, kwargs)

    def lock_account(self, username):
        return self._lock_account(username)

    def reset_account(self, username):
        self.lock_account(username)
        return self._reset_account(username)

    def reset_account_with_new_password(self, username, reset_code, new_password):
        """Generates a token which is need to unlock an account and a password reest"""
        return self._reset_account_with_new_password(username, reset_code, new_password)

    def get_validation_code(self, username):
        return self._get_validation_code(username)

    def get_reset_code(self, username):
        return self._get_reset_code(username)

    def set_password(self, username, password):
        return self._set_password(username, password)


def _compute_hash(string_to_hash):
    return hashlib.sha256(string_to_hash.encode("utf8")).hexdigest()


class CustomAuthUserManagement(UserManagement):

    def __init__(self, connection, meta_data, secret):
        self.class_factory = DataStoreFactory(connection, meta_data)
        self.user = self.class_factory.create("users")
        self.user_auth = self.class_factory.create("user_auth_internal")
        self.secret = secret

    def _get_user(self, username):
        return self.user.find_one(username, "username")

    def _get_user_auth(self, username):
        user_obj = self._get_user(username)
        user_id = user_obj.id
        return self.user_auth.find_one(user_id, "user_id")

    def _validate_password(self, username, password):
        user_auth_obj = self._get_user_auth(username)

        hashed_pwd = _compute_hash(password)
        if user_auth_obj.sha == hashed_pwd:
            return True
        else:
            return False

    def _validate_user(self, username):
        user_obj = self._get_user(username)
        if user_obj is not None:
            if self._get_user_auth(username):
                return True
            else:
                return False
        else:
            return False

    def _create_user(self, username, kwargs_dict):
        user_id = self.user.insert_struct({"username": username, "created_at": datetime.datetime.utcnow()})

        kwargs_dict["user_id"] = user_id
        kwargs_dict["is_account_validated"] = False
        kwargs_dict["validation_code"] = self._create_validation_code()
        kwargs_dict["validation_code_created_at"] = datetime.datetime.utcnow()
        kwargs_dict["created_at"] = datetime.datetime.utcnow()

        if "password" in kwargs_dict:
            password = kwargs_dict["password"]
            sha = _compute_hash(password)
            kwargs_dict.pop("password")
            kwargs_dict["sha"] = sha

        user_auth = self.user_auth.insert_struct(kwargs_dict)

        return user_auth

    def _create_validation_code(self):
        return _compute_hash(self.secret + str(random.random()))

    def _check_if_account_is_validated(self, username):
        user_auth_obj = self._get_user_auth(username)

        if user_auth_obj.is_account_validated:
            return True
        else:
            return False

    def _validate_user_account(self, username, validation_code, max_time_lapse=1800):
        user_auth_obj = self._get_user_auth(username)

        current_utc_time = datetime.datetime.utcnow()
        time_delta = current_utc_time - user_auth_obj.validation_code_created_at
        time_lapse = time_delta.total_seconds()

        if time_lapse <= max_time_lapse:
            if validation_code == user_auth_obj.validation_code:
                user_update_dict = {"validation_code": None, "validation_code_created_at": None, "is_account_validated": True}
                self.user_auth.update_struct(user_auth_obj.id, user_update_dict)
                return True
            else:
                return False
        else:
            return False

    def _lock_account(self, username):
        user_auth_obj = self._get_user_auth(username)
        user_auth_id = user_auth_obj.id
        self.user_auth.update_struct(user_auth_id, {"is_account_locked": True})

    def _check_if_is_locked(self, username):
        user_auth_obj = self._get_user_auth(username)
        return user_auth_obj.is_account_locked

    def _get_validation_code(self, username):
        user_auth_obj = self._get_user_auth(username)
        return user_auth_obj.validation_code

    def _get_reset_code(self, username):
        user_auth_obj = self._get_user_auth(username)
        return user_auth_obj.reset_code

    def _reset_account(self, username):
        user_auth_obj = self._get_user_auth(username)
        user_auth_id = user_auth_obj.id
        reset_utc_datetime = datetime.datetime.utcnow()
        reset_code = self._create_validation_code()
        self.user_auth.update_struct(user_auth_id, {"reset_code": reset_code, "reset_code_created_at": reset_utc_datetime})

    def _reset_account_with_new_password(self, username, reset_code, new_password, max_time_lapse=1800):

        user_auth_obj = self._get_user_auth(username)

        if user_auth_obj.reset_code is not None:

            current_utc_time = datetime.datetime.utcnow()
            time_delta = current_utc_time - user_auth_obj.reset_code_created_at
            time_lapse = time_delta.total_seconds()

            if time_lapse <= max_time_lapse:

                if reset_code == user_auth_obj.reset_code:

                    sha = _compute_hash(new_password)
                    id = user_auth_obj.id
                    self.user_auth.update_struct(id, {"is_account_locked": False, "reset_code": None,
                                                      "reset_code_created_at": None, "sha": sha})

                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def _set_password(self, username, password):

        user_auth_obj = self._get_user_auth(username)
        user_auth_id = user_auth_obj.id
        sha = _compute_hash(password)

        self.user_auth.update_struct(user_auth_id, {"sha": sha})