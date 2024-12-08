function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Update your fetch requests to include the CSRF token
const csrftoken = getCookie('csrftoken');

// Use it in your fetch headers like this:
// Add image loading handler
document.addEventListener('DOMContentLoaded', function() {
    const heroBackground = document.querySelector('.hero-background');
    
    if (heroBackground) {
        heroBackground.classList.add('loading');
        
        // Create a new image object to preload
        const img = new Image();
        img.src = heroBackground.style.backgroundImage.replace(/url\(['"]?(.*?)['"]?\)/i, '$1');
        
        img.onload = function() {
            heroBackground.classList.remove('loading');
        };
        
        img.onerror = function() {
            heroBackground.style.backgroundImage = `url('${defaultImageUrl}')`;
            heroBackground.classList.remove('loading');
        };
    }
}); 

// Add debouncing for search
let searchTimeout;
document.getElementById('menuSearch').addEventListener('input', function(e) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        const searchTerm = e.target.value.toLowerCase();
        const menuItems = document.querySelectorAll('.menu-item');
        
        menuItems.forEach(item => {
            const itemName = item.querySelector('h3').textContent.toLowerCase();
            const itemDescription = item.querySelector('.description').textContent.toLowerCase();
            const matches = itemName.includes(searchTerm) || itemDescription.includes(searchTerm);
            item.style.display = matches ? 'flex' : 'none';
        });
        
        // Show/hide empty state for categories
        document.querySelectorAll('.menu-section').forEach(section => {
            const visibleItems = section.querySelectorAll('.menu-item[style="display: flex"]');
            section.style.display = visibleItems.length ? 'block' : 'none';
        });
    }, 300);
});

// Enhance filter functionality
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const filter = this.dataset.filter;
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        const menuItems = document.querySelectorAll('.menu-item');
        menuItems.forEach(item => {
            switch(filter) {
                case 'veg':
                    item.style.display = item.querySelector('.veg-badge') ? 'flex' : 'none';
                    break;
                case 'non-veg':
                    item.style.display = !item.querySelector('.veg-badge') ? 'flex' : 'none';
                    break;
                case 'bestseller':
                    item.style.display = item.classList.contains('bestseller') ? 'flex' : 'none';
                    break;
                default:
                    item.style.display = 'flex';
            }
        });
    });
}); 

// Add favorite functionality
document.querySelectorAll('.favorite-btn').forEach(btn => {
    btn.addEventListener('click', async function(e) {
        e.preventDefault();
        const itemId = this.dataset.itemId;
        
        try {
            const response = await fetch('/api/favorites/toggle/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ item_id: itemId })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.classList.toggle('active');
                this.querySelector('i').classList.toggle('far');
                this.querySelector('i').classList.toggle('fas');
                
                // Show feedback toast
                showToast(data.is_favorite ? 'Added to favorites' : 'Removed from favorites');
            }
        } catch (error) {
            console.error('Error toggling favorite:', error);
            showToast('Error updating favorites', 'error');
        }
    });
});

// Cart class to manage cart operations
class Cart {
    constructor() {
        this.items = JSON.parse(localStorage.getItem('cart') || '[]');
        this.init();
    }

    init() {
        this.updateCartUI();
        // Add event listeners for add to cart buttons
        document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const button = e.currentTarget;
                const itemData = {
                    id: button.dataset.itemId,
                    name: button.dataset.itemName,
                    price: parseFloat(button.dataset.itemPrice),
                    image: button.dataset.itemImage,
                    quantity: 1
                };
                this.addItem(itemData);
                showToast('Item added to cart');
            });
        });

        // Add event delegation for quantity buttons
        const cartItemsContainer = document.querySelector('.cart-items');
        if (cartItemsContainer) {
            cartItemsContainer.addEventListener('click', (e) => {
                const button = e.target.closest('.quantity-btn');
                if (!button) return;

                const cartItem = button.closest('.cart-item');
                const itemId = cartItem.dataset.id;
                
                if (button.classList.contains('plus')) {
                    this.updateQuantity(itemId, 1);
                    showToast('Quantity increased');
                } else if (button.classList.contains('minus')) {
                    this.updateQuantity(itemId, -1);
                    showToast('Quantity decreased');
                }
            });
        }
    }

    updateQuantity(itemId, change) {
        const item = this.items.find(item => item.id === itemId);
        if (item) {
            item.quantity += change;
            if (item.quantity <= 0) {
                // Remove item if quantity is 0 or less
                this.items = this.items.filter(i => i.id !== itemId);
                showToast('Item removed from cart');
            }
            this.saveCart();
            this.updateCartUI();
        }
    }

    addItem(newItem) {
        const existingItem = this.items.find(item => item.id === newItem.id);
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.items.push(newItem);
        }
        this.saveCart();
        this.updateCartUI();
    }

    saveCart() {
        localStorage.setItem('cart', JSON.stringify(this.items));
    }

    updateCartUI() {
        const cartItems = document.querySelector('.cart-items');
        const subtotal = document.querySelector('.amount');
        const checkoutBtn = document.querySelector('.checkout-btn');
        const cartTotal = document.querySelector('.cart-total');

        if (!cartItems) return;

        cartItems.innerHTML = '';
        let total = 0;

        this.items.forEach(item => {
            total += item.price * item.quantity;
            cartItems.innerHTML += `
                <div class="cart-item" data-id="${item.id}">
                    <div class="cart-item-content">
                        <div class="cart-item-image">
                            <img src="${item.image}" alt="${item.name}">
                        </div>
                        <div class="cart-item-details">
                            <h4>${item.name}</h4>
                            <p class="item-price">₹${(item.price * item.quantity).toFixed(2)}</p>
                        </div>
                    </div>
                    <div class="cart-item-quantity">
                        <button class="quantity-btn minus"><i class="fas fa-minus"></i></button>
                        <span class="quantity">${item.quantity}</span>
                        <button class="quantity-btn plus"><i class="fas fa-plus"></i></button>
                    </div>
                </div>
            `;
        });

        if (subtotal) subtotal.textContent = `₹${total.toFixed(2)}`;
        if (cartTotal) cartTotal.textContent = `₹${total.toFixed(2)}`;
        if (checkoutBtn) checkoutBtn.disabled = this.items.length === 0;

        // Update cart visibility
        const cartContainer = document.querySelector('.cart-container');
        if (cartContainer) {
            cartContainer.classList.toggle('has-items', this.items.length > 0);
        }
    }
}

// Initialize cart when document loads
document.addEventListener('DOMContentLoaded', function() {
    window.cart = new Cart();
});

// Highlight active menu category while scrolling
const observerOptions = {
    root: null,
    rootMargin: '-20% 0px -79% 0px',
    threshold: 0
};

const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const id = entry.target.id;
            document.querySelectorAll('.menu-categories a').forEach(link => {
                link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
            });
        }
    });
}, observerOptions);

document.querySelectorAll('.menu-section').forEach(section => {
    observer.observe(section);
}); 

// Add this function to handle favorites
async function toggleFavorite(button, itemId) {
    try {
        const response = await fetch(`/user/toggle-favorite/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Toggle the active class and icon
            button.classList.toggle('active');
            const icon = button.querySelector('i');
            icon.className = data.is_favorite ? 'fas fa-heart' : 'far fa-heart';
            
            // Show feedback toast
            showToast(data.message);
        } else {
            showToast(data.message || 'Failed to update favorite status', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('An error occurred while updating favorite status', 'error');
    }
}

// Add this function for toast notifications
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 2000);
    }, 100);
} 