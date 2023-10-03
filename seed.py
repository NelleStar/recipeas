from app import app
from models import db, User, Favorite, PantryIngredients
from flask_bcrypt import Bcrypt

db.drop_all()
db.create_all()

bcrypt = Bcrypt()

u1 = User(
    email = "joey@joey.com",
    password = bcrypt.generate_password_hash("friends").decode("utf-8"),
    first_name = "Joey",
    last_name = "Tribbiani",
)
u2 = User(
    email = "rachel@rachel.com",
    password = bcrypt.generate_password_hash("friends").decode("utf-8"),
    first_name = "Rachel",
    last_name = "Green",
)
u3 = User(
    email = "ross@ross.com",
    password = bcrypt.generate_password_hash("friends").decode("utf-8"),
    first_name = "Ross",
    last_name = "Geller",
)
u4 = User(
    email = "monica@monica.com",
    password = bcrypt.generate_password_hash("friends").decode("utf-8"),
    first_name = "Monica",
    last_name = "Geller"
)
u5 = User(
    email = "chandler@chandler.com",
    password = bcrypt.generate_password_hash("friends").decode("utf-8"),
    first_name = "Chandler",
    last_name = "Bing",
)
u6 = User(
    email = "pheobe@pheobe.com",
    password = bcrypt.generate_password_hash("friends").decode("utf-8"),
    first_name = "Pheobe",
    last_name = "Buffay",
)

db.session.add_all([u1,u2,u3,u4,u5,u6])
db.session.commit()

f1 = Favorite(
    user_id = 6,
    recipe_id = 664470,
    recipe_name = "Vegan Pea and Mint Pesto Bruschetta"
)
f2 = Favorite(
    user_id = 1,
    recipe_id = 650700,
    recipe_name = "Mama Mia's Minestrone"
)
f3 = Favorite(
    user_id = 3,
    recipe_id = 664017,
    recipe_name = "Turkey Chorizo and Potato Tacos"
)
f4 = Favorite(
    user_id = 2,
    recipe_id = 636732,
    recipe_name = "Cajun Lobster Pasta"
)
f5 = Favorite(
    user_id = 4,
    recipe_id = 641270,
    recipe_name = "Dark Chocolate Walnut Biscotti"
)
f6 = Favorite(
    user_id = 5,
    recipe_id = 665170,
    recipe_name = "White Chocolate Cherry Hand Pies"
)

db.session.add_all([f1,f2,f3,f4,f5,f6])
db.session.commit()

p1 = PantryIngredients(
    user_id = 1,
    ingredient_name = "tuna",
)
p2 = PantryIngredients(
    user_id = 2,
    ingredient_name = "romaine",
)
p3 = PantryIngredients(
    user_id = 3,
    ingredient_name = "pepper",
)
p4 = PantryIngredients(
    user_id = 4,
    ingredient_name = "steak",
)
p5 = PantryIngredients(
    user_id = 5,
    ingredient_name = "pinto beans",
)
p6 = PantryIngredients(
    user_id = 6,
    ingredient_name = "flour",
)

db.session.add_all([p1,p2,p3,p4,p5,p6])
db.session.commit()
