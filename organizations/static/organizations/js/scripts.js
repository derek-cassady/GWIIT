document.addEventListener("DOMContentLoaded", function () {
    // Get the dropdown element and the description field
    const nameDropdown = document.getElementById("id_name");
    const descriptionField = document.getElementById("id_description");

    // Disable the description field (read-only)
    if (descriptionField) {
        descriptionField.setAttribute("readonly", "readonly");
        descriptionField.setAttribute("placeholder", "Description will update based on selection");
    }

    // Add an event listener to the dropdown to fetch the description when an option is selected
    nameDropdown.addEventListener("change", function () {
        const selectedName = this.value; // Get the selected name

        // If no name is selected, clear the description field
        if (!selectedName) {
            descriptionField.value = "";
            return;
        }

        // Make an AJAX request to fetch the description for the selected name
        fetch(`/organizations/type-description/?name=${encodeURIComponent(selectedName)}`)
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then((data) => {
                // Update the description field with the returned description
                descriptionField.value = data.description || "";
            })
            .catch((error) => {
                console.error("Error fetching description:", error);
                descriptionField.value = "Error fetching description";
            });
    });
});

// Function to fetch organization type details and populate the edit form
function showEditForm(pk) {
    const editSection = document.getElementById('edit-type-section');
    const editForm = document.getElementById('edit-type-form');

    // Fetch organization type data via API
    fetch(`/organizations/types/edit/${pk}/`)
        .then(response => response.json())
        .then(data => {
            // Populate the form fields with the fetched data
            editForm.elements['name'].value = data.name;
            editForm.elements['description'].value = data.description;

            // Add the PK to the form for submission
            editForm.action = `/organizations/types/edit/${pk}/`;
            
            // Show the edit form section
            editSection.style.display = 'block';
        })
        .catch(error => {
            console.error('Error fetching organization type data:', error);
        });
}

// Function to hide the edit form
function hideEditForm() {
    document.getElementById('edit-type-section').style.display = 'none';
}

// Add functionality to reset the form after submission
document.getElementById('add-type-form').addEventListener(
    'submit', function(event) {setTimeout(() => {
        // Reset the form fields after submission
        this.reset();
    }, 
    // Slight delay to ensure the form processes
    1000);
});

// Function to show the delete confirmation modal and set the form action
function showDeleteConfirmation(pk) {
    const deleteModal = document.getElementById('delete-confirmation-modal');
    const deleteForm = document.getElementById('delete-type-form');

    // Update the form action with the correct pk
    deleteForm.action = `/organizations/types/delete/${pk}/`;

    // Show the delete confirmation modal
    deleteModal.style.display = 'block';
}

// Function to hide the delete confirmation modal
function hideDeleteConfirmation() {
    const deleteModal = document.getElementById('delete-confirmation-modal');
    deleteModal.style.display = 'none';
}