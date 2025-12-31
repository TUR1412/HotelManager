(() => {
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

    const formatCny = (cents) => {
      const n = Number(cents);
      if (!Number.isFinite(n)) return "--";
      return `¥ ${new Intl.NumberFormat("zh-CN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(n / 100)}`;
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
        el.textContent = typeof value === "number" ? String(value) : "--";
      });

      const list = document.querySelector('[data-booking-list="latest"]');
      if (list) {
        const all = Array.isArray(snapshot.bookings) ? snapshot.bookings : [];
        const latest = all
          .filter((b) => b && b.status === "reserved")
          .sort((a, b) => String(b.created_at || "").localeCompare(String(a.created_at || "")))
          .slice(0, 3);

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

      const meta = [
        snapshot.app_version ? `v${snapshot.app_version}` : null,
        snapshot.generated_at ? `生成时间 ${snapshot.generated_at}` : null,
      ]
        .filter(Boolean)
        .join(" · ");
      setStatus("success", meta ? `已导入快照（${meta}）` : "已导入快照");

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
        }
      };
      reader.onerror = () => {
        setStatus("error", "导入失败：无法读取文件");
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
      fileInput?.click();
    });

    dropzone.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        fileInput?.click();
      }
    });

    fileInput?.addEventListener("change", () => {
      const file = fileInput.files?.[0];
      if (file) handleFile(file);
      fileInput.value = "";
    });

    importButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        fileInput?.click();
      });
    });
  }
})();
