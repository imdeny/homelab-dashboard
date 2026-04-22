let discordBotContainer = 'discord-bot';

async function loadConfig() {
  try {
    const cfg = await fetch('/api/config').then(r => r.json());
    discordBotContainer = cfg.discord_bot_container || 'discord-bot';
  } catch (_) {}
}

function formatUptime(seconds) {
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (d > 0) return `${d}d ${h}h`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

function setBar(id, pct) {
  const bar = document.getElementById(id);
  bar.style.width = pct + '%';
  bar.className = 'bar' + (pct > 85 ? ' danger' : pct > 65 ? ' warn' : '');
}

async function refreshSystem() {
  try {
    const s = await fetch('/api/system').then(r => r.json());
    setBar('cpu-bar', s.cpu_percent);
    document.getElementById('cpu-val').textContent = s.cpu_percent.toFixed(1) + '%';

    setBar('ram-bar', s.ram.percent);
    document.getElementById('ram-val').textContent =
      `${s.ram.used_mb}/${s.ram.total_mb} MB`;

    setBar('disk-bar', s.disk.percent);
    document.getElementById('disk-val').textContent =
      `${s.disk.used_gb}/${s.disk.total_gb} GB`;

    const tempEl = document.getElementById('temp-val');
    if (s.temperature_c !== null) {
      tempEl.textContent = s.temperature_c + '°C';
      tempEl.style.color = s.temperature_c > 75 ? 'var(--red)' : s.temperature_c > 60 ? 'var(--yellow)' : 'var(--green)';
    } else {
      tempEl.textContent = 'N/A';
    }

    document.getElementById('uptime-val').textContent = formatUptime(s.uptime_seconds);
  } catch (e) {
    document.getElementById('cpu-val').textContent = 'ERR';
  }
}

async function refreshContainers() {
  const el = document.getElementById('containers-list');
  try {
    const containers = await fetch('/api/containers').then(r => r.json());
    if (!containers.length) {
      el.innerHTML = '<div class="loading">No containers found</div>';
      return;
    }
    el.innerHTML = containers.map(c => {
      const dotClass = c.running ? 'running' : (c.status === 'paused' ? 'other' : 'stopped');
      const isBot = c.name === discordBotContainer;
      return `
        <div class="container-item">
          <div class="status-dot ${dotClass}"></div>
          <span class="container-name${isBot ? ' discord' : ''}">${c.name}${isBot ? ' 🤖' : ''}</span>
          <span class="container-status">${c.status}</span>
        </div>`;
    }).join('');
  } catch (e) {
    el.innerHTML = '<div class="error-msg">Docker unavailable</div>';
  }
}

async function refreshStocks() {
  const el = document.getElementById('stocks-list');
  try {
    const stocks = await fetch('/api/stocks').then(r => r.json());
    if (!stocks.length) {
      el.innerHTML = '<div class="loading">No tickers configured</div>';
      return;
    }
    el.innerHTML = stocks.map(s => {
      if (s.error) {
        return `<div class="stock-card">
          <div class="stock-ticker">${s.ticker}</div>
          <div class="stock-error">${s.error}</div>
        </div>`;
      }
      const up = s.change >= 0;
      return `<div class="stock-card">
        <div class="stock-ticker">${s.ticker}</div>
        <div class="stock-price">$${s.price.toFixed(2)}</div>
        <div class="stock-change ${up ? 'up' : 'down'}">
          ${up ? '▲' : '▼'} ${Math.abs(s.change).toFixed(2)} (${up ? '+' : ''}${s.change_pct.toFixed(2)}%)
        </div>
      </div>`;
    }).join('');
  } catch (e) {
    el.innerHTML = '<div class="error-msg">Stock data unavailable</div>';
  }
}

async function refreshDeals() {
  const el = document.getElementById('deals-list');
  try {
    const deals = await fetch('/api/deals').then(r => r.json());
    if (!deals.length) {
      el.innerHTML = '<div class="loading">No deals found</div>';
      return;
    }
    el.innerHTML = deals.map(d => {
      const thumb = d.thumb
        ? `<img class="deal-thumb" src="${d.thumb}" alt="" loading="lazy" onerror="this.style.display='none'">`
        : `<div class="deal-thumb-placeholder">🎮</div>`;
      const pricing = d.free
        ? `<span class="deal-free-badge">FREE</span>`
        : `<span class="deal-sale-price">$${d.sale_price}</span>
           <span class="deal-orig-price">$${d.normal_price}</span>
           <span class="deal-savings">-${d.savings}%</span>`;
      return `<div class="deal-card">
        <a href="${d.url}" target="_blank" rel="noopener">
          ${thumb}
          <div class="deal-body">
            <div class="deal-source">${d.source}</div>
            <div class="deal-title">${d.title}</div>
            <div class="deal-pricing">${pricing}</div>
          </div>
        </a>
      </div>`;
    }).join('');
  } catch (e) {
    el.innerHTML = '<div class="error-msg">Deals unavailable</div>';
  }
}

function updateTimestamp() {
  document.getElementById('last-updated').textContent =
    'Updated ' + new Date().toLocaleTimeString();
}

async function refreshFast() {
  await Promise.all([refreshSystem(), refreshContainers()]);
  updateTimestamp();
}

async function refreshSlow() {
  await Promise.all([refreshStocks(), refreshDeals()]);
}

async function init() {
  await loadConfig();
  await Promise.all([refreshFast(), refreshSlow()]);
  setInterval(refreshFast, 10_000);   // system + containers every 10s
  setInterval(refreshStocks, 300_000); // stocks every 5min
  setInterval(refreshDeals, 1_800_000); // deals every 30min
}

init();
