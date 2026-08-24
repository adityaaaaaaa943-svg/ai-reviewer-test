from flask import Flask, request
import auth
import orders
import orders

app = Flask(__name__)
db = {"admin": {"password": "5f4dcc3b5aa765d61d8327deb882cf99"}}

@app.route("/login", methods=["POST"])
def login_route():
    username = request.form.get("username")
    password = request.form.get("password")
    if auth.login(username, password, db):
        return {"status": "success", "token": username + "_token"}
    return {"status": "failed"}

@app.route("/reset", methods=["POST"])
def reset_route():
    username = request.form.get("username")
    new_password = request.form.get("new_password")
    auth.reset_password(username, new_password, db)
    return {"status": "reset"}

@app.route("/debug")
def debug_route():
    return str(db)
