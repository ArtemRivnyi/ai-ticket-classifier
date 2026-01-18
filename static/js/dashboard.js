document.addEventListener('DOMContentLoaded', function () {
    const token = localStorage.getItem('jwt_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
    document.getElementById('userEmail').textContent = userInfo.email || 'User';
    document.getElementById('currentTier').textContent = (userInfo.tier || 'Free').toUpperCase();

    // Logout handler
    document.getElementById('logoutBtn').addEventListener('click', function (e) {
        e.preventDefault();
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('user_info');
        window.location.href = '/login';
    });

    // Fetch API Keys
    fetchKeys();

    // Create Key Handler
    document.getElementById('saveKeyBtn').addEventListener('click', async function () {
        const name = document.getElementById('keyName').value;
        if (!name) return;

        try {
            const response = await fetch('/api/v1/auth/keys', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'X-API-Key': 'dummy' // Some endpoints might check this, but JWT auth should bypass or we need to handle it
                },
                body: JSON.stringify({ name })
            });

            const data = await response.json();

            if (response.ok) {
                document.getElementById('createKeyForm').classList.add('d-none');
                document.getElementById('newKeyDisplay').classList.remove('d-none');
                document.getElementById('newKeyValue').value = data.key;
                document.getElementById('saveKeyBtn').style.display = 'none';
                fetchKeys(); // Refresh list
            } else {
                alert(data.error || 'Failed to create key');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred');
        }
    });

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
            tbody.innerHTML = '';

            document.getElementById('activeKeysCount').textContent = data.total || 0;

            if (data.keys) {
                data.keys.forEach(key => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${key.name}</td>
                        <td><code>${key.prefix || '...'}</code></td>
                        <td>${new Date(key.created_at).toLocaleDateString()}</td>
                        <td><span class="badge bg-${key.is_active ? 'success' : 'danger'}">${key.is_active ? 'Active' : 'Inactive'}</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline-danger" onclick="revokeKey('${key.id}')">Revoke</button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
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

    window.startCheckout = async function (tier) {
        try {
            const response = await fetch('/api/v1/billing/create-checkout-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ tier })
            });

            const data = await response.json();

            if (response.ok && data.checkout_url) {
                window.location.href = data.checkout_url;
            } else {
                alert(data.error || 'Failed to start checkout');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred');
        }
    };

    // Check for success/cancel query params
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('success')) {
        alert('Payment successful! Your tier will be updated shortly.');
        // Optionally clear query params
        window.history.replaceState({}, document.title, "/dashboard");
    } else if (urlParams.get('canceled')) {
        alert('Payment canceled.');
        window.history.replaceState({}, document.title, "/dashboard");
    }
});
