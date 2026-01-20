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

        const response = await fetch(url, {
            ...options,
            headers,
            credentials: 'include'
        });

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
        return this.makeRequest(`/projects/${projectId}/linearity/`, {
            method: 'POST',
            body: JSON.stringify({ concentrations, responses })
        });
    }

    async getLinearity(projectId) {
        return this.makeRequest(`/projects/${projectId}/linearity/`);
    }

    async submitAccuracy(projectId, level, measured_values) {
        return this.makeRequest(`/projects/${projectId}/accuracy/`, {
            method: 'POST',
            body: JSON.stringify({ level, measured_values })
        });
    }

    async getAccuracy(projectId) {
        return this.makeRequest(`/projects/${projectId}/accuracy/`);
    }

    async submitPrecision(projectId, replicate_values) {
        return this.makeRequest(`/projects/${projectId}/precision/`, {
            method: 'POST',
            body: JSON.stringify({ replicate_values })
        });
    }

    async getPrecision(projectId) {
        return this.makeRequest(`/projects/${projectId}/precision/`);
    }

    async submitLODLOQ(projectId, blank_responses, slope) {
        return this.makeRequest(`/projects/${projectId}/lod-loq/`, {
            method: 'POST',
            body: JSON.stringify({ blank_responses, slope })
        });
    }

    async getLODLOQ(projectId) {
        return this.makeRequest(`/projects/${projectId}/lod-loq/`);
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
}

const api = new APIService();
