// Cart management functions using localStorage
function getCart() {
    return JSON.parse(localStorage.getItem('cart')) || [];
}

function saveCart(cartData) {
    localStorage.setItem('cart', JSON.stringify(cartData));
}

function addToCart(productId, quantity = 1) {
    fetch(`/api/cart/add`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: parseInt(quantity)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }
        
        const cart = getCart();
        const existingItemIndex = cart.findIndex(item => item.id === productId);
        if (existingItemIndex !== -1) {
            cart[existingItemIndex].quantity += parseInt(quantity);
        } else {
            cart.push({
                id: data.product.id,
                name: data.product.name,
                price: data.product.price,
                image_url: data.product.image_url,
                quantity: parseInt(quantity)
            });
        }
        
        saveCart(cart);
        updateCartDisplay();
        updateCartCount();
    });
}

function updateCartCount() {
    const cart = getCart();
    const cartCount = cart.reduce((total, item) => total + item.quantity, 0);
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        cartCountElement.textContent = cartCount;
    }
}

function updateCartDisplay() {
    const cart = getCart();
    const cartItems = document.getElementById('cart-items');
    const emptyCart = document.getElementById('empty-cart');
    
    if (!cartItems || !emptyCart) return;
    
    if (cart.length === 0) {
        cartItems.style.display = 'none';
        emptyCart.style.display = 'block';
        return;
    }
    
    cartItems.style.display = 'block';
    emptyCart.style.display = 'none';
    
    cartItems.innerHTML = cart.map(item => `
        <div class="card mb-3">
            <div class="row g-0">
                <div class="col-md-2">
                    <img src="${item.image_url}" class="img-fluid rounded-start" alt="${item.name}">
                </div>
                <div class="col-md-10">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <h5 class="card-title">${item.name}</h5>
                            <button class="btn btn-sm btn-danger" onclick="removeFromCart(${item.id})">
                                <i data-feather="trash-2"></i>
                            </button>
                        </div>
                        <p class="card-text">
                            <div class="d-flex align-items-center">
                                <div class="input-group w-25">
                                    <button class="btn btn-outline-secondary" onclick="updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                                    <input type="number" class="form-control text-center" value="${item.quantity}" min="1" onchange="updateQuantity(${item.id}, this.value)">
                                    <button class="btn btn-outline-secondary" onclick="updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                                </div>
                                <span class="ms-auto">$${(item.price * item.quantity).toFixed(2)}</span>
                            </div>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    updateCartSummary();
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
}

function updateCartSummary() {
    const cart = getCart();
    const subtotal = cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    const shipping = subtotal > 0 ? 10 : 0;
    const total = subtotal + shipping;
    
    const subtotalElement = document.getElementById('subtotal');
    const shippingElement = document.getElementById('shipping');
    const totalElement = document.getElementById('total');
    
    if (subtotalElement) subtotalElement.textContent = `$${subtotal.toFixed(2)}`;
    if (shippingElement) shippingElement.textContent = `$${shipping.toFixed(2)}`;
    if (totalElement) totalElement.textContent = `$${total.toFixed(2)}`;
}

function removeFromCart(productId) {
    const cart = getCart();
    const itemIndex = cart.findIndex(item => item.id === productId);
    if (itemIndex > -1) {
        cart.splice(itemIndex, 1);
        saveCart(cart);
        updateCartDisplay();
        updateCartCount();
    }
}

function updateQuantity(productId, newQuantity) {
    newQuantity = parseInt(newQuantity);
    if (newQuantity < 1) return;
    
    const cart = getCart();
    const itemIndex = cart.findIndex(item => item.id === productId);
    if (itemIndex > -1) {
        cart[itemIndex].quantity = newQuantity;
        saveCart(cart);
        updateCartDisplay();
        updateCartCount();
    }
}

function proceedToCheckout() {
    const cart = getCart();
    if (cart.length === 0) {
        alert('Your cart is empty!');
        return;
    }
    window.location.href = '/checkout';
}

// Initialize cart count on page load
document.addEventListener('DOMContentLoaded', function() {
    updateCartCount();
    updateCartDisplay();
});
