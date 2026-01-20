/**
 * Utility functions for the frontend
 */

class Utils {
    static showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    static showError(message) {
        this.showNotification(message, 'error');
    }

    static showSuccess(message) {
        this.showNotification(message, 'success');
    }

    static formatDate(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
        return new Date(dateString).toLocaleDateString('en-US', options);
    }

    static getStatusColor(status) {
        const colors = {
            'draft': '#6c757d',
            'linearity': '#0dcaf0',
            'accuracy': '#0d6efd',
            'precision': '#6366f1',
            'lod_loq': '#8b5cf6',
            'review': '#fd7e14',
            'approved': '#198754',
            'PASS': '#198754',
            'FAIL': '#dc3545'
        };
        return colors[status] || '#6c757d';
    }

    static stringToColor(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
        }
        const color = (hash & 0x00FFFFFF).toString(16).toUpperCase();
        return '#' + '00000'.substring(0, 6 - color.length) + color;
    }

    static parseValidationResponse(response) {
        return {
            status: response.status,
            metrics: response.metrics || {},
            justification: response.justification || ''
        };
    }

    static displayValidationResult(resultContainer, result) {
        resultContainer.innerHTML = `
            <div class="validation-result">
                <div class="result-header">
                    <h3>Validation Result: <span class="status-badge status-${result.status.toLowerCase()}">${result.status}</span></h3>
                </div>
                <div class="result-metrics">
                    <h4>Metrics:</h4>
                    <ul>
                        ${Object.entries(result.metrics).map(([key, value]) => {
                            if (Array.isArray(value)) {
                                return `<li><strong>${key}:</strong> [${value.join(', ')}]</li>`;
                            }
                            return `<li><strong>${key}:</strong> ${typeof value === 'number' ? value.toFixed(4) : value}</li>`;
                        }).join('')}
                    </ul>
                </div>
                <div class="result-justification">
                    <h4>Justification:</h4>
                    <p>${result.justification}</p>
                </div>
            </div>
        `;
    }

    static isAuthenticated() {
        return localStorage.getItem('auth_token') !== null;
    }

    static getCurrentUser() {
        const user = localStorage.getItem('current_user');
        return user ? JSON.parse(user) : null;
    }

    static getUserRole() {
        const user = this.getCurrentUser();
        return user ? user.role : null;
    }

    static hasRole(requiredRole) {
        const userRole = this.getUserRole();
        const roleHierarchy = { 'analyst': 1, 'reviewer': 2, 'qa': 3 };
        const requiredLevel = roleHierarchy[requiredRole] || 0;
        const userLevel = roleHierarchy[userRole] || 0;
        return userLevel >= requiredLevel;
    }

    static redirectToLogin() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login/';
        }
    }

    static generateChart(canvasId, labels, data, label, backgroundColor = '#0d6efd') {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const canvas = ctx.getContext('2d');
        const width = ctx.width;
        const height = ctx.height;

        // Simple bar chart
        const barWidth = width / (labels.length + 1);
        const maxValue = Math.max(...data);
        const scale = (height - 40) / maxValue;

        canvas.fillStyle = '#f8f9fa';
        canvas.fillRect(0, 0, width, height);

        // Draw axes
        canvas.strokeStyle = '#dee2e6';
        canvas.beginPath();
        canvas.moveTo(30, 20);
        canvas.lineTo(30, height - 20);
        canvas.lineTo(width - 10, height - 20);
        canvas.stroke();

        // Draw bars
        canvas.fillStyle = backgroundColor;
        data.forEach((value, index) => {
            const x = 30 + (index + 1) * barWidth;
            const barHeight = value * scale;
            canvas.fillRect(x, height - 20 - barHeight, barWidth * 0.8, barHeight);
        });

        // Draw labels
        canvas.fillStyle = '#495057';
        canvas.font = '12px Arial';
        canvas.textAlign = 'center';
        labels.forEach((label, index) => {
            const x = 30 + (index + 1) * barWidth + barWidth * 0.4;
            canvas.fillText(label, x, height - 5);
        });
    }
}
