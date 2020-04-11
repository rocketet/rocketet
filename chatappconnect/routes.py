import os
import secrets
from datetime import datetime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from chatappconnect import app, db, bcrypt, mail
from chatappconnect.forms import (SignupForm, LoginForm, UpdateAccountForm,
                                  PostForm, EditPostForm, RequestResetForm,
                                  ResetPasswordForm)
from chatappconnect.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

@app.route("/")
@app.route("/home")
@app.route("/index")
def index():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    return render_template("index.html", posts=posts)

@app.route("/about")
def about():
    return render_template("about.html", title="About")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been created. You can now login.", category="success")
        return redirect(url_for("login"))
    return render_template("signup.html", title="Signup", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash("Login unsuccessful. Please check email and password.", "danger")
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static/profile_pics", picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn

def delete_old_picture():
    picture_path = os.path.join(app.root_path, "static/profile_pics", current_user.image_file)
    os.remove(picture_path)

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            if current_user.image_file != "default.jpg":
                delete_old_picture()
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("You account has been updated!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for("static", filename=f"profile_pics/{current_user.image_file}")
    return render_template("account.html", title="Account", image_file=image_file, form=form)

@app.route("/chat")
@login_required
def chat():
    return redirect(url_for("index"))

@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("You're post has been created!", "success")
        return redirect(url_for("index"))
    return render_template("create_post.html", title="New Post",
                           form=form, legend="New Post")

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)

@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = EditPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.edited = datetime.utcnow()
        db.session.commit()
        flash("Post Edited!", "success")
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template("create_post.html", title="Edit Post",
                           form=form, legend="Edit Post")

@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post Deleted", "success")
    return redirect(url_for("index"))

@app.route("/user/<string:username>")
def user_profile(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(per_page=5, page=page)
    return render_template("user_profile.html", title=user.username, posts=posts, user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request",
                  sender="ChatAppConnect",
                  recipients=[user.email])
    msg.body = f"""To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, simply ignore this email, and no changes will be made.
"""
    mail.send(msg)

@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password.", "info")
        return redirect(url_for("login"))
    return render_template("reset_request.html", title="Reset Password", form=form)

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    user = User.verify_reset_token(token)
    if not user:
        flash("That is an invalid or expired token.", "warning")
        return redirect(url_for("reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        db.session.commit()
        flash(f"Your password has been updated! You can now login.", category="success")
        return redirect(url_for("login"))
    return render_template("reset_token.html", title="Reset Password", form=form)

