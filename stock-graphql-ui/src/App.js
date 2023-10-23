// Set up a WebSocket connection
const socket = io.connect('http://localhost:5000');

let dataPoints = [];
const ctx = document.getElementById('stockChart').getContext('2d');
const stockChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Stock Price',
            data: dataPoints,
            borderColor: 'rgb(75, 192, 192)',
            fill: false
        }]
    },
    options: {
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'second'
                }
            }
        }
    }
});

// Handle incoming real-time updates
socket.on('stock_price_update', function(data) {
    stockChart.data.labels.push(data.timestamp);
    dataPoints.push(data.price);
    stockChart.update();
});
