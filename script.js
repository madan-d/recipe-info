let currentPage = 1;
let resultsPerPage = 10;

document.getElementById("results-per-page").addEventListener("change", function () {
    resultsPerPage = parseInt(this.value);
    currentPage = 1;
    fetchRecipes();
});

document.getElementById("prev-page").addEventListener("click", function () {
    if (currentPage > 1) {
        currentPage--;
        fetchRecipes();
    }
});

document.getElementById("next-page").addEventListener("click", function () {
    currentPage++;
    fetchRecipes();
});

async function fetchRecipes() {
    try {
        const skip = (currentPage - 1) * resultsPerPage;
        const response = await fetch(`http://localhost:8000/recipes_info?skip=${skip}&limit=${resultsPerPage}`);
        
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

            updatePageInfo();
        } else {
            console.error('Failed to fetch recipes:', response.statusText);
        }
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function updatePageInfo() {
    document.getElementById("page-info").textContent = currentPage;
}

window.onload = fetchRecipes;
