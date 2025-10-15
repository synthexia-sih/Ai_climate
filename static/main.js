// --- India Bounding Box
const indiaBounds = [
  [6.5546079, 68.1113787],   // SW corner
  [35.6745457, 97.395561]    // NE corner
];

let map = L.map('map', {
    maxBounds: indiaBounds,
    maxBoundsViscosity: 1.0,
    minZoom: 4,
    maxZoom: 10
}).setView([22.9734, 78.6569], 5);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
}).addTo(map);

// Optional: Draw India rectangle
L.rectangle(indiaBounds, {color: "#ff7800", weight: 2, fillOpacity: 0.0}).addTo(map);

const cities = {
  "Delhi": [28.6139, 77.2090],
  "Mumbai": [19.0760, 72.8777],
  "Kolkata": [22.5726, 88.3639],
  "Chennai": [13.0827, 80.2707],
  "Bengaluru": [12.9716, 77.5946],
  "Chandigarh": [30.7333, 76.7794]
};

let cityMarker = null;

function highlightCity() {
  const city = document.getElementById("city").value;
  const coords = cities[city];
  if (!coords) return;
  
  if (cityMarker) {
    map.removeLayer(cityMarker);
  }
  
  cityMarker = L.marker(coords).addTo(map)
    .bindPopup(`<b>${city}</b><br>Heatwave Prediction Zone`).openPopup();
  map.flyTo(coords, 7, { animate: true, duration: 1.5 });
}

function getRiskClass(riskLevel) {
  if (riskLevel.includes("Extreme")) return "risk-extreme";
  if (riskLevel.includes("High")) return "risk-high";
  if (riskLevel.includes("Moderate")) return "risk-moderate";
  if (riskLevel.includes("Low")) return "risk-low";
  return "risk-very-low";
}

function displayResults(data) {
  const resultsDiv = document.getElementById("results");
  const resultsBody = document.getElementById("resultsBody");
  
  if (data.error) {
    document.getElementById("status").innerHTML = 
      `<div class="error">❌ Error: ${data.error}</div>`;
    resultsDiv.classList.add("hidden");
    return;
  }
  
  // Clear previous results
  resultsBody.innerHTML = "";
  
  // Display results in table
  data.results.forEach(result => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
        ${result.DATE}
      </td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        ${(result.Heatwave_Prob * 100).toFixed(1)}%
      </td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        ${result.Heatwave_Pred ? "🌡️ Heatwave" : "✅ Normal"}
      </td>
      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
        <span class="${getRiskClass(result.Risk_Level)}">${result.Risk_Level}</span>
      </td>
    `;
    resultsBody.appendChild(row);
  });
  
  // Show results table
  resultsDiv.classList.remove("hidden");
  
  // Update status
  document.getElementById("status").innerHTML = 
    `<div class="success">
      ✅ Predictions completed for <strong>${data.city}</strong><br>
      📅 Period: ${data.start_date} to ${data.results[data.results.length-1].DATE}<br>
      📊 ${data.results.length} days analyzed
    </div>`;
}

async function predict() {
  const city = document.getElementById("city").value;
  const date = document.getElementById("startDate").value;
  const days = document.getElementById("days").value;
  
  // Validate inputs
  if (!city) {
    document.getElementById("status").innerHTML = 
      `<div class="error">❌ Please select a city</div>`;
    return;
  }
  
  if (days < 1 || days > 15) {
    document.getElementById("status").innerHTML = 
      `<div class="error">❌ Days must be between 1 and 15</div>`;
    return;
  }
  
  // Show loading state
  document.getElementById("status").innerHTML = 
    `<div class="flex items-center justify-center gap-2">
      <div class="loading"></div>
      ⏳ Analyzing weather patterns for ${city}...
    </div>`;
  
  // Hide previous results
  document.getElementById("results").classList.add("hidden");
  
  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        city: city,
        start_date: date,
        days: parseInt(days)
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    displayResults(data);
    
  } catch (error) {
    console.error("Prediction error:", error);
    document.getElementById("status").innerHTML = 
      `<div class="error">❌ Failed to get predictions: ${error.message}</div>`;
    document.getElementById("results").classList.add("hidden");
  }
}

// Set default date to today
function setDefaultDate() {
  const today = new Date().toISOString().split('T')[0];
  document.getElementById("startDate").value = today;
}

// Initialize the application
function init() {
  setDefaultDate();
  highlightCity();
  
  // Add event listeners
  document.getElementById("city").addEventListener("change", highlightCity);
  document.getElementById("days").addEventListener("input", function(e) {
    const value = parseInt(e.target.value);
    if (value < 1) e.target.value = 1;
    if (value > 15) e.target.value = 15;
  });
}

// Initialize when page loads
document.addEventListener("DOMContentLoaded", init);

// Also initialize on window load as fallback
window.addEventListener("load", init);
