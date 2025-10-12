let knownLogsData = [];
let unknownLogsData = [];

// Fetch logs from API
async function fetchLogs(url) {
  try {
    const response = await fetch(url);
    return await response.json();
  } catch (error) {
    console.error("Error fetching logs:", error);
    return [];
  }
}

// Render logs in a table
function renderTable(logs, tableId) {
  const table = document.getElementById(tableId);
  table.innerHTML = "";

  logs.forEach(log => {
    const row = `
      <tr>
        <td>${log.timestamp}</td>
        <td>${log.face_name || "N/A"}</td>
        <td>${log.objects_detected.join(", ")}</td>
        <td>${log.alert ? "⚠️ ALERT" : "✅ Safe"}</td>
        <td>${log.capture_path ? `<img src="${log.capture_path}" class="capture-img">` : "—"}</td>
      </tr>
    `;
    table.innerHTML += row;
  });
}

// Filter logs by date & time
function filterLogs(logs, dateInput, timeInput) {
  return logs.filter(log => {
    const [logDate, logTime] = log.timestamp.split(" ");
    const dateMatch = dateInput ? logDate === dateInput : true;
    const timeMatch = timeInput ? logTime.startsWith(timeInput) : true;
    return dateMatch && timeMatch;
  });
}

// Add listener for common filters
function addCommonSearchListeners() {
  const dateEl = document.getElementById("dateFilter");
  const timeEl = document.getElementById("timeFilter");

  function applyFilter() {
    const date = dateEl.value;
    const time = timeEl.value;

    renderTable(filterLogs(knownLogsData, date, time), "knownLogsTable");
    renderTable(filterLogs(unknownLogsData, date, time), "unknownLogsTable");
  }

  dateEl.addEventListener("change", applyFilter);
  timeEl.addEventListener("change", applyFilter);
}

// Load logs from API and initialize dashboard
async function loadAllLogs() {
  knownLogsData = await fetchLogs("http://127.0.0.1:8000/api/logs/known");
  unknownLogsData = await fetchLogs("http://127.0.0.1:8000/api/logs/unknown");

  // Sort latest first
  knownLogsData.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  unknownLogsData.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

  renderTable(knownLogsData, "knownLogsTable");
  renderTable(unknownLogsData, "unknownLogsTable");

  addCommonSearchListeners();
}

// Initialize
loadAllLogs();
