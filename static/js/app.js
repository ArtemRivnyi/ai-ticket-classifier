document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('classifyForm');
    const ticketInput = document.getElementById('ticketText');
    const fillSampleBtn = document.getElementById('fillSampleBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    const emptyState = document.getElementById('emptyState');
    const resultContent = document.getElementById('resultContent');

    // Sample tickets
    const samples = [
        "I cannot access my account even though I reset my password. It says 'User not found'.",
        "The billing page is throwing a 500 error when I try to download my invoice.",
        "Can you please add a dark mode to the dashboard? My eyes are hurting.",
        "My internet speed is extremely slow today, I'm only getting 2Mbps.",
        "I was charged twice for the same subscription this month."
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
        } else {
            btn.disabled = false;
            btnText.textContent = 'Classify Ticket';
            btnSpinner.classList.add('hidden');
            btn.classList.remove('opacity-75', 'cursor-not-allowed');
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
    }
});
