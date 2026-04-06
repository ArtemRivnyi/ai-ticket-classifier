document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('classifyForm');
    const ticketInput = document.getElementById('ticketText');
    const btnText = document.getElementById('submitBtnText');
    const btnSpinner = document.getElementById('submitBtnSpinner');
    const emptyState = document.getElementById('emptyState');
    const resultContent = document.getElementById('resultContent');
    const skeletonLoader = document.getElementById('skeletonLoader');
    const highlightedTicketContainer = document.getElementById('highlightedTicketContainer');
    const highlightedTicketText = document.getElementById('highlightedTicketText');
    const systemStatus = document.getElementById('systemStatus');

    // System Status Check
    async function checkSystemStatus() {
        if (!systemStatus) return;
        try {
            const response = await fetch('/api/v1/health');
            if (response.ok) {
                systemStatus.innerHTML = '<span class="text-green-500">●</span> System Ready';
                systemStatus.className = 'ml-3 px-2 py-0.5 rounded text-xs font-medium bg-green-50 text-green-700 hidden md:inline-block border border-green-100';
            } else {
                systemStatus.innerHTML = '<span class="text-red-500">●</span> Degraded';
                systemStatus.className = 'ml-3 px-2 py-0.5 rounded text-xs font-medium bg-red-50 text-red-700 hidden md:inline-block border border-red-100';
            }
        } catch (e) {
            systemStatus.innerHTML = '<span class="text-red-500">●</span> Offline';
            systemStatus.className = 'ml-3 px-2 py-0.5 rounded text-xs font-medium bg-red-50 text-red-700 hidden md:inline-block border border-red-100';
        }
    }
    checkSystemStatus();

    // Mobile Menu Logic
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');

    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', () => {
            navLinks.classList.toggle('hidden');
            navLinks.classList.toggle('flex');

            // Change icon based on state
            const isExpanded = !navLinks.classList.contains('hidden');
            mobileMenuBtn.innerHTML = isExpanded
                ? '<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>'
                : '<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>';
        });
    }

    // Rate Limiting State
    let isProcessing = false;

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

    // Theme Toggle Logic
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const themeToggleMobile = document.getElementById('themeToggleMobile');
    const themeIconMobile = document.getElementById('themeIconMobile');
    const root = document.documentElement;

    function toggleTheme() {
        root.classList.toggle('dark');
        const isDark = root.classList.contains('dark');
        const icon = isDark ? '☀️' : '🌙';

        if (themeIcon) themeIcon.textContent = icon;
        if (themeIconMobile) themeIconMobile.textContent = icon;

        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    if (themeToggleMobile) {
        themeToggleMobile.addEventListener('click', toggleTheme);
    }

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        root.classList.add('dark');
        if (themeIcon) themeIcon.textContent = '☀️';
        if (themeIconMobile) themeIconMobile.textContent = '☀️';
    }

    // Analytics Tracking
    function trackClassification(category) {
        // Placeholder for analytics
        console.log(`[Analytics] Classification Event: ${category}`);
        if (window.gtag) {
            gtag('event', 'classify', {
                'event_category': 'ticket_classification',
                'event_label': category
            });
        }
    }

    // Sample tickets covering all categories
    const samples = [
        "I cannot log in. The verification code is invalid.",
        "Reset link expired before I could use it.",
        "My account has been locked after too many failed attempts.",
        "I was charged twice for the same subscription.",
        "Invoice says $100 but processor charged $150.",
        "Camera stopped working after firmware update.",
        "My laptop screen is flickering and goes black randomly.",
        "Slack integration only sends alerts to half of our team.",
        "VPN keeps disconnecting every few minutes.",
        "Internet connection drops every 10 minutes exactly.",
        "App crashes when trying to export PDF reports.",
        "Can you add dark mode support to the mobile app?"
    ];

    // Dynamic Example Buttons
    const exampleButtonsData = [
        { text: "Network Issue", description: "My internet connection keeps dropping every few minutes" },
        { text: "Password Reset", description: "I forgot my password and need to reset it" },
        { text: "Hardware Issue", description: "The printer is jammed and showing error code E503" },
        { text: "Billing Query", description: "Need clarification on last month's invoice charges" }
    ];

    const exampleButtonsContainer = document.getElementById('exampleButtonsContainer');
    if (exampleButtonsContainer) {
        exampleButtonsContainer.innerHTML = ''; // Clear existing

        exampleButtonsData.forEach(btn => {
            const button = document.createElement('button');
            button.className = 'example-btn text-xs px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg transition';
            button.textContent = btn.text;
            button.onclick = () => loadExample(btn.description);
            exampleButtonsContainer.appendChild(button);
        });

        // Add Random Button
        const randomBtn = document.createElement('button');
        randomBtn.className = 'example-btn text-xs px-3 py-1.5 bg-indigo-100 hover:bg-indigo-200 text-indigo-700 rounded-lg transition font-medium';
        randomBtn.innerHTML = '🎲 Random Example';

        // Define function before usage or ensure it's available
        const loadRandomExample = () => {
            const randomSample = samples[Math.floor(Math.random() * samples.length)];
            if (ticketInput) {
                ticketInput.value = randomSample;
                ticketInput.focus();
            }
        };

        randomBtn.onclick = loadRandomExample;
        exampleButtonsContainer.appendChild(randomBtn);
    }

    // Reset View Helper
    window.resetView = function () {
        if (document.getElementById('batchResultContent')) {
            document.getElementById('batchResultContent').classList.add('hidden');
        }
        if (document.getElementById('resultContent')) {
            document.getElementById('resultContent').classList.add('hidden');
        }
        if (document.getElementById('emptyState')) {
            document.getElementById('emptyState').classList.remove('hidden');
        }
        if (document.getElementById('ticketText')) {
            document.getElementById('ticketText').value = '';
            document.getElementById('ticketText').disabled = false;
        }
    };

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Rate Limiting Check
        if (isProcessing) {
            showToast('Please wait for the current classification to complete.', 'error');
            return;
        }

        const text = ticketInput.value.trim();
        if (!text) return;

        // UI Loading State
        setLoading(true);

        try {
            const apiKey = window.DEMO_API_KEY;

            const response = await fetch('/api/v1/classify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': apiKey
                },
                body: JSON.stringify({ ticket: text, no_cache: true })
            });

            // Network error handling (response.ok check)
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            displayResult(data);
            addToHistory(data, text);
            trackClassification(data.category);
            showToast('Classification successful', 'success');
            setLoading(false);

        } catch (error) {
            console.error('Classification Error:', error);
            // Show specific error message to help debugging
            showToast(`Classification failed: ${error.message}`, 'error');
            setLoading(false);
            // Ensure empty state is visible if no result is shown
            if (resultContent.classList.contains('hidden')) {
                emptyState.classList.remove('hidden');
            }
        }
    });

    function setLoading(isLoading) {
        isProcessing = isLoading; // Update rate limiting flag

        if (isLoading) {
            if (btnText) btnText.textContent = 'Processing...';
            if (btnSpinner) btnSpinner.classList.remove('hidden');
            if (ticketInput) ticketInput.disabled = true;

            // Immediately hide result and show skeleton
            if (resultContent) resultContent.classList.add('hidden');
            if (document.getElementById('batchResultContent')) {
                document.getElementById('batchResultContent').classList.add('hidden');
            }
            if (emptyState) emptyState.classList.add('hidden');
            if (skeletonLoader) skeletonLoader.classList.remove('hidden');

        } else {
            if (btnText) btnText.textContent = 'Classify Ticket';
            if (btnSpinner) btnSpinner.classList.add('hidden');
            if (ticketInput) ticketInput.disabled = false;

            // Always hide skeleton when loading completes
            if (skeletonLoader) skeletonLoader.classList.add('hidden');
        }
    }

    function displayResult(data) {
        // Hide skeleton first
        if (skeletonLoader) skeletonLoader.classList.add('hidden');

        // Hide empty state
        if (emptyState) emptyState.classList.add('hidden');

        // Hide batch results if open
        if (document.getElementById('batchResultContent')) {
            document.getElementById('batchResultContent').classList.add('hidden');
        }

        // Always show result content
        if (resultContent) {
            resultContent.classList.remove('hidden');
            resultContent.classList.remove('opacity-0');
        }

        // Update highlighted ticket
        if (highlightedTicketContainer && highlightedTicketText) {
            const ticketValue = ticketInput.value.trim();
            if (ticketValue) {
                highlightedTicketText.textContent = ticketValue;
                highlightedTicketContainer.classList.remove('hidden');
            }
        }

        // Update fields with safety checks
        if (document.getElementById('resCategory')) document.getElementById('resCategory').textContent = data.category || 'Unknown';

        // Confidence color
        const confidenceEl = document.getElementById('resConfidence');
        if (confidenceEl) {
            const confidenceVal = data.confidence !== undefined ? data.confidence : 0;
            const confidence = (confidenceVal * 100).toFixed(0);
            confidenceEl.textContent = `${confidence}% Confidence`;

            if (confidence > 80) {
                confidenceEl.className = 'ml-3 px-2.5 py-0.5 rounded-full text-sm font-medium bg-green-100 text-green-800';
            } else if (confidence > 50) {
                confidenceEl.className = 'ml-3 px-2.5 py-0.5 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800';
            } else {
                confidenceEl.className = 'ml-3 px-2.5 py-0.5 rounded-full text-sm font-medium bg-red-100 text-red-800';
            }
        }

        // Priority color
        const priorityEl = document.getElementById('resPriority');
        if (priorityEl) {
            priorityEl.textContent = data.priority || 'Medium';
            if (data.priority === 'High' || data.priority === 'Critical') {
                priorityEl.className = 'inline-flex items-center px-3 py-1 rounded-lg text-base font-medium bg-red-100 text-red-800';
            } else if (data.priority === 'Medium') {
                priorityEl.className = 'inline-flex items-center px-3 py-1 rounded-lg text-base font-medium bg-yellow-100 text-yellow-800';
            } else {
                priorityEl.className = 'inline-flex items-center px-3 py-1 rounded-lg text-base font-medium bg-green-100 text-green-800';
            }
        }

        if (document.getElementById('resTime')) document.getElementById('resTime').textContent = `${(data.processing_time || 0).toFixed(3)}s`;
        if (document.getElementById('resProvider')) document.getElementById('resProvider').textContent = data.provider || 'AI';
        if (document.getElementById('resReqId')) {
            document.getElementById('resReqId').textContent = data.request_id || '';
            document.getElementById('resReqId').title = data.request_id || '';
        }

        // Show matched pattern if available
        if (highlightedTicketContainer && highlightedTicketText) {
            if (data.matched_pattern) {
                highlightedTicketContainer.classList.remove('hidden');
                highlightedTicketText.textContent = data.matched_pattern;
            } else {
                highlightedTicketContainer.classList.add('hidden');
            }
        }

        // Reset feedback section
        if (document.getElementById('feedbackSection')) document.getElementById('feedbackSection').classList.remove('hidden');
        if (document.getElementById('feedbackConfirmation')) document.getElementById('feedbackConfirmation').classList.add('hidden');
    }

    // History Management
    loadHistory();
    if (document.getElementById('clearHistoryBtn')) {
        document.getElementById('clearHistoryBtn').addEventListener('click', clearHistory);
    }

    function addToHistory(data, text) {
        try {
            const historyItem = {
                text: text,
                category: data.category || 'Unknown',
                priority: data.priority || 'Medium',
                timestamp: new Date().toISOString()
            };

            let history = JSON.parse(localStorage.getItem('classificationHistory') || '[]');
            history.unshift(historyItem);
            if (history.length > 50) history.pop();
            localStorage.setItem('classificationHistory', JSON.stringify(history));

            renderHistory(history);
        } catch (e) {
            console.error('Failed to save history:', e);
        }
    }

    function loadHistory() {
        try {
            const history = JSON.parse(localStorage.getItem('classificationHistory') || '[]');
            renderHistory(history);
        } catch (e) {
            console.error('Failed to load history:', e);
        }
    }

    function renderHistory(history) {
        const historyList = document.getElementById('historyList');
        if (!historyList) return;

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

    // Expose sendFeedback to global scope
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
    };

    // Alias for backward compatibility
    window.loadExample = window.tryExample;



    // CSV Upload Handler
    const csvForm = document.getElementById('csvUploadForm');
    if (csvForm) {
        csvForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('csvFile');
            const file = fileInput.files[0];

            if (!file) {
                showToast('Please select a CSV file', 'error');
                return;
            }

            // File Size Validation (5MB)
            if (file.size > 5 * 1024 * 1024) {
                showToast('File too large. Maximum size is 5MB.', 'error');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            const btn = csvForm.querySelector('button');
            const originalText = btn.textContent;
            btn.textContent = 'Processing...';
            btn.disabled = true;

            // Show loading state in main area
            if (emptyState) emptyState.classList.add('hidden');
            if (resultContent) resultContent.classList.add('hidden');
            if (document.getElementById('batchResultContent')) document.getElementById('batchResultContent').classList.add('hidden');
            if (skeletonLoader) skeletonLoader.classList.remove('hidden');

            try {
                const apiKey = window.DEMO_API_KEY;

                const response = await fetch('/api/v1/classify/batch-csv', {
                    method: 'POST',
                    headers: {
                        'X-API-Key': apiKey
                    },
                    body: formData
                });

                const data = await response.json();

                if (response.ok) {
                    showToast(`Processed ${data.total} tickets successfully!`, 'success');

                    // Render Batch Results
                    const batchContainer = document.getElementById('batchResultContent');
                    const batchList = document.getElementById('batchList');
                    const batchSummary = document.getElementById('batchSummary');

                    if (batchContainer && batchList) {
                        batchSummary.textContent = `Processed ${data.total} tickets (${data.successful} success, ${data.failed} failed) in ${data.processing_time}s`;
                        batchList.innerHTML = '';

                        // Combine results and errors for display
                        const allItems = [
                            ...data.results.map(r => ({ ...r, status: 'success' })),
                            ...data.errors.map(e => ({ ...e, status: 'error' }))
                        ];

                        allItems.forEach(item => {
                            const div = document.createElement('div');
                            div.className = 'p-3 rounded-lg border text-sm ' +
                                (item.status === 'success'
                                    ? 'bg-white border-slate-200 dark:bg-slate-800 dark:border-slate-700'
                                    : 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800');

                            if (item.status === 'success') {
                                div.innerHTML = `
                                    <div class="flex justify-between mb-1">
                                        <span class="font-semibold text-slate-900 dark:text-white">${item.category}</span>
                                        <span class="text-xs text-slate-500">${(item.confidence * 100).toFixed(0)}%</span>
                                    </div>
                                    <p class="text-slate-600 dark:text-slate-400 truncate">${item.ticket || 'Ticket text'}</p>
                                `;
                            } else {
                                div.innerHTML = `
                                    <div class="font-semibold text-red-600 dark:text-red-400 mb-1">Error</div>
                                    <p class="text-slate-600 dark:text-slate-400 truncate">${item.ticket || 'Ticket text'}</p>
                                    <p class="text-xs text-red-500 mt-1">${item.error}</p>
                                `;
                            }
                            batchList.appendChild(div);
                        });

                        skeletonLoader.classList.add('hidden');
                        batchContainer.classList.remove('hidden');
                    }

                } else {
                    throw new Error(data.error || 'Batch processing failed');
                }
            } catch (error) {
                console.error('Batch error:', error);
                showToast(`Batch failed: ${error.message}`, 'error');
                skeletonLoader.classList.add('hidden');
                emptyState.classList.remove('hidden');
            } finally {
                btn.textContent = originalText;
                btn.disabled = false;
                fileInput.value = '';
            }
        });
    }
});
