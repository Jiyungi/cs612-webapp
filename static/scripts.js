document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.task-checkbox');
    const completedCountElement = document.querySelector('#completed-count');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const taskId = this.dataset.taskId;
            fetch(`/task/${taskId}/toggle_complete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken() // Ensure CSRF protection
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const completedTasks = document.querySelectorAll('.task-checkbox:checked').length;
                    completedCountElement.textContent = completedTasks;
                } else {
                    console.error('Failed to toggle task completion');
                }
            });
        });
    });

    // Add event listener for toggle buttons
    const toggleButtons = document.querySelectorAll('.toggle-btn');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const subtasks = this.nextElementSibling;
            if (subtasks.style.display === 'none' || subtasks.style.display === '') {
                subtasks.style.display = 'block';
            } else {
                subtasks.style.display = 'none';
            }
        });
    });
});

function getCSRFToken() {
    // Implement this function to retrieve the CSRF token from your page
    return document.querySelector('input[name="csrf_token"]').value;
}
