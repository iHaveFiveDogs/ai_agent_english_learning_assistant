document.addEventListener('DOMContentLoaded', function() {
    const article = document.getElementById('article');
    const bubble = document.getElementById('bubble');

    article.addEventListener('contextmenu', function(event) {
        event.preventDefault();
        const selectedText = window.getSelection().toString();
        if (selectedText) {
            // Display sample response in bubble
            const sampleResponse = 'Sample response for selected text.';
            bubble.textContent = sampleResponse;
            bubble.style.top = `${event.pageY}px`;
            bubble.style.left = `${event.pageX}px`;
            bubble.classList.remove('hidden');
        }
    });

    document.addEventListener('click', function(event) {
        if (!bubble.contains(event.target)) {
            bubble.classList.add('hidden');
        }
    });
});
