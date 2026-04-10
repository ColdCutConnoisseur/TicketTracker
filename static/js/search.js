
// Inventory search bar + click interaction logic

document.getElementById('inventory-search').addEventListener('input', async function() {
    const query = this.value.trim();
    const suggestions = document.getElementById('suggestions');

    if (query.length < 2) {
        suggestions.style.display = 'none';
        suggestions.innerHTML = '';
        return;
    }

    try {
        const response = await fetch(`${search_endpoint}?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        suggestions.innerHTML = '';

        if (data.length === 0) {
            suggestions.style.display = 'none';
            return;
        }

        data.forEach(item => {
            const newDiv = document.createElement('div');
            newDiv.className = 'inventory-search-dropdown-item';
            newDiv.textContent = item.event_name;
            newDiv.onclick = () => {
                document.getElementById('inventory-search').value = item.event_name;
                suggestions.style.display = 'none';

                document.getElementById('readonly-item-event_id').value = item.event_id;

                document.getElementById('update-item-qty-purchased').value = item.qty_purchased;
                document.getElementById('update-item-total-cost').value = item.total_cost;
                document.getElementById('update-item-cost-per').value = item.cost_per;

                document.getElementById('update-item-self-use-qty').value = item.self_use_qty;
                document.getElementById('update-item-sale-total-proceeds').value = item.sale_total_proceeds;
                document.getElementById('update-item-sale-marketplace').value = item.sale_marketplace;
                document.getElementById('update-item-eventNotes').value = item.notes;
                document.getElementById('update-item-check-price-url').value = item.check_price_url;
            };
            suggestions.appendChild(newDiv);
        });

        suggestions.style.display = 'block';
    } catch (err) {
        console.error("Search error:", err);
        suggestions.style.display = 'none';
    }
});


