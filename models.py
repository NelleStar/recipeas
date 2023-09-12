"""SQLAlchemy models for recipeas"""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    first_name = db.Column(
        db.Text,
        nullable=False,
    )

    last_name = db.Column(
        db.Text,
        nullable=False,
    )

    # a user can have multiple recipes (12m)
    recipes = db.relationship('Recipe', backref='author', lazy=True)

class Recipe(db.Model):
    """instance of a recipe"""

    __tablename__ = 'recipes'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text
    )
    
    instructions = db.Column(
        db.Text
    )

    # a recipe can have multiple ingredients (m2m via RecipeIngredient)
    ingredients = db.relationships('RecipeIngredient', backref='recipe', lazy=True)
    # a recipe can have multiple comments (12m)
    comments = db.relationship('Comment', backref='recipe', lazy=True)
    # a recipe can be marked as a favorite by multiple users (m2m via Favorites)
    favorited_by = db.relationship('User', secondary='favorites', back_populates='favorite_recipes')

class Favorites(db.Model):
    """Mapping users favorite recipes."""

    __tablename__ = 'favorites' 

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey('recipes.id', ondelete='cascade'),
        unique=True
    )

    # m2m between users and favorite recipes
    user = db.relationship('User', backref='favorites', lazy=True)
    recipe = db.relationship('Recipe', backref='favorites', lazy=True)


class Ingredient(db.Model):
    """instance of a single ingredient"""

    __tablename__ = 'ingredients'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    name = db.Column(
        db.Text,
        nullable=false,
    )

    # m2m via RecipeIngredient
    recipes = db.relationship('RecipeIngredient', backref='ingredient', lazy=True)


class RecipeIngredients(db.Model):
    """mapping ingredients to recipes"""

    __tablename__ = "recipe_ingredients"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey('recipes.id', ondelete='cascade'),
        nullable=False,
    )

    ingredient_id = db.Column(
        db.Integer,
        db.ForeignKey('ingredients.id', ondelete='cascade'),
        nullable=False,
    )

    quantity = db.Column(
        db.String(50), 
        nullable=False,
    )

    # m2m relationship linking recipe and ingredients
    recipe = db.relationship('Recipe', backref='recipe_ingredients')
    ingredient = db.relationship('Ingredient', backref='recipe_ingredients')

class Comment(db.Model):
    """An individual comment."""

    __tablename__ = 'comments'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    text = db.Column(
        db.String(140),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    # a comment belongs to a specific user (12m)
    user = db.relationship('User', backref='comments', lazy=True)
    # a comment is associated with a specific recipe (12m)
    recipe = db.relationship('Recipe', backref='comments', lazy=True)