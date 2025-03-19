let currentPage = 1;
let resultsPerPage = 10;
let allRecipes = []; // Store all search results
let searchParams = {
    title: "",
    cuisine: "",
    calories: "",
    rating: "",
    total_time: ""
};

document.getElementById("results-per-page").addEventListener("change", function () {
    resultsPerPage = parseInt(this.value);
    currentPage = 1;
    displayRecipes(allRecipes);
});

document.getElementById("prev-page").addEventListener("click", function () {
    if (currentPage > 1) {
        currentPage--;
        displayRecipes(allRecipes);
    }
});

document.getElementById("next-page").addEventListener("click", function () {
    const maxPages = Math.ceil(allRecipes.length / resultsPerPage);
    if (currentPage < maxPages) {
        currentPage++;
        displayRecipes(allRecipes);
    }
});

document.getElementById("search-button").addEventListener("click", function () {
    // Reset to first page when searching
    currentPage = 1;
    
    // Get all search parameters
    searchParams = {
        title: document.getElementById("search-title").value.trim(),
        cuisine: document.getElementById("search-cuisine").value.trim(),
        calories: document.getElementById("search-calories").value.trim(),
        rating: document.getElementById("search-rating").value.trim(),
        total_time: document.getElementById("search-time").value.trim()
    };
    
    fetchRecipes();
});

async function fetchRecipes() {
    try {
        // Build the search URL with parameters
        let apiUrl = "http://localhost:8000/api/recipes/search?";
        const params = new URLSearchParams();
        
        // Add non-empty search parameters
        Object.entries(searchParams).forEach(([key, value]) => {
            if (value) {
                params.append(key, value);
            }
        });
        
        apiUrl += params.toString();
        
        const response = await fetch(apiUrl);

        if (response.ok) {
            allRecipes = await response.json();
            displayRecipes(allRecipes);
        } else {
            console.error("Failed to fetch recipes:", response.statusText);
            alert("Failed to fetch recipes. Please try again.");
        }
    } catch (error) {
        console.error("Error fetching data:", error);
        alert("Error fetching recipes. Please try again.");
    }
}

function displayRecipes(data) {
    const tableBody = document.querySelector("#recipes-table tbody");
    tableBody.innerHTML = "";

    if (data.length === 0) {
        const row = document.createElement("tr");
        row.innerHTML = `<td colspan="5" class="no-results">No recipes found matching your search criteria.</td>`;
        tableBody.appendChild(row);
    } else {
        // Calculate pagination
        const startIndex = (currentPage - 1) * resultsPerPage;
        const endIndex = startIndex + resultsPerPage;
        const paginatedData = data.slice(startIndex, endIndex);

        paginatedData.forEach(recipe => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${recipe.title || "N/A"}</td>
                <td>${recipe.cuisine || "N/A"}</td>
                <td>${recipe.rating ? recipe.rating.toFixed(1) : "N/A"}</td>
                <td>${recipe.total_time ? recipe.total_time + " min" : "N/A"}</td>
                <td>${recipe.serves || "N/A"}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    updatePagination(data.length);
}

function updatePagination(totalItems) {
    const totalPages = Math.ceil(totalItems / resultsPerPage);
    document.getElementById("page-info").textContent = `Page ${currentPage} of ${totalPages}`;
    document.getElementById("prev-page").disabled = currentPage === 1;
    document.getElementById("next-page").disabled = currentPage >= totalPages;
}

// Add event listeners for Enter key in search fields
document.querySelectorAll('.search-bar').forEach(input => {
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('search-button').click();
        }
    });
});

window.onload = fetchRecipes;