document.body.addEventListener('htmx:afterSwap', function(evt) {
    if (evt.detail.target.id === 'resultContainer') {

        // Find the hidden raw markdown text injected by Django
        const rawMarkdownEl = document.getElementById('rawMarkdown');
        const contentDiv = document.getElementById('blogContent');
        const resultCard = document.getElementById('resultCard');
        
        if (rawMarkdownEl && contentDiv) {
            // Convert Markdown to HTML
            contentDiv.innerHTML = marked.parse(rawMarkdownEl.textContent);
            
            // Smooth Fade-in
            setTimeout(() => {
                resultCard.classList.remove('opacity-0');
                resultCard.classList.add('opacity-100');
                resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 50);
            
            // Setup Copy Button Logic
            const copyBtn = document.getElementById('copyBtn');
            const copyText = document.getElementById('copyText');
            
            copyBtn.addEventListener('click', async () => {
                await navigator.clipboard.writeText(rawMarkdownEl.textContent);
                copyBtn.classList.add('text-green-600', 'bg-green-50', 'border-green-200');
                copyText.innerText = 'Copied!';
                copyBtn.querySelector('i').classList.replace('fa-copy', 'fa-check');
                setTimeout(() => {
                    copyBtn.classList.remove('text-green-600', 'bg-green-50', 'border-green-200');
                    copyText.innerText = 'Copy';
                    copyBtn.querySelector('i').classList.replace('fa-check', 'fa-copy');
                }, 2000);
            });
        }
    }
});

// Optional: Error handling for HTMX
document.body.addEventListener('htmx:responseError', function(evt) {
    alert("An error occurred: " + evt.detail.xhr.responseText);
});


// blog_result.html

(function () {
    // Render markdown
    const raw = document.getElementById('rawMarkdown');
    const content = document.getElementById('blogContent');
    const card = document.getElementById('resultCard');

    if (raw && content) {
        content.innerHTML = marked.parse(raw.textContent.trim());
    }

    // Animate card in
    requestAnimationFrame(() => {
        requestAnimationFrame(() => { card.classList.add('visible'); });
    });
})();


// Copy handler
function handleCopy(btn) {
    const raw = document.getElementById('rawMarkdown');

    if (!raw) return;
    navigator.clipboard.writeText(raw.textContent.trim()).then(() => {
        btn.classList.add('copied');
        document.getElementById('copyText').textContent = 'Copied!';
        btn.querySelector('i').className = 'fa-solid fa-check';
        setTimeout(() => {
            btn.classList.remove('copied');
            document.getElementById('copyText').textContent = 'Copy';
            btn.querySelector('i').className = 'fa-regular fa-copy';
        }, 2000);
    });
}

/* ── Download PDF ───────────────────────────────────── */
function handleDownloadPDF(btn) {
    const printArea = document.getElementById('pdf-print-area');
    const icon      = btn.querySelector('i');
    const label     = btn.querySelector('span');
 
    btn.classList.add('downloading');
    icon.className = 'fa-solid fa-spinner fa-spin';
    if (label) label.textContent = 'Preparing…';
 
    printArea.style.display = 'block';
 
    setTimeout(() => {
        window.print();
        printArea.style.display = 'none';
        btn.classList.remove('downloading');
        icon.className = 'fa-solid fa-file-arrow-down';
        if (label) label.textContent = 'Download PDF';
    }, 350);
}