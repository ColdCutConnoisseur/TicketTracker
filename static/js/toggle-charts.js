// Handles chart show/hide toggle buttons

function showPriceChart(index, buttonElement) {
    const chartParentElement = document.getElementById("priceChartParent-" + index);
    const visible = chartParentElement.style.display !== 'none';
    chartParentElement.style.display = visible ? 'none' : 'block';
    buttonElement.innerText = visible ? "Show Price Chart" : "Hide Price Chart";
}

function showSupplyChart(index, buttonElement) {
    const chartParentElement = document.getElementById("supplyChartParent-" + index);
    const visible = chartParentElement.style.display !== 'none';
    chartParentElement.style.display = visible ? 'none' : 'block';
    buttonElement.innerText = visible ? "Show Supply Chart" : "Hide Supply Chart";
}