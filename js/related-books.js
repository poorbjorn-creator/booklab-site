// Related Books — loads from /data/related-books.json
// Inject before </body> on any review page. Renders a "You Might Also Like" section.
(function () {
  // Extract slug from URL path: /reviews/some-book.html → some-book
  var path = window.location.pathname;
  var m = path.match(/\/reviews\/([^\/]+)\.html$/);
  if (!m) return;
  var slug = m[1];

  fetch('/data/related-books.json')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var entry = data[slug];
      if (!entry || !entry.related || !entry.related.length) return;

      // Build title map from all entries (slug → readable title)
      // We'll grab titles from the review pages' <title> tags via the JSON keys
      // For now, derive readable titles from slugs
      var cards = entry.related.map(function (relSlug) {
        var title = relSlug
          .replace(/-/g, ' ')
          .replace(/\b\w/g, function (c) { return c.toUpperCase(); });
        // Fix common words that shouldn't be capitalized
        title = title
          .replace(/ By /g, ' by ')
          .replace(/ Of /g, ' of ')
          .replace(/ The /g, ' the ')
          .replace(/ And /g, ' and ')
          .replace(/ On /g, ' on ')
          .replace(/ A /g, ' a ')
          .replace(/ In /g, ' in ')
          .replace(/ To /g, ' to ')
          .replace(/ From /g, ' from ')
          .replace(/ For /g, ' for ');
        // First letter always caps
        title = title.charAt(0).toUpperCase() + title.slice(1);

        // Split author from title (last two words usually = author for our slugs)
        // Not perfect, but works for display
        return '<a href="/reviews/' + relSlug + '.html" class="related-card">' +
          '<span class="related-title">' + title + '</span>' +
          '</a>';
      });

      var section = document.createElement('div');
      section.className = 'related-section';
      section.innerHTML =
        '<h2>📚 You Might Also Like</h2>' +
        '<div class="related-grid">' + cards.join('') + '</div>';

      // Insert before the back-link or before footer
      var backLink = document.querySelector('.back-link');
      var parent = backLink ? backLink.parentNode : document.querySelector('.article');
      if (backLink) {
        parent.insertBefore(section, backLink);
      } else if (parent) {
        parent.appendChild(section);
      }
    })
    .catch(function () { /* silent fail */ });
})();
