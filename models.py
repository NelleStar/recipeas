"""SQLAlchemy models for recipeas"""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect the database to the Flask app."""
    db.app = app
    db.init_app(app)


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
    user_recipes = db.relationship(
        'Recipe', 
        backref='author', 
        lazy=True,
    )

    favorite_recipes = db.relationship(
        'Recipe',
        secondary='favorites',
        back_populates='favorited_by',
        lazy=True
    )

    @classmethod
    def signup(cls, email, password, first_name, last_name):
        """Signs user up for app
        
        Hashes password and adds user to the system
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(
            email=email,
            password=hashed_pwd,
            first_name=first_name,
            last_name=last_name,
        )
        
        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, email, password):
        """find user with email and password
        
        called on class not individual user - searches for user and if found will return the user object
        """

        user = cls.query.filter_by(email=email).first()

        if user:
            is_auth=bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


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

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    # a recipe can have multiple ingredients (m2m via RecipeIngredient)
    recipe_ingredients = db.relationship(
        'RecipeIngredient', 
        backref='recipe',  
        lazy=True
    )
    
    # a recipe can have multiple comments (12m)
    comments = db.relationship(
        'Comment', 
        backref='recipe_comment', 
        lazy='dynamic'
    )
    
    # a recipe can be marked as a favorite by multiple users (m2m via Favorites)
    favorited_by = db.relationship(
        'User', 
        secondary='favorites', 
        back_populates='favorite_recipes',
        lazy=True,
    )


class Favorite(db.Model):
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
    user = db.relationship(
        'User', 
        backref='favorites', 
        lazy=True
    )
    recipe = db.relationship(
        'Recipe', 
        backref='favorites', 
        lazy=True
    )


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
        nullable=False,
    )

    # m2m via RecipeIngredient
    recipes = db.relationship(
        'RecipeIngredient', 
        backref='ingredient_association', 
        lazy=True,
    )
    # relationship for User to access the pantry
    User.pantry = db.relationship(
        'PantryIngredients', 
        back_populates='user', 
        lazy=True,
    )


class RecipeIngredient(db.Model):
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
    recipe_relationship = db.relationship(
        'Recipe', 
        backref='ingredients_relationship'
    )
    ingredient = db.relationship(
        'Ingredient', 
        backref='recipe_ingredients'
    )

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

    recipe_id = db.Column(
        db.Integer, 
        db.ForeignKey('recipes.id', ondelete='CASCADE'),
        nullable=False,
    )


    # a comment belongs to a specific user (12m)
    user = db.relationship(
        'User', 
        backref='user_comments', 
        lazy=True
    )
    # a comment is associated with a specific recipe (12m)
    recipe = db.relationship(
        'Recipe', 
        backref='recipe_comments', 
        lazy=True
    )


class PantryIngredients(db.Model):
    """Pantry ingredients for each user."""

    __tablename__ = 'pantry_ingredients'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    ingredient_name = db.Column(
        db.String,
        nullable=False,
    )

    # Define the relationship between users and pantry ingredients
    user = db.relationship(
        'User', 
        backref='pantry_ingredients', 
        lazy=True
    )

