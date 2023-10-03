from flask import Flask, redirect, render_template, session, flash, jsonify, g, request, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from secret import API_SECRET_KEY
import requests

from werkzeug.security import check_password_hash

from models import db, connect_db, User, Favorite, PantryIngredients
from forms import CommentForm, UserAddForm, UserEditForm, LoginForm, AddItemToPantry
from secret import API_SECRET_KEY

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_recipes'
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
        return redirect(f"/user/{user.id}")
    
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
                print(session[CURR_USER_KEY])
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
#user profile and edit route
@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
def show_user(user_id):
    """Show a specific user profile.
    
    SHOW:  name, email, pantry list
    * Each pantry list item should have: a delete button next to the li and be a link to a /recipes/search.html where that ingredient is put into the ingredient search bar and random recipes are shown.

    LINK: Edit profile, delete profile
    """
    user = User.query.get_or_404(user_id)
    form = AddItemToPantry()

    print(f'User.id = {user}')

    pantry = PantryIngredients.query.filter_by(user_id=user.id).all()
    favorites = Favorite.query.filter_by(user_id=user.id).all()

    if form.validate_on_submit():
        ingredient_name = form.ingredient_name.data
        
        if ingredient_name:
            pantry_item = PantryIngredients(user_id=user.id, ingredient_name=ingredient_name)
            db.session.add(pantry_item)
            db.session.commit()

        return redirect(url_for('show_user', user_id=user_id))

    return render_template('users/profile.html', user=user, form=form, pantry=pantry, favorites=favorites)

@app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """Update profile for current user."""
 
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/login")

    user = User.query.get_or_404(user_id)
    if g.user.id != user.id:
        flash("You can only edit your own profile.", "danger")
        return redirect(f"/users/{g.user.id}")

    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        # Check the password entered by the user
        if User.authenticate(g.user.email, form.password.data):
            # Password is correct, proceed with the update
            
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data

            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(f'/user/{user.id}')
        else:
            flash("Password incorrect!", 'danger')
            

    return render_template('/users/edit.html', user=user, form=form)

@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")

########################################################################
# add to pantry

@app.route('/user/<int:user_id>/add_to_pantry', methods=['POST'])
def add_to_pantry(user_id):
    """add pantry items"""

    user = User.query.get_or_404(user_id)
    ingredient_name = request.form.get('ingredient_name')

    if ingredient_name:
        pantry_item = PantryIngredients(user_id=user.id, ingredient_name=ingredient_name)
        db.session.add(pantry_item)
        db.session.commit()

    return redirect(url_for('show_user', user_id=user_id))


@app.route('/user/<int:user_id>/delete_pantry_item/<int:item_id>', methods=['GET', 'POST'])
def delete_pantry_item(user_id, item_id):
    pantry_item = PantryIngredients.query.get_or_404(item_id)
    
    # Check if the pantry item belongs to the user
    if pantry_item.user_id == user_id:
        db.session.delete(pantry_item)
        db.session.commit()

    return redirect(url_for('show_user', user_id=user_id))

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

    api_url = f'https://api.spoonacular.com/recipes/complexSearch?apiKey={API_SECRET_KEY}&number=21&sort=random'

    try:
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            recipes = data['results']
            user = session.get('user') 
            print(f"User ID in session in group_recipe route: {user}")

            return render_template("/recipes/recipes.html", recipes=recipes, user=user)
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

    if 'curr_user' not in session:
        flash('Please log in to access this page', 'danger')
        return redirect('/login')  # Redirect to the login page

    try:
        response = requests.get(api_url)

        if response.status_code == 200:
            user_id = session.get('curr_user')
            print(f'user_id = {user_id}')

            session_user_id = session.get('curr_user')
            print(f'session_user_id = {session_user_id}')
           

            recipe_data = response.json()
            # Extract the relevant information from the API response

            ingredients = []
            for ingredient in recipe_data['extendedIngredients']:
                ingredient_info = {
                    'name': ingredient['nameClean'],
                    'amount': ingredient['amount'],
                    'unit': ingredient['unit']
                }
                ingredients.append(ingredient_info)

            print(recipe_data)
            recipe = {
                'id': recipe_data['id'],
                'title': recipe_data['title'],
                'image': recipe_data['image'],
                'readyInMinutes': recipe_data['readyInMinutes'],
                'servings': recipe_data['servings'],
                'summary': recipe_data['summary'],
                'ingredients': ingredients,
                'instructions': recipe_data['instructions'].split('\n') if 'instructions' in recipe_data else [],
            }

            return render_template("/recipes/individual.html", recipe=recipe, user_id=user_id)
        else:
            return render_template("/recipes/error.html", error="Failed to fetch recipe")
    except Exception as e:
        return render_template("/recipes/error.html", error=str(e))
    
def fetch_recipe_data_by_id(recipe_id):
    api_url = f'https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={API_SECRET_KEY}'

    print(api_url)
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        recipe_data = response.json()
        return recipe_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching recipe data: {e}")
        return None
    
@app.route('/add_to_favorites', methods=['POST'])
def add_to_favorites():
    user_id = session.get('curr_user')

    if user_id is None:
        flash("Please Log In.", "danger")
        return jsonify(success=False, error="User not logged in")

    recipe_id = request.json.get('recipe_id')
    
    # Assuming you fetch the recipe name along with the recipe details from the API
    recipe_data = fetch_recipe_data_by_id(recipe_id)
    
    if not recipe_data:
        return jsonify(success=False, error="Recipe not found")

    recipe_name = recipe_data.get('title')

    # Check if the user has already liked the recipe
    existing_favorite = Favorite.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()

    try:
        if existing_favorite:
            # unliking a recipe
            db.session.delete(existing_favorite)
            db.session.commit()
            return jsonify(success=True, message="Recipe removed from favorites.")
        else:
            # liking a recipe
            favorite = Favorite(user_id=user_id, recipe_id=recipe_id, recipe_name=recipe_name)
            db.session.add(favorite)
            db.session.commit()
            return jsonify(success=True, message="Recipe added to favorites.")
    except Exception as e:
        return jsonify(success=False, error=str(e))





@app.route('/recipes/search', methods=['GET', 'POST'])
def search_recipes():
    """Search recipes based on diet, cuisine, or ingredients."""
    
    cuisines = [
        "African", "Asian", "American", "British", "Cajun", "Caribbean", "Chinese", "Eastern European", "European", "French", "German", "Greek", "Indian", "Irish", "Italian", "Japanese", "Jewish", "Korean", "Latin American", "Mediterranean", "Mexican", "Middle Eastern", "Nordic", "Southern", "Spanish", "Thai", "Vietnamese"
    ]

    diets = [
        'Gluten Free', 'Keto', 'Vegetarian', 'Lacto-Vegetarian', 'Ovo-Vegetarian', 'Vegan', 'Pescetarian', 'Paleo', 'Primal', 'Low FODMAP', 'Whole30'
    ]

    ingredient_name = request.args.get('ingredients')

    if request.method == 'POST':
        # Retrieve search criteria from the form
        diet = request.form.get('diet')
        cuisine = request.form.get('cuisine')
        ingredients = request.form.get('ingredients')

        # Build the API request URL with the selected parameters
        api_url = f'https://api.spoonacular.com/recipes/complexSearch?apiKey={API_SECRET_KEY}&number=21&sort=random'

        if diet:
            api_url += f'&diet={diet}'
        if cuisine:
            api_url += f'&cuisine={cuisine}'
        if ingredients:
            api_url += f'&includeIngredients={ingredients}'

        print("API URL:", api_url)

        try:
            # Make an API request to the Spoonacular API
            response = requests.get(api_url)

            if response.status_code == 200:
                data = response.json()
                recipes = data['results']
            else:
                recipes = []

        except Exception as e:
            print(str(e))
            recipes = []

        # Pass the list of recipes to the search template
        return render_template('/recipes/search.html', cuisines=cuisines, diets=diets, recipes=recipes, ingredient_name=ingredient_name)

    return render_template('/recipes/search.html', cuisines=cuisines, diets=diets, ingredient_name=ingredient_name)

@app.route('/recipes/search/<string:query>', methods=['GET'])
def search_recipes_query(query):
    api_url = f' https://api.spoonacular.com/food/ingredients/search?apiKey={API_SECRET_KEY}&query={query}'

    print("API URL:", api_url)

    try:
        # Make an API request to the Spoonacular API
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            ingredients = data['results']
        else:
            ingredients = []

    except Exception as e:
        print(str(e))
        ingredients = []
    return jsonify({'result': {'search_results': ingredients}})