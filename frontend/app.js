const API_BASE = window.API_BASE_URL || "http://127.0.0.1:8000";

const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const copyBtn = document.getElementById("copyBtn");
const downloadBtn = document.getElementById("downloadBtn");
const saveEditedBtn = document.getElementById("saveEditedBtn");
const toggleJsonBtn = document.getElementById("toggleJsonBtn");
const designEditor = document.getElementById("designEditor");
const jsonOut = document.getElementById("jsonOut");
const jsonSection = document.getElementById("jsonSection");
const statusEl = document.getElementById("status");
const resultTabs = document.getElementById("resultTabs");
const batchMeta = document.getElementById("batchMeta");
const themeToggleBtn = document.getElementById("themeToggleBtn");

const THEME_KEY = "pptx_design_md_theme";

let currentRunId = null;
let batchResults = [];
let activeIndex = 0;
let currentPayload = null;

function resolveInitialTheme() {
  const stored = localStorage.getItem(THEME_KEY);
  if (stored === "light" || stored === "dark") {
    return stored;
  }
  return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const isDark = theme === "dark";
  themeToggleBtn.textContent = isDark ? "Light mode" : "Dark mode";
  themeToggleBtn.setAttribute("aria-pressed", String(isDark));
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  const next = current === "dark" ? "light" : "dark";
  localStorage.setItem(THEME_KEY, next);
  applyTheme(next);
}

function setStatus(message) {
  statusEl.textContent = message;
}

function refreshActionsState() {
  const hasText = Boolean(designEditor.value && designEditor.value.trim());
  copyBtn.disabled = !hasText;
  downloadBtn.disabled = !hasText;
  saveEditedBtn.disabled = !(hasText && currentRunId);
  toggleJsonBtn.disabled = !currentPayload;
}

function renderTabs() {
  resultTabs.innerHTML = "";
  if (!batchResults.length) {
    batchMeta.textContent = "No files analyzed yet.";
    return;
  }
  batchMeta.textContent = `${batchResults.length} file${batchResults.length > 1 ? "s" : ""} analyzed.`;

  batchResults.forEach((item, idx) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `result-tab${idx === activeIndex ? " active" : ""}`;
    button.textContent = item.filename || `result-${idx + 1}`;
    button.addEventListener("click", () => selectResult(idx));
    resultTabs.appendChild(button);
  });
}

function selectResult(index) {
  const selected = batchResults[index];
  if (!selected) {
    return;
  }
  activeIndex = index;
  currentRunId = selected.run_id || null;
  currentPayload = selected;
  designEditor.value = selected.design_md || "";
  jsonOut.textContent = JSON.stringify(selected, null, 2);
  renderTabs();
  refreshActionsState();
}

async function uploadFiles(fileList) {
  const files = Array.from(fileList || []).filter((f) => f.name.toLowerCase().endsWith(".pptx"));
  if (!files.length) {
    setStatus("Please upload at least one .pptx file.");
    return;
  }

  setStatus(files.length === 1 ? "Uploading and analyzing..." : `Uploading ${files.length} files...`);

  try {
    if (files.length === 1) {
      const form = new FormData();
      form.append("file", files[0]);
      const res = await fetch(`${API_BASE}/extract`, { method: "POST", body: form });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Request failed" }));
        throw new Error(err.detail || "Request failed");
      }
      const payload = await res.json();
      batchResults = [{ filename: files[0].name, ...payload }];
      activeIndex = 0;
      selectResult(0);
      setStatus("Done.");
      return;
    }

    const form = new FormData();
    files.forEach((file) => form.append("files", file));
    const res = await fetch(`${API_BASE}/extract/batch`, {
      method: "POST",
      body: form,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Batch request failed" }));
      throw new Error(err.detail || "Batch request failed");
    }
    const payload = await res.json();
    batchResults = payload.results || [];
    activeIndex = 0;
    selectResult(0);
    setStatus("Batch done. Switch between files above.");
  } catch (err) {
    setStatus(`Error: ${err.message}`);
  }
}

function handleDropzoneKeydown(event) {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    fileInput.click();
  }
}

browseBtn.addEventListener("click", () => fileInput.click());
dropzone.addEventListener("keydown", handleDropzoneKeydown);
fileInput.addEventListener("change", (event) => uploadFiles(event.target.files));

["dragenter", "dragover"].forEach((eventName) => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.add("dragover");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.remove("dragover");
  });
});

dropzone.addEventListener("drop", (event) => {
  uploadFiles(event.dataTransfer.files);
});

copyBtn.addEventListener("click", async () => {
  if (!designEditor.value.trim()) {
    return;
  }
  await navigator.clipboard.writeText(designEditor.value);
  setStatus("Copied design.md to clipboard.");
});

downloadBtn.addEventListener("click", () => {
  if (!designEditor.value.trim()) {
    return;
  }
  const blob = new Blob([designEditor.value], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "design.md";
  link.click();
  URL.revokeObjectURL(url);
});

saveEditedBtn.addEventListener("click", async () => {
  if (!currentRunId || !designEditor.value.trim()) {
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/design/save`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        run_id: currentRunId,
        design_md: designEditor.value,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Save failed" }));
      throw new Error(err.detail || "Save failed");
    }
    const payload = await res.json();
    setStatus(`Edited design saved for run ${payload.run_id}.`);
  } catch (err) {
    setStatus(`Error: ${err.message}`);
  }
});

toggleJsonBtn.addEventListener("click", () => {
  jsonSection.classList.toggle("hidden");
});

themeToggleBtn.addEventListener("click", toggleTheme);
applyTheme(resolveInitialTheme());
refreshActionsState();
