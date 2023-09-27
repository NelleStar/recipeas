from flask import Flask, redirect, render_template, session, flash, g, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from secret import API_SECRET_KEY
import requests

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

    if 'curr_user' in session:
        session.pop('curr_user')
        flash("Logged out successfully", "success")
    else:
        flash("No user is currently logged in", "info")
    
    return redirect("/login")


################################################################################
#user profile and favorites route
@app.route('/user/<int:user_id>')
def show_user(user_id):
    """Show a specific user profile 
    
    SHOW: Full name, email, date joined, pantry list
    *each pantry list should have: a delete button next to the li and be a link to a recipes list that includes that ingredient

    LINK: Edit profile, delete profile
    """
    user = User.query.get_or_404(user_id)

    return render_template('/users/profile.html', user=user)


################################################################################
#recipes list and individual page
@app.route('/recipes')
def recipes():
    """
    Show random list of recipes when first accessing the page

    Have Search box to search recipes by ingredient

    Have Search box to search recipes by cuisine style

    Each recipe should have a picture (if available) with the recipe name overlaying it at the bottom and a spoon icon for favoriting
    """

    api_url = f'https://api.spoonacular.com/recipes/random?number=21&apiKey={API_SECRET_KEY}'

    try:
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            recipes = data['recipes']

            return render_template("/recipes/recipes.html", recipes=recipes)
        else:
            return render_template("/recipes/error.html", error="Failed to fetch recipes")
    except Exception as e:
        return render_template("/recipes/error.html", error=str(e))
    
@app.route('/recipes/<int:id>')
def individual_recipe(id):
    """
    Display an individual recipe by its ID.
    """
    api_url = f'https://api.spoonacular.com/recipes/{id}/information?apiKey={API_SECRET_KEY}'

    try:
        response = requests.get(api_url)

        if response.status_code == 200:
            recipe_data = response.json()
            # Extract the relevant information from the API response
            recipe = {
                'id': recipe_data['id'],
                'title': recipe_data['title'],
                'image': recipe_data['image'],
                'readyInMinutes': recipe_data['readyInMinutes'],
                'servings': recipe_data['servings'],
                'summary': recipe_data['summary'],
                'instructions': recipe_data['instructions'].split('\n') if 'instructions' in recipe_data else [],
            }

            return render_template("/recipes/individual.html", recipe=recipe)
        else:
            return render_template("/recipes/error.html", error="Failed to fetch recipe")
    except Exception as e:
        return render_template("/recipes/error.html", error=str(e))
    
@app.route('/recipes/search', methods=['GET', 'POST'])
def search_recipes():
    """search recipes based off of diet, cuisine or ingredients"""

    if request.method == 'POST':
        # Retrieve search criteria from the form
        diet = request.form.get('diet')
        cuisine = request.form.get('cuisine')
        ingredients = request.form.get('ingredients')

        # Build the search query based on the criteria
        # You can use these criteria to construct the 'diet', 'cuisine', and 'includeIngredients' parameters for the Spoonacular API request

        # Make the API request with the constructed query
        # Parse the response and display the search results in the template
        # You can use the same 'recipes.html' template for displaying search results

    return render_template('recipes/search.html')
