from flask import Flask, redirect, render_template, session, flash, g, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from secret import API_SECRET_KEY

from werkzeug.security import check_password_hash

from models import db, connect_db, User, Recipe, Favorite, Ingredient, RecipeIngredient, Comment
from forms import CommentForm, UserAddForm, UserEditForm, LoginForm
from secret import API_SECRET_KEY

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///recipeas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

app.app_context().push()

connect_db(app)
db.create_all()

app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

################################################################################
#home route aka recipes
@app.route('/')
def homepage():
    """returns a list of recipes and header for user to login/sign up/logout and search using a q param"""

    if g.user:
        return render_template('home.html')
    
    else:
        return render_template("home-anon.html")


################################################################################
#login / signup / logout routes
@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that email: flash message
    and re-present form.
    """
    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user=User.signup(
                email=form.email.data,
                password = form.password.data,
                first_name = form.first_name.data,
                last_name=form.last_name.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Email already taken", 'danger')
            return render_template("users/signup.html", form=form)
        
        do_login(user)
        return redirect("/recipes")
    
    else:
        return render_template('users/signup.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login"""

    form = LoginForm()

    if form.validate_on_submit():
        print(f'email: {form.email.data} password: {form.password.data}')
        
        try:
            user = User.authenticate(form.email.data, form.password.data)
            
            if user:
                print(f"User object: {user}")

                do_login(user)
                flash(f"Hello, {user.first_name}", "success")
                return redirect(f"/user/{user.id}")

            flash('Invalid; try again!', 'danger')

        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('users/login.html', form=form)



@app.route("/logout")
def logout():
    """Handle user logout"""

    session.pop('curr_user')
    flash("Successfully logged out. See you soon!")

    return redirect('/login')

################################################################################
#user profile and favorites route
@app.route('/user/<int:user_id>')
def show_user(user_id):
    """Show a specific user profile 
    
    SHOW: Full name, email, date joined, pantry list
    *each pantry list should have: a delete button next to the li and be a link to a recipes list that includes that ingredient

    LINK: Edit profile, delete profile
    """
    return render_template('/users/profile.html')

@app.route('/user/<int:user_id>/favorites')
def show_favorites(user_id):
    """Show a list of recipe this user has liked
    
    LINKED in HEADER once they are logged in?
    """
