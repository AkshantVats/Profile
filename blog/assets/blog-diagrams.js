/**
 * Theme-aware Mermaid for blog posts. Call after mermaid.min.js loads.
 * Re-renders on #theme-toggle so diagrams stay readable in light and dark.
 */
(function () {
  var LIGHT_TEXT = "#242424";
  var DARK_TEXT = "#ececea";

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
        primaryTextColor: DARK_TEXT,
        primaryBorderColor: "#5bd37a",
        secondaryColor: "#1a2744",
        secondaryTextColor: DARK_TEXT,
        secondaryBorderColor: "#93c5fd",
        tertiaryColor: "#3d3420",
        tertiaryTextColor: DARK_TEXT,
        tertiaryBorderColor: "#fbbf24",
        lineColor: "#a8a89e",
        textColor: DARK_TEXT,
        nodeTextColor: DARK_TEXT,
        titleColor: DARK_TEXT,
        edgeLabelBackground: "#171716",
        clusterBkg: "#1f1f1e",
        clusterBorder: "#7c7c74",
        actorBorder: "#a8a89e",
        actorBkg: "#1e3328",
        actorTextColor: DARK_TEXT,
        signalColor: "#a8a89e",
        labelBoxBkgColor: "#1e3328",
        labelBoxBorderColor: "#5bd37a",
        labelTextColor: DARK_TEXT,
        noteBkgColor: "#3d3420",
        noteTextColor: DARK_TEXT,
        noteBorderColor: "#fbbf24",
      };
    }
    return {
      background: "transparent",
      mainBkg: "transparent",
      secondBkg: "transparent",
      tertiaryBkg: "transparent",
      primaryColor: "#ecfdf5",
      primaryTextColor: LIGHT_TEXT,
      primaryBorderColor: "#059669",
      secondaryColor: "#f0f4ff",
      secondaryTextColor: LIGHT_TEXT,
      secondaryBorderColor: "#2563eb",
      tertiaryColor: "#fef3c7",
      tertiaryTextColor: LIGHT_TEXT,
      tertiaryBorderColor: "#d97706",
      lineColor: "#6b6b6b",
      textColor: LIGHT_TEXT,
      nodeTextColor: LIGHT_TEXT,
      titleColor: LIGHT_TEXT,
      edgeLabelBackground: "#ffffff",
      clusterBkg: "#f6f6f4",
      clusterBorder: "#757575",
      actorBorder: "#6b6b6b",
      actorBkg: "#ecfdf5",
      actorTextColor: LIGHT_TEXT,
      signalColor: "#6b6b6b",
      labelBoxBkgColor: "#ecfdf5",
      labelBoxBorderColor: "#059669",
      labelTextColor: LIGHT_TEXT,
      noteBkgColor: "#fef3c7",
      noteTextColor: LIGHT_TEXT,
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
        el.innerHTML = "";
        el.textContent = el.dataset.mermaidSrc;
        el.removeAttribute("data-processed");
      }
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
      var computed = window.getComputedStyle(el).fill;
      return parseCssColor(computed);
    } catch (_e) {
      return null;
    }
  }

  function textColorForFill(fillColor) {
    var rgb = parseCssColor(fillColor);
    if (!rgb) return isDark() ? DARK_TEXT : LIGHT_TEXT;
    return relativeLuminance(rgb.r, rgb.g, rgb.b) > 0.55 ? LIGHT_TEXT : DARK_TEXT;
  }

  function setLabelColor(labelEl, color) {
    labelEl.style.setProperty("fill", color, "important");
    labelEl.style.setProperty("color", color, "important");
    labelEl.setAttribute("fill", color);
    labelEl.querySelectorAll("span, p, div").forEach(function (child) {
      child.style.setProperty("color", color, "important");
    });
  }

  function applyTextColorToGroup(group, fillColor) {
    var textColor = fillColor ? textColorForFill(fillColor) : isDark() ? DARK_TEXT : LIGHT_TEXT;
    group.querySelectorAll("text, tspan").forEach(function (t) {
      setLabelColor(t, textColor);
    });
    group.querySelectorAll("foreignObject").forEach(function (fo) {
      fo.style.setProperty("color", textColor, "important");
      fo.querySelectorAll(".nodeLabel, .label, span, p, div").forEach(function (el) {
        el.style.setProperty("color", textColor, "important");
      });
    });
  }

  function shapeFill(group) {
    var shape = group.querySelector("rect, polygon, circle, ellipse, path");
    var fill = colorFromElement(shape);
    if (fill) return fill;
    var cluster = group.closest(".cluster");
    if (cluster && cluster !== group) {
      return shapeFill(cluster);
    }
    return null;
  }

  function applyReadabilityOverrides() {
    var vars = themeVariables();
    var fallbackText = vars.nodeTextColor || vars.textColor || LIGHT_TEXT;
    var line = vars.lineColor || "#6b6b6b";

    document.querySelectorAll(".prose .mermaid svg").forEach(function (svg) {
      svg.querySelectorAll(".node, .cluster").forEach(function (group) {
        var fill = shapeFill(group);
        applyTextColorToGroup(
          group,
          fill ? "rgb(" + fill.r + "," + fill.g + "," + fill.b + ")" : null
        );
      });

      svg.querySelectorAll(".edgeLabel").forEach(function (labelGroup) {
        var bg = labelGroup.querySelector("rect, polygon");
        var bgFill = colorFromElement(bg);
        if (bgFill) {
          applyTextColorToGroup(
            labelGroup,
            "rgb(" + bgFill.r + "," + bgFill.g + "," + bgFill.b + ")"
          );
        }
      });

      svg.querySelectorAll("text").forEach(function (t) {
        var parentNode = t.closest(".node, .cluster, .edgeLabel");
        if (parentNode) return;
        var styleAttr = t.getAttribute("style") || "";
        if (!styleAttr.includes("fill") && !t.hasAttribute("fill")) {
          t.style.fill = fallbackText;
        }
      });

      svg.querySelectorAll("[stroke]").forEach(function (el) {
        var styleAttr = el.getAttribute("style") || "";
        if (!styleAttr.includes("stroke")) {
          el.style.stroke = line;
        }
      });
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
      flowchart: { htmlLabels: false },
      sequence: { useMaxWidth: true },
    });
    var nodes = document.querySelectorAll("pre.mermaid");
    if (nodes.length) {
      await mermaid.run({ nodes: nodes });
    }

    applyReadabilityOverrides();
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
