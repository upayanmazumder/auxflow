---
title: "Changelog"
nav_order: 6
---

# Changelog

All notable changes and releases are documented here.
This page loads releases dynamically from the [GitHub Releases API](https://api.github.com/repos/upayanmazumder/auxflow/releases).

<div id="filter-controls" style="margin: 1.5rem 0; padding: 1rem; background: var(--color-bg-subtle, #1e2228); border: 1px solid var(--color-border-subtle, #30363d); border-radius: 6px;">
  <label for="tag-filter" style="font-weight: bold; margin-right: 0.5rem;">Filter by version:</label>
  <select id="tag-filter" style="padding: 0.4rem 0.8rem; background: var(--color-bg-default, #0d1117); color: inherit; border: 1px solid var(--color-border-default, #30363d); border-radius: 4px;">
    <option value="all">All releases</option>
  </select>
  <span id="release-count" style="margin-left: 1rem; color: var(--color-fg-muted, #8b949e); font-size: 0.9em;"></span>
</div>

<div id="changelog-loading" style="padding: 2rem 0; text-align: center; color: var(--color-fg-muted, #8b949e);">
  Loading releases from GitHub...
</div>

<div id="changelog-container"></div>

<noscript>
  <div class="note">
    JavaScript is disabled. View releases directly on <a href="https://github.com/upayanmazumder/auxflow/releases">GitHub Releases</a>.
  </div>
</noscript>

<script>
(function() {
  const container = document.getElementById('changelog-container');
  const loading = document.getElementById('changelog-loading');
  const select = document.getElementById('tag-filter');
  const countEl = document.getElementById('release-count');

  const params = new URLSearchParams(window.location.search);
  const versionParam = params.get('version') || params.get('tag') || 'all';
  const limitParam = parseInt(params.get('limit') || '30', 10);

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function formatBody(body) {
    if (!body) return '<p><em>No release notes provided.</em></p>';
    let html = escapeHtml(body);
    // basic code blocks
    html = html.replace(/```([a-z]*)\n([\s\S]*?)```/g, function(match, lang, code) {
      return '<pre><code>' + code + '</code></pre>';
    });
    // inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    // headers
    html = html.replace(/^### (.*$)/gim, '<h4>$1</h4>');
    html = html.replace(/^## (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^# (.*$)/gim, '<h2>$1</h2>');
    // links
    html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    // list items
    html = html.replace(/^\s*-\s+(.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');
    // line breaks to paragraphs
    return html.replace(/\n\n+/g, '<br><br>');
  }

  function render(releases, selectedTag) {
    container.innerHTML = '';
    const filtered = selectedTag === 'all'
      ? releases
      : releases.filter(r => r.tag_name === selectedTag || r.tag_name === 'v' + selectedTag || r.name === selectedTag);

    countEl.textContent = 'Showing ' + filtered.length + ' of ' + releases.length + ' release(s)';

    if (filtered.length === 0) {
      container.innerHTML = '<p>No releases match <code>' + escapeHtml(selectedTag) + '</code>. <a href="?version=all">View all releases</a></p>';
      return;
    }

    filtered.forEach(r => {
      const card = document.createElement('article');
      card.className = 'release-entry';
      card.style.cssText = 'margin-bottom: 2.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--color-border-subtle, #30363d);';

      const published = new Date(r.published_at).toLocaleDateString(undefined, {
        year: 'numeric', month: 'short', day: 'numeric'
      });

      card.innerHTML =
        '<div style="display: flex; align-items: baseline; gap: 0.75rem; flex-wrap: wrap;">' +
          '<h2 style="margin: 0; font-size: 1.5rem;">' +
            '<a href="' + escapeHtml(r.html_url) + '" target="_blank" rel="noopener">' + escapeHtml(r.name || r.tag_name) + '</a>' +
          '</h2>' +
          '<span style="background: var(--color-accent-emphasis, #1f6feb); color: #fff; padding: 0.15rem 0.5rem; border-radius: 12px; font-size: 0.8em; font-weight: 500;">' +
            escapeHtml(r.tag_name) +
          '</span>' +
          (r.prerelease ? '<span style="background: #d29922; color: #fff; padding: 0.15rem 0.5rem; border-radius: 12px; font-size: 0.8em;">Pre-release</span>' : '') +
          '<time style="color: var(--color-fg-muted, #8b949e); font-size: 0.9em;">Released on ' + published + '</time>' +
        '</div>' +
        '<div class="release-body" style="margin-top: 1rem; line-height: 1.6;">' +
          formatBody(r.body) +
        '</div>' +
        '<div style="margin-top: 1rem; font-size: 0.85em;">' +
          '<a href="' + escapeHtml(r.html_url) + '" target="_blank" rel="noopener">View release on GitHub &rarr;</a>' +
        '</div>';

      container.appendChild(card);
    });
  }

  fetch('https://api.github.com/repos/upayanmazumder/auxflow/releases?per_page=' + limitParam)
    .then(res => {
      if (!res.ok) throw new Error('GitHub API HTTP ' + res.status);
      return res.json();
    })
    .then(releases => {
      loading.style.display = 'none';

      releases.forEach(r => {
        const opt = document.createElement('option');
        opt.value = r.tag_name;
        opt.textContent = (r.name && r.name !== r.tag_name) ? r.name + ' (' + r.tag_name + ')' : r.tag_name;
        select.appendChild(opt);
      });

      let initialSelection = 'all';
      if (versionParam !== 'all') {
        const match = releases.find(r => r.tag_name === versionParam || r.tag_name === 'v' + versionParam || r.name === versionParam);
        if (match) {
          initialSelection = match.tag_name;
          select.value = match.tag_name;
        }
      }

      select.addEventListener('change', function() {
        const val = this.value;
        const newUrl = new URL(window.location);
        if (val === 'all') {
          newUrl.searchParams.delete('version');
        } else {
          newUrl.searchParams.set('version', val);
        }
        window.history.pushState({}, '', newUrl);
        render(releases, val);
      });

      render(releases, initialSelection);
    })
    .catch(err => {
      loading.innerHTML =
        '<p style="color: #f85149;">Unable to load changelogs directly from GitHub (' + escapeHtml(err.message) + ').</p>' +
        '<p><a href="https://github.com/upayanmazumder/auxflow/releases" target="_blank" rel="noopener">Browse releases on GitHub &rarr;</a></p>';
    });
})();
</script>
