// All the Chart.js-related logic, including grouping datapoints and rendering

console.log("Running chart rendering script...");

const openEventGroups = {};

for (let i = 0; i < openEventIds.length; i++) {
    const currentID = openEventIds[i];
    const eventPrices = [], eventDates = [], eventSupply = [];

    Object.values(openEventDps).forEach(datapoint => {
        if (datapoint[0] == currentID) {
            eventPrices.push(datapoint[1]);
            eventDates.push(datapoint[2]);
            eventSupply.push(datapoint[3]);
        }
    });

    openEventGroups[currentID] = [eventPrices, eventDates, eventSupply];
}

for (let i = 0; i < openEventIds.length; i++) {
    const [prices, labels, supply] = openEventGroups[openEventIds[i]];

    new Chart(document.getElementById(`priceChart-${openEventIds[i]}`), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{ label: 'Price', backgroundColor: 'rgb(255, 99, 132)', borderColor: 'rgb(255, 99, 132)', data: prices }]
        },
        options: {
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true } }
        }
    });

    new Chart(document.getElementById(`supplyChart-${openEventIds[i]}`), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{ label: 'Section Supply', backgroundColor: 'rgb(255, 99, 132)', borderColor: 'rgb(255, 99, 132)', data: supply }]
        },
        options: {
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true } }
        }
    });
}