from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class CommentForm(FlaskForm):
    """Form for adding.editing messages"""

    text = TextAreaField('text', validators=[DataRequired()])

class UserAddForm(FlaskForm):
    """Form for adding a new user"""

    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[Length(min=6)])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])

class LoginForm(FlaskForm):
    """Form for user login"""

    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[Length(min=6)])

class UserEditForm(FlaskForm):
    """Form for user to edit their personal information"""

    email = StringField("Email", validators=[DataRequired(), Email()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class AddItemToPantry(FlaskForm):
    """basic form for user to submit new pantry items"""

    ingredient_name = StringField('Ingredient Name', validators=[DataRequired()])
