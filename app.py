from flask import Flask
from flask import render_template, flash, redirect, request, session, get_flashed_messages
import sqlalchemy as sa
import json
from functional.user_management import CustomAuthUserManagement as UserAuthManagement

app = Flask(__name__)
app.development = True
if app.development:
    app.secret_key = "drn4D3Bz8D4b9CGP8cKR"


def get_database_connection():
    engine = sa.create_engine(app.configuration["database_connection_uri"])
    connection = engine.connect()
    meta_data = sa.MetaData(connection, schema=app.configuration["database_schema"])
    meta_data.reflect()

    return connection, meta_data

@app.route("/", methods=["GET"])
def stub():
    return render_template("index.html")


@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username")
    if "data_store_name" in session:
        session.pop("data_store_name")
    return redirect("/login")


@app.route("/register_user", methods=["GET"])
def get_register_user():
    return render_template("register_user.html")


@app.route("/validate_user_registration", methods=["POST"])
def validate_user_registration():

    connection, metadata = get_database_connection()
    user_auth_manager = UserAuthManagement(connection, metadata, secret=app.secret_key)

    username = request.form["username"]
    email = request.form["email"]
    email = email.strip()

    password = request.form["password"]
    password = password.strip()

    confirm = request.form["confirm"]

    user_check = user_auth_manager.check_user(username)

    passed_checks = True
    if user_check:
        flash("Username already exists")
        passed_checks = False

    if password != confirm:
        flash("Passwords do not match")
        passed_checks = False

    if len(password) < 8:
        flash("Password must at least 8 characters")
        passed_checks = False

    if len(email) == 0:
        flash("Email address cannot be blank")
        passed_checks = False

    if not passed_checks:
        return redirect("/register_user")
    else:
        # Create a user
        user_auth_manager.create_user(username, password=password, account_email_address=email)

        if app.debug:
            validation_code = user_auth_manager.get_validation_code(username)
            user_auth_manager.validate_user_account(username, validation_code)
        else:
            # TODO: Send validation code to user
            pass

        flash("Account created")
        session["username"] = username

        return redirect("/")


@app.route("/validate_login", methods=["GET", "POST"])
def validate_login():

    connection, metadata = get_database_connection()
    user_auth_manager = UserAuthManagement(connection, metadata, secret=app.secret_key)

    username = request.form["username"]
    password = request.form["password"]

    status, message = user_auth_manager.login_with_password(username, password)

    if status:
        session["username"] = username
        return redirect("/")
    else:
        flash(message)
        return redirect("/login")


if __name__ == "__main__":
    app.debug = True
    if app.debug:
        with open("./config_dev.json") as f:
            config = json.load(f)
            app.configuration = config
    app.run()