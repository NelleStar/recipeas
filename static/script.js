// document.addEventListener("DOMContentLoaded", function () {
//   const ingredientInput = document.getElementById("ingredientInput");
//   const addIngredientButton = document.getElementById("addIngredientButton");
//   const pantryList = document.getElementById("pantryList");

//   addIngredientButton.addEventListener("click", function (e) {
//     e.preventDefault();
//     const ingredientName = ingredientInput.value.trim();

//     if (ingredientName) {
//       const listItem = document.createElement("li");
//       listItem.innerHTML = `
//                 <span class="ingredient">${ingredientName}</span>
//                 <button class="deleteIngredient">x</button>
//             `;

//       pantryList.appendChild(listItem);

//       // Populate the hidden form field with the ingredient name
//       document.getElementById("ingredient_name").value = ingredientName;

//       // Perform the form submission
//       document.getElementById("addIngredientForm").submit();
//     } else {
//       // Optionally, you can display a message or prevent submission when the input is empty
//       console.log("Ingredient name is empty");
//     }
//   });

//   pantryList.addEventListener("click", function (e) {
//     if (e.target.classList.contains("deleteIngredient")) {
//       e.target.parentElement.remove();
//     }
//   });
// });
// ==============================================================================
// // Your frontend API endpoint
// const elem = document.getElementById("ingredients");
// elem.addEventListener("keydown", queryResults);
// console.log("howdy 2")
// const frontendEndpoint = "/recipes/search/";
// function queryResults () {
//   // Make a request to your backend, which will include the secret token
//   console.log("howdy")
//   axios
//   .get(frontendEndpoint + this.value)
//   .then((response) => {
//     // Handle the response from your backend
//     console.log(response.data);
//   })
//   .catch((error) => {
//     // Handle any errors
//     console.error(error);
//   });
// }

// ============================================================================
function toggleFavorite(user_id, recipeId) {
  console.log("toggleFavorite() called");

  const requestData = `{"user_id": ${user_id}, "recipe_id": ${recipeId}}`;

  axios
    .post("/add_to_favorites", requestData, {
      headers: {
        "Content-Type": "application/json",
      },
    })
    .then(function (response) {
      if (response.data.success) {
        // Toggle the star icon
        const starIcon = document.getElementById("star-icon");
        if (starIcon.classList.contains("fas")) {
          starIcon.classList.remove("fas", "fa-star");
          starIcon.classList.add("far", "fa-star");
        } else {
          starIcon.classList.remove("far", "fa-star");
          starIcon.classList.add("fas", "fa-star");
        }
      } else {
        // Handle any error messages or logic here
      }
    })
    .catch(function (error) {
      console.error(error);
    });
}







