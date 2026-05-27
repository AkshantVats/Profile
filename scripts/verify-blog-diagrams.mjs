/**
 * Verify blog Mermaid diagram text visibility (light + dark).
 * Run: node scripts/verify-blog-diagrams.mjs
 */
import { chromium } from "playwright";
import { createServer } from "http";
import { readFileSync, statSync } from "fs";
import { join, extname } from "path";
import { fileURLToPath } from "url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));
const ROOT = join(__dirname, "..");

const POSTS = [
  {
    slug: "day11",
    path: "/blog/series/ai-learning/day-11-semantic-caching-vs-exact-match-redis.html",
    diagrams: 3,
    requiredClassDefs: ["classDef exact", "classDef semantic", "classDef pipeline"],
  },
  {
    slug: "ota",
    path: "/blog/series/experience/ota-at-scale-at-least-once-is-a-feature.html",
    diagrams: 3,
    requiredClassDefs: ["classDef exact", "classDef pipeline"],
    requiredAssets: ["blog-diagrams.js", "blog-diagrams.css"],
  },
];

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
      return {
        r: parseInt(h.slice(0, 2), 16),
        g: parseInt(h.slice(2, 4), 16),
        b: parseInt(h.slice(4, 6), 16),
      };
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
    const block = blocks[idx];
    const svg = block?.querySelector("svg");
    if (!svg) return { error: "no svg", kind: "missing" };
    const isSequence = !!svg.querySelector(".actor");
    if (isSequence) {
      const actors = [];
      svg.querySelectorAll(".actor").forEach((actor) => {
        const text = actor.querySelector("text, tspan");
        const rect = actor.querySelector("rect");
        if (!text || !rect) return;
        const fill =
          rect.getAttribute("fill") ||
          rect.style.fill ||
          window.getComputedStyle(rect).fill;
        const textFill = window.getComputedStyle(text).fill;
        actors.push({
          label: (text.textContent || "").trim().slice(0, 40),
          fill,
          textFill,
        });
      });
      return { kind: "sequence", count: actors.length, samples: actors };
    }
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
    return { kind: "flowchart", count: samples.length, samples };
  }, diagramIndex);
}

function checkContrast(samples, theme) {
  const issues = [];
  for (const s of samples || []) {
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
  return issues;
}

function checkSource(html, post) {
  const issues = [];
  for (const needle of post.requiredClassDefs || []) {
    if (!html.includes(needle)) {
      issues.push({ problem: `missing ${needle} in mermaid source` });
    }
  }
  for (const asset of post.requiredAssets || ["blog-diagrams.js", "blog-diagrams.css"]) {
    if (!html.includes(asset)) {
      issues.push({ problem: `missing asset link: ${asset}` });
    }
  }
  const mermaidBlocks = (html.match(/<pre class="mermaid">/g) || []).length;
  if (mermaidBlocks !== post.diagrams) {
    issues.push({ problem: `expected ${post.diagrams} mermaid blocks, found ${mermaidBlocks}` });
  }
  if (html.includes("subgraph ") && post.slug === "ota") {
    issues.push({ problem: "OTA post should not use subgraphs for simple flows" });
  }
  return issues;
}

async function verifyPost(page, port, post) {
  const html = readFileSync(join(ROOT, post.path.slice(1)), "utf8");
  const sourceIssues = checkSource(html, post);
  const url = `http://127.0.0.1:${port}${post.path}`;
  await page.goto(url, { waitUntil: "networkidle" });
  await page.waitForSelector(".prose pre.mermaid svg", { timeout: 15000 });

  const results = { source: sourceIssues, light: {}, dark: {} };

  for (const theme of ["light", "dark"]) {
    await page.evaluate((t) => {
      document.documentElement.setAttribute("data-theme", t);
      localStorage.setItem("theme", t);
    }, theme);
    await page.evaluate(() => window.renderBlogMermaid());
    await page.waitForTimeout(500);

    for (let d = 0; d < post.diagrams; d++) {
      const data = await sampleDiagramLabels(page, d);
      if (data.error) {
        results[theme][`diagram${d + 1}`] = { kind: data.kind, nodes: 0, issues: [{ problem: data.error }] };
        continue;
      }
      const issues =
        data.kind === "sequence"
          ? checkContrast(data.samples, theme)
          : data.count === 0
            ? [{ problem: "no flowchart nodes sampled" }]
            : checkContrast(data.samples, theme);
      results[theme][`diagram${d + 1}`] = {
        kind: data.kind,
        nodes: data.count,
        issues,
      };
    }
  }

  return results;
}

async function main() {
  const { server, port } = await serve();
  const browser = await chromium.launch();
  const page = await browser.newPage();
  let failed = false;

  console.log("\n=== Blog diagram theme verification ===\n");

  for (const post of POSTS) {
    console.log(`## ${post.slug.toUpperCase()} (${post.path})\n`);
    const results = await verifyPost(page, port, post);

    if (results.source.length) {
      failed = true;
      console.log("  SOURCE: FAIL");
      results.source.forEach((i) => console.log("   ", JSON.stringify(i)));
    } else {
      console.log("  SOURCE: PASS");
    }

    for (const theme of ["light", "dark"]) {
      console.log(`  --- ${theme.toUpperCase()} ---`);
      for (const [key, val] of Object.entries(results[theme])) {
        const ok = val.issues.length === 0;
        const kind = val.kind || "?";
        console.log(`    ${key} (${kind}): ${val.nodes} labels — ${ok ? "PASS" : "FAIL"}`);
        if (!ok) {
          failed = true;
          val.issues.forEach((i) => console.log("      ", JSON.stringify(i)));
        }
      }
    }
    console.log("");
  }

  await browser.close();
  server.close();

  console.log(failed ? "OVERALL: FAIL\n" : "OVERALL: PASS\n");
  process.exit(failed ? 1 : 0);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
