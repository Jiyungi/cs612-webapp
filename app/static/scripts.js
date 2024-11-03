document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.task-checkbox');
    const completedCountElement = document.querySelector('#completed-count');

    // Add event listeners to checkboxes for task completion
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const taskId = this.dataset.taskId;
            const isCompleted = this.checked; // Get the completion status from the checkbox

            // Send request to toggle completion status
            fetch(`/task/${taskId}/toggle_complete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken() // Ensure CSRF protection
                },
                body: JSON.stringify({ is_completed: isCompleted })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.deleted) {
                        // Remove the task element from the DOM if it was deleted
                        const taskElement = document.querySelector(`#task-${taskId}`);
                        if (taskElement) {
                            taskElement.remove();
                        }
                    } else {
                        // Update the completed task count if needed
                        const completedTasks = document.querySelectorAll('.task-checkbox:checked').length;
                        completedCountElement.textContent = completedTasks;
                    }
                } else {
                    console.error('Failed to toggle task completion');
                    alert('Failed to update task completion status.');
                    // Optionally, revert the checkbox state if the request fails
                    this.checked = !isCompleted;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while updating task completion.');
                // Optionally, revert the checkbox state if the request fails
                this.checked = !isCompleted;
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

// Retrieve CSRF token function
function getCSRFToken() {
    return document.querySelector('input[name="csrf_token"]').value;
}