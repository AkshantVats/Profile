/**
 * Theme-aware Mermaid for blog posts. Call after mermaid.min.js loads.
 * Gold standard: blog/DIAGRAM-STYLE.md — light node fills, green stroke, dark labels in both themes.
 */
(function () {
  var NODE_TEXT = "#111827";
  var NODE_TEXT_ALT = "#242424";
  var PAGE_TEXT_LIGHT = "#242424";
  var PAGE_TEXT_DARK = "#ececea";
  var LUMINANCE_LIGHT_FILL = 0.55;

  function isDark() {
    return document.documentElement.getAttribute("data-theme") === "dark";
  }

  function themeVariables() {
    var pageText = isDark() ? PAGE_TEXT_DARK : PAGE_TEXT_LIGHT;
    var line = isDark() ? "#a8a89e" : "#6b6b6b";
    var nodeBkg = isDark() ? "#1e3328" : "#ecfdf5";
    var nodeText = isDark() ? PAGE_TEXT_DARK : NODE_TEXT;
    return {
      background: "transparent",
      mainBkg: "transparent",
      secondBkg: "transparent",
      tertiaryBkg: "transparent",
      primaryColor: nodeBkg,
      primaryTextColor: nodeText,
      primaryBorderColor: "#059669",
      secondaryColor: isDark() ? "#1a2744" : "#f0f4ff",
      secondaryTextColor: nodeText,
      secondaryBorderColor: "#2563eb",
      tertiaryColor: "#fef3c7",
      tertiaryTextColor: NODE_TEXT,
      tertiaryBorderColor: "#d97706",
      lineColor: line,
      textColor: pageText,
      nodeTextColor: nodeText,
      titleColor: pageText,
      edgeLabelBackground: isDark() ? "#171716" : "#ffffff",
      clusterBkg: isDark() ? "#1f1f1e" : "#f6f6f4",
      clusterBorder: isDark() ? "#7c7c74" : "#757575",
      actorBorder: line,
      actorBkg: nodeBkg,
      actorTextColor: nodeText,
      signalColor: line,
      labelBoxBkgColor: nodeBkg,
      labelBoxBorderColor: "#059669",
      labelTextColor: nodeText,
      noteBkgColor: "#fef3c7",
      noteTextColor: NODE_TEXT,
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

  function isLightFill(rgb) {
    return relativeLuminance(rgb.r, rgb.g, rgb.b) > LUMINANCE_LIGHT_FILL;
  }

  function textColorForFill(fillColor) {
    var rgb = parseCssColor(fillColor);
    if (!rgb) return isDark() ? PAGE_TEXT_DARK : PAGE_TEXT_LIGHT;
    return isLightFill(rgb) ? NODE_TEXT : isDark() ? PAGE_TEXT_DARK : PAGE_TEXT_LIGHT;
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
    var textColor = fillColor
      ? textColorForFill(fillColor)
      : isDark()
        ? PAGE_TEXT_DARK
        : PAGE_TEXT_LIGHT;
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
    if (best) return best;
    var cluster = group.closest(".cluster");
    if (cluster && cluster !== group) {
      return shapeFill(cluster);
    }
    return null;
  }

  function applyReadabilityOverrides() {
    var vars = themeVariables();
    var fallbackText = vars.textColor || PAGE_TEXT_LIGHT;
    var line = vars.lineColor || "#6b6b6b";

    document.querySelectorAll(".prose .mermaid svg").forEach(function (svg) {
      svg.querySelectorAll(".node").forEach(function (group) {
        var fill = shapeFill(group);
        applyTextColorToGroup(
          group,
          fill ? "rgb(" + fill.r + "," + fill.g + "," + fill.b + ")" : null
        );
      });

      svg.querySelectorAll(".cluster").forEach(function (group) {
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
    requestAnimationFrame(applyReadabilityOverrides);
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
