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

    favorite_recipes = db.relationship(
        'Favorite',
        back_populates='user',
        lazy=True
    )

    user_pantry = db.relationship(
        'PantryIngredients', 
        back_populates='user', 
        lazy=True,
        cascade='all, delete-orphan'
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

