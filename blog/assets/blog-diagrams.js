/**
 * Theme-aware Mermaid for blog posts. Call after mermaid.min.js loads.
 * Re-renders on #theme-toggle so diagrams stay readable in light and dark.
 */
(function () {
  function isDark() {
    return document.documentElement.getAttribute("data-theme") === "dark";
  }

  function themeVariables() {
    if (isDark()) {
      return {
        background: "transparent",
        mainBkg: "transparent",
        secondBkg: "transparent",
        tertiaryBkg: "transparent",
        primaryColor: "#1e3328",
        primaryTextColor: "#ececea",
        primaryBorderColor: "#5bd37a",
        secondaryColor: "#1a2744",
        secondaryTextColor: "#ececea",
        secondaryBorderColor: "#93c5fd",
        tertiaryColor: "#3d3420",
        tertiaryTextColor: "#ececea",
        tertiaryBorderColor: "#fbbf24",
        lineColor: "#a8a89e",
        textColor: "#ececea",
        nodeTextColor: "#ececea",
        titleColor: "#ececea",
        edgeLabelBackground: "#171716",
        clusterBkg: "#1f1f1e",
        clusterBorder: "#7c7c74",
        actorBorder: "#a8a89e",
        actorBkg: "#1e3328",
        actorTextColor: "#ececea",
        signalColor: "#a8a89e",
        labelBoxBkgColor: "#1e3328",
        labelBoxBorderColor: "#5bd37a",
        labelTextColor: "#ececea",
        noteBkgColor: "#3d3420",
        noteTextColor: "#ececea",
        noteBorderColor: "#fbbf24",
      };
    }
    return {
      background: "transparent",
      mainBkg: "transparent",
      secondBkg: "transparent",
      tertiaryBkg: "transparent",
      primaryColor: "#ecfdf5",
      primaryTextColor: "#242424",
      primaryBorderColor: "#059669",
      secondaryColor: "#f0f4ff",
      secondaryTextColor: "#242424",
      secondaryBorderColor: "#2563eb",
      tertiaryColor: "#fef3c7",
      tertiaryTextColor: "#242424",
      tertiaryBorderColor: "#d97706",
      lineColor: "#6b6b6b",
      textColor: "#242424",
      nodeTextColor: "#242424",
      titleColor: "#242424",
      edgeLabelBackground: "#ffffff",
      clusterBkg: "#f6f6f4",
      clusterBorder: "#757575",
      actorBorder: "#6b6b6b",
      actorBkg: "#ecfdf5",
      actorTextColor: "#242424",
      signalColor: "#6b6b6b",
      labelBoxBkgColor: "#ecfdf5",
      labelBoxBorderColor: "#059669",
      labelTextColor: "#242424",
      noteBkgColor: "#fef3c7",
      noteTextColor: "#242424",
      noteBorderColor: "#d97706",
    };
  }

  function stashSources() {
    document.querySelectorAll("pre.mermaid").forEach(function (el) {
      if (!el.dataset.mermaidSrc) {
        el.dataset.mermaidSrc = el.textContent.trim();
      }
    });
  }

  function restoreSources() {
    document.querySelectorAll("pre.mermaid").forEach(function (el) {
      if (el.dataset.mermaidSrc) {
        el.textContent = el.dataset.mermaidSrc;
        el.removeAttribute("data-processed");
      }
    });
  }

  async function renderBlogMermaid() {
    if (typeof mermaid === "undefined") return;
    stashSources();
    restoreSources();
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "loose",
      theme: "base",
      themeVariables: themeVariables(),
    });
    var nodes = document.querySelectorAll("pre.mermaid");
    if (nodes.length) {
      await mermaid.run({ nodes: nodes });
    }
  }

  window.renderBlogMermaid = renderBlogMermaid;

  function onReady() {
    renderBlogMermaid();
    var btn = document.getElementById("theme-toggle");
    if (btn) {
      btn.addEventListener("click", function () {
        setTimeout(renderBlogMermaid, 0);
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onReady);
  } else {
    onReady();
  }
})();
