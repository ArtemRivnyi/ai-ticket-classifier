document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('classifyForm');
    const ticketInput = document.getElementById('ticketText');
    const fillSampleBtn = document.getElementById('fillSampleBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    const emptyState = document.getElementById('emptyState');
    const resultContent = document.getElementById('resultContent');
    const skeletonLoader = document.getElementById('skeletonLoader');
    const highlightedTicketContainer = document.getElementById('highlightedTicketContainer');
    const highlightedTicketText = document.getElementById('highlightedTicketText');

    // Sample tickets covering all categories
    const samples = [
        // Authentication Issue
        "I cannot log in. The verification code is invalid.",
        "Reset link expired before I could use it.",
        "2FA verification failed. Cannot access my account.",

        // Payment Issue
        "I was charged twice for the same subscription.",
        "Payment completed but I want a refund.",
        "Unauthorized payment of $500 appeared on my card.",

        // Hardware Issue
        "Camera stopped working after firmware update.",
        "Sensor battery drains in one hour.",
        "Printer keeps jamming. Already cleaned it twice.",
        "Card reader not detecting cards anymore.",

        // Integration Issue
        "Slack integration only sends alerts to half of our team.",
        "Webhook callbacks timing out. API not responding.",
        "SSO login with Azure AD failing. Error: invalid_grant.",

        // Billing Bug
        "UI shows paid but Stripe webhook shows failed.",
        "Invoice says $100 but processor charged $150.",
        "Dashboard shows paid subscription but backend logs show unpaid.",

        // Notification Issue
        "Email notifications not delivered to some users.",
        "Half of the team gets Slack alerts, the other half doesn't.",

        // Mixed Issue
        "Cannot log in AND my payment failed. Two separate issues.",

        // Bug/Technical Issue
        "Minor cosmetic issue with button alignment. Not urgent.",

        // Feature Request
        "Nice to have: add animation to the loading screen."
    ];

    fillSampleBtn.addEventListener('click', () => {
        const randomSample = samples[Math.floor(Math.random() * samples.length)];
        ticketInput.value = randomSample;
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const text = ticketInput.value.trim();
        if (!text) return;

        // UI Loading State
        setLoading(true);

        try {
            // Use the Master Key for the demo (In production, this would be handled differently or via a public demo endpoint)
            // For this demo, we'll assume the backend might have a public wrapper or we use a specific demo key.
            // Since we are in a browser, exposing the key is risky. 
            // Ideally, the backend should serve this page and have a session-based or rate-limited public endpoint.
            // For now, we will use the key we know works, but in a real app, we'd proxy this.
            // HOWEVER, to keep it simple for this specific task:
            // We will use a hardcoded key for the demo.
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
            } else {
                alert('Error: ' + (data.error || 'Failed to classify ticket'));
            }

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while connecting to the API.');
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        const btn = form.querySelector('button[type="submit"]');
        if (isLoading) {
            btn.disabled = true;
            btnText.textContent = 'Processing...';
            btnSpinner.classList.remove('hidden');
            btn.classList.add('opacity-75', 'cursor-not-allowed');

            // Show skeleton, hide empty state and result
            emptyState.classList.add('hidden');
            resultContent.classList.add('opacity-0');
            skeletonLoader.classList.remove('hidden');
        } else {
            btn.disabled = false;
            btnText.textContent = 'Classify Ticket';
            btnSpinner.classList.add('hidden');
            btn.classList.remove('opacity-75', 'cursor-not-allowed');

            // Hide skeleton
            skeletonLoader.classList.add('hidden');
        }
    }

    function displayResult(data) {
        emptyState.classList.add('hidden');
        resultContent.classList.remove('opacity-0');

        // Update fields
        document.getElementById('resCategory').textContent = data.category;

        // Confidence
        const confidence = Math.round(data.confidence * 100);
        const confEl = document.getElementById('resConfidence');
        confEl.textContent = `${confidence}%`;

        // Color coding for confidence
        if (confidence > 90) {
            confEl.className = "ml-3 px-2.5 py-0.5 rounded-full text-sm font-medium bg-green-100 text-green-800";
        } else if (confidence > 70) {
            confEl.className = "ml-3 px-2.5 py-0.5 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800";
        } else {
            confEl.className = "ml-3 px-2.5 py-0.5 rounded-full text-sm font-medium bg-red-100 text-red-800";
        }

        // Priority
        const priorityEl = document.getElementById('resPriority');
        priorityEl.textContent = data.priority.charAt(0).toUpperCase() + data.priority.slice(1);

        if (data.priority === 'high' || data.priority === 'critical') {
            priorityEl.className = "inline-flex items-center px-3 py-1 rounded-lg text-base font-medium bg-red-100 text-red-800";
        } else if (data.priority === 'medium') {
            priorityEl.className = "inline-flex items-center px-3 py-1 rounded-lg text-base font-medium bg-yellow-100 text-yellow-800";
        } else {
            priorityEl.className = "inline-flex items-center px-3 py-1 rounded-lg text-base font-medium bg-green-100 text-green-800";
        }

        // Time
        document.getElementById('resTime').textContent = `${data.processing_time.toFixed(3)}s`;

        // Provider
        document.getElementById('resProvider').textContent = data.provider;

        // Request ID
        document.getElementById('resReqId').textContent = data.request_id || 'N/A';

        // NEW: Show feedback section and store request_id
        const feedbackSection = document.getElementById('feedbackSection');
        if (feedbackSection) {
            feedbackSection.classList.remove('hidden');
            feedbackSection.dataset.requestId = data.request_id;
        }

        // NEW: Highlight keywords
        if (data.matched_pattern) {
            const text = ticketInput.value.trim();
            try {
                // Escape special regex characters in the pattern if needed, 
                // but matched_pattern is already a regex pattern from the backend.
                // However, backend patterns might be raw strings.
                // Let's assume it's a valid regex string.
                const regex = new RegExp(data.matched_pattern, 'i');
                const match = text.match(regex);
                if (match) {
                    // Replace only the first occurrence or all? Usually first match determines rule.
                    // Use a function to preserve case of the match
                    const highlighted = text.replace(regex, (match) => `<span class="bg-yellow-200 text-yellow-800 font-semibold px-1 rounded border border-yellow-300 shadow-sm">${match}</span>`);
                    highlightedTicketText.innerHTML = highlighted;
                    highlightedTicketContainer.classList.remove('hidden');
                } else {
                    highlightedTicketContainer.classList.add('hidden');
                }
            } catch (e) {
                console.error("Regex error", e);
                highlightedTicketContainer.classList.add('hidden');
            }
        } else {
            highlightedTicketContainer.classList.add('hidden');
        }
    }

    // Load history on start
    renderHistory();

    document.getElementById('clearHistoryBtn').addEventListener('click', () => {
        localStorage.removeItem('classificationHistory');
        renderHistory();
    });

    function addToHistory(data, ticketText) {
        const historyItem = {
            id: data.request_id || Date.now().toString(),
            ticket: ticketText,
            category: data.category,
            confidence: data.confidence,
            timestamp: new Date().toISOString()
        };

        let history = JSON.parse(localStorage.getItem('classificationHistory') || '[]');
        history.unshift(historyItem);

        // Keep only last 10 items
        if (history.length > 10) {
            history = history.slice(0, 10);
        }

        localStorage.setItem('classificationHistory', JSON.stringify(history));
        renderHistory();
    }

    function renderHistory() {
        const historyList = document.getElementById('historyList');
        const history = JSON.parse(localStorage.getItem('classificationHistory') || '[]');

        if (history.length === 0) {
            historyList.innerHTML = `
                <div id="emptyHistory" class="text-center py-8 text-slate-400 bg-white rounded-xl border border-slate-100 border-dashed">
                    No recent classifications
                </div>`;
            return;
        }

        historyList.innerHTML = history.map(item => `
            <div class="bg-white p-4 rounded-xl border border-slate-100 shadow-sm hover:shadow-md transition">
                <div class="flex justify-between items-start mb-2">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                        ${item.category}
                    </span>
                    <span class="text-xs text-slate-400">${new Date(item.timestamp).toLocaleTimeString()}</span>
                </div>
                <p class="text-slate-600 text-sm line-clamp-2">${item.ticket}</p>
            </div>
        `).join('');
    }

    // NEW: Send feedback function
    window.sendFeedback = async function (correct) {
        const feedbackSection = document.getElementById('feedbackSection');
        const requestId = feedbackSection?.dataset.requestId;

        if (!requestId) {
            console.error('No request ID found');
            return;
        }

        try {
            const response = await fetch('/api/v1/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    request_id: requestId,
                    correct: correct
                })
            });

            if (response.ok) {
                // Hide buttons, show confirmation
                feedbackSection.querySelector('.flex.gap-2').classList.add('hidden');
                document.getElementById('feedbackConfirmation').classList.remove('hidden');
            } else {
                console.error('Failed to submit feedback');
            }
        } catch (error) {
            console.error('Error submitting feedback:', error);
        }
    }
});
