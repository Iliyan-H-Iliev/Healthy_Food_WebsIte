import os
import secrets
from PIL import Image
from system import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request
from system.forms import RegistrationForm, LoginForm, UpdateAccountForm, RecipeForm
from system.models import User, Post, Recipe
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():  # put application's code here
    recs = Recipe.query.all()
    return render_template("home.html", posts=recs, title="Home")


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


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    file_name, file_extension = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_extension
    picture_path = os.path.join(app.root_path, "static/profile_pics", picture_filename)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_filename


def save_recipe_picture(form_picture):
    random_hex = secrets.token_hex(8)
    file_name, file_extension = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_extension
    picture_path = os.path.join(app.root_path, "static/recipe_pics", picture_filename)
    form_picture.save(picture_path)
    return picture_filename


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_filename = save_picture(form.picture.data)
            current_user.image_file = picture_filename

        current_user.username = form.username.data
        current_user.emai = form.email.data
        db.session.commit()
        flash("Вашият профил беше обновен", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("account.html", title="Account", image_file=image_file, form=form)


@app.route("/recipe/new", methods=["GET", "POST"])
@login_required
def new_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        # recipe_picture = save_recipe_picture(form.picture.data)
        recipe = Recipe(title=form.title.data, ingredients=form.ingredients.data, preparation=form.preparation.data, category="food", user_id=current_user.username)
        db.session.add(recipe)
        db.session.commit()
        flash("Вашият рецпта беше създадена", "success")
        return redirect(url_for("home"))
    return render_template("create_recipe.html", title="New Recipe", form=form, legend="New Recipe")

