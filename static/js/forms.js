// Handles the update form submit

function cleanEmptyStringsToNull(obj) {
    for (const key in obj) {
        if (obj[key] === "") {
            obj[key] = null;
        }
    }
    return obj;
}

document.getElementById("update-event-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const updatedData = {
        event_id: document.getElementById("readonly-item-event_id").value,
        event_name: document.getElementById("inventory-search").value,

        qty_purchased: document.getElementById("update-item-qty-purchased").value,
        total_cost: document.getElementById("update-item-total-cost").value,
        cost_per: document.getElementById("update-item-cost-per").value,
        sale_total_proceeds: document.getElementById("update-item-sale-total-proceeds").value,
        sale_marketplace: document.getElementById("update-item-sale-marketplace").value,
        notes: document.getElementById("update-item-eventNotes").value,
        check_price_url: document.getElementById("update-item-check-price-url").value
    };

    cleanEmptyStringsToNull(updatedData);

    const response = await fetch("/update_inventory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedData)
    });

    const result = await response.json();
    alert(result.message);
});