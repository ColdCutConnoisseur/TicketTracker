function showPriceChart(eventId, buttonElement) {
    const chartId = "priceChartParent-" + eventId;
    const chartParentElement = document.getElementById(chartId);

    if (chartParentElement.style.display === "none") {
        chartParentElement.style.display = "block";
        buttonElement.innerText = "Hide Price Chart";
    } else {
        chartParentElement.style.display = "none";
        buttonElement.innerText = "Show Price Chart";
    }
}

function showSupplyChart(eventId, buttonElement) {
    const chartId = "supplyChartParent-" + eventId;
    const chartParentElement = document.getElementById(chartId);

    if (chartParentElement.style.display === "none") {
        chartParentElement.style.display = "block";
        buttonElement.innerText = "Hide Supply Chart";
    } else {
        chartParentElement.style.display = "none";
        buttonElement.innerText = "Show Supply Chart";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".show-price-btn").forEach((button) => {
        button.addEventListener("click", function () {
            const eventId = this.getAttribute("data-event-id");
            showPriceChart(eventId, this);
        });
    });

    document.querySelectorAll(".show-supply-btn").forEach((button) => {
        button.addEventListener("click", function () {
            const eventId = this.getAttribute("data-event-id");
            showSupplyChart(eventId, this);
        });
    });
});