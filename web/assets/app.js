(() => {
  const qs = (selector, root = document) => root.querySelector(selector);
  const qsa = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const clamp = (n, min, max) => Math.min(max, Math.max(min, n));

  const formatCny = (cents) => {
    const n = Number(cents);
    if (!Number.isFinite(n)) return "--";
    return `¥ ${new Intl.NumberFormat("zh-CN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(n / 100)}`;
  };

  const formatYmd = (d) => {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  };

  const formatWeekdayZh = (d) => new Intl.DateTimeFormat("zh-CN", { weekday: "short" }).format(d);

  const toastStack = qs("[data-toast-stack]");
  const pushToast = ({ kind = "info", title = "提示", message = "", timeoutMs = 3200 } = {}) => {
    if (!toastStack) return;

    const toast = document.createElement("div");
    toast.className = `toast is-${kind}`;

    const titleRow = document.createElement("div");
    titleRow.className = "toast-title";

    const titleEl = document.createElement("div");
    titleEl.textContent = title;

    const closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.setAttribute("aria-label", "关闭");
    closeBtn.textContent = "×";

    titleRow.appendChild(titleEl);
    titleRow.appendChild(closeBtn);

    const msgEl = document.createElement("div");
    msgEl.className = "toast-msg";
    msgEl.textContent = message;

    toast.appendChild(titleRow);
    toast.appendChild(msgEl);

    const close = () => {
      if (toast.classList.contains("is-leaving")) return;
      toast.classList.add("is-leaving");
      window.setTimeout(() => toast.remove(), 260);
    };

    closeBtn.addEventListener("click", close);
    window.setTimeout(() => close(), clamp(timeoutMs, 1200, 10000));

    toastStack.appendChild(toast);
  };

  const THEME_KEY = "hotelmanager_theme";
  const getSystemTheme = () => {
    const mq = window.matchMedia?.("(prefers-color-scheme: light)");
    return mq && mq.matches ? "light" : "dark";
  };

  const applyTheme = (theme) => {
    const normalized = theme === "light" ? "light" : "dark";
    document.documentElement.dataset.theme = normalized;

    const themeBtn = qs(".js-theme");
    if (themeBtn) {
      themeBtn.setAttribute("aria-pressed", normalized === "light" ? "true" : "false");
      themeBtn.textContent = normalized === "light" ? "浅色" : "深色";
    }
  };

  const toggleTheme = () => {
    const current = document.documentElement.dataset.theme === "light" ? "light" : "dark";
    const next = current === "light" ? "dark" : "light";
    applyTheme(next);
    try {
      localStorage.setItem(THEME_KEY, next);
    } catch {
      // ignore
    }
    pushToast({
      kind: "info",
      title: "主题已切换",
      message: next === "light" ? "已切换为浅色模式" : "已切换为深色模式",
      timeoutMs: 2200,
    });
  };

  applyTheme((() => {
    try {
      return localStorage.getItem(THEME_KEY) || getSystemTheme();
    } catch {
      return getSystemTheme();
    }
  })());

  qs(".js-theme")?.addEventListener("click", toggleTheme);

  const renderToday = () => {
    const now = new Date();
    const label = `${formatYmd(now)} · ${formatWeekdayZh(now)}`;
    const el = qs("[data-today-label]");
    if (el) el.textContent = label;
  };
  renderToday();

  const syncNavActive = () => {
    const hash = window.location.hash || "#overview";
    qsa(".nav a").forEach((a) => {
      a.classList.toggle("is-active", a.getAttribute("href") === hash);
    });
  };

  syncNavActive();
  window.addEventListener("hashchange", syncNavActive);
  qsa(".nav a").forEach((a) => a.addEventListener("click", () => window.setTimeout(syncNavActive, 0)));

  let currentSnapshot = null;
  let openImportPicker = null;

  const animateNumber = (
    el,
    { from, to, durationMs = 650, formatter = (v) => String(Math.round(v)) } = {},
  ) => {
    if (!el || !Number.isFinite(from) || !Number.isFinite(to)) {
      return;
    }

    const startedAt = performance.now();
    const delta = to - from;

    const tick = (now) => {
      const t = clamp((now - startedAt) / durationMs, 0, 1);
      const eased = 1 - (1 - t) ** 3;
      el.textContent = formatter(from + delta * eased);
      if (t < 1) window.requestAnimationFrame(tick);
    };

    window.requestAnimationFrame(tick);
  };

  const pickLatestReservedBookings = (bookings, limit = 3) => {
    const all = Array.isArray(bookings) ? bookings : [];
    const top = [];

    const keyOf = (b) => String(b?.created_at || b?.start_date || "");

    for (const b of all) {
      if (!b || b.status !== "reserved") continue;
      const key = keyOf(b);
      if (!key) continue;

      let inserted = false;
      for (let i = 0; i < top.length; i += 1) {
        if (key > keyOf(top[i])) {
          top.splice(i, 0, b);
          inserted = true;
          break;
        }
      }
      if (!inserted) top.push(b);
      if (top.length > limit) top.length = limit;
    }

    return top;
  };

  const computeOpsMetrics = (snapshot, todayStr) => {
    const rooms = Array.isArray(snapshot?.rooms) ? snapshot.rooms : [];
    const bookings = Array.isArray(snapshot?.bookings) ? snapshot.bookings : [];

    const activeRooms = rooms.filter((r) => r && r.status === "active").length;
    const maintenanceRooms = rooms.filter((r) => r && r.status === "maintenance").length;

    const statsRoomCount = Number(snapshot?.stats?.room_count);
    const roomDenom = activeRooms || (Number.isFinite(statsRoomCount) ? statsRoomCount : 0);

    const reserved = bookings.filter((b) => b && b.status === "reserved");

    const occupiedSet = new Set();
    for (const b of reserved) {
      const start = String(b.start_date || "");
      const end = String(b.end_date || "");
      const roomNumber = b.room_number;
      if (!start || !end || !roomNumber) continue;
      if (start <= todayStr && todayStr < end) {
        occupiedSet.add(String(roomNumber));
      }
    }

    const occupied = occupiedSet.size;
    const available = roomDenom ? Math.max(0, roomDenom - occupied) : 0;

    const arrivals = reserved.filter((b) => String(b.start_date || "") === todayStr).length;
    const departures = reserved.filter((b) => String(b.end_date || "") === todayStr).length;

    const occupancyRate = roomDenom ? occupied / roomDenom : 0;

    return {
      roomDenom,
      activeRooms,
      maintenanceRooms,
      occupied,
      available,
      arrivals,
      departures,
      occupancyRate,
    };
  };

  const computeRevenueSeries = (snapshot, days) => {
    const values = new Array(days.length).fill(0);
    const bookings = Array.isArray(snapshot?.bookings) ? snapshot.bookings : [];

    for (const b of bookings) {
      if (!b || b.status !== "reserved") continue;
      const start = String(b.start_date || "");
      const end = String(b.end_date || "");
      const price = Number(b.price_per_night_cents);
      if (!start || !end || !Number.isFinite(price)) continue;

      for (let i = 0; i < days.length; i += 1) {
        const day = days[i];
        if (start <= day && day < end) {
          values[i] += price;
        }
      }
    }

    return values;
  };

  const applyOpsSummary = (snapshot) => {
    const todayStr = formatYmd(new Date());
    const metrics = computeOpsMetrics(snapshot, todayStr);
    const percent = Math.round(metrics.occupancyRate * 100);

    const occRateEl = qs("[data-occupancy-rate]");
    if (occRateEl) {
      const prev = Number.parseInt(String(occRateEl.textContent || "").replace(/[^\d]/g, ""), 10);
      if (Number.isFinite(prev)) {
        animateNumber(occRateEl, { from: prev, to: percent, formatter: (v) => `${Math.round(v)}%` });
      } else {
        occRateEl.textContent = `${percent}%`;
      }
    }

    const occBarEl = qs("[data-occupancy-bar]");
    if (occBarEl) {
      occBarEl.style.width = `${clamp(percent, 0, 100)}%`;
    }

    const arrivalsEl = qs("[data-arrivals]");
    if (arrivalsEl) arrivalsEl.textContent = `${metrics.arrivals} 组`;

    const departuresEl = qs("[data-departures]");
    if (departuresEl) departuresEl.textContent = `${metrics.departures} 间`;

    qsa("[data-room-summary]").forEach((el) => {
      const key = el.dataset.roomSummary;
      if (key === "available") el.textContent = `${metrics.available} 间`;
      if (key === "occupied") el.textContent = `${metrics.occupied} 间`;
      if (key === "maintenance") el.textContent = `${metrics.maintenanceRooms} 间`;
    });

    return metrics;
  };

  const applyRevenueChart = (snapshot) => {
    const line = qs('[data-chart-line="revenue"]');
    const fill = qs('[data-chart-fill="revenue"]');
    if (!line || !fill) return;

    const days = [];
    for (let offset = 13; offset >= 0; offset -= 1) {
      const d = new Date();
      d.setDate(d.getDate() - offset);
      days.push(formatYmd(d));
    }

    const values = computeRevenueSeries(snapshot, days);
    const max = Math.max(...values, 1);

    const left = 10;
    const right = 390;
    const top = 40;
    const bottom = 190;
    const step = (right - left) / Math.max(1, values.length - 1);

    const points = values
      .map((v, i) => {
        const x = left + step * i;
        const y = bottom - (v / max) * (bottom - top);
        return `${x.toFixed(2)},${y.toFixed(2)}`;
      })
      .join(" ");

    line.setAttribute("points", points);
    fill.setAttribute("points", `${points} ${right},220 ${left},220`);
  };

  const downloadTextFile = (filename, content, mime = "text/plain;charset=utf-8") => {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.rel = "noopener";
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const generateDailyReportMarkdown = (snapshot) => {
    const now = new Date();
    const todayStr = formatYmd(now);
    const metrics = computeOpsMetrics(snapshot, todayStr);
    const stats = snapshot?.stats || {};

    const appVersion = snapshot?.app_version ? `v${snapshot.app_version}` : "—";
    const generatedAt = snapshot?.generated_at || "—";

    const latest = pickLatestReservedBookings(snapshot?.bookings, 3);

    const lines = [];
    lines.push(`# HotelManager 运营日报（${todayStr}）`);
    lines.push("");
    lines.push(`- 快照版本: ${appVersion}`);
    lines.push(`- 生成时间: ${generatedAt}`);
    lines.push("");
    lines.push("## 核心指标");
    lines.push(`- 房间数: ${stats.room_count ?? "--"}（active=${metrics.activeRooms}，maintenance=${metrics.maintenanceRooms}）`);
    lines.push(`- 住客数: ${stats.guest_count ?? "--"}`);
    lines.push(`- 预订总数: ${stats.booking_count ?? "--"}（reserved=${stats.reserved_booking_count ?? "--"}）`);
    lines.push("");
    lines.push("## 今日运营");
    lines.push(`- 入住率: ${Math.round(metrics.occupancyRate * 100)}%（${metrics.occupied}/${metrics.roomDenom || 0}）`);
    lines.push(`- 今日到店: ${metrics.arrivals}`);
    lines.push(`- 今日离店: ${metrics.departures}`);
    lines.push("");
    lines.push("## 最新预订（reserved）");
    if (!latest.length) {
      lines.push("- （无）");
    } else {
      latest.forEach((b) => {
        const title = `${b.room_number || "--"} · ${b.room_type || "--"}`;
        const range = `${b.start_date || "--"} - ${b.end_date || "--"}`;
        const name = b.guest_name || b.guest_email || "--";
        const amount = typeof b.total_cents === "number" ? formatCny(b.total_cents) : "—";
        lines.push(`- ${title} | ${name} | ${range} | ${amount}`);
      });
    }
    lines.push("");
    lines.push("> 说明：该日报由静态 Web UI 在本地生成，不联网。");
    lines.push("");

    return lines.join("\n");
  };

  const reportBtn = qs(".js-report");
  reportBtn?.addEventListener("click", async () => {
    if (!currentSnapshot) {
      pushToast({
        kind: "info",
        title: "尚未导入快照",
        message: "请先导入 snapshot.json，导入后可生成并导出日报。",
      });
      qs(".dropzone")?.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }

    const md = generateDailyReportMarkdown(currentSnapshot);
    const filename = `hotelmanager_daily_report_${formatYmd(new Date())}.md`;
    downloadTextFile(filename, md, "text/markdown;charset=utf-8");

    let copied = false;
    try {
      await navigator.clipboard.writeText(md);
      copied = true;
    } catch {
      // ignore (file:// may not allow clipboard)
    }

    pushToast({
      kind: "success",
      title: "日报已生成",
      message: copied ? `已下载并复制到剪贴板：${filename}` : `已下载：${filename}`,
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.defaultPrevented) return;
    if (event.ctrlKey || event.metaKey || event.altKey) return;

    const target = event.target;
    if (
      target instanceof HTMLElement &&
      (target.isContentEditable || ["input", "textarea", "select"].includes(target.tagName.toLowerCase()))
    ) {
      return;
    }

    const key = String(event.key || "").toLowerCase();
    if (key === "i") {
      if (openImportPicker) {
        openImportPicker();
      } else {
        pushToast({ kind: "info", title: "导入快照", message: "未检测到导入区域（dropzone）。" });
      }
    }
    if (key === "t") {
      toggleTheme();
    }
    if (key === "g") {
      reportBtn?.click();
    }
  });

  const palette = ["#7c9dff", "#7ef1d6", "#ffb86b", "#ffffff"];

  const spawnConfetti = (anchor) => {
    const layer = anchor.querySelector(".confetti-layer") || anchor;
    for (let i = 0; i < 16; i += 1) {
      const piece = document.createElement("span");
      piece.className = "confetti";
      piece.style.left = `${Math.random() * 90 + 5}%`;
      piece.style.background = palette[i % palette.length];
      piece.style.animationDelay = `${Math.random() * 0.15}s`;
      layer.appendChild(piece);
      setTimeout(() => piece.remove(), 1200);
    }
  };

  document.querySelectorAll(".js-confetti").forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.classList.remove("shimmer");
      void btn.offsetWidth;
      btn.classList.add("shimmer");
      const card = btn.closest(".card") || document.body;
      spawnConfetti(card);
    });
  });

  const dropzone = document.querySelector(".dropzone");
  if (dropzone) {
    const importCard = dropzone.closest(".card") || document.body;

    const defaultText = dropzone.dataset.default || dropzone.textContent;
    const activeText = dropzone.dataset.active || "松开即可导入";

    const fileInput = importCard.querySelector(".file-input");
    const statusEl = importCard.querySelector("[data-import-status]");
    const importButtons = document.querySelectorAll(".js-import");

    openImportPicker = () => fileInput?.click();

    const setStatus = (kind, message) => {
      if (statusEl) {
        statusEl.textContent = message;
      }
      dropzone.classList.toggle("is-success", kind === "success");
      dropzone.classList.toggle("is-error", kind === "error");
    };

    const setActive = (active) => {
      dropzone.classList.toggle("is-dragging", active);
      dropzone.textContent = active ? activeText : defaultText;
    };

    const validateSnapshot = (data) => {
      if (!data || typeof data !== "object") {
        throw new Error("文件不是有效的 JSON 对象");
      }

      if (data.schema_version !== 1) {
        throw new Error(`不支持的 schema_version：${String(data.schema_version)}`);
      }

      if (!data.stats || typeof data.stats !== "object") {
        throw new Error("快照缺少 stats 字段");
      }

      for (const key of [
        "room_count",
        "guest_count",
        "booking_count",
        "reserved_booking_count",
      ]) {
        if (typeof data.stats[key] !== "number") {
          throw new Error(`stats.${key} 必须为 number`);
        }
      }

      for (const key of ["rooms", "guests", "bookings"]) {
        if (!Array.isArray(data[key])) {
          throw new Error(`${key} 必须为数组`);
        }
      }
    };

    const applySnapshot = (snapshot) => {
      currentSnapshot = snapshot;

      const stats = snapshot.stats || {};
      const kpiMap = {
        room_count: stats.room_count,
        guest_count: stats.guest_count,
        booking_count: stats.booking_count,
        reserved_booking_count: stats.reserved_booking_count,
      };

      document.querySelectorAll("[data-kpi]").forEach((el) => {
        const key = el.dataset.kpi;
        if (!key) return;
        const value = kpiMap[key];
        if (typeof value !== "number") {
          el.textContent = "--";
          return;
        }
        const prev = Number.parseInt(String(el.textContent || ""), 10);
        if (Number.isFinite(prev)) {
          animateNumber(el, { from: prev, to: value });
        } else {
          el.textContent = String(value);
        }
      });

      const list = document.querySelector('[data-booking-list="latest"]');
      if (list) {
        const all = Array.isArray(snapshot.bookings) ? snapshot.bookings : [];
        const latest = pickLatestReservedBookings(all, 3);

        list.innerHTML = "";
        if (!latest.length) {
          const li = document.createElement("li");
          li.className = "booking-item";
          li.innerHTML =
            '<div class="booking-meta"><strong>暂无预订</strong><span>快照中没有 reserved 状态的预订</span></div><span class="badge muted">空</span>';
          list.appendChild(li);
        } else {
          latest.forEach((b) => {
            const li = document.createElement("li");
            li.className = "booking-item";

            const title = `${b.room_number || "--"} · ${b.room_type || "--"}`;
            const nights = typeof b.nights === "number" ? b.nights : "--";
            const range = `${b.start_date || "--"} - ${b.end_date || "--"}`;
            const subtitle = `${b.guest_name || "--"} · ${nights} 晚 · ${range}`;
            const amount = typeof b.total_cents === "number" ? formatCny(b.total_cents) : "—";

            const badgeClass = typeof b.total_cents === "number" ? "success" : "muted";

            const metaEl = document.createElement("div");
            metaEl.className = "booking-meta";
            const strong = document.createElement("strong");
            strong.textContent = title;
            const span = document.createElement("span");
            span.textContent = subtitle;
            metaEl.appendChild(strong);
            metaEl.appendChild(span);

            const badgeEl = document.createElement("span");
            badgeEl.className = `badge ${badgeClass}`;
            badgeEl.textContent = amount;

            li.appendChild(metaEl);
            li.appendChild(badgeEl);
            list.appendChild(li);
          });
        }
      }

      applyOpsSummary(snapshot);
      applyRevenueChart(snapshot);

      const meta = [
        snapshot.app_version ? `v${snapshot.app_version}` : null,
        snapshot.generated_at ? `生成时间 ${snapshot.generated_at}` : null,
      ]
        .filter(Boolean)
        .join(" · ");
      setStatus("success", meta ? `已导入快照（${meta}）` : "已导入快照");
      pushToast({
        kind: "success",
        title: "快照已导入",
        message: meta ? `已导入（${meta}）` : "已导入快照",
        timeoutMs: 3600,
      });

      spawnConfetti(importCard);
    };

    const handleFile = (file) => {
      if (!file) return;
      setStatus("info", `正在解析：${file.name}…`);
      dropzone.classList.remove("is-success", "is-error");

      const reader = new FileReader();
      reader.onload = () => {
        try {
          const text = String(reader.result || "");
          const parsed = JSON.parse(text);
          validateSnapshot(parsed);
          applySnapshot(parsed);
        } catch (err) {
          const msg = err instanceof Error ? err.message : "导入失败：未知错误";
          setStatus("error", `导入失败：${msg}`);
          pushToast({ kind: "error", title: "导入失败", message: msg, timeoutMs: 5200 });
        }
      };
      reader.onerror = () => {
        setStatus("error", "导入失败：无法读取文件");
        pushToast({ kind: "error", title: "导入失败", message: "无法读取文件", timeoutMs: 5200 });
      };
      reader.readAsText(file);
    };

    ["dragenter", "dragover"].forEach((evt) => {
      dropzone.addEventListener(evt, (event) => {
        event.preventDefault();
        setActive(true);
      });
    });

    ["dragleave", "drop"].forEach((evt) => {
      dropzone.addEventListener(evt, (event) => {
        event.preventDefault();
        setActive(false);
      });
    });

    dropzone.addEventListener("drop", (event) => {
      const files = event.dataTransfer?.files;
      if (files && files.length > 0) {
        handleFile(files[0]);
      }
    });

    dropzone.addEventListener("click", () => {
      openImportPicker?.();
    });

    dropzone.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openImportPicker?.();
      }
    });

    fileInput?.addEventListener("change", () => {
      const file = fileInput.files?.[0];
      if (file) handleFile(file);
      fileInput.value = "";
    });

    importButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        openImportPicker?.();
      });
    });
  }
})();
