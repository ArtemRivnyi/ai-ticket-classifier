document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('classifyForm');
    const ticketInput = document.getElementById('ticketText');
    const fillSampleBtn = document.getElementById('fillSampleBtn'); // May not exist
    const btnText = document.getElementById('submitBtnText'); // Updated ID
    const btnSpinner = document.getElementById('submitBtnSpinner'); // Updated ID
    const emptyState = document.getElementById('emptyState');
    const resultContent = document.getElementById('resultContent');
    const skeletonLoader = document.getElementById('skeletonLoader');
    const highlightedTicketContainer = document.getElementById('highlightedTicketContainer');
    const highlightedTicketText = document.getElementById('highlightedTicketText');
    const systemStatus = document.getElementById('systemStatus');

    // Toast Notification System
    function showToast(message, type = 'error') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');

        const colors = type === 'success' ? 'bg-green-500' : 'bg-red-500';
        const icon = type === 'success' ? '✅' : '⚠️';

        toast.className = `toast flex items-center w-full max-w-xs p-4 mb-4 text-white rounded-lg shadow ${colors}`;
        toast.innerHTML = `
            <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 text-white rounded-lg bg-white/20">
                ${icon}
            </div>
            <div class="ml-3 text-sm font-normal">${message}</div>
            <button type="button" class="ml-auto -mx-1.5 -my-1.5 bg-white/20 text-white hover:text-gray-100 rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 hover:bg-white/30 inline-flex h-8 w-8" aria-label="Close" onclick="this.parentElement.remove()">
                <span class="sr-only">Close</span>
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
            </button>
        `;

        container.appendChild(toast);

        // Trigger animation
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        // Auto remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    // Health Check
    async function checkSystemHealth() {
        try {
            const response = await fetch('/api/v1/health');
            if (response.ok) {
                systemStatus.innerHTML = '● System Online';
                systemStatus.className = 'ml-3 px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800';
            } else {
                throw new Error('Health check failed');
            }
        } catch (error) {
            console.error('System health check failed:', error);
            systemStatus.innerHTML = '● System Offline';
            systemStatus.className = 'ml-3 px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800';
            showToast('Cannot connect to server. Please try again later.', 'error');
        }
    }

    // Run health check on load
    checkSystemHealth();

    // Sample tickets covering all categories
    const samples = [
        "I cannot log in. The verification code is invalid.",
        "Reset link expired before I could use it.",
        "I was charged twice for the same subscription.",
        "Camera stopped working after firmware update.",
        "Slack integration only sends alerts to half of our team.",
        "Invoice says $100 but processor charged $150.",
        "Email notifications not delivered to some users.",
        "Cannot log in AND my payment failed. Two separate issues.",
        "Nice to have: add animation to the loading screen."
    ];

    // Quick Try Buttons
    document.querySelectorAll('.quick-try-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            ticketInput.value = btn.dataset.text;
            // Optional: Auto-submit or highlight
            ticketInput.focus();
        });
    });

    // Example ticket buttons
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            ticketInput.value = btn.dataset.text;
            ticketInput.focus();
        });
    });

    // Legacy fill sample button (hidden but kept for compatibility if needed)
    if (fillSampleBtn) {
        fillSampleBtn.addEventListener('click', () => {
            const randomSample = samples[Math.floor(Math.random() * samples.length)];
            ticketInput.value = randomSample;
        });
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const text = ticketInput.value.trim();
        if (!text) return;

        // UI Loading State
        setLoading(true);

        try {
            const apiKey = "sk_ORulUQRLvLHAueF3Ht1gXj9gTsY7xme3QD-UeVrO8nY";

            const response = await fetch('/api/v1/classify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': apiKey
                },
                body: JSON.stringify({ ticket: text })
            });

            const data = await response.json();

            if (response.ok) {
                displayResult(data);
                addToHistory(data, text);
                showToast('Classification successful', 'success');
            } else {
                showToast(data.error || 'Failed to classify ticket', 'error');
                setLoading(false); // Reset loading state on error
                // Ensure empty state is visible if no result is shown
                if (resultContent.classList.contains('hidden')) {
                    emptyState.classList.remove('hidden');
                }
            }

        } catch (error) {
            console.error('Error:', error);
            showToast('An error occurred while connecting to the API.', 'error');
            setLoading(false);
            // Ensure empty state is visible if no result is shown
            if (resultContent.classList.contains('hidden')) {
                emptyState.classList.remove('hidden');
            }
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            if (btnText) btnText.textContent = 'Processing...';
            if (btnSpinner) btnSpinner.classList.remove('hidden');
            if (fillSampleBtn) fillSampleBtn.disabled = true;
            if (ticketInput) ticketInput.disabled = true;

            // Show skeleton, hide others
            if (emptyState) emptyState.classList.add('hidden');
            if (resultContent) resultContent.classList.add('hidden');
            if (skeletonLoader) skeletonLoader.classList.remove('hidden');
        } else {
            if (btnText) btnText.textContent = 'Classify Ticket';
            if (btnSpinner) btnSpinner.classList.add('hidden');
            if (fillSampleBtn) fillSampleBtn.disabled = false;
            if (ticketInput) ticketInput.disabled = false;

            // Hide skeleton
            if (skeletonLoader) skeletonLoader.classList.add('hidden');
        }
    }

    function displayResult(data) {
        // Hide skeleton
        skeletonLoader.classList.add('hidden');
        // Show result
        resultContent.classList.remove('hidden');
        // Trigger reflow to enable transition
        void resultContent.offsetWidth;
        resultContent.classList.remove('opacity-0');

        // Update fields
        document.getElementById('resCategory').textContent = data.category;

        // Confidence color
        const confidenceEl = document.getElementById('resConfidence');
        const confidence = (data.confidence * 100).toFixed(0);
        confidenceEl.textContent = `${confidence}%`;

        if (confidence > 80) {
            confidenceEl.className = 'ml-3 px-2.5 py-0.5 rounded-full text-sm font-medium bg-green-100 text-green-800';
        } else if (confidence > 50) {
            confidenceEl.className = 'ml-3 px-2.5 py-0.5 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800';
        } else {
            confidenceEl.className = 'ml-3 px-2.5 py-0.5 rounded-full text-sm font-medium bg-red-100 text-red-800';
        }

        // Priority color
        const priorityEl = document.getElementById('resPriority');
        priorityEl.textContent = data.priority;
        if (data.priority === 'High' || data.priority === 'Critical') {
            priorityEl.className = 'inline-flex items-center px-3 py-1 rounded-lg text-base font-medium bg-red-100 text-red-800';
        } else if (data.priority === 'Medium') {
            priorityEl.className = 'inline-flex items-center px-3 py-1 rounded-lg text-base font-medium bg-yellow-100 text-yellow-800';
        } else {
            priorityEl.className = 'inline-flex items-center px-3 py-1 rounded-lg text-base font-medium bg-green-100 text-green-800';
        }

        document.getElementById('resTime').textContent = `${data.processing_time.toFixed(3)}s`;
        document.getElementById('resProvider').textContent = data.provider;
        document.getElementById('resReqId').textContent = data.request_id;
        document.getElementById('resReqId').title = data.request_id;

        // Show matched pattern if available
        if (data.matched_pattern) {
            highlightedTicketContainer.classList.remove('hidden');
            highlightedTicketText.textContent = data.matched_pattern;
        } else {
            highlightedTicketContainer.classList.add('hidden');
        }

        // Reset feedback section
        document.getElementById('feedbackSection').classList.remove('hidden');
        document.getElementById('feedbackConfirmation').classList.add('hidden');

        setLoading(false);
    }

    // History Management
    loadHistory();
    document.getElementById('clearHistoryBtn').addEventListener('click', clearHistory);

    function addToHistory(data, text) {
        const historyItem = {
            text: text,
            category: data.category,
            priority: data.priority,
            timestamp: new Date().toISOString()
        };

        let history = JSON.parse(localStorage.getItem('classificationHistory') || '[]');
        history.unshift(historyItem);
        if (history.length > 10) history.pop(); // Keep last 10
        localStorage.setItem('classificationHistory', JSON.stringify(history));

        renderHistory(history);
    }

    function loadHistory() {
        const history = JSON.parse(localStorage.getItem('classificationHistory') || '[]');
        renderHistory(history);
    }

    function renderHistory(history) {
        const historyList = document.getElementById('historyList');
        historyList.innerHTML = '';

        if (history.length === 0) {
            historyList.innerHTML = '<p class="text-slate-400 col-span-full text-center">No history yet.</p>';
            return;
        }

        history.forEach(item => {
            const date = new Date(item.timestamp).toLocaleTimeString();
            const el = document.createElement('div');
            el.className = 'bg-white p-4 rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition';

            let priorityColor = 'bg-gray-100 text-gray-800';
            if (item.priority === 'High' || item.priority === 'Critical') priorityColor = 'bg-red-100 text-red-800';
            else if (item.priority === 'Medium') priorityColor = 'bg-yellow-100 text-yellow-800';
            else priorityColor = 'bg-green-100 text-green-800';

            el.innerHTML = `
                <div class="flex justify-between items-start mb-2">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                        ${item.category}
                    </span>
                    <span class="text-xs text-slate-400">${date}</span>
                </div>
                <p class="text-slate-600 text-sm line-clamp-2 mb-3" title="${item.text}">${item.text}</p>
                <div class="flex items-center justify-between">
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${priorityColor}">
                        ${item.priority}
                    </span>
                </div>
            `;
            historyList.appendChild(el);
        });
    }

    function clearHistory() {
        localStorage.removeItem('classificationHistory');
        renderHistory([]);
        showToast('History cleared', 'success');
    }

    // Expose sendFeedback to global scope for onclick
    // Expose sendFeedback to global scope for onclick
    window.sendFeedback = async function (isCorrect) {
        document.getElementById('feedbackConfirmation').classList.remove('hidden');

        const reqId = document.getElementById('resReqId').textContent;
        const ticketText = document.getElementById('ticketText').value;
        const category = document.getElementById('resCategory').textContent;

        try {
            await fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    request_id: reqId,
                    ticket: ticketText,
                    predicted: category,
                    correct: isCorrect
                })
            });
            showToast('Thanks for your feedback!', 'success');
        } catch (error) {
            console.error('Error sending feedback:', error);
            showToast('Failed to save feedback', 'error');
        }
    };

    // Expose tryExample to global scope
    window.tryExample = function (text) {
        ticketInput.value = text;
        ticketInput.focus();
        // Optional: Auto-submit
        // form.dispatchEvent(new Event('submit'));
    };

    // Alias for backward compatibility
    window.loadExample = window.tryExample;


    // CSV Upload Handler
    const csvForm = document.getElementById('csvForm');
    if (csvForm) {
        csvForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('csvFile');
            const file = fileInput.files[0];

            if (!file) {
                showToast('Please select a CSV file', 'error');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            const btn = csvForm.querySelector('button');
            const originalText = btn.textContent;
            btn.textContent = 'Processing...';
            btn.disabled = true;

            try {
                const apiKey = "sk_ORulUQRLvLHAueF3Ht1gXj9gTsY7xme3QD-UeVrO8nY";
                const response = await fetch('/api/classify/batch', {
                    method: 'POST',
                    headers: {
                        'X-API-Key': apiKey
                    },
                    body: formData
                });

                const data = await response.json();

                if (response.ok) {
                    showToast(`Processed ${data.total} tickets successfully!`, 'success');
                    console.log('Batch results:', data.results);
                    // In a real app, we would display these results in a table/modal
                    // For MVP, just showing toast and logging is fine, or we could alert
                    alert(`Batch processing complete!\nTotal: ${data.total}\nCheck console for details.`);
                } else {
                    showToast(data.error || 'Batch processing failed', 'error');
                }
            } catch (error) {
                console.error('Batch error:', error);
                showToast('Error uploading file', 'error');
            } finally {
                btn.textContent = originalText;
                btn.disabled = false;
                fileInput.value = '';
            }
        });
    }
});
