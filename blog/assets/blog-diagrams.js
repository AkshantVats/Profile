/**
 * Theme-aware Mermaid for blog posts. Call after mermaid.min.js loads.
 * Gold standard: blog/DIAGRAM-STYLE.md — Day 11 diagram 2.
 */
(function () {
  var ACCENT_FILL = "#fef3c7";
  var ACCENT_TEXT = "#111827";
  var ACCENT_RGB = { r: 254, g: 243, b: 199 };

  var LIGHT_VARS = {
    darkMode: false,
    background: "transparent",
    mainBkg: "transparent",
    secondBkg: "transparent",
    tertiaryBkg: "transparent",
    primaryColor: "#ffffff",
    primaryTextColor: "#111827",
    primaryBorderColor: "#059669",
    secondaryColor: "#f0f4ff",
    secondaryTextColor: "#111827",
    secondaryBorderColor: "#2563eb",
    tertiaryColor: ACCENT_FILL,
    tertiaryTextColor: ACCENT_TEXT,
    tertiaryBorderColor: "#d97706",
    lineColor: "#059669",
    textColor: "#242424",
    nodeTextColor: "#111827",
    titleColor: "#242424",
    edgeLabelBackground: "#ffffff",
    clusterBkg: "#f6f6f4",
    clusterBorder: "#757575",
    actorBorder: "#059669",
    actorBkg: "#ffffff",
    actorTextColor: "#111827",
    signalColor: "#059669",
    labelBoxBkgColor: "#ffffff",
    labelBoxBorderColor: "#059669",
    labelTextColor: "#111827",
    noteBkgColor: ACCENT_FILL,
    noteTextColor: ACCENT_TEXT,
    noteBorderColor: "#d97706",
  };

  var DARK_VARS = {
    darkMode: true,
    background: "transparent",
    mainBkg: "transparent",
    secondBkg: "transparent",
    tertiaryBkg: "transparent",
    primaryColor: "#1e3328",
    primaryTextColor: "#ececea",
    primaryBorderColor: "#059669",
    secondaryColor: "#1a2744",
    secondaryTextColor: "#ececea",
    secondaryBorderColor: "#60a5fa",
    tertiaryColor: ACCENT_FILL,
    tertiaryTextColor: ACCENT_TEXT,
    tertiaryBorderColor: "#d97706",
    lineColor: "#059669",
    textColor: "#ececea",
    nodeTextColor: "#ececea",
    titleColor: "#ececea",
    edgeLabelBackground: "#171716",
    clusterBkg: "#1f1f1e",
    clusterBorder: "#7c7c74",
    actorBorder: "#059669",
    actorBkg: "#1e3328",
    actorTextColor: "#ececea",
    signalColor: "#059669",
    labelBoxBkgColor: "#1e3328",
    labelBoxBorderColor: "#059669",
    labelTextColor: "#ececea",
    noteBkgColor: ACCENT_FILL,
    noteTextColor: ACCENT_TEXT,
    noteBorderColor: "#d97706",
  };

  var DARK_CLASSDEF_REPLACEMENTS = [
    [
      /classDef pipeline fill:#ffffff,stroke:#059669,color:#111827/g,
      "classDef pipeline fill:#1e3328,stroke:#059669,color:#ececea",
    ],
    [
      /classDef exact fill:#ecfdf5,stroke:#059669,color:#111827/g,
      "classDef exact fill:#1e3328,stroke:#059669,color:#ececea",
    ],
    [
      /classDef semantic fill:#f0f4ff,stroke:#2563eb,color:#111827/g,
      "classDef semantic fill:#1a2744,stroke:#60a5fa,color:#ececea",
    ],
    [
      /style ([A-Za-z0-9_-]+) fill:#fef3c7,stroke:#d97706,color:#111827/g,
      "style $1 fill:#5b3b12,stroke:#f59e0b,color:#ececea",
    ],
  ];

  function decodeHtmlEntities(str) {
    if (!str || str.indexOf("&") === -1) return str;
    var el = document.createElement("textarea");
    el.innerHTML = str;
    return el.value;
  }

  function normalizeMermaidSource(src) {
    return decodeHtmlEntities(src);
  }

  function isDark() {
    return document.documentElement.getAttribute("data-theme") === "dark";
  }

  function themeVariables() {
    return isDark() ? DARK_VARS : LIGHT_VARS;
  }

  function adaptSourceForTheme(src) {
    if (!isDark()) return src;
    var out = src;
    DARK_CLASSDEF_REPLACEMENTS.forEach(function (pair) {
      out = out.replace(pair[0], pair[1]);
    });
    return out;
  }

  function stashSources() {
    document.querySelectorAll("pre.mermaid").forEach(function (el) {
      if (!el.dataset.mermaidSrc) {
        el.dataset.mermaidSrc = normalizeMermaidSource(el.textContent.trim());
      }
    });
  }

  function prepareSourcesForRender() {
    document.querySelectorAll("pre.mermaid").forEach(function (el) {
      if (!el.dataset.mermaidSrc) {
        el.dataset.mermaidSrc = normalizeMermaidSource(el.textContent.trim());
      }
      var src = adaptSourceForTheme(normalizeMermaidSource(el.dataset.mermaidSrc));
      el.innerHTML = "";
      el.textContent = src;
      el.removeAttribute("data-processed");
    });
  }

  function parseHex(hex) {
    var h = hex.replace("#", "");
    if (h.length === 3) {
      h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
    }
    if (h.length !== 6) return null;
    return {
      r: parseInt(h.slice(0, 2), 16),
      g: parseInt(h.slice(2, 4), 16),
      b: parseInt(h.slice(4, 6), 16),
    };
  }

  function relativeLuminance(r, g, b) {
    var srgb = [r, g, b].map(function (c) {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * srgb[0] + 0.7152 * srgb[1] + 0.0722 * srgb[2];
  }

  function parseCssColor(value) {
    if (!value || value === "none" || value === "transparent") return null;
    var v = value.trim().toLowerCase();
    if (v.startsWith("#")) return parseHex(v);
    var rgb = v.match(/^rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)(?:\s*,\s*([\d.]+))?/);
    if (rgb) {
      var alpha = rgb[4] !== undefined ? parseFloat(rgb[4]) : 1;
      if (alpha <= 0) return null;
      return {
        r: Math.round(parseFloat(rgb[1])),
        g: Math.round(parseFloat(rgb[2])),
        b: Math.round(parseFloat(rgb[3])),
      };
    }
    return null;
  }

  function colorFromElement(el) {
    if (!el) return null;
    var style = el.getAttribute("style") || "";
    var styleFill = style.match(/(?:^|;)\s*fill\s*:\s*([^;]+)/i);
    if (styleFill) return parseCssColor(styleFill[1]);
    var attrFill = el.getAttribute("fill");
    if (attrFill) return parseCssColor(attrFill);
    try {
      return parseCssColor(window.getComputedStyle(el).fill);
    } catch (_e) {
      return null;
    }
  }

  function shapeFill(group) {
    var shapes = group.querySelectorAll("rect, polygon, circle, ellipse, path");
    var best = null;
    var bestLum = -1;
    shapes.forEach(function (shape) {
      var fill = colorFromElement(shape);
      if (!fill) return;
      var lum = relativeLuminance(fill.r, fill.g, fill.b);
      if (lum > bestLum) {
        bestLum = lum;
        best = fill;
      }
    });
    return best;
  }

  function setLabelColor(labelEl, color) {
    labelEl.style.setProperty("fill", color, "important");
    labelEl.setAttribute("fill", color);
    labelEl.style.setProperty("color", color, "important");
    labelEl.setAttribute("color", color);
  }

  function labelNodesForContrast() {
    var LIGHT_TEXT = "#ececea";
    var DARK_TEXT = "#111827";
    var LUMINANCE_THRESHOLD = 0.52;
    document.querySelectorAll(".prose .mermaid svg .node").forEach(function (group) {
      var fill = shapeFill(group);
      if (!fill) return;
      var lum = relativeLuminance(fill.r, fill.g, fill.b);
      var textColor = lum >= LUMINANCE_THRESHOLD ? DARK_TEXT : LIGHT_TEXT;

      group.querySelectorAll("text, tspan, .nodeLabel").forEach(function (t) {
        setLabelColor(t, textColor);
      });

      group.querySelectorAll("foreignObject").forEach(function (fo) {
        fo.querySelectorAll("div, span, p").forEach(function (el) {
          el.style.setProperty("color", textColor, "important");
          el.style.setProperty("fill", textColor, "important");
        });
      });
    });
  }

  function fixSvgEntityLabels() {
    document.querySelectorAll(".prose .mermaid svg text, .prose .mermaid svg tspan").forEach(function (el) {
      var t = el.textContent;
      if (!t || t.indexOf("&") === -1) return;
      var decoded = decodeHtmlEntities(t);
      if (decoded !== t) {
        el.textContent = decoded;
      }
    });
  }

  async function renderBlogMermaid() {
    if (typeof mermaid === "undefined") return;
    stashSources();
    prepareSourcesForRender();
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "loose",
      theme: "base",
      themeVariables: themeVariables(),
      flowchart: { htmlLabels: false },
      sequence: { useMaxWidth: true },
    });
    var nodes = document.querySelectorAll("pre.mermaid");
    if (nodes.length) {
      await mermaid.run({ nodes: nodes });
    }
    fixSvgEntityLabels();
    labelNodesForContrast();
    requestAnimationFrame(function () {
      fixSvgEntityLabels();
      labelNodesForContrast();
    });
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
