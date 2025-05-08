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

    function setActiveButton(activeBtn) {
        document.querySelectorAll('.control-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        activeBtn.classList.add('active');
    }
});