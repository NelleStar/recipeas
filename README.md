API: https://spoonacular.com/food-api

This project initially was going to be quite a bit larger than it is currently. I had great aspirations to make it into something more. I was then given my hard deadline and had to ask myself, what can I realistically do within 14 days as a first time app from start to finish?

Instead of putting in all the routes I wanted and include all the features right now, I opted to show what I could do in a smaller app but do it to the very best of my ability. Thus we have reciPEAS 1.0.

My goal is to continue to expand on this project and maybe once the bootcamp is over even rework it with some new languages to really include everything from the course. I want to add many new features as well, such as grocery lists, a better search function (such as main vs side dishes and intolerances), and commenting.

Currently the features that I included and feel confident in are:
*login
*logout
*signup
*delete user
*API GET calls for recipes 
    *randon recipes for inspiration
    *recipes by diet type
    *recipes by cuisine style
    *recipes by ingredient
*Database models for
    *users
    *pantry ingredients
    *favorite recipes
*lists that can have items added and deleted for pantry and favorites
*WTForms and Jinja2 Templates help me to build user inputs on
    *search page
    *user profile page
    *login/signup
*JS Axios/async/await call for favorite button/clicks

currently I have the website set up in such a way that new users are able to browse the recipes by picture and name however they are unable to access them directly without being signed in. They are prompted to login or sign up when they try to access. Once they are logged in, they are taken to their profile page where they can easily access their pantry items (along with adding more into it) and their favorite recipes. They are also able to edit or delete their account from this page.

The search page gives the user a chance to be more specific with their search. They can choose ingredients they want the recipe to include, a diet type and/or a style of food. multiple inputs can be used at once to give the user a specified recipe search.

The user can also get inspired by random finds simply by clicking the navbar reciPEAS title which will give them a page of randomly picked recipes to choose from. Should they browse and find one they like they simply need to press the star/favorite button to add it to their favorites list. If they want to remove a favorite they can unclick it to take it off their list.
