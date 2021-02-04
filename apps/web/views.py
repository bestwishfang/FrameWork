# -*- coding: utf-8 -*-

import hashlib
import functools

from flask import request
from flask import session
from flask import render_template, redirect

from . import web, web_api
from .models import WebUser


def set_pwd(password):
    SALT = b'bestwish'
    md5 = hashlib.md5(SALT)
    md5.update(password.encode('utf-8'))
    ret = md5.hexdigest()
    return ret


def login_valid(func):
    @functools.wraps(func)  # 保留原函数的名称
    def inner(*args, **kwargs):
        username = request.cookies.get("username")
        id = request.cookies.get("id", "0")
        user = WebUser.query.get(int(id))
        session_username = session.get("username")
        if user:  # 检测是否有对应id的用户
            if user.username == username and username == session_username:  # 用户名是否对应
                return func(*args, **kwargs)
            else:
                return redirect("/login")
        else:
            return redirect("/login")

    return inner


@web.route("/register", methods=["GET", "POST"])
def register():
    """
    form表单提交的数据由request.form 接收
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        user = WebUser()
        user.username = username
        user.password = set_pwd(password)
        user.email = email
        user.save()
    return render_template("web/register.html")


@web.route("/login", methods=["get", "post"])
def login():
    error = ""
    if request.method == "POST":
        form_data = request.form
        email = form_data.get("email")
        password = form_data.get("password")

        user = WebUser.query.filter_by(email=email).first()
        if user:
            db_password = user.password
            if set_pwd(password) == db_password:
                response = redirect("/web")
                response.set_cookie("username", user.username)
                response.set_cookie("email", user.email)
                response.set_cookie("id", str(user.id))
                session["username"] = user.username
                return response
            else:
                error = "密码错误"
        else:
            error = "用户名不存在"
    return render_template("web/login.html", error=error)


@web.route("/logout")
def logout():
    response = redirect("/login/")
    response.delete_cookie("username")
    response.delete_cookie("email")
    response.delete_cookie("id")
    session.pop("username")
    del session["username"]
    return response


@web.route('/')
def index():
    return render_template('web/index.html')