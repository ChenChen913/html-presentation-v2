/* ============================================================
   mdshow :: runtime — 放映交互
   键盘 ←/→/空格 翻页 + 右下角页码（构建时静态生成）
   O 总览网格 / F 全屏 / Esc 退出
   点击左右半屏翻页 + 触屏滑动
   分步显示：列表项/金句卡按 fragment 逐条浮现
   ============================================================ */
(function () {
  "use strict";

  var stage = document.getElementById("stage");
  var viewport = document.getElementById("viewport");
  var slides = Array.prototype.slice.call(document.querySelectorAll(".slide"));
  var N = slides.length;
  var frags = slides.map(function (s) {
    return Array.prototype.slice.call(s.querySelectorAll(".fragment"));
  });

  var cur = 0;      // 当前页下标
  var shown = 0;    // 当前页已显示的 fragment 数
  var overview = false;

  function apply() {
    slides.forEach(function (s, i) {
      s.classList.toggle("active", i === cur);
      s.classList.toggle("current", i === cur);
    });
    frags[cur].forEach(function (f, i) {
      f.classList.toggle("shown", i < shown);
    });
    try { history.replaceState(null, "", "#/" + (cur + 1)); } catch (e) { /* file:// 下可能受限 */ }
  }

  function next() {
    if (shown < frags[cur].length) { shown++; apply(); }
    else if (cur < N - 1) { cur++; shown = 0; apply(); }
  }

  function prev() {
    if (shown > 0) { shown--; apply(); }
    else if (cur > 0) { cur--; shown = frags[cur].length; apply(); }
  }

  function jump(i) {
    cur = Math.max(0, Math.min(N - 1, i));
    shown = frags[cur].length;   // 跳转落地时展示整页
    apply();
  }

  /* ---------- 等比缩放 1280x720 -> 视口 ---------- */
  function fit() {
    if (overview) { layoutOverview(); return; }
    var s = Math.min(window.innerWidth / 1280, window.innerHeight / 720);
    stage.style.transform = "scale(" + s + ")";
  }
  window.addEventListener("resize", fit);

  /* ---------- 总览模式 ---------- */
  function layoutOverview() {
    var vw = window.innerWidth, vh = window.innerHeight;
    var cols = Math.ceil(Math.sqrt(N));
    var rows = Math.ceil(N / cols);
    var cw = vw / cols, ch = vh / rows;
    var s = Math.min(cw / 1280, ch / 720) * 0.86;
    slides.forEach(function (el, i) {
      var c = i % cols, r = Math.floor(i / cols);
      var x = c * cw + (cw - 1280 * s) / 2;
      var y = r * ch + (ch - 720 * s) / 2;
      el.style.transform = "translate(" + x + "px," + y + "px) scale(" + s + ")";
    });
  }

  function setOverview(on) {
    overview = on;
    document.body.classList.toggle("overview", on);
    if (on) {
      stage.style.transform = "none";
      layoutOverview();
    } else {
      slides.forEach(function (el) { el.style.transform = ""; });
      fit();
    }
  }

  /* ---------- 全屏 ---------- */
  function toggleFullscreen() {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen();
    }
  }

  /* ---------- 键盘 ---------- */
  document.addEventListener("keydown", function (e) {
    var k = e.key;
    if (k === "ArrowRight" || k === "ArrowDown" || k === " " || k === "PageDown" || k === "Enter") {
      e.preventDefault();
      if (overview) { setOverview(false); } else { next(); }
    } else if (k === "ArrowLeft" || k === "ArrowUp" || k === "PageUp") {
      e.preventDefault();
      if (overview) { setOverview(false); } else { prev(); }
    } else if (k === "Home") {
      if (overview) { setOverview(false); }
      cur = 0; shown = 0; apply();
    } else if (k === "End") {
      if (overview) { setOverview(false); }
      jump(N - 1);
    } else if (k === "o" || k === "O") {
      setOverview(!overview);
    } else if (k === "f" || k === "F") {
      toggleFullscreen();
    } else if (k === "Escape") {
      if (overview) { setOverview(false); }
    }
  });

  /* ---------- 点击左右半屏翻页 ---------- */
  viewport.addEventListener("click", function (e) {
    if (overview) { return; }                 // 总览由 slide 自己的点击处理
    if (e.target.closest && e.target.closest("a")) { return; }   // 链接放行
    var ratio = e.clientX / window.innerWidth;
    if (ratio < 0.3) { prev(); } else { next(); }
  });

  /* ---------- 总览里点击某页跳转 ---------- */
  slides.forEach(function (el, i) {
    el.addEventListener("click", function (e) {
      if (!overview) { return; }
      e.stopPropagation();
      setOverview(false);
      jump(i);
    });
  });

  /* ---------- 触屏滑动 ---------- */
  var touchX = null, touchY = null;
  document.addEventListener("touchstart", function (e) {
    touchX = e.touches[0].clientX;
    touchY = e.touches[0].clientY;
  }, { passive: true });
  document.addEventListener("touchend", function (e) {
    if (touchX === null) { return; }
    var dx = e.changedTouches[0].clientX - touchX;
    var dy = e.changedTouches[0].clientY - touchY;
    if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) {
      if (dx < 0) { next(); } else { prev(); }
    }
    touchX = touchY = null;
  }, { passive: true });

  /* ---------- 初始化：支持 #/3 式页码定位 ---------- */
  var m = (location.hash || "").match(/^#\/(\d+)/);
  if (m) { cur = Math.max(0, Math.min(N - 1, parseInt(m[1], 10) - 1)); }
  shown = frags[cur].length;
  fit();
  apply();

  setTimeout(function () {
    var h = document.getElementById("helpbar");
    if (h) { h.classList.add("fade"); }
  }, 4000);
})();
