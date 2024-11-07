document.addEventListener('DOMContentLoaded', function() {
    displayOrderSummary();
    const paymentButton = document.getElementById('payment-button');
    if (paymentButton) {
        paymentButton.addEventListener('click', handlePayment);
    }
});

function displayOrderSummary() {
    const orderItems = document.getElementById('order-items');
    const cartItems = JSON.parse(localStorage.getItem('cart')) || [];
    
    if (!cartItems.length) {
        orderItems.innerHTML = '<p>Your cart is empty</p>';
        return;
    }
    
    orderItems.innerHTML = cartItems.map(item => `
        <div class="d-flex justify-content-between mb-2">
            <span>${item.name} x ${item.quantity}</span>
            <span>$${(item.price * item.quantity).toFixed(2)}</span>
        </div>
    `).join('');
    
    updateTotals();
}

function updateTotals() {
    const cartItems = JSON.parse(localStorage.getItem('cart')) || [];
    const subtotal = cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);
    const shipping = subtotal > 0 ? 10 : 0;
    const total = subtotal + shipping;
    
    document.getElementById('checkout-subtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('checkout-shipping').textContent = `$${shipping.toFixed(2)}`;
    document.getElementById('checkout-total').textContent = `$${total.toFixed(2)}`;
}

async function handlePayment(e) {
    e.preventDefault();
    
    const cartItems = JSON.parse(localStorage.getItem('cart')) || [];
    if (!cartItems.length) {
        alert('Your cart is empty');
        return;
    }
    
    const form = document.getElementById('shipping-form');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const paymentButton = document.getElementById('payment-button');
    paymentButton.disabled = true;
    paymentButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
    
    try {
        const response = await fetch('/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                cart_items: cartItems,
                shipping_info: {
                    firstName: document.getElementById('firstName').value,
                    lastName: document.getElementById('lastName').value,
                    address: document.getElementById('address').value,
                    city: document.getElementById('city').value,
                    state: document.getElementById('state').value,
                    zip: document.getElementById('zip').value
                }
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Payment processing failed');
        }
        
        if (data.redirect) {
            // Clear cart after successful order
            localStorage.removeItem('cart');
            window.location.href = data.redirect;
        }
    } catch (error) {
        console.error('Error:', error);
        alert(error.message || 'An error occurred during checkout. Please try again.');
    } finally {
        paymentButton.disabled = false;
        paymentButton.innerHTML = 'Proceed to Payment';
    }
}
