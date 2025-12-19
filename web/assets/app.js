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
    const defaultText = dropzone.dataset.default || dropzone.textContent;
    const activeText = dropzone.dataset.active || "松开即可导入";

    const setActive = (active) => {
      dropzone.classList.toggle("is-dragging", active);
      dropzone.textContent = active ? activeText : defaultText;
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
  }
})();
