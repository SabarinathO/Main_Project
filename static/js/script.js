// Script for navigation bar
const bar = document.getElementById('bar');
const nav = document.getElementById('navbar');
const close = document.getElementById('close');

if (bar) {
    bar.addEventListener('click', () => {
        nav.classList.add('active');
    });
}

if (close) {
    close.addEventListener('click', () => {
        nav.classList.remove('active');
    });
}

// Function to get CSRF Token
function getCSRFToken() {
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value;
    console.log("CSRF Token:", csrfToken); // Debugging
    return csrfToken || "";
}

// Function to update order status
function updateOrderStatus(orderId, status, orderCard) {
    fetch(`/update_order_status/${orderId}/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json().then(data => ({ status: response.status, body: data })))
    .then(({ status, body }) => {
        if (status === 200 && body.success) {
            orderCard.remove(); // Remove from the Pending section
            
            const deliveredOrdersSection = document.getElementById("delivered-orders");

            // Prevent duplicate entries
            if (document.querySelector(`.order-card[data-order-id="${orderId}"]`)) {
                console.warn(`Order ${orderId} already exists in delivered section.`);
                return;
            }

            // Create the delivered order card
            const newDeliveredCard = document.createElement("div");
            newDeliveredCard.classList.add("order-card", "delivered");
            newDeliveredCard.setAttribute("data-order-id", orderId);

            let deliveredDateText = "Unknown date";
            if (body.delivered_date) {
                const deliveredDate = new Date(body.delivered_date);
                if (!isNaN(deliveredDate)) {
                    deliveredDateText = deliveredDate.toLocaleDateString("en-GB", {
                        day: "2-digit",
                        month: "short",
                        year: "numeric"
                    });
                }
            }

            newDeliveredCard.innerHTML = `<h4>Order ID: ${orderId}</h4>`;

            // Ensure correct image rendering
            if (body.items && body.items.length > 0) {
                body.items.forEach(item => {
                    newDeliveredCard.innerHTML += `
                        <div class="order-item">
                            <img src="${item.product_image}" alt="${item.product_name}" class="order-image" style="width: 100px; height: 100px; object-fit: cover;">
                            <p><strong>Product:</strong> ${item.product_name}</p>
                            <p><strong>Quantity:</strong> ${item.quantity}</p>
                        </div>
                    `;
                });
            } else {
                newDeliveredCard.innerHTML += "<p>No items found.</p>";
            }

            newDeliveredCard.innerHTML += `
                <div class="order-status">
                    <span class="status-delivered">● Delivered on ${deliveredDateText}</span>
                    <p>Your items have been delivered.</p>
                </div>
            `;

            deliveredOrdersSection.appendChild(newDeliveredCard);
        } else {
            console.error("Failed to update order:", body.error);
            alert("Failed to update the order: " + (body.error || "Unknown error"));
        }
    })
    .catch(error => {
        console.error("Error updating order:", error);
        alert("Something went wrong. Please try again.");
    });
}
// Function for confirming item delivery
function confirmDelivery(radio) {
    const orderId = radio.name.replace("order", ""); // Extract order ID
    const orderCard = radio.closest(".order-card");

    // Show confirmation popup before proceeding
    const isConfirmed = window.confirm("Are you sure, you will receive this item?");
    
    if (isConfirmed) {
        updateOrderStatus(orderId, "delivered", orderCard);
    } else {
        radio.checked = false; // Uncheck the radio button if user cancels
    }
}

// Function for marking item as not received
function confirmNotReceived(radio) {
    alert("We will review your request. Please contact support.");
}

// Attach event listeners for radio buttons when the page loads
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".confirm-checkbox").forEach(radio => {
        radio.addEventListener("change", function () {
            if (this.value === "received") {
                confirmDelivery(this);
            } else if (this.value === "not-received") {
                confirmNotReceived(this);
            }
        });
    });
});
