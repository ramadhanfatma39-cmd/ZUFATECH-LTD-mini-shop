alert("ZUFATECH is loading the updated script.js!");
/* =========================================
   ZUFATECH LTD
   FRONTEND + FLASK API + SHOPPING CART
========================================= */

let cart = [];
let total = 0;
let apiProducts = [];

const API_URL = "/api";

/* =========================================
   1. PRICE HELPERS
========================================= */

function parsePrice(value) {
    if (typeof value === "number") {
        return Number.isFinite(value) ? value : 0;
    }

    // Also handles values such as "KSh 130,000".
    const cleaned = String(value ?? "").replace(/[^\d.-]/g, "");
    const number = Number(cleaned);

    return Number.isFinite(number) ? number : 0;
}

function moneyKES(value) {
    return parsePrice(value).toLocaleString("en-KE", {
        maximumFractionDigits: 2
    });
}

function getProductPrices(product) {
    if (!product) return [];

    let prices = product.prices;

    // Support an API that returns prices as a JSON string.
    if (typeof prices === "string") {
        try {
            prices = JSON.parse(prices);
        } catch {
            prices = [prices];
        }
    }

    if (!Array.isArray(prices)) {
        if (product.price !== undefined && product.price !== null) {
            prices = [product.price];
        } else {
            return [];
        }
    }

    return prices
        .map(price => {
            if (typeof price === "object" && price !== null) {
                return parsePrice(price.price ?? price.amount);
            }

            return parsePrice(price);
        })
        .filter(price => price > 0);
}

/* =========================================
   2. FIND CART ELEMENTS
========================================= */

function findCartElement(...selectors) {
    for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element) return element;
    }

    return null;
}

/* =========================================
   3. REUSABLE SHOPPING DIALOG
========================================= */

function showShopDialog(title) {
    document.getElementById("shop-dialog-overlay")?.remove();

    const overlay = document.createElement("div");
    overlay.id = "shop-dialog-overlay";

    Object.assign(overlay.style, {
        position: "fixed",
        inset: "0",
        background: "rgba(0,0,0,0.65)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "16px",
        zIndex: "999999",
        overflowY: "auto"
    });

    const panel = document.createElement("div");

    Object.assign(panel.style, {
        background: "#ffffff",
        color: "#222222",
        width: "100%",
        maxWidth: "460px",
        maxHeight: "90vh",
        overflowY: "auto",
        padding: "24px",
        borderRadius: "12px",
        boxShadow: "0 8px 30px rgba(0,0,0,0.3)",
        fontFamily: "Arial, sans-serif"
    });

    const heading = document.createElement("h2");
    heading.textContent = title;
    heading.style.marginTop = "0";

    panel.appendChild(heading);
    overlay.appendChild(panel);
    document.body.appendChild(overlay);

    return { overlay, panel };
}

function addDialogField(form, labelText, name, type) {
    const wrapper = document.createElement("div");
    wrapper.style.marginBottom = "14px";

    const label = document.createElement("label");
    label.textContent = labelText;
    label.htmlFor = `shop-field-${name}`;
    label.style.display = "block";
    label.style.marginBottom = "6px";
    label.style.fontWeight = "bold";

    const input = document.createElement("input");
    input.id = `shop-field-${name}`;
    input.name = name;
    input.type = type;
    input.required = true;

    Object.assign(input.style, {
        width: "100%",
        boxSizing: "border-box",
        padding: "11px",
        border: "1px solid #bbbbbb",
        borderRadius: "6px",
        fontSize: "16px"
    });

    wrapper.append(label, input);
    form.appendChild(wrapper);

    return input;
}

function styleDialogButton(button, background) {
    Object.assign(button.style, {
        padding: "11px 16px",
        border: "none",
        borderRadius: "6px",
        background,
        color: "#ffffff",
        cursor: "pointer",
        fontSize: "15px",
        fontWeight: "bold",
        marginRight: "8px",
        marginTop: "8px"
    });
}

/* =========================================
   4. LOAD PRODUCTS FROM FLASK
========================================= */

async function loadApiProductsAndConnectButtons() {
    try {
        const response = await fetch(`${API_URL}/products`);

        if (!response.ok) {
            throw new Error(`Product request failed: HTTP ${response.status}`);
        }

        const data = await response.json();
        apiProducts = Array.isArray(data)
            ? data
            : (data.products || []);

        const cards = document.querySelectorAll("#products .product");

        if (cards.length === 0) {
            console.warn(
                'No product cards found. Check that your HTML uses #products .product.'
            );
        }

        cards.forEach((card, index) => {
            // This preserves the existing card order in  website.
            const product = apiProducts[index];
            const button = card.querySelector("button");

            if (!product || !button) return;

            card.dataset.productId = String(product.id);
            // Load the product image through Flask.
const productImage = card.querySelector("img");

if (productImage && product.image) {
    productImage.src = "/images/" + encodeURIComponent(product.image);
    productImage.alt = product.name || "Product image";
    productImage.onerror = function () {
        console.warn("Image could not be loaded:", product.image);
    };
}

            // Remove an old inline click handler so products aren't added twice.
            button.removeAttribute("onclick");

            if (button.dataset.cartConnected === "true") return;

            button.dataset.cartConnected = "true";
            button.textContent = "Add to Cart";

            button.addEventListener("click", function () {
                addApiProductToCart(product);
            });
        });

        console.log(`Backend connected. Products received: ${apiProducts.length}`);
        console.log(`Product cards found: ${cards.length}`);

        setupProductCategoryFilters();

    } catch (error) {
        console.error("Product loading error:", error);
        alert("Could not load products. Check that Flask is running.");
    }
}

/* =========================================
   5. ADD PRODUCTS TO CART
========================================= */

function addApiProductToCart(product) {
    const prices = getProductPrices(product);

    if (prices.length === 0) {
        alert("This product has no valid price available.");
        return;
    }

    if (prices.length === 1) {
        saveProductToCart(product, prices[0]);
        return;
    }

    const { overlay, panel } = showShopDialog("Choose a Product Price");

    const description = document.createElement("p");
    description.textContent = `Choose a price for ${product.name}:`;
    panel.appendChild(description);

    const select = document.createElement("select");

    Object.assign(select.style, {
        width: "100%",
        padding: "12px",
        marginBottom: "18px",
        borderRadius: "6px",
        fontSize: "16px"
    });

    prices.forEach((price, index) => {
        const option = document.createElement("option");
        option.value = String(price);
        option.textContent = `Option ${index + 1} — KSh ${moneyKES(price)}`;
        select.appendChild(option);
    });

    panel.appendChild(select);

    const addButton = document.createElement("button");
    addButton.type = "button";
    addButton.textContent = "Add to Cart";
    styleDialogButton(addButton, "#087f5b");

    addButton.addEventListener("click", function () {
        const selectedPrice = parsePrice(select.value);
        overlay.remove();
        saveProductToCart(product, selectedPrice);
    });

    const cancelButton = document.createElement("button");
    cancelButton.type = "button";
    cancelButton.textContent = "Cancel";
    styleDialogButton(cancelButton, "#555555");
    cancelButton.addEventListener("click", () => overlay.remove());

    panel.append(addButton, cancelButton);
}

function saveProductToCart(product, price) {
    price = parsePrice(price);

    if (!product || product.id === undefined || price <= 0) {
        alert("Could not add this product. Check its ID and price.");
        return;
    }

    const existingItem = cart.find(item =>
        String(item.product_id) === String(product.id) &&
        item.price === price
    );

    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            product_id: product.id,
            name: product.name || product.title || "Product",
            price: price,
            quantity: 1
        });
    }

    updateCart();

    console.log("Product added:", product.name, "Price:", price);
}


/* =========================================
   6. UPDATE CART AND TOTAL
========================================= */

function updateCart() {
    const cartItems = findCartElement(
        "#cart-items",
        "#cartItems",
        "[data-cart-items]"
    );

    const cartCount = findCartElement(
        "#cart-count",
        "#cartCount",
        "[data-cart-count]"
    );

    const cartTotal = findCartElement(
        "#cart-total",
        "#cartTotal",
        "[data-cart-total]"
    );

    let totalItems = 0;
    let totalPrice = 0;

    // Calculate the total number of units and the total cost.
    cart.forEach(item => {
        const quantity = Math.max(
            1,
            parseInt(item.quantity, 10) || 1
        );

        const price = parsePrice(item.price);

        totalItems += quantity;
        totalPrice += price * quantity;
    });

    total = totalPrice;

    if (cartCount) {
        cartCount.textContent = String(totalItems);
    }

    if (cartTotal) {
        cartTotal.textContent = moneyKES(totalPrice);
    }

    if (!cartItems) {
        console.error("Cart items element not found.");
        return;
    }

    cartItems.replaceChildren();

    if (cart.length === 0) {
        const emptyMessage = document.createElement("li");
        emptyMessage.textContent = "Your cart is empty.";
        cartItems.appendChild(emptyMessage);
        return;
    }

    cart.forEach((item, index) => {
        const quantity = Math.max(
            1,
            parseInt(item.quantity, 10) || 1
        );

        const price = parsePrice(item.price);
        const lineTotal = price * quantity;

        const li = document.createElement("li");
        li.style.marginBottom = "15px";

        // Product name and price.
        const itemText = document.createElement("span");
        itemText.textContent =
            `${item.name} — KSh ${moneyKES(price)} each`;

        li.appendChild(itemText);

        // Quantity controls.
        const quantityRow = document.createElement("div");
        quantityRow.style.display = "flex";
        quantityRow.style.alignItems = "center";
        quantityRow.style.gap = "10px";
        quantityRow.style.marginTop = "6px";

        const decreaseButton = document.createElement("button");
        decreaseButton.type = "button";
        decreaseButton.textContent = "−";
        decreaseButton.setAttribute(
            "aria-label",
            `Decrease quantity of ${item.name}`
        );
        decreaseButton.disabled = quantity <= 1;

        decreaseButton.addEventListener("click", function () {
            if (item.quantity > 1) {
                item.quantity -= 1;
                updateCart();
            }
        });

        const quantityText = document.createElement("span");
        quantityText.textContent = `Qty: ${quantity}`;

        const increaseButton = document.createElement("button");
        increaseButton.type = "button";
        increaseButton.textContent = "+";
        increaseButton.setAttribute(
            "aria-label",
            `Increase quantity of ${item.name}`
        );

        increaseButton.addEventListener("click", function () {
            if (item.quantity < 100) {
                item.quantity += 1;
                updateCart();
            } else {
                alert("Maximum quantity is 100 per item.");
            }
        });

        quantityRow.append(
            decreaseButton,
            quantityText,
            increaseButton
        );

        // Subtotal for this product.
        const subtotal = document.createElement("p");
        subtotal.textContent =
            `Subtotal: KSh ${moneyKES(lineTotal)}`;
        subtotal.style.marginTop = "5px";

        // Remove this product completely.
        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.textContent = "Remove";
        removeButton.style.marginTop = "5px";

        removeButton.addEventListener("click", function () {
            cart.splice(index, 1);
            updateCart();
        });

        li.append(
            quantityRow,
            subtotal,
            removeButton
        );

        cartItems.appendChild(li);
    });

    console.log(
        "Cart units:", totalItems,
        "| Cart total: KSh", moneyKES(totalPrice)
    );
}


/* =========================================
   7. CLEAR CART
========================================= */

function clearCart() {
    cart = [];
    total = 0;
    updateCart();
}

/* =========================================
   8. CHECKOUT AND SAVE ORDER IN SQLITE
========================================= */

async function readServerResponse(response) {
    const text = await response.text();

    try {
        return text ? JSON.parse(text) : {};
    } catch {
        console.error("Server returned a non-JSON response:", {
            status: response.status,
            body: text.slice(0, 1000)
        });

        throw new Error(
            `The server returned an invalid response (HTTP ${response.status}). ` +
            "Check the Flask terminal for the error."
        );
    }
}

function checkout() {
    if (cart.length === 0) {
        alert("Your cart is empty. Please add a product first.");
        return;
    }

    // Prevent checkout with invalid prices or missing product IDs.
    const invalidItem = cart.some(item =>
        item.product_id === undefined ||
        parsePrice(item.price) <= 0 ||
        Number(item.quantity) < 1
    );

    if (invalidItem) {
        alert("One or more cart items have invalid details. Remove them and try again.");
        return;
    }

    const { overlay, panel } = showShopDialog("Complete Your Order");

    const summary = document.createElement("p");
    summary.textContent =
        `${cart.reduce((sum, item) => sum + Number(item.quantity), 0)} item(s). ` +
        `Total: KSh ${moneyKES(total)}`;

    panel.appendChild(summary);

    const form = document.createElement("form");

    const nameInput = addDialogField(form, "Full Name", "customer-name", "text");
    nameInput.autocomplete = "name";
    nameInput.minLength = 2;

    const emailInput = addDialogField(
        form, "Email Address", "customer-email", "email"
    );
    emailInput.autocomplete = "email";

    const phoneInput = addDialogField(
        form, "Phone Number", "customer-phone", "tel"
    );
    phoneInput.autocomplete = "tel";

    const status = document.createElement("p");
    status.setAttribute("role", "status");
    form.appendChild(status);

    const submitButton = document.createElement("button");
    submitButton.type = "submit";
    submitButton.textContent = "Place Order";
    styleDialogButton(submitButton, "#087f5b");

    const cancelButton = document.createElement("button");
    cancelButton.type = "button";
    cancelButton.textContent = "Cancel";
    styleDialogButton(cancelButton, "#555555");
    cancelButton.addEventListener("click", () => overlay.remove());

    form.append(submitButton, cancelButton);
    panel.appendChild(form);

    
form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const customerName = nameInput.value.trim();
    const email = emailInput.value.trim();
    const phone = phoneInput.value.trim();

    if (
        customerName.length < 2 ||
        !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) ||
        !phone
    ) {
        status.textContent = "Enter a valid name, email address, and phone number.";
        status.style.color = "#d62828";
        return;
    }

    const orderItems = cart.map(item => ({
        product_id: item.product_id,
        price: parsePrice(item.price),
        quantity: Number(item.quantity) || 1
    }));

    const orderTotal = orderItems.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
    );

    submitButton.disabled = true;
    submitButton.textContent = "Opening M-Pesa Demo...";

    alert("M-Pesa checkout code reached!");

    showMpesaPayment(
        orderTotal,
        phone,
        async function () {
            status.textContent = "Saving order to the database...";

            try {
                const response = await fetch(`${API_URL}/orders`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        customer_name: customerName,
                        email: email,
                        phone: phone,
                        items: orderItems
                    })
                });

                const result = await readServerResponse(response);

                if (!response.ok) {
                    throw new Error(
                        result.error || `Could not save order (HTTP ${response.status}).`
                    );
                }

                overlay.remove();
                clearCart();

                alert(
                    "Demo payment successful!\n\n" +
                    `Order number: ${result.order_id ?? "Confirmed"}\n` +
                    `Total: KSh ${moneyKES(result.total ?? orderTotal)}\n\n` +
                    "No real M-Pesa payment was made."
                );
            } catch (error) {
                console.error("Checkout error:", error);
                status.textContent = "Could not save the order: " + error.message;
                status.style.color = "#d62828";
                submitButton.disabled = false;
                submitButton.textContent = "Try Again";
            }
        },
        function () {
            submitButton.disabled = false;
            submitButton.textContent = "Place Order";
            status.textContent = "Payment cancelled. Your cart is unchanged.";
            status.style.color = "#d62828";
        }
    );
});

}

/* =========================================
   9. DARK / LIGHT MODE
========================================= */

function connectThemeButton() {
    const themeButton = document.getElementById("theme-toggle");

    if (!themeButton || themeButton.dataset.themeConnected === "true") {
        return;
    }

    themeButton.dataset.themeConnected = "true";

    themeButton.addEventListener("click", function () {
        document.body.classList.toggle("dark-mode");

        const isDark = document.body.classList.contains("dark-mode");

        themeButton.textContent = isDark
            ? "☀️ Light Mode"
            : "🌙 Dark Mode";

        themeButton.setAttribute(
            "aria-label",
            isDark ? "Switch to light mode" : "Switch to dark mode"
        );
    });
}

/* =========================================
   10. CONTACT FORM
========================================= */

function connectContactFormToApi() {
    const form = document.getElementById("contact-form");

    if (!form || form.dataset.apiConnected === "true") return;

    form.dataset.apiConnected = "true";

    

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const customerName = nameInput.value.trim();
    const email = emailInput.value.trim();
    const phone = phoneInput.value.trim();

    if (
        customerName.length < 2 ||
        !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) ||
        !phone
    ) {
        status.textContent =
            "Enter a valid name, email address, and phone number.";
        status.style.color = "#d62828";
        return;
    }

    const orderItems = cart.map(item => ({
        product_id: item.product_id,
        price: parsePrice(item.price),
        quantity: Number(item.quantity) || 1
    }));

    const orderTotal = orderItems.reduce(
        (sum, item) => sum + item.price * item.quantity,
        0
    );

    submitButton.disabled = true;
    submitButton.textContent = "Opening M-Pesa Demo...";

alert("M-Pesa checkout code reached!");

    showMpesaPayment(
        orderTotal,
        phone,
        async function () {
            status.textContent = "Saving order to the database...";
            status.style.color = "#333333";

            try {
                const response = await fetch(`${API_URL}/orders`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        customer_name: customerName,
                        email: email,
                        phone: phone,
                        items: orderItems
                    })
                });

                const result = await readServerResponse(response);

                if (!response.ok) {
                    throw new Error(
                        result.error ||
                        `Could not save the order (HTTP ${response.status}).`
                    );
                }

                overlay.remove();
                clearCart();

                
alert(
    "ZUFATECH LTD - ORDER CONFIRMED\n\n" +
    "Order number: #" + result.order_id + "\n" +
    "Total: KSh " + moneyKES(result.total) + "\n" +
    "Currency: " + (result.currency || "KES") + "\n\n" +
    "Your order has been saved successfully!\n" +
    "M-Pesa was simulated ; no real payment was made."
);

            } catch (error) {
                console.error("Checkout error:", error);

                status.textContent =
                    "The demo payment was simulated, but saving the order failed: " +
                    error.message;
                status.style.color = "#d62828";

                submitButton.disabled = false;
                submitButton.textContent = "Try Again";
            }
        },
        function () {
            submitButton.disabled = false;
            submitButton.textContent = "Place Order";

            status.textContent =
                "Payment cancelled. Your cart is unchanged.";
            status.style.color = "#d62828";
        }
    );
});

}

/* =========================================
   11. START WHEN THE PAGE LOADS
========================================= */

document.addEventListener("DOMContentLoaded", function () {
    connectThemeButton();
    connectContactFormToApi();
    updateCart();
    loadApiProductsAndConnectButtons();
});

/* =========================================
    SIMULATED M-PESA PAYMENT
========================================= */

function showMpesaPayment(amount, phone, onSuccess, onCancel) {
    // Remove any previous payment dialog.
    document.getElementById("mpesa-demo-overlay")?.remove();

    const overlay = document.createElement("div");
    overlay.id = "mpesa-demo-overlay";

    Object.assign(overlay.style, {
        position: "fixed",
        inset: "0",
        zIndex: "1000000",
        background: "rgba(0,0,0,0.7)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "16px"
    });

    const panel = document.createElement("div");
    Object.assign(panel.style, {
        background: "#ffffff",
        color: "#222222",
        width: "100%",
        maxWidth: "420px",
        padding: "25px",
        borderRadius: "14px",
        textAlign: "center",
        fontFamily: "Arial, sans-serif",
        boxSizing: "border-box"
    });

    const heading = document.createElement("h2");
    heading.textContent = "M-Pesa Payment";

    const notice = document.createElement("p");
    notice.textContent =
        "DEMO ONLY — no real M-Pesa payment will be made.";
    notice.style.color = "#b42318";
    notice.style.fontWeight = "bold";

    const details = document.createElement("p");
    details.textContent =
        "Amount: KSh " +
        Number(amount).toLocaleString("en-KE") +
        "\nPhone: " + phone;
    details.style.whiteSpace = "pre-line";
    details.style.fontSize = "17px";

    const status = document.createElement("p");
    status.setAttribute("role", "status");
    status.textContent =
        "In a real integration, you would receive an STK Push prompt.";

    const successButton = document.createElement("button");
    successButton.type = "button";
    successButton.textContent = "Simulate Successful Payment";

    Object.assign(successButton.style, {
        background: "#087f5b",
        color: "#ffffff",
        border: "none",
        padding: "12px",
        width: "100%",
        borderRadius: "7px",
        cursor: "pointer",
        marginTop: "10px",
        fontWeight: "bold"
    });

    const cancelButton = document.createElement("button");
    cancelButton.type = "button";
    cancelButton.textContent = "Cancel Payment";

    Object.assign(cancelButton.style, {
        background: "#555555",
        color: "#ffffff",
        border: "none",
        padding: "12px",
        width: "100%",
        borderRadius: "7px",
        cursor: "pointer",
        marginTop: "10px"
    });

    successButton.addEventListener("click", function () {
        successButton.disabled = true;
        status.textContent =
            "Demo payment successful. This is not a real transaction.";
        status.style.color = "#087f5b";

        // Continue to the checkout success callback.
        overlay.remove();
        if (typeof onSuccess === "function") {
            onSuccess();
        }
    });

    cancelButton.addEventListener("click", function () {
        overlay.remove();
        if (typeof onCancel === "function") {
            onCancel();
        }
    });

    panel.append(
        heading,
        notice,
        details,
        status,
        successButton,
        cancelButton
    );

    overlay.appendChild(panel);
    document.body.appendChild(overlay);
}


/*  product search */
function setupProductSearch() {
    const searchInput = document.getElementById("product-search");
    const searchButton = document.getElementById("search-button");
    const searchMessage = document.getElementById("search-message");

    if (!searchInput || !searchButton) {
        console.warn("Search bar elements were not found.");
        return;
    }

    function searchProducts() {
        const query = searchInput.value.trim().toLowerCase();
        const products = document.querySelectorAll("#products .product");
        let visibleCount = 0;

        products.forEach(product => {
            const productText = product.textContent.toLowerCase();
            const matches = productText.includes(query);

            product.style.display = matches ? "" : "none";

            if (matches) visibleCount++;
        });

        if (searchMessage) {
            searchMessage.textContent = query
                ? `${visibleCount} product(s) found.`
                : "";
        }
    }

    searchButton.addEventListener("click", searchProducts);

    searchInput.addEventListener("input", searchProducts);

    searchInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            searchProducts();
        }
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupProductSearch);
} else {
    setupProductSearch();
}

/* ==========================
   ZUFATECH SIDE MENU
========================== */

document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.getElementById("menu-toggle");
    const sideMenu = document.getElementById("side-menu");
    const menuClose = document.getElementById("menu-close");
    const menuOverlay = document.getElementById("menu-overlay");

    if (!menuToggle || !sideMenu || !menuClose || !menuOverlay) {
        console.error("ZUFATECH menu elements were not found.");
        return;
    }

    function openMenu() {
        sideMenu.classList.add("open");
        menuOverlay.classList.add("open");
        document.body.classList.add("menu-open");
        menuToggle.setAttribute("aria-expanded", "true");
    }

    function closeMenu() {
        sideMenu.classList.remove("open");
        menuOverlay.classList.remove("open");
        document.body.classList.remove("menu-open");
        menuToggle.setAttribute("aria-expanded", "false");
    }

    menuToggle.addEventListener("click", openMenu);
    menuClose.addEventListener("click", closeMenu);
    menuOverlay.addEventListener("click", closeMenu);

    document.querySelectorAll("#side-menu a").forEach(function (link) {
    link.addEventListener("click", function (event) {
        if (link.getAttribute("href") !== "#why-choose-us") {
            closeMenu();
        }
    });
});

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeMenu();
        }
    });
});


// ======================================
//  PRODUCT CATEGORY FILTER
// ======================================


function identifyProductCategory(product) {
    const name = (product.name || "").toLowerCase();
    const description = (product.description || "").toLowerCase();
    const details = name + " " + description;

    // Tablets

        if (/ipad|tablet|galaxy tab|lenovo tab|modio/.test(name)) {
    return "tablets";
}
    

    // Headphones
    if (/headphone|headset|earbud|earphone|airpods|gaming headset/.test(name)) {
    return "headphones";
}

    // Chargers and cables
    if (/charger|charging cable|usb cable|type.?c cable|lightning cable|power adapter/.test(details)) {
        return "chargers";
    }

    // Phones
    if (/iphone|samsung|galaxy|huawei|honor|nokia|tecno|camon|spark|pova|phantom|infinix|itel|redmi|xiaomi|oppo|vivo|realme|oneplus|smartphone|mobile phone/.test(details)) {
        return "phones";
    }

    return "accessories";
}


function setupProductCategoryFilters() {
    const cards = document.querySelectorAll("#products .product");

    cards.forEach(function (card, index) {
        const product = apiProducts[index];

        if (product) {
            card.dataset.category = identifyProductCategory(product);
        }
    });

    document.querySelectorAll("[data-category-filter]").forEach(function (link) {
        link.addEventListener("click", function (event) {
            event.preventDefault();

            const selectedCategory = link.dataset.categoryFilter;
            const heading = document.querySelector("#products h2");

            cards.forEach(function (card) {
                const matches =
                    selectedCategory === "all" ||
                    card.dataset.category === selectedCategory;

                card.style.display = matches ? "" : "none";
            });

            if (heading) {
                heading.textContent =
                    selectedCategory === "all"
                        ? "Our Products"
                        : link.textContent.trim();
            }

            document.getElementById("products").scrollIntoView({
                behavior: "smooth"
            });

            document.getElementById("side-menu")?.classList.remove("open");
            document.getElementById("menu-overlay")?.classList.remove("open");
            document.body.classList.remove("menu-open");
        });
    });
}

// Show Why Choose Us only when clicked
document.addEventListener("DOMContentLoaded", function () {
    const whyLink = document.querySelector(
        '.side-menu-links a[href="#why-choose-us"]'
    );
    const whySection = document.getElementById("why-choose-us");

    if (!whyLink || !whySection) return;

    whyLink.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopImmediatePropagation();

        whySection.classList.add("show-section");

        document.getElementById("side-menu")?.classList.remove("open");
        document.getElementById("menu-overlay")?.classList.remove("open");
        document.body.classList.remove("menu-open");

        window.scrollTo({
            top: whySection.getBoundingClientRect().top + window.scrollY,
            behavior: "smooth"
        });
    });
});

// Close the Why Choose Us section
document.addEventListener("DOMContentLoaded", function () {
    const closeButton = document.getElementById("close-why-us");
    const whySection = document.getElementById("why-choose-us");

    if (closeButton && whySection) {
        closeButton.addEventListener("click", function () {
            whySection.classList.remove("show-section");
        });
    }
});

/* ==========================
   WHY CHOOSE US SIDEBAR TOGGLE
========================== */

document.addEventListener("DOMContentLoaded", function () {

    const whyToggle = document.getElementById("why-menu-toggle");
    const whySection = document.getElementById("why-choose-us");
    const closeWhyButton = document.getElementById("close-why-us");

    if (!whyToggle || !whySection || !closeWhyButton) {
        console.error("Why Choose Us elements could not be found.");
        return;
    }

    // Open or close the description
    whyToggle.addEventListener("click", function (event) {
        event.preventDefault();

        whySection.classList.toggle("show-section");
    });

    // Close the description
    closeWhyButton.addEventListener("click", function () {
        whySection.classList.remove("show-section");
    });

});
