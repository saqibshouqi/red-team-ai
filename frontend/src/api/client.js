/**
 * API client for Red Team AI backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Experiments API
export const experimentsAPI = {
    create: async (config, runImmediately = false) => {
        const response = await apiClient.post('/experiments/', {
            config,
            run_immediately: runImmediately
        });
        return response.data;
    },

    list: async (skip = 0, limit = 100, status = null) => {
        const params = { skip, limit };
        if (status) params.status = status;
        const response = await apiClient.get('/experiments/', { params });
        return response.data;
    },

    get: async (experimentId) => {
        const response = await apiClient.get(`/experiments/${experimentId}`);
        return response.data;
    },

    run: async (experimentId) => {
        const response = await apiClient.post(`/experiments/${experimentId}/run`);
        return response.data;
    },

    delete: async (experimentId) => {
        const response = await apiClient.delete(`/experiments/${experimentId}`);
        return response.data;
    },

    export: async (experimentId, format = 'json') => {
        const response = await apiClient.get(`/experiments/${experimentId}/export`, {
            params: { format }
        });
        return response.data;
    }
};

// Agents API
export const agentsAPI = {
    getStrategies: async () => {
        const response = await apiClient.get('/agents/strategies');
        return response.data;
    },

    getStrategy: async (strategy) => {
        const response = await apiClient.get(`/agents/strategies/${strategy}`);
        return response.data;
    },

    getModels: async () => {
        const response = await apiClient.get('/agents/models');
        return response.data;
    },

    getMetrics: async () => {
        const response = await apiClient.get('/agents/metrics');
        return response.data;
    }
};

export default apiClient;