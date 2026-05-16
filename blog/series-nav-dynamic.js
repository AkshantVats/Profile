/**
 * Series sidebar from blog/series-index.json (single source of truth).
 * In each post HTML: <div id="series-nav-mount" data-series-slug="experience"></div> (slug: ai-learning | experience | lensai)
 * Path to this script from blog/series/<slug>/page.html: ../../series-nav-dynamic.js
 */
(function () {
  function esc(s) {
    if (s == null) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function pad2(n) {
    return n < 10 ? "0" + n : String(n);
  }

  function postEntry(raw) {
    if (!raw) return { href: "", kicker: "", title: "", desc: "" };
    if (typeof raw === "string") return { href: raw, kicker: "", title: "", desc: "" };
    return {
      href: raw.href || "",
      kicker: raw.kicker || "",
      title: raw.title || "",
      desc: raw.desc || ""
    };
  }

  function basename(href) {
    if (!href || href === "#") return "";
    var parts = href.split("/");
    return parts[parts.length - 1] || "";
  }

  /** Last path segment without trailing slash or .html — matches clean URLs and .html pages. */
  function pageSlugFromPathname(pathname) {
    var seg = pathname.replace(/\/+$/, "").split("/").pop() || "";
    return seg.replace(/\.html?$/i, "");
  }

  function postSlugFromHref(href) {
    return pageSlugFromPathname(basename(href));
  }

  function relHref(jsonHref) {
    if (!jsonHref || jsonHref === "#") return "#";
    return basename(jsonHref);
  }

  function initToc() {
    var toc = document.querySelectorAll(".toc-list a");
    if (!toc.length) return;
    var sections = Array.prototype.slice
      .call(toc)
      .map(function (a) {
        var id = a.getAttribute("href");
        return id && id.charAt(0) === "#" ? document.getElementById(id.slice(1)) : null;
      })
      .filter(Boolean);
    if (!sections.length) return;
    var obs = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            toc.forEach(function (a) {
              a.classList.remove("active");
            });
            var found = Array.prototype.slice.call(toc).find(function (a) {
              return a.getAttribute("href") === "#" + e.target.id;
            });
            if (found) found.classList.add("active");
          }
        });
      },
      { rootMargin: "-20% 0px -70% 0px" }
    );
    sections.forEach(function (s) {
      obs.observe(s);
    });
  }

  function seriesIndexUrl() {
    var nodes = document.querySelectorAll('script[src*="series-nav-dynamic"]');
    var el = nodes.length ? nodes[nodes.length - 1] : null;
    if (el && el.src) {
      try {
        var u = new URL(el.src, window.location.href);
        u.pathname = u.pathname.replace(/series-nav-dynamic\.js$/i, "series-index.json");
        return u.toString();
      } catch (e) {}
    }
    return new URL("../../series-index.json", window.location.href).href;
  }

  function fillSeriesNav() {
    var mount = document.getElementById("series-nav-mount");
    if (!mount) return Promise.resolve();
    var slug = mount.getAttribute("data-series-slug");
    if (!slug) return Promise.resolve();

    return fetch(seriesIndexUrl(), { credentials: "same-origin" })
      .then(function (r) {
        return r.ok ? r.json() : Promise.reject();
      })
      .then(function (data) {
        var series = (data.series || []).find(function (s) {
          return s.slug === slug;
        });
        if (!series || !series.posts || !series.posts.length) {
          mount.innerHTML = "";
          return;
        }

        var posts = series.posts.map(postEntry);
        var path = window.location.pathname.replace(/\/+$/, "");
        var pageSlug = pageSlugFromPathname(path);
        var total = posts.length;
        var curIdx = 0;
        posts.forEach(function (p, i) {
          var ps = postSlugFromHref(p.href);
          if (ps && pageSlug === ps) curIdx = i + 1;
        });

        var slugLine = series.slugLine || series.title || slug;
        var labelLine = slugLine + " · " + (curIdx || "?") + " of " + total;
        var subTitle = series.navSubtitle != null ? series.navSubtitle : series.title;

        var html = [];
        html.push('<div class="series-nav">');
        html.push('<div class="series-label">' + esc(labelLine) + "</div>");
        html.push('<div class="series-title">' + esc(subTitle) + "</div>");
        html.push('<div class="series-posts">');

        posts.forEach(function (p, idx) {
          var n = idx + 1;
          var href = p.href;
          var isDraft = !href || href === "#";
          var isCurrent = !isDraft && postSlugFromHref(href) === pageSlug;
          var rowCls = "series-post" + (isCurrent ? " current" : "") + (isDraft ? " series-post--draft" : "");
          var numSpan = '<span class="series-post-num">' + (isCurrent ? pad2(n) + " →" : pad2(n)) + "</span> ";
          var kicker = p.kicker || "Part " + n + " / " + total;
          var title = p.title || (isDraft ? "Coming soon" : basename(href).replace(/\.html$/i, "").replace(/-/g, " "));
          var desc = p.desc || "";

          html.push('<div class="' + rowCls + '">');
          html.push('<div class="series-post-kicker">' + numSpan + esc(kicker) + "</div>");
          if (!isDraft) {
            html.push(
              '<a class="series-post-title" href="' +
                esc(relHref(href)) +
                '">' +
                esc(title) +
                "</a>"
            );
          } else {
            html.push('<div class="series-post-title">' + esc(title) + "</div>");
          }
          if (desc) html.push('<p class="series-post-desc">' + esc(desc) + "</p>");
          html.push("</div>");
        });

        html.push("</div></div>");
        mount.innerHTML = html.join("");
      })
      .catch(function () {
        mount.innerHTML = "";
      });
  }

  fillSeriesNav().then(initToc).catch(initToc);
})();
