from flask import render_template, request, Blueprint, redirect, url_for
from fusionchat.models import Post
from flask_login import login_required

main = Blueprint("main", __name__)

@main.route("/")
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    return render_template("index.html", posts=posts)

@main.route("/about")
def about():
    return render_template("about.html", title="About")

@main.route("/chat")
@login_required
def chat():
    return redirect(url_for("main.home"))