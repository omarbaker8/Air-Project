
window.addEventListener('message', function(event) {
    console.log('Message received:', event.data);
    if (event.data.type === 'toggleFavorite') {
        toggleFavorite(event.data.uid);
    }
});

function showMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.textContent = message;
    messageElement.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        z-index: 1000;
    `;
    document.body.appendChild(messageElement);

    setTimeout(() => {
        document.body.removeChild(messageElement);
    }, 1500);
}

function toggleFavorite(uid) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch(`api/toggle_favorite/${uid}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log('Favorite status:', data.is_favorite);
        showMessage(data.is_favorite ? 'Added to favorites' : 'Removed from favorites');
        setTimeout(() => location.reload(), 1500);
    })
    .catch((error) => {
        console.error('Error:', error);
        showMessage('Error updating favorite status');
    });
}