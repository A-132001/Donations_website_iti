// CSRF token setup for AJAX requests
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
            return cookie.substring('csrftoken='.length, cookie.length);
        }
    }
    return null;
}

const csrfToken = getCSRFToken();

// AJAX request to make a donation
function makeDonation(url, amount) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ amount: amount }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Donation successful!');
        } else {
            alert('Donation failed. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An unexpected error occurred. Please try again later.');
    });
}

// Attach event listener to donation buttons
document.querySelectorAll('.donate-button').forEach(button => {
    button.addEventListener('click', event => {
        const url = event.target.dataset.url;
        let amount = prompt('Enter donation amount:');
        amount = parseFloat(amount);
        if (amount > 0) {
            makeDonation(url, amount);
        } else {
            alert('Please enter a valid donation amount.');
        }
    });
});