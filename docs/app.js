const MANIFEST_SOURCES = [
  "./ecosystem.json",
  "https://raw.githubusercontent.com/rfdetoni/kitt/main/ecosystem.json",
];

const moduleLabels = {
  protocol: "API",
  memory: "MEM",
  toolbox: "NAT",
  assistant: "AI",
  "agent-cli": "CLI",
  "ai-workers": "WRK",
  "reverse-proxy": "WEB",
};

const installOptions = {
  unix: {
    command: "curl -fsSL https://raw.githubusercontent.com/rfdetoni/kitt/main/install.sh | sh",
    note: "Interactive installer for Linux, macOS and POSIX systems.",
  },
  windows: {
    command: "irm https://raw.githubusercontent.com/rfdetoni/kitt/main/install.ps1 | iex",
    note: "Run from PowerShell. The installer resolves selected modules and their required dependencies.",
  },
  docker: {
    command: "cp .env.docker.example .env\ndocker compose up -d browser reverse-proxy\ndocker compose run --rm agent",
    note: "Docker is optional. Native installation remains the canonical path for the complete resident/native stack.",
  },
};

async function loadManifest() {
  let lastError;
  for (const source of MANIFEST_SOURCES) {
    try {
      const response = await fetch(source, { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError || new Error("Unable to load ecosystem manifest");
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function renderModules(manifest) {
  const grid = document.querySelector("#module-grid");
  if (!grid) return;
  grid.replaceChildren();

  const modules = Object.entries(manifest.modules || {})
    .sort(([, a], [, b]) => (a.order || 0) - (b.order || 0));

  for (const [id, module] of modules) {
    const card = el("article", "module-card");
    card.append(el("span", "module-icon", moduleLabels[id] || "KIT"));
    card.append(el("h3", "", module.name || id));
    card.append(el("p", "", module.description || "K.I.T.T. ecosystem module."));

    const meta = el("div", "module-meta");
    for (const prerequisite of module.prerequisites || []) {
      meta.append(el("span", "", prerequisite));
    }
    card.append(meta);

    if (module.repository) {
      const link = el("a", "module-link");
      link.href = `https://github.com/${module.repository}`;
      link.target = "_blank";
      link.rel = "noreferrer";
      link.append(document.createTextNode("Repository "));
      const arrow = el("span", "", "↗");
      arrow.setAttribute("aria-hidden", "true");
      link.append(arrow);
      card.append(link);
    }
    grid.append(card);
  }
}

function renderPresets(manifest) {
  const grid = document.querySelector("#preset-grid");
  if (!grid) return;
  grid.replaceChildren();

  for (const [id, preset] of Object.entries(manifest.presets || {})) {
    const card = el("article", "preset-card");
    card.append(el("h3", "", preset.name || id));
    card.append(el("p", "", preset.description || "K.I.T.T. installation preset."));
    card.append(el("small", "", `--preset ${id}`));
    grid.append(card);
  }
}

function renderManifestError() {
  const grid = document.querySelector("#module-grid");
  if (!grid) return;
  grid.replaceChildren();
  const card = el("article", "module-card module-loading");
  card.append(el("span", "module-icon", "!"));
  card.append(el("h3", "", "Manifest unavailable"));
  card.append(el("p", "", "The live catalog could not be loaded. The repositories remain available through the main GitHub project."));
  grid.append(card);
}

function initInstallTabs() {
  const command = document.querySelector("#install-command");
  const note = document.querySelector("#install-note");
  const tabs = [...document.querySelectorAll(".install-tab")];

  for (const tab of tabs) {
    tab.addEventListener("click", () => {
      const option = installOptions[tab.dataset.install];
      if (!option || !command || !note) return;
      command.textContent = option.command;
      note.textContent = option.note;
      for (const item of tabs) {
        const active = item === tab;
        item.classList.toggle("active", active);
        item.setAttribute("aria-selected", String(active));
      }
    });
  }
}

function initCopyButton() {
  const button = document.querySelector("#copy-install");
  const command = document.querySelector("#install-command");
  if (!button || !command) return;

  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(command.textContent || "");
      const original = button.textContent;
      button.textContent = "Copied";
      window.setTimeout(() => { button.textContent = original; }, 1400);
    } catch {
      button.textContent = "Select & copy";
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(command);
      selection?.removeAllRanges();
      selection?.addRange(range);
    }
  });
}

function setExternalLinksSafety() {
  for (const link of document.querySelectorAll('a[target="_blank"]')) {
    const rel = new Set((link.getAttribute("rel") || "").split(/\s+/).filter(Boolean));
    rel.add("noopener");
    rel.add("noreferrer");
    link.setAttribute("rel", [...rel].join(" "));
  }
}

async function main() {
  initInstallTabs();
  initCopyButton();
  setExternalLinksSafety();

  try {
    const manifest = await loadManifest();
    renderModules(manifest);
    renderPresets(manifest);
  } catch (error) {
    console.warn("K.I.T.T. ecosystem manifest could not be loaded", error);
    renderManifestError();
  }
}

main();
