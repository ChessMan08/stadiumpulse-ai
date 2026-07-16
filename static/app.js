const $ = (selector) => document.querySelector(selector);

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || `Request failed (${response.status})`);
  }
  return data;
}

// ---------- Accessibility preferences ----------
function applyStoredPreferences() {
  const contrast = localStorage.getItem("sp-contrast") === "on";
  const scale = localStorage.getItem("sp-font-scale") || "1";
  document.documentElement.classList.toggle("high-contrast", contrast);
  document.documentElement.style.setProperty("--font-scale", scale);
  $("#contrast-toggle").setAttribute("aria-pressed", String(contrast));
}

function initPreferenceControls() {
  $("#contrast-toggle").addEventListener("click", () => {
    const isOn = document.documentElement.classList.toggle("high-contrast");
    localStorage.setItem("sp-contrast", isOn ? "on" : "off");
    $("#contrast-toggle").setAttribute("aria-pressed", String(isOn));
  });
  const step = (delta) => {
    const current = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--font-scale")) || 1;
    const next = Math.min(1.6, Math.max(0.8, current + delta));
    document.documentElement.style.setProperty("--font-scale", next);
    localStorage.setItem("sp-font-scale", String(next));
  };
  $("#font-increase").addEventListener("click", () => step(0.1));
  $("#font-decrease").addEventListener("click", () => step(-0.1));
}

// ---------- Tabs ----------
function initTabs() {
  const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
  const activate = (tab) => {
    tabs.forEach((t) => {
      const selected = t === tab;
      t.setAttribute("aria-selected", String(selected));
      t.classList.toggle("active", selected);
      document.getElementById(t.getAttribute("aria-controls")).hidden = !selected;
    });
    tab.focus();
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => activate(tab));
    tab.addEventListener("keydown", (event) => {
      if (event.key === "ArrowRight") activate(tabs[(index + 1) % tabs.length]);
      if (event.key === "ArrowLeft") activate(tabs[(index - 1 + tabs.length) % tabs.length]);
    });
  });
}

// ---------- Dashboard ----------
function densityClass(value) {
  if (value >= 3.5) return "danger";
  if (value >= 2.5) return "warn";
  return "";
}

function renderDashboard(data) {
  const banner = $("#alert-banner");
  if (data.active_alert_count > 0) {
    banner.hidden = false;
    banner.textContent = `${data.active_alert_count} gate(s) above safe crowd density — peak at ${data.peak_gate} gate.`;
  } else {
    banner.hidden = true;
  }

  const list = $("#gate-bars");
  list.innerHTML = "";
  for (const reading of data.sensors.readings) {
    const item = document.createElement("li");
    const pct = Math.min(100, (reading.density / 6) * 100).toFixed(0);
    item.innerHTML = `
      <div>${reading.gate} gate — ${reading.density} persons/sqm${reading.anomaly ? ` (${reading.anomaly})` : ""}</div>
      <div class="gate-bar-track"><div class="gate-bar-fill ${densityClass(reading.density)}" style="width:${pct}%"></div></div>
    `;
    list.appendChild(item);
  }

  $("#sustainability-tip").textContent = data.sustainability_tip;
  $("#workforce-coverage").textContent = `${data.workforce_filled_percent}% of volunteer shifts filled.`;
}

async function loadEnergyZones() {
  try {
    const report = await fetchJSON("/api/sustainability/report");
    const list = $("#energy-zones");
    list.innerHTML = report.zones
      .map((z) => `<li>${z.gate}: ${z.estimated_kw} kW${z.reducible ? ` (reducible, saves ${z.potential_savings_kw} kW)` : ""}</li>`)
      .join("");
  } catch {
    // dashboard already shows the tip; zone breakdown is supplementary
  }
}

async function loadDashboard() {
  try {
    renderDashboard(await fetchJSON("/api/dashboard/summary"));
  } catch (err) {
    $("#sustainability-tip").textContent = `Error loading dashboard: ${err.message}`;
  }
  loadEnergyZones();
}

// ---------- Transit ----------
async function loadTransitCities() {
  const select = $("#transit-city");
  const cities = await fetchJSON("/api/transit/cities");
  select.innerHTML = cities.map((c) => `<option value="${c.id}">${c.label} (${c.stadium})</option>`).join("");
}

function initTransitForm() {
  $("#transit-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const box = $("#transit-result");
    box.textContent = "Finding your route…";
    try {
      const body = {
        city: $("#transit-city").value,
        origin: $("#transit-origin").value,
        language: $("#transit-language").value,
      };
      const data = await fetchJSON("/api/transit/route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      box.textContent =
        `${data.narrative}\n\nModes: ${data.modes.join(" → ")} | ETA: ${data.estimated_minutes} min | Gate: ${data.recommended_gate}` +
        (data.congestion_warning ? `\n⚠ ${data.congestion_warning}` : "");
    } catch (err) {
      box.textContent = `Error: ${err.message}`;
    }
  });

  $("#wayfind-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const box = $("#wayfind-result");
    box.textContent = "Finding directions…";
    try {
      const body = { section: $("#wayfind-section").value, amenity: $("#wayfind-amenity").value };
      const data = await fetchJSON("/api/navigation/wayfind", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      box.textContent =
        `${data.narrative}\n\nDestination: ${data.destination} | ~${data.walk_minutes} min` +
        (data.congestion_warning ? `\n⚠ ${data.congestion_warning}` : "");
    } catch (err) {
      box.textContent = `Error: ${err.message}`;
    }
  });
}

// ---------- Accessibility demo ----------
async function loadAccessibilityEvents() {
  const events = await fetchJSON("/api/accessibility/events");
  const list = $("#event-list");
  list.innerHTML = events
    .map((e) => `<li><button type="button" data-event="${e.id}">Min ${e.minute}: ${e.event_type.replace("_", " ")}</button></li>`)
    .join("");
  list.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-event]");
    if (!button) return;
    await narrateEvent(button.dataset.event);
  });
}

async function narrateEvent(eventId) {
  const box = $("#commentary-result");
  box.textContent = "Generating description…";
  try {
    const body = {
      event_id: eventId,
      language: $("#access-language").value,
      verbosity: $("#access-verbosity").value,
    };
    const data = await fetchJSON("/api/accessibility/commentary", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    box.textContent = data.text;
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(data.text);
      speechSynthesis.cancel();
      speechSynthesis.speak(utterance);
    }
  } catch (err) {
    box.textContent = `Error: ${err.message}`;
  }
}

// ---------- Multilingual FAQ ----------
async function loadFaqTopics() {
  const topics = await fetchJSON("/api/multilingual/topics");
  const list = $("#faq-topics");
  list.innerHTML = topics.map((t) => `<li><button type="button" data-topic="${t.id}">${t.label}</button></li>`).join("");
  list.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-topic]");
    if (!button) return;
    const box = $("#faq-result");
    box.textContent = "Looking that up…";
    try {
      const data = await fetchJSON("/api/multilingual/faq", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic_id: button.dataset.topic, language: $("#faq-language").value }),
      });
      box.textContent = data.answer;
    } catch (err) {
      box.textContent = `Error: ${err.message}`;
    }
  });
}

// ---------- Ops copilot ----------
function initOpsForm() {
  $("#ops-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const box = $("#ops-result");
    box.textContent = "Analyzing…";
    try {
      const data = await fetchJSON("/api/ops/query", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-API-Key": $("#ops-key").value },
        body: JSON.stringify({ question: $("#ops-question").value }),
      });
      const sops = data.retrieved_sops.map((s) => s.title).join(", ") || "none";
      box.textContent = `${data.narrative}\n\nReferenced protocols: ${sops}`;
    } catch (err) {
      box.textContent = `Error: ${err.message}`;
    }
  });
}

// ---------- Workforce ----------
function initWorkforceControls() {
  $("#optimize-btn").addEventListener("click", async () => {
    const box = $("#optimize-result");
    box.textContent = "Running genetic algorithm…";
    try {
      const data = await fetchJSON("/api/workforce/optimize", {
        method: "POST",
        headers: { "X-API-Key": $("#workforce-key").value },
      });
      box.textContent =
        `Fitness: ${data.fitness} over ${data.generations_run} generations\n` +
        `${data.filled_percent}% of ${data.total_shifts} shifts filled, ${data.constraint_violations} constraint violations.`;
    } catch (err) {
      box.textContent = `Error: ${err.message}`;
    }
  });

  $("#briefing-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const box = $("#briefing-result");
    box.textContent = "Drafting message…";
    try {
      const id = $("#volunteer-id").value.trim();
      const data = await fetchJSON(`/api/workforce/briefing/${encodeURIComponent(id)}`, {
        headers: { "X-API-Key": $("#workforce-key").value },
      });
      box.textContent = `${data.volunteer_name}: ${data.message}`;
    } catch (err) {
      box.textContent = `Error: ${err.message}`;
    }
  });
}

// ---------- Init ----------
applyStoredPreferences();
initPreferenceControls();
initTabs();
initTransitForm();
initOpsForm();
initWorkforceControls();
loadDashboard();
loadTransitCities();
loadAccessibilityEvents();
loadFaqTopics();
setInterval(loadDashboard, 8000);
