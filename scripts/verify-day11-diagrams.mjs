/**
 * Verify Day 11 diagram text visibility in light and dark themes.
 * Run: node scripts/verify-day11-diagrams.mjs
 */
import { chromium } from "playwright";
import { createServer } from "http";
import { readFileSync, statSync } from "fs";
import { join, extname } from "path";
import { fileURLToPath } from "url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const ROOT = join(__dirname, "..");
const POST =
  "/blog/series/ai-learning/day-11-semantic-caching-vs-exact-match-redis.html";

const MIME = {
  ".html": "text/html",
  ".js": "application/javascript",
  ".css": "text/css",
  ".png": "image/png",
  ".json": "application/json",
};

function serve() {
  return new Promise((resolve) => {
    const server = createServer((req, res) => {
      let path = join(ROOT, req.url === "/" ? "index.html" : req.url.split("?")[0]);
      try {
        if (statSync(path).isDirectory()) path = join(path, "index.html");
        const body = readFileSync(path);
        res.writeHead(200, { "Content-Type": MIME[extname(path)] || "text/plain" });
        res.end(body);
      } catch {
        res.writeHead(404);
        res.end("Not found");
      }
    });
    server.listen(0, () => resolve({ server, port: server.address().port }));
  });
}

function parseRgb(str) {
  const m = str.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (!m) return null;
  return { r: +m[1], g: +m[2], b: +m[3] };
}

function parseColor(str) {
  if (!str || str === "none" || str === "transparent") return null;
  const rgb = parseRgb(str);
  if (rgb) return rgb;
  if (str.startsWith("#")) {
    const h = str.replace("#", "");
    if (h.length === 6) {
      return { r: parseInt(h.slice(0, 2), 16), g: parseInt(h.slice(2, 4), 16), b: parseInt(h.slice(4, 6), 16) };
    }
  }
  return null;
}

function luminance({ r, g, b }) {
  const s = [r, g, b].map((c) => {
    c /= 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * s[0] + 0.7152 * s[1] + 0.0722 * s[2];
}

function contrast(textLum, fillLum) {
  const lighter = Math.max(textLum, fillLum);
  const darker = Math.min(textLum, fillLum);
  return (lighter + 0.05) / (darker + 0.05);
}

async function sampleDiagramLabels(page, diagramIndex) {
  return page.evaluate((idx) => {
    function parseRgb(str) {
      const m = str.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
      if (!m) return null;
      return { r: +m[1], g: +m[2], b: +m[3] };
    }
    function luminance({ r, g, b }) {
      const s = [r, g, b].map((c) => {
        c /= 255;
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * s[0] + 0.7152 * s[1] + 0.0722 * s[2];
    }
    function shapeFill(node) {
      const shapes = node.querySelectorAll("rect, polygon, circle, ellipse, path");
      let best = null;
      let bestLum = -1;
      shapes.forEach((shape) => {
        const raw =
          shape.getAttribute("fill") ||
          shape.style.fill ||
          window.getComputedStyle(shape).fill;
        const rgb = parseRgb(raw);
        if (!rgb) return;
        const lum = luminance(rgb);
        if (lum > bestLum) {
          bestLum = lum;
          best = raw;
        }
      });
      return best;
    }
    const blocks = document.querySelectorAll(".prose pre.mermaid");
    const svg = blocks[idx]?.querySelector("svg");
    if (!svg) return { error: "no svg" };
    const samples = [];
    svg.querySelectorAll(".node").forEach((node, i) => {
      const text = node.querySelector("text, tspan");
      if (!text) return;
      const fill = shapeFill(node);
      if (!fill) return;
      const textFill = window.getComputedStyle(text).fill;
      const label = (text.textContent || "").trim().slice(0, 40);
      samples.push({ i, label, fill, textFill });
    });
    return { count: samples.length, samples };
  }, diagramIndex);
}

async function main() {
  const { server, port } = await serve();
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const url = `http://127.0.0.1:${port}${POST}`;
  await page.goto(url, { waitUntil: "networkidle" });
  await page.waitForSelector(".prose pre.mermaid svg", { timeout: 15000 });

  const results = { light: {}, dark: {} };

  for (const theme of ["light", "dark"]) {
    await page.evaluate((t) => {
      document.documentElement.setAttribute("data-theme", t);
      localStorage.setItem("theme", t);
    }, theme);
    await page.evaluate(() => window.renderBlogMermaid());
    await page.waitForTimeout(500);

    for (let d = 0; d < 3; d++) {
      const data = await sampleDiagramLabels(page, d);
      const issues = [];
      for (const s of data.samples || []) {
        const fillRgb = parseColor(s.fill);
        const textRgb = parseColor(s.textFill);
        if (!textRgb) continue;
        const textLum = luminance(textRgb);
        const isAccent =
          fillRgb &&
          fillRgb.r >= 250 &&
          fillRgb.g >= 240 &&
          fillRgb.b >= 190 &&
          fillRgb.b <= 220;
        if (isAccent && textLum > 0.35) {
          issues.push({ label: s.label, problem: "accent should have dark text", text: s.textFill });
        } else if (!isAccent && theme === "dark" && textLum < 0.45) {
          issues.push({ label: s.label, problem: "dark text on dark fill in dark mode", text: s.textFill });
        } else if (!isAccent && theme === "light" && textLum > 0.65) {
          issues.push({ label: s.label, problem: "light text on light fill in light mode", text: s.textFill });
        }
      }
      results[theme][`diagram${d + 1}`] = { nodes: data.count, issues };
    }
  }

  await browser.close();
  server.close();

  let failed = false;
  console.log("\n=== Day 11 diagram theme verification ===\n");
  for (const theme of ["light", "dark"]) {
    console.log(`--- ${theme.toUpperCase()} ---`);
    for (const [key, val] of Object.entries(results[theme])) {
      const ok = val.issues.length === 0;
      console.log(`  ${key}: ${val.nodes} nodes — ${ok ? "PASS" : "FAIL"}`);
      if (!ok) {
        failed = true;
        val.issues.forEach((i) => console.log("    ", JSON.stringify(i)));
      }
    }
  }
  console.log(failed ? "\nOVERALL: FAIL\n" : "\nOVERALL: PASS\n");
  process.exit(failed ? 1 : 0);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
