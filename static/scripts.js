document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.toggle-btn').forEach(button => {
        button.addEventListener('click', () => {
            const subtasks = button.nextElementSibling;
            if (subtasks && subtasks.classList.contains('subtasks')) {
                subtasks.style.display = subtasks.style.display === 'none' ? 'block' : 'none';
            }
        });
    });
});
