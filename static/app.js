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