document.addEventListener('DOMContentLoaded', function () {
    const token = localStorage.getItem('jwt_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    // Modal Logic
    const modal = document.getElementById('createKeyModal');
    const openBtn = document.getElementById('openCreateKeyModalBtn');
    const closeBtn = document.getElementById('closeModalBtn');
    const modalBackdrop = document.getElementById('modalBackdrop');

    function openModal() {
        modal.classList.remove('hidden');
        // Reset form state
        document.getElementById('createKeyForm').classList.remove('hidden');
        document.getElementById('newKeyDisplay').classList.add('hidden');
        document.getElementById('saveKeyBtn').classList.remove('hidden');
        document.getElementById('keyName').value = '';
    }

    function closeModal() {
        modal.classList.add('hidden');
    }

    if (openBtn) openBtn.addEventListener('click', openModal);
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (modalBackdrop) modalBackdrop.addEventListener('click', closeModal);

    // Fetch API Keys
    fetchKeys();

    // Create Key Handler
    const saveKeyBtn = document.getElementById('saveKeyBtn');
    if (saveKeyBtn) {
        saveKeyBtn.addEventListener('click', async function () {
            const name = document.getElementById('keyName').value;
            if (!name) return;

            // Show loading state
            const originalText = saveKeyBtn.textContent;
            saveKeyBtn.textContent = 'Creating...';
            saveKeyBtn.disabled = true;

            try {
                const response = await fetch('/api/v1/auth/keys', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ name })
                });

                const data = await response.json();

                if (response.ok) {
                    document.getElementById('createKeyForm').classList.add('hidden');
                    document.getElementById('newKeyDisplay').classList.remove('hidden');
                    document.getElementById('newKeyValue').value = data.key;
                    saveKeyBtn.classList.add('hidden');
                    fetchKeys(); // Refresh list
                } else {
                    alert(data.error || 'Failed to create key');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred');
            } finally {
                saveKeyBtn.textContent = originalText;
                saveKeyBtn.disabled = false;
            }
        });
    }

    async function fetchKeys() {
        try {
            const response = await fetch('/api/v1/auth/keys', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.status === 401) {
                // Token might be expired or invalid
                localStorage.removeItem('jwt_token');
                window.location.href = '/login';
                return;
            }

            const data = await response.json();
            const tbody = document.getElementById('keysTableBody');
            if (tbody) {
                tbody.innerHTML = '';

                const countEl = document.getElementById('activeKeysCount');
                if (countEl) countEl.textContent = data.total || 0;

                if (data.keys) {
                    data.keys.forEach(key => {
                        const tr = document.createElement('tr');
                        const statusClass = key.is_active
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
                        const statusText = key.is_active ? 'Active' : 'Inactive';

                        tr.innerHTML = `
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900 dark:text-white">${key.name}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500 dark:text-slate-400"><code class="bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">${key.prefix || '...'}</code></td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500 dark:text-slate-400">${new Date(key.created_at).toLocaleDateString()}</td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusClass}">
                                    ${statusText}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500 dark:text-slate-400">
                                <button class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 font-medium transition" onclick="revokeKey('${key.id}')">Revoke</button>
                            </td>
                        `;
                        tbody.appendChild(tr);
                    });
                }
            }
        } catch (error) {
            console.error('Error fetching keys:', error);
        }
    }

    window.revokeKey = async function (keyId) {
        if (!confirm('Are you sure you want to revoke this key?')) return;

        try {
            const response = await fetch(`/api/v1/auth/keys/${keyId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                fetchKeys();
            } else {
                alert('Failed to revoke key');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    };

    // Check for success/cancel query params
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('success')) {
        alert('Payment successful! Your tier will be updated shortly.');
        window.history.replaceState({}, document.title, "/dashboard");
    } else if (urlParams.get('canceled')) {
        alert('Payment canceled.');
        window.history.replaceState({}, document.title, "/dashboard");
    }
});
