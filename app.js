const CHART_COLORS = {
  year: "#b7791f",
  month: "#2f855a",
  week: "#2b6cb0",
};

function formatJPDate(dateStr) {
  const d = new Date(dateStr);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

function sliceByDays(rows, days) {
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - days);
  return rows.filter((r) => new Date(r.date) >= cutoff);
}

function createLineChart(canvasId, rows, color) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;

  new Chart(ctx, {
    type: "line",
    data: {
      labels: rows.map((r) => formatJPDate(r.date)),
      datasets: [
        {
          label: "JPY/g",
          data: rows.map((r) => r.jpyPerGram),
          borderColor: color,
          backgroundColor: `${color}33`,
          borderWidth: 2,
          tension: 0.24,
          pointRadius: 0,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          mode: "index",
          intersect: false,
          callbacks: {
            label: (ctx2) => ` ${ctx2.parsed.y.toLocaleString("ja-JP")} 円/g`,
          },
        },
      },
      interaction: {
        mode: "nearest",
        intersect: false,
      },
      scales: {
        x: {
          ticks: { maxTicksLimit: 8 },
          grid: { display: false },
        },
        y: {
          ticks: {
            callback: (v) => `${Number(v).toLocaleString("ja-JP")} 円`,
          },
        },
      },
    },
  });
}

function setupQr() {
  const pageUrl = window.location.href;
  document.getElementById("pageUrl").textContent = pageUrl;
  const encoded = encodeURIComponent(pageUrl);
  document.getElementById("qrImage").src =
    `https://api.qrserver.com/v1/create-qr-code/?size=320x320&data=${encoded}`;
}

async function init() {
  setupQr();

  const errorEl = document.getElementById("error");
  const updatedAtEl = document.getElementById("updatedAt");

  try {
    const res = await fetch("/api/gold", { cache: "no-store" });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();
    const rows = data.data || [];
    if (!rows.length) {
      throw new Error("金価格データが空です");
    }

    const year = sliceByDays(rows, 365);
    const month = sliceByDays(rows, 31);
    const week = sliceByDays(rows, 7);

    createLineChart("chartYear", year, CHART_COLORS.year);
    createLineChart("chartMonth", month, CHART_COLORS.month);
    createLineChart("chartWeek", week, CHART_COLORS.week);

    updatedAtEl.textContent = `最終更新: ${new Date(data.fetchedAt).toLocaleString("ja-JP")} (${data.unit})`;
  } catch (err) {
    errorEl.hidden = false;
    errorEl.textContent = `データ取得に失敗しました: ${err.message}`;
    updatedAtEl.textContent = "データ取得に失敗しました";
  }
}

window.addEventListener("DOMContentLoaded", init);
