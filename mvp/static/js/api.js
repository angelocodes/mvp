/**
 * API Service - Handles all communication with Django REST API
 */

class APIService {
    constructor() {
        this.token = this.getStoredToken();
    }

    getStoredToken() {
        return localStorage.getItem('auth_token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
    }

    getCSRFToken() {
        // Try to get from meta tag first
        const token = document.querySelector('meta[name="csrf-token"]');
        if (token) {
            return token.getAttribute('content');
        }
        
        // Fallback to cookie
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    async makeRequest(endpoint, options = {}) {
        const url = `/api${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        // Add CSRF token for POST, PUT, DELETE requests
        const csrfToken = this.getCSRFToken();
        if (csrfToken && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method)) {
            headers['X-CSRFToken'] = csrfToken;
        }

        console.log(`API Request: ${options.method || 'GET'} ${url}`, options.body || '');

        const response = await fetch(url, {
            ...options,
            headers,
            credentials: 'include'
        });

        console.log(`API Response: ${response.status} ${url}`);

        if (response.status === 401) {
            this.clearToken();
            window.location.href = '/login/';
        }

        // Handle 204 No Content responses
        if (response.status === 204) {
            return { status: response.status, data: {} };
        }

        const data = await response.json();
        return { status: response.status, data };
    }

    // Auth endpoints
    async login(username, password) {
        return this.makeRequest('/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    }

    async logout() {
        return this.makeRequest('/auth/logout/', {
            method: 'POST'
        });
    }

    async getCurrentUser() {
        return this.makeRequest('/users/me/');
    }

    // User endpoints
    async getUsers() {
        return this.makeRequest('/users/');
    }

    async createUser(userData) {
        return this.makeRequest('/users/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async updateUser(userId, userData) {
        return this.makeRequest(`/users/${userId}/`, {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    }

    async deleteUser(userId) {
        return this.makeRequest(`/users/${userId}/`, {
            method: 'DELETE'
        });
    }

    // Project endpoints
    async getProjects() {
        return this.makeRequest('/projects/');
    }

    async getProject(projectId) {
        return this.makeRequest(`/projects/${projectId}/`);
    }

    async createProject(projectData) {
        return this.makeRequest('/projects/', {
            method: 'POST',
            body: JSON.stringify(projectData)
        });
    }

    async updateProject(projectId, projectData) {
        return this.makeRequest(`/projects/${projectId}/`, {
            method: 'PUT',
            body: JSON.stringify(projectData)
        });
    }

    async deleteProject(projectId) {
        return this.makeRequest(`/projects/${projectId}/`, {
            method: 'DELETE'
        });
    }

    async startValidation(projectId) {
        return this.makeRequest(`/projects/${projectId}/start-validation/`, {
            method: 'POST'
        });
    }

    async reviewProject(projectId, comment) {
        return this.makeRequest(`/projects/${projectId}/review/`, {
            method: 'POST',
            body: JSON.stringify({ comment })
        });
    }

    async approveProject(projectId) {
        return this.makeRequest(`/projects/${projectId}/approve/`, {
            method: 'POST'
        });
    }

    // Validation endpoints
    async submitLinearity(projectId, concentrations, responses) {
        return this.makeRequest(`/validation/projects/${projectId}/linearity/`, {
            method: 'POST',
            body: JSON.stringify({ concentrations, responses })
        });
    }

    async getLinearity(projectId) {
        return this.makeRequest(`/validation/projects/${projectId}/linearity/`);
    }

    async submitAccuracy(projectId, level, measured_values) {
        return this.makeRequest(`/validation/projects/${projectId}/accuracy/`, {
            method: 'POST',
            body: JSON.stringify({ level, measured_values })
        });
    }

    async getAccuracy(projectId) {
        return this.makeRequest(`/validation/projects/${projectId}/accuracy/`);
    }

    async submitPrecision(projectId, replicate_values) {
        return this.makeRequest(`/validation/projects/${projectId}/precision/`, {
            method: 'POST',
            body: JSON.stringify({ replicate_values })
        });
    }

    async getPrecision(projectId) {
        return this.makeRequest(`/validation/projects/${projectId}/precision/`);
    }

    async submitLODLOQ(projectId, blank_responses, slope) {
        return this.makeRequest(`/validation/projects/${projectId}/lod-loq/`, {
            method: 'POST',
            body: JSON.stringify({ blank_responses, slope })
        });
    }

    async getLODLOQ(projectId) {
        return this.makeRequest(`/validation/projects/${projectId}/lod-loq/`);
    }

    // Report endpoints
    async generateReport(projectId) {
        return this.makeRequest(`/reports/${projectId}/`, {
            method: 'POST'
        });
    }

    async downloadReport(projectId) {
        return `/api/reports/${projectId}/`;
    }

    // Audit endpoints (QA only)
    async getAuditLogs() {
        return this.makeRequest('/audit/');
    }

    async getProjectAuditLogs(projectId) {
        return this.makeRequest(`/audit/${projectId}/`);
    }

    // Workflow endpoint
    async getProjectWorkflow(projectId) {
        return this.makeRequest(`/projects/${projectId}/workflow/`);
    }

    // Document endpoints
    async getDocuments(projectId, stepId = null) {
        const query = stepId ? `?step_id=${stepId}` : '';
        return this.makeRequest(`/validation/projects/${projectId}/documents/${query}`);
    }

    async uploadDocument(projectId, file, fileType = 'other', description = '', validationStepId = null) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('file_type', fileType);
        formData.append('description', description);
        if (validationStepId) {
            formData.append('validation_step_id', validationStepId);
        }

        return this.makeRequest(`/validation/projects/${projectId}/documents/`, {
            method: 'POST',
            body: formData,
            headers: {} // Let browser set Content-Type with boundary for FormData
        });
    }

    async deleteDocument(projectId, documentId) {
        return this.makeRequest(`/validation/projects/${projectId}/documents/${documentId}/`, {
            method: 'DELETE'
        });
    }

    downloadDocument(projectId, documentId) {
        return `/api/validation/projects/${projectId}/documents/${documentId}/download/`;
    }

    // Review endpoints
    async getValidationSummary(projectId) {
        return this.makeRequest(`/validation/projects/${projectId}/summary/`);
    }

    async submitDetailedReview(projectId, reviewData) {
        return this.makeRequest(`/validation/projects/${projectId}/review/`, {
            method: 'POST',
            body: JSON.stringify(reviewData)
        });
    }

    // User Settings endpoints
    async updateProfile(userData) {
        return this.makeRequest('/users/me/profile/', {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    }

    async changePassword(passwords) {
        return this.makeRequest('/users/me/password/', {
            method: 'POST',
            body: JSON.stringify(passwords)
        });
    }

    async getUserStats() {
        return this.makeRequest('/users/me/stats/');
    }

    async getUserStatsById(userId) {
        return this.makeRequest(`/users/${userId}/stats/`);
    }

    async updateUserProfileById(userId, userData) {
        return this.makeRequest(`/users/${userId}/profile/`, {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    }
}

const api = new APIService();
