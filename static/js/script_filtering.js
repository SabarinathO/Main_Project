const productsPerPage = 4; // Number of products to display per page
let currentPage = 1;
let filteredProducts = []; // To store filtered products

// Function to handle pagination logic
function paginateProducts() {
  const products = filteredProducts.length > 0 ? filteredProducts : document.querySelectorAll(".pro");
  const totalProducts = products.length;
  const totalPages = Math.ceil(totalProducts / productsPerPage);

  // Hide all products initially
  document.querySelectorAll(".pro").forEach((product) => {
    product.style.display = "none";
  });

  // Show products for the current page
  const start = (currentPage - 1) * productsPerPage;
  const end = start + productsPerPage;
  for (let i = start; i < end && i < totalProducts; i++) {
    products[i].style.display = "block";
  }

  // Update pagination buttons
  const paginationContainer = document.getElementById("pagination");
  paginationContainer.innerHTML = ""; // Clear previous buttons

  if (totalPages > 1) {
    for (let i = 1; i <= totalPages; i++) {
      const button = document.createElement("button");
      button.innerText = i;
      button.className = "pagination-button";
      if (i === currentPage) button.classList.add("active");
      button.addEventListener("click", () => {
        currentPage = i;
        paginateProducts();
      });
      paginationContainer.appendChild(button);
    }
  }
}

// Function to filter products by search
function filterProducts() {
  const searchValue = document.getElementById("search-input").value.toLowerCase();
  const products = document.querySelectorAll(".pro");
  filteredProducts = []; // Reset filtered products array

  // Filter products based on search value
  products.forEach((product) => {
    const model = product.getAttribute("data-name").toLowerCase();
    if (model.includes(searchValue)) {
      filteredProducts.push(product);
      product.style.display = ""; // Show matching product
    } else {
      product.style.display = "none"; // Hide non-matching product
    }
  });


  // Show or hide "No products found" message
  const noProducts = document.getElementById("no-products");
  if (noProducts) {
    noProducts.style.display = filteredProducts.length === 0 ? "block" : "none";
  }

  currentPage = 1; // Reset to the first page
  paginateProducts(); // Re-apply pagination after filtering
}

// Function to filter products by category
function filterCategory(category) {
  const products = document.querySelectorAll(".pro");
  const buttons = document.querySelectorAll(".button-value");

  // Remove 'actived' class from all buttons
  buttons.forEach((button) => button.classList.remove("actived"));

  // Highlight the selected category button
  const selectedButton = Array.from(buttons).find((button) =>
    button.getAttribute("onclick").includes(category)
  );
  if (selectedButton) selectedButton.classList.add("actived");

  // Filter products based on category
  filteredProducts = [];
  products.forEach((product) => {
    const productModel = product.getAttribute("data-model").toLowerCase();
    const isVisible = category === "all" || productModel === category.toLowerCase();
    if (isVisible) {
      filteredProducts.push(product);
      product.style.display = ""; // Show matching product
    } else {
      product.style.display = "none"; // Hide non-matching product
    }
  });

  // Show or hide "No products found" message
  const noProducts = document.getElementById("no-products");
  if (noProducts) {
    noProducts.style.display = filteredProducts.length === 0 ? "block" : "none";
  }

  currentPage = 1; // Reset to the first page
  paginateProducts(); // Re-apply pagination after filtering
}

// Function to reset all filters and show all products
function showAllProducts() {
  filteredProducts = []; // Reset filtered products
  document.querySelectorAll(".pro").forEach((product) => {
    product.style.display = "";
  });

  currentPage = 1; // Reset to the first page
  paginateProducts(); // Re-apply pagination for all products
}

// Initialize the script on page load
document.addEventListener("DOMContentLoaded", () => {
  paginateProducts(); // Initial pagination setup
});

