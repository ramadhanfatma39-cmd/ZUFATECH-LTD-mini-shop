
const loginPanel = document.getElementById("login-panel");
const dashboard = document.getElementById("dashboard");
const loginForm = document.getElementById("login-form");
const productForm = document.getElementById("product-form");
const productsList = document.getElementById("products-list");
const message = document.getElementById("message");

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        credentials: "same-origin",
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        }
    });

    const result = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(result.error || `Request failed (${response.status})`);
    }

    return result;
}

function showMessage(text, isError = false) {
    message.textContent = text;
    message.style.color = isError ? "#b42318" : "#137333";
}

function resetProductForm() {
    productForm.reset();
    document.getElementById("product-id").value = "";
    document.getElementById("product-active").checked = true;
    document.getElementById("form-title").textContent = "Add a New Product";
    document.getElementById("save-btn").textContent = "Add Product";
    document.getElementById("cancel-btn").classList.add("hidden");
}

async function loadProducts() {
    productsList.textContent = "Loading products...";

    try {
        const result = await apiRequest("/api/admin/products");
        productsList.replaceChildren();

        if (!result.products || result.products.length === 0) {
            productsList.textContent = "No products found.";
            return;
        }

        result.products.forEach(product => {
            const card = document.createElement("div");
            card.className = "product";

            const title = document.createElement("h4");
            title.textContent = product.name;

            const description = document.createElement("p");
            description.textContent = product.description || "No description";

            const prices = document.createElement("p");
            prices.textContent = "Prices: " +
                (product.prices || []).map(price =>
                    "KSh " + Number(price).toLocaleString("en-KE")
                ).join(" / ");

            const status = document.createElement("p");
            status.textContent = product.active ? "Active" : "Inactive";

            const editButton = document.createElement("button");
            editButton.type = "button";
            editButton.textContent = "Edit";
            editButton.addEventListener("click", () => editProduct(product));

            const toggleButton = document.createElement("button");
            toggleButton.type = "button";
            toggleButton.className = "secondary";
            toggleButton.textContent = product.active ? "Deactivate" : "Activate";
            toggleButton.addEventListener("click", () => toggleProduct(product));

            card.append(title, description, prices, status, editButton, toggleButton);
            productsList.appendChild(card);
        });
    } catch (error) {
        productsList.textContent = error.message;
        if (error.message.toLowerCase().includes("log in")) {
            dashboard.classList.add("hidden");
            loginPanel.classList.remove("hidden");
        }
    }
}

function editProduct(product) {
    document.getElementById("product-id").value = product.id;
    document.getElementById("product-name").value = product.name || "";
    document.getElementById("product-description").value =
        product.description || "";
    document.getElementById("product-image").value = product.image || "";
    document.getElementById("product-prices").value =
        (product.prices || []).join(", ");
    document.getElementById("product-active").checked = Boolean(product.active);

    document.getElementById("form-title").textContent = "Edit Product";
    document.getElementById("save-btn").textContent = "Save Changes";
    document.getElementById("cancel-btn").classList.remove("hidden");

    productForm.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function toggleProduct(product) {
    const updatedProduct = {
        name: product.name,
        description: product.description || "",
        image: product.image || "",
        prices: product.prices,
        active: !product.active
    };

    try {
        await apiRequest(`/api/admin/products/${product.id}`, {
            method: "PUT",
            body: JSON.stringify(updatedProduct)
        });

        showMessage("Product status updated.");
        await loadProducts();
    } catch (error) {
        showMessage(error.message, true);
    }
}

loginForm.addEventListener("submit", async event => {
    event.preventDefault();
    showMessage("Checking login...");

    try {
        await apiRequest("/api/admin/login", {
            method: "POST",
            body: JSON.stringify({
                username: document.getElementById("username").value.trim(),
                password: document.getElementById("password").value
            })
        });

        loginPanel.classList.add("hidden");
        dashboard.classList.remove("hidden");
        document.getElementById("password").value = "";

        showMessage("Login successful.");
        await loadProducts();
    } catch (error) {
        showMessage(error.message, true);
    }
});

if (productForm) {
    productForm.addEventListener("submit", async event => {
        event.preventDefault();
        
    const rawPrices = document.getElementById("product-prices").value;
    const prices = rawPrices.split(",").map(value => Number(value.trim()));

    if (!prices.length || prices.some(price => !Number.isFinite(price) || price <= 0)) {
        showMessage("Enter valid prices greater than zero, separated by commas.", true);
        return;
    }

    const product = {
        name: document.getElementById("product-name").value.trim(),
        description: document.getElementById("product-description").value.trim(),
        image: document.getElementById("product-image").value.trim(),
        prices,
        active: document.getElementById("product-active").checked
    };

    const productId = document.getElementById("product-id").value;
    const url = productId
        ? `/api/admin/products/${productId}`
        : "/api/admin/products";
    const method = productId ? "PUT" : "POST";

    try {
        const result = await apiRequest(url, {
            method,
            body: JSON.stringify(product)
        });

        showMessage(result.message || "Product saved successfully.");
        resetProductForm();
        await loadProducts();
       } catch (error) {
        showMessage(error.message, true);
    }
    });
}

document.getElementById("refresh-btn").addEventListener("click", loadProducts);
document.getElementById("cancel-btn").addEventListener("click", resetProductForm);

document.getElementById("logout-btn").addEventListener("click", async () => {
    try {
        await apiRequest("/api/admin/logout", { method: "POST" });
        dashboard.classList.add("hidden");
        loginPanel.classList.remove("hidden");
        resetProductForm();
        showMessage("You have logged out.");
    } catch (error) {
        showMessage(error.message, true);
    }
});

dashboard.classList.add("hidden");


document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("password");
    const togglePassword = document.getElementById("toggle-password");

    if (!passwordInput || !togglePassword) {
        console.error("Password field or eye button not found.");
        return;
    }

    togglePassword.addEventListener("click", function (event) {
        event.preventDefault();

        console.log("Before:", passwordInput.type);

        console.log("EYE BUTTON CLICKED");

        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            togglePassword.textContent = "🙈";
        } else {
            passwordInput.type = "password";
            togglePassword.textContent = "👁";
        }
    });
});