document.addEventListener('DOMContentLoaded', async () => {
    // 1. Fetch Backend Data
    let products = [];
    try {
        const response = await fetch('/api/products');
        if (response.ok) {
            products = await response.json();
            console.log("Successfully fetched products from backend:", products);
        } else {
            console.error("Backend returned an error.");
        }
    } catch (error) {
        console.error("Failed to connect to backend server. Make sure server.py is running.", error);
    }

    // 2. Render Products with Animations
    const productGrid = document.getElementById('product-grid');
    
    function renderProducts() {
        if (!productGrid) return;
        
        products.forEach((product, i) => {
            const card = document.createElement('div');
            card.className = 'product-card animate-scale';
            card.style.transitionDelay = `${i * 0.1}s`;
            card.innerHTML = `
                <div class="product-img">
                    <img src="${product.image}" alt="${product.title}" loading="lazy">
                </div>
                <div class="product-info">
                    <span class="product-category">${product.category}</span>
                    <h3 class="product-title">${product.title}</h3>
                    <div class="product-price-row">
                        <span class="product-price">$${product.price.toFixed(2)}</span>
                        <button class="add-to-cart" data-id="${product.id}" aria-label="Add to cart">
                            <ion-icon name="add-outline"></ion-icon>
                        </button>
                    </div>
                </div>
            `;
            productGrid.appendChild(card);
        });
        
        // Re-observe newly added elements
        observeElements();
    }

    if (products.length > 0) {
        renderProducts();
    } else {
        productGrid.innerHTML = `<p style="grid-column: 1/-1; text-align: center;">No products found from server.</p>`;
    }

    // 3. Cart Logic & Backend Integration
    const cartBadge = document.getElementById('cart-badge');

    productGrid.addEventListener('click', async (e) => {
        const btn = e.target.closest('.add-to-cart');
        if (btn) {
            // Spin animation
            btn.style.transform = 'rotate(360deg) scale(1.2)';
            setTimeout(() => btn.style.transform = '', 500);

            const productId = parseInt(btn.dataset.id);
            const product = products.find(p => p.id === productId);
            
            try {
                const res = await fetch('/api/cart', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: productId, title: product.title, price: product.price })
                });
                
                const data = await res.json();
                
                // Update badge using the reliable backend cart size state
                cartBadge.textContent = data.cart_size;
                
                // Pop animation
                cartBadge.style.transition = 'transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                cartBadge.style.transform = 'scale(1.8)';
                setTimeout(() => {
                    cartBadge.style.transform = 'scale(1)';
                }, 400);

                showToast(`Added ${product.title} to cart`);
            } catch (err) {
                showToast(`Server Error: Could not add item.`);
                console.error(err);
            }
        }
    });

    // 4. Toast Notifications
    const toastContainer = document.getElementById('toast-container');

    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerHTML = `
            <ion-icon name="checkmark-circle" style="font-size: 1.8rem; color: var(--accent-red)"></ion-icon>
            <span style="font-weight: 600;">${message}</span>
        `;
        
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('hiding');
            toast.addEventListener('animationend', () => {
                toast.remove();
            });
        }, 3000);
    }

    // 5. Navbar Scroll Effect
    const navbar = document.getElementById('navbar');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // 6. Intersection Observer for Scroll Animations
    function observeElements() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: "0px 0px -50px 0px"
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        document.querySelectorAll('.animate-up, .animate-scale, .cat-card').forEach((el, index) => {
            // Apply stagger delay to cat-cards
            if(el.classList.contains('cat-card')) {
                el.classList.add('animate-up');
                el.style.transitionDelay = `${index * 0.15}s`;
            }
            observer.observe(el);
        });
    }
    
    // Initial observe
    observeElements();
    
    // Trigger visible class immediately for above-fold items
    setTimeout(() => {
        document.querySelectorAll('.hero .animate-up').forEach(el => el.classList.add('visible'));
    }, 100);
});
