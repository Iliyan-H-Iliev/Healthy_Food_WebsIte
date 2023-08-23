from system import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request
from system.forms import RegistrationForm, LoginForm
from system.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

posts = [
    {
        "author": "Corey Schafer",
        "title": "Blog Post 1",
        "content": "First post content",
        "date_posted": "April 20, 2018",
    },
    {
        "author": "Jane Doe",
        "title": "Blog Post 2",
        "content": "Second post content",
        "date_posted": "April 21, 2019",
    },
]

sort_recipes = {
    "Закуски": "breakfast",
    "Салати": "salads",
    "Супи": "soups",
    "Основни ястия": "main_dishes",
    "Десерти": "desserts",
    "Напитки": "drinks",
    "Други": "other",

}


@app.route("/")
@app.route("/home")
def home():  # put application's code here
    return render_template("home.html", posts=posts)


@app.route("/recipes")
def recipes():  # put application's code here
    return render_template("recipes.html", title="Recipes")


@app.route("/about")
def about():  # put application's code here
    return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Акаунтът беше успешно създаден", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Здрaвей {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("account"))
        else:
            flash("Неуспешен вход. Грешен емейл или парола", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/account")
@login_required
def account():
    image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
    return render_template("account.html", title="Account", image_file=image_file)
