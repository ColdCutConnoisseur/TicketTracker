document.addEventListener("DOMContentLoaded", function () {
    // Expect openEventIds and openEventDps to already be defined via a <script> tag in index.html
    const openEventGroups = {};

    for (let i = 0; i < openEventIds.length; i++) {
        const currentID = openEventIds[i];
        const eventPrices = [];
        const eventDates = [];
        const eventSupply = [];

        Object.values(openEventDps).forEach((datapoint) => {
            const [obsId, price, time, supply] = datapoint;
            if (obsId === currentID) {
                eventPrices.push(price);
                eventDates.push(time);
                eventSupply.push(supply);
            }
        });

        openEventGroups[currentID] = [eventPrices, eventDates, eventSupply];

    }

    // Render charts
    console.log(openEventIds);
    openEventIds.forEach(currentID => {
        const [eventPrices, eventLabels, eventSupply] = openEventGroups[currentID];

        const priceChart = new Chart(
            document.getElementById(`priceChart-${currentID}`),
            {
                type: 'line',
                data: {
                    labels: eventLabels,
                    datasets: [{
                        label: 'Price',
                        backgroundColor: 'rgb(255, 99, 132)',
                        borderColor: 'rgb(255, 99, 132)',
                        data: eventPrices,
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            }
        );

        const supplyChart = new Chart(
            document.getElementById(`supplyChart-${currentID}`),
            {
                type: 'line',
                data: {
                    labels: eventLabels,
                    datasets: [{
                        label: 'Supply',
                        backgroundColor: 'rgb(99, 132, 255)',
                        borderColor: 'rgb(99, 132, 255)',
                        data: eventSupply,
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            }
        );
    });
});