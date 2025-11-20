function toggleBasket() {
    document.getElementById('basketDropdown').classList.toggle('show');
}

function addToCart(url, itemId) {
    const formData = new FormData();
    formData.append('item_id', itemId);
    formData.append('quantity', 1);
    formData.append('action', 'create_order');

    fetch(url, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                location.reload();
            }
        })
        .catch(error => console.error('Error:', error));
}

function removeOrder(url, orderId) {
    const formData = new FormData();
    formData.append('order_id', orderId);
    formData.append('action', 'delete_order');
    fetch(url, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                location.reload();
            }
        })
        .catch(error => console.error('Error:', error));
}

function checkoutAll(url, stripePublicKey) {
    const orders = document.querySelectorAll('.basket-item');
    if (orders.length === 0) {
        alert('Your cart is empty!');
        return;
    }
    fetch(url, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(data => {
            if (data.session_id) {
                const stripe = Stripe(stripePublicKey);
                stripe.redirectToCheckout({ sessionId: data.session_id });
            }
        })
        .catch(error => console.error('Error:', error));
}

window.onclick = function (event) {
    if (!event.target.closest('.basket')) {
        document.getElementById('basketDropdown').classList.remove('show');
    }
}