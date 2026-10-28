---
title: "Changelog"
nav_order: 6
---

# Changelog

All releases and updates for AuxFlow.
This page fetches release notes directly from [GitHub Releases](https://github.com/upayanmazumder/auxflow/releases).

## Unreleased

- Runtime normalization reads braces inside optional bibliography labels before it finds the closing bracket.
- `auxflow update` works in a pipx installation. The pipx environment has no pip, so AuxFlow runs `pipx upgrade auxflow` there. In any other environment without pip, it explains how to update.
- Reports and `auxflow check` print `file:line:column` instead of character offsets. Paths under the current directory print relative to it.
- The cycle report uses plain words. `auxflow classify -v` adds the internal fact names. `auxflow plan --explain` describes each pass in plain words.
- `auxflow run` names a missing TeX tool and suggests `auxflow plan`. It prints each pass on stderr.
- `auxflow check` reports the convergence state, so it agrees with `auxflow classify`.
- Mistyped commands suggest the nearest command.
- New `auxflow doctor` command checks for `pdflatex`, `bibtex`, and `makeindex`.
- New `--json` option on `check`, `classify`, and `plan`. New global `--quiet` option.
- `auxflow classify` suggests a next step on stderr. `--force` on an AMPLIFYING document prints a warning.
- When a TeX tool fails, `auxflow run` names the log file to read, such as `main.log`.

## 0.3.0

- `auxflow run` now limits each TeX tool invocation to 600 seconds by default. Use `--timeout SECONDS` to change the limit.
- Runtime verification rejects auxiliary symlinks outside the work directory. Local package inventory also ignores files outside the project root.
- Installation guidance now recommends `pipx` before the optional installer script. A corpus test guards ordinary table-of-contents classification.
- `auxflow update --check` queries the latest PyPI release. `auxflow update` installs a newer release only when invoked explicitly.
- Normal commands can show a cached update notice without waiting for the network. The check runs at most daily while a command remains active.

<div id="changelog-controls" style="margin: 1.5rem 0; padding: 1rem; background: var(--color-bg-subtle, #1e2228); border: 1px solid var(--color-border-subtle, #30363d); border-radius: 6px;">
  <label for="release-select" style="font-weight: 600; margin-right: 0.5rem;">Select release:</label>
  <select id="release-select" style="padding: 0.4rem 0.8rem; background: var(--color-bg-default, #0d1117); color: inherit; border: 1px solid var(--color-border-default, #30363d); border-radius: 4px;">
    <option value="all">All releases</option>
  </select>
  <span id="release-count" style="margin-left: 1rem; color: var(--color-fg-muted, #8b949e); font-size: 0.9em;"></span>
</div>

<div id="changelog-feed">
  <p id="changelog-status" style="color: var(--color-fg-muted, #8b949e);">Loading releases...</p>
</div>

<noscript>
  <p>JavaScript is required for live release filtering. View releases directly on <a href="https://github.com/upayanmazumder/auxflow/releases">GitHub</a>.</p>
</noscript>

<script>
window.addEventListener('DOMContentLoaded', function() {
  var feed = document.getElementById('changelog-feed');
  var status = document.getElementById('changelog-status');
  var select = document.getElementById('release-select');
  var count = document.getElementById('release-count');

  var urlParams = new URLSearchParams(window.location.search);
  var targetVersion = urlParams.get('version') || urlParams.get('tag') || 'all';

  function clean(str) {
    var div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
  }

  function renderRelease(rel) {
    var wrapper = document.createElement('div');
    wrapper.style.marginBottom = '2rem';
    wrapper.style.paddingBottom = '1.5rem';
    wrapper.style.borderBottom = '1px solid var(--color-border-subtle, #30363d)';

    var date = new Date(rel.published_at).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });

    var title = clean(rel.name || rel.tag_name);
    var tag = clean(rel.tag_name);
    var body = clean(rel.body);

    body = body.replace(/```([a-z]*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
    body = body.replace(/`([^`]+)`/g, '<code>$1</code>');
    body = body.replace(/\n\n+/g, '<br><br>');

    wrapper.innerHTML =
      '<div style="display:flex; align-items:center; gap:0.6rem; flex-wrap:wrap; margin-bottom:0.75rem;">' +
        '<h2 style="margin:0; font-size:1.4rem;"><a href="' + clean(rel.html_url) + '" target="_blank" rel="noopener">' + title + '</a></h2>' +
        '<span style="background:var(--color-accent-emphasis, #1f6feb); color:#fff; padding:0.15rem 0.5rem; border-radius:12px; font-size:0.8rem; font-weight:600;">' + tag + '</span>' +
        '<time style="color:var(--color-fg-muted, #8b949e); font-size:0.85rem;">' + date + '</time>' +
      '</div>' +
      '<div style="line-height:1.6; margin-top:0.75rem;">' + body + '</div>' +
      '<div style="margin-top:0.85rem;"><a href="' + clean(rel.html_url) + '" target="_blank" rel="noopener" style="font-size:0.85rem;">View on GitHub &rarr;</a></div>';

    return wrapper;
  }

  fetch('https://api.github.com/repos/upayanmazumder/auxflow/releases')
    .then(function(res) {
      if (!res.ok) {
        throw new Error('HTTP ' + res.status);
      }
      return res.json();
    })
    .then(function(releases) {
      if (status) {
        status.remove();
      }

      if (!releases || releases.length === 0) {
        feed.innerHTML = '<p>No releases found.</p>';
        return;
      }

      for (var i = 0; i < releases.length; i++) {
        var opt = document.createElement('option');
        opt.value = releases[i].tag_name;
        opt.textContent = releases[i].tag_name;
        select.appendChild(opt);
      }

      function applyFilter(selected) {
        feed.innerHTML = '';
        var matched = 0;
        for (var j = 0; j < releases.length; j++) {
          var item = releases[j];
          if (selected === 'all' || item.tag_name === selected || item.tag_name === 'v' + selected || item.name === selected) {
            feed.appendChild(renderRelease(item));
            matched++;
          }
        }
        count.textContent = 'Showing ' + matched + ' of ' + releases.length + ' release(s)';
        if (matched === 0) {
          feed.innerHTML = '<p>No release matches <code>' + clean(selected) + '</code>. <a href="?version=all">Show all</a></p>';
        }
      }

      if (targetVersion !== 'all') {
        select.value = targetVersion;
      }

      select.addEventListener('change', function() {
        var val = this.value;
        var newUrl = new URL(window.location);
        if (val === 'all') {
          newUrl.searchParams.delete('version');
        } else {
          newUrl.searchParams.set('version', val);
        }
        window.history.pushState({}, '', newUrl);
        applyFilter(val);
      });

      applyFilter(targetVersion);
    })
    .catch(function(err) {
      feed.innerHTML =
        '<p style="color:#cf222e;">Failed to load releases (' + clean(err.message) + ').</p>' +
        '<p><a href="https://github.com/upayanmazumder/auxflow/releases" target="_blank" rel="noopener">Open GitHub Releases directly &rarr;</a></p>';
    });
});
</script>
