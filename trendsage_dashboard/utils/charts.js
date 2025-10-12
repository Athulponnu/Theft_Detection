function createLineChart(canvasId, dataset) {
  new Chart(document.getElementById(canvasId), {
    type: 'line',
    data: {
      labels: dataset.labels,
      datasets: [{
        label: "Trend Growth",
        data: dataset.data,
        borderColor: "cyan",
        fill: false,
        tension: 0.3
      }]
    },
    options: { responsive: true }
  });
}

function createBarChart(canvasId, dataset) {
  new Chart(document.getElementById(canvasId), {
    type: 'bar',
    data: {
      labels: dataset.labels,
      datasets: [{
        label: "Topic Comparison",
        data: dataset.data,
        backgroundColor: "orange"
      }]
    },
    options: { responsive: true }
  });
}

function createPieChart(canvasId, dataset) {
  new Chart(document.getElementById(canvasId), {
    type: 'pie',
    data: {
      labels: dataset.labels,
      datasets: [{
        data: dataset.data,
        backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4CAF50", "#9C27B0"]
      }]
    },
    options: { responsive: true }
  });
}
