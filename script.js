let currentPage = 1;
let resultsPerPage = 10;

document.getElementById("results-per-page").addEventListener("change", function () {
    resultsPerPage = parseInt(this.value);
    currentPage = 1;
    fetchRecipes();
});

async function fetchRecipes() {
    try {
        const response = await fetch('http://localhost:8000/recipes_info?limit=10');
        if (response.ok) {
            const data = await response.json();
            const tableBody = document.querySelector('#recipes-table tbody');
            tableBody.innerHTML = ''; 
            
            data.forEach(recipe => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${recipe.title || 'N/A'}</td>
                    <td>${recipe.cuisine || 'N/A'}</td>
                    <td>${recipe.rating ? recipe.rating : 'N/A'}</td>
                    <td>${recipe.total_time ? recipe.total_time : 'N/A'}</td>
                    <td>${recipe.serves || 'N/A'}</td>
                `;
                tableBody.appendChild(row);
            });
        } else {
            console.error('Failed to fetch recipes:', response.statusText);
        }
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function renderPagination(totalRecords) {
    const totalPages = Math.ceil(totalRecords / resultsPerPage);
    const paginationControls = document.getElementById("pagination-controls");
    paginationControls.innerHTML = "";
    for (let i = 1; i <= totalPages; i++) {
        const button = document.createElement("button");
        button.textContent = i;
        button.classList.add("page-button");
        if (i === currentPage) button.classList.add("active");
        button.addEventListener("click", () => {
            currentPage = i;
            fetchRecipes();
        });
        paginationControls.appendChild(button);
    }
}

window.onload = fetchRecipes;