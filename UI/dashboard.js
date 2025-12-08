let attackChart;
let attackData = [];
let labels = [];
let lastAttackCount = 0;

async function updateDashboard() {
    const res = await fetch("http://127.0.0.1:8000/events");
    const events = await res.json();

    updateDevices(events);
    updateSummary(events);
    updateLogs(events);
    updateGraph(events);
}

/* ========== PAGE SWITCHING ========== */
function showPage(page) {
    document.querySelectorAll(".page").forEach(p => p.style.display = "none");
    document.getElementById("page-" + page).style.display = "block";

    document.querySelectorAll(".menu-item").forEach(m => m.classList.remove("active"));
    [...document.querySelectorAll(".menu-item")]
        .find(m => m.textContent.trim().toLowerCase() === page)
        .classList.add("active");
}

/* ========== DEVICE STATUS ========== */
function updateDevices(events) {
    const grid = document.getElementById("device-grid");
    grid.innerHTML = "";

    const latest = {};

    events.forEach(ev => latest[ev.device_type] = ev.status);

    for (let dev in latest) {
        const isAttack = latest[dev] === "ATTACK DETECTED";

        const tile = `
            <div class="device-tile">
                <div class="device-name">${dev}</div>
                <div class="${isAttack ? 'device-status-alert' : 'device-status-ok'}">
                    ${isAttack ? "⚠ Alert" : "✓ Normal"}
                </div>
            </div>
        `;

        grid.innerHTML += tile;
    }

    // Also update STATUS page
    document.getElementById("status-grid").innerHTML = grid.innerHTML;
}

/* ========== SUMMARY ========== */
function updateSummary(events) {
    const body = document.getElementById("summary-body");
    body.innerHTML = "";

    const count = {};
    events.forEach(ev => count[ev.status] = (count[ev.status] || 0) + 1);

    for (let s in count) {
        body.innerHTML += `<tr><td>${s}</td><td>${count[s]}</td></tr>`;
    }
}

/* ========== LOGS ========== */
function updateLogs(events) {
    const body = document.getElementById("logs-body");
    body.innerHTML = "";

    events.slice().reverse().forEach(ev => {
        const cls = ev.status === "ATTACK DETECTED" ? "status-blocked" : "status-logged";
        const action = ev.status === "ATTACK DETECTED" ? "Blocked" : "Logged";

        body.innerHTML += `
            <tr>
                <td>${new Date(ev.timestamp * 1000).toLocaleTimeString()}</td>
                <td>${ev.device_type}</td>
                <td>${ev.status}</td>
                <td class="${cls}">${action}</td>
            </tr>
        `;
    });
}

/* ========== ATTACK TREND GRAPH ========== */
function updateGraph(events) {
    const attackCount = events.filter(e => e.status === "ATTACK DETECTED").length;

    if (attackCount > lastAttackCount) showPopup();
    lastAttackCount = attackCount;

    attackData.push(attackCount);
    labels.push(new Date().toLocaleTimeString());

    if (attackData.length > 20) {
        attackData.shift();
        labels.shift();
    }

    if (!attackChart) {
        const ctx = document.getElementById("attackChart").getContext("2d");
        attackChart = new Chart(ctx, {
            type: "line",
            data: {
                labels,
                datasets: [{
                    data: attackData,
                    label: "Attacks",
                    borderColor: "#ef4444",
                    backgroundColor: "rgba(239,68,68,0.3)"
                }]
            },
            options: { animation: false }
        });
    } else {
        attackChart.update();
    }
}

/* ========== POPUP ALERT ========== */
function showPopup() {
    const popup = document.getElementById("alert-popup");
    popup.textContent = "⚠ Attack Detected!";
    popup.style.display = "block";
    setTimeout(() => popup.style.display = "none", 2000);
}

setInterval(updateDashboard, 2000);
updateDashboard();
