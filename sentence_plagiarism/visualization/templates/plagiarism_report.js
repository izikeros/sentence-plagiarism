document.addEventListener('DOMContentLoaded', function() {
    // Show/Hide all buttons
    document.getElementById('show-all-btn').addEventListener('click', function() {
        document.querySelectorAll('.plagiarized').forEach(el => {
            el.classList.remove('hidden');
        });
        setActiveButton(this);
    });

    document.getElementById('hide-all-btn').addEventListener('click', function() {
        document.querySelectorAll('.plagiarized').forEach(el => {
            el.classList.add('hidden');
        });
        setActiveButton(this);
    });

    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const docId = this.getAttribute('data-doc');

            // Hide all plagiarism highlights
            document.querySelectorAll('.plagiarized').forEach(el => {
                el.classList.add('hidden');
            });

            // Show only the selected document's highlights
            document.querySelectorAll('.plag-doc-' + docId).forEach(el => {
                el.classList.remove('hidden');
            });

            setActiveButton(this);
        });
    });

    // Similarity slider functionality
    const slider = document.getElementById('similarity-slider');
    const sliderValueDisplay = document.getElementById('slider-value');

    slider.addEventListener('input', function() {
        const similarityThreshold = parseFloat(slider.value) / 100; // Convert percentage to 0-1 range
        sliderValueDisplay.textContent = slider.value + '%';

        document.querySelectorAll('.plagiarized').forEach(el => {
            const similarity = parseFloat(el.getAttribute('data-similarity'));
            if (similarity >= similarityThreshold) {
                el.classList.remove('hidden');
            } else {
                el.classList.add('hidden');
            }
        });

        updateHighlightedCount();
    });

    const highlightedCountDisplay = document.getElementById('highlighted-count');

    function updateHighlightedCount() {
        const highlightedCount = document.querySelectorAll('.plagiarized:not(.hidden)').length;
        highlightedCountDisplay.textContent = `Highlighted Sentences: ${highlightedCount}`;
    }

    // Update count on filter button clicks
    document.querySelectorAll('.filter-btn, #show-all-btn, #hide-all-btn').forEach(btn => {
        btn.addEventListener('click', updateHighlightedCount);
    });

    // Initial count update
    updateHighlightedCount();

    function setActiveButton(activeBtn) {
        document.querySelectorAll('.control-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        activeBtn.classList.add('active');
    }
});