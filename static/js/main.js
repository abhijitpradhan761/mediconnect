/**
 * MediConnect Frontend Utility JavaScript
 * Handles alert dismissal, interactive tooltips, and dynamic UI elements.
 */

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alert banners after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // Initialize Bootstrap tooltips if any
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Dynamic unread notification counter
    const notifPill = document.getElementById('unread-notif-pill');
    if (notifPill) {
        fetch('/api/notifications/unread-count/')
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                return null;
            })
            .then(data => {
                if (data && data.unread_count > 0) {
                    notifPill.textContent = data.unread_count > 99 ? '99+' : data.unread_count;
                    notifPill.style.display = 'inline-block';
                } else if (notifPill) {
                    notifPill.style.display = 'none';
                }
            })
            .catch(() => {
                // Silently ignore if unauthenticated or endpoint not active
            });
    }

    console.log('MediConnect core scripts initialized successfully.');
});
