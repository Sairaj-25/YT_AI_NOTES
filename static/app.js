/* ═══════════════════════════════════════════════════
   app.js — YT-AI-Note
   ═══════════════════════════════════════════════════ */

// Configure marked.js for proper GitHub-flavored markdown
marked.setOptions({
    breaks: true,   // Treat single newlines as <br>
    gfm: true,      // GitHub Flavored Markdown (tables, strikethrough, etc.)
});

/**
 * After HTMX swaps the blog_result.html partial into #resultContainer:
 *  1. Read raw markdown from the JSON <script> tag (#rawMarkdownData)
 *  2. Parse it with marked.js and inject into #blogContent
 *  3. Animate the card into view
 *  4. Set the PDF date labels
 */
document.body.addEventListener('htmx:afterSwap', function (evt) {
    if (evt.detail.target.id !== 'resultContainer') return;

    const rawDataEl  = document.getElementById('rawMarkdownData');
    const rawEl      = document.getElementById('rawMarkdown');
    const contentDiv = document.getElementById('blogContent');
    const resultCard = document.getElementById('resultCard');

    if (!rawDataEl || !contentDiv || !resultCard) return;

    // ── Safely decode the JSON-encoded markdown string ──────
    let markdown = '';
    try {
        markdown = JSON.parse(rawDataEl.textContent);
    } catch (e) {
        console.error('Failed to parse rawMarkdownData JSON:', e);
        return;
    }

    // Populate the hidden #rawMarkdown div for copy/PDF handlers
    if (rawEl) rawEl.textContent = markdown;

    // ── Render markdown → HTML ───────────────────────────────
    contentDiv.innerHTML = marked.parse(markdown);

    // ── Style chapter banner h2 ──────────────────────────────
    styleChapterBanner(contentDiv);

    // ── Animate card in (remove opacity-0 + translate-y-5) ──
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            resultCard.classList.remove('opacity-0', 'translate-y-5');
            resultCard.classList.add('opacity-100', 'translate-y-0');
        });
    });

    // ── Scroll to result ────────────────────────────────────
    setTimeout(() => {
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);

    // ── PDF date stamps ──────────────────────────────────────
    const now = new Date().toLocaleDateString('en-US', {
        year: 'numeric', month: 'long', day: 'numeric'
    });
    const pdfDate       = document.getElementById('pdfDate');
    const pdfFooterDate = document.getElementById('pdfFooterDate');
    if (pdfDate)       pdfDate.textContent       = now;
    if (pdfFooterDate) pdfFooterDate.textContent = now;
});


/* ── Chapter banner styler ────────────────────────────────── */
/**
 * Takes the first h2 inside the rendered content (expected text like
 * "Chapter · 01   Introduction to Python") and restructures its
 * inner HTML into a two-part layout: a bold dark label + the title.
 */
function styleChapterBanner(container) {
    const h2 = container.querySelector('h2');
    if (!h2) return;

    const text = h2.textContent.trim();

    // Match: "Chapter · 01   Title text here"
    // The AI outputs: ## Chapter · 01 &nbsp;&nbsp; Title
    // After marked.js parses it, &nbsp; becomes \u00a0
    const match = text.match(/^(Chapter\s*[·•]\s*\d+)\s+([\s\S]+)$/i);
    if (match) {
        const label = match[1].trim(); // "Chapter · 01"
        const title = match[2].replace(/\u00a0/g, ' ').trim();
        h2.innerHTML =
            `<span style="font-weight:900;margin-right:16px;white-space:nowrap;">${label}</span>` +
            `<span style="font-weight:600;">${title}</span>`;
    }
}


/* ── Copy handler (called from onclick in blog_result.html) ── */
function handleCopy(btn) {
    const raw = document.getElementById('rawMarkdown');
    if (!raw) return;

    navigator.clipboard.writeText(raw.textContent.trim()).then(() => {
        // Copied state — green
        btn.classList.add('!text-green-400', '!bg-green-500/10', '!border-green-500/30');
        const copyText = document.getElementById('copyText');
        const icon = btn.querySelector('i');
        if (copyText) copyText.textContent = 'Copied!';
        if (icon) icon.className = 'fa-solid fa-check';

        setTimeout(() => {
            btn.classList.remove('!text-green-400', '!bg-green-500/10', '!border-green-500/30');
            if (copyText) copyText.textContent = 'Copy';
            if (icon) icon.className = 'fa-regular fa-copy';
        }, 2000);
    });
}


/* ── PDF download handler ─────────────────────────────────── */
function handleDownloadPDF(btn) {
    const printArea = document.getElementById('pdf-print-area');
    const icon      = btn.querySelector('i');
    const label     = btn.querySelector('span');

    // Copy rendered HTML into print area
    const blogContent = document.getElementById('blogContent');
    const pdfBody     = document.getElementById('pdfBody');
    if (blogContent && pdfBody) {
        pdfBody.innerHTML = blogContent.innerHTML;
    }

    // Show loading state
    if (icon)  icon.className  = 'fa-solid fa-spinner fa-spin';
    if (label) label.textContent = 'Preparing…';
    if (printArea) printArea.style.display = 'block';

    setTimeout(() => {
        window.print();
        if (printArea) printArea.style.display = 'none';
        if (icon)  icon.className  = 'fa-solid fa-file-arrow-down';
        if (label) label.textContent = 'PDF';
    }, 350);
}


/* ── HTMX error handler ───────────────────────────────────── */
document.body.addEventListener('htmx:responseError', function (evt) {
    console.error('HTMX error:', evt.detail.xhr.responseText);
});