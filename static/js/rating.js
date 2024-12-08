function openRatingModal(orderId) {
    const modal = document.getElementById('ratingModal');
    modal.style.display = 'block';
    
    fetch(`/order/${orderId}/rate/`)
        .then(response => response.text())
        .then(html => {
            modal.innerHTML = html;
            initRatingForm();
        });
}

function closeRatingModal() {
    const modal = document.getElementById('ratingModal');
    modal.style.display = 'none';
}

function initRatingForm() {
    const form = document.getElementById('ratingForm');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                closeRatingModal();
                location.reload();
            } else {
                // Handle errors
                Object.keys(data.errors).forEach(key => {
                    const errorElement = document.createElement('div');
                    errorElement.className = 'error-message';
                    errorElement.textContent = data.errors[key];
                    form.querySelector(`[name="${key}"]`).parentNode.appendChild(errorElement);
                });
            }
        });
    });
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('ratingModal');
    if (event.target == modal) {
        closeRatingModal();
    }
} 