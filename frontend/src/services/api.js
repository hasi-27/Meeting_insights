import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: `${API_BASE_URL}/api`,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const meetingsAPI = {
    /**
     * Upload a meeting file
     */
    uploadMeeting: async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/meetings/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },

    /**
     * Get meeting results
     */
    getMeeting: async (meetingId) => {
        return api.get(`/meetings/${meetingId}`);
    },

    /**
     * Process a meeting
     */
    processMeeting: async (meetingId) => {
        return api.post(`/meetings/${meetingId}/process`);
    },

    /**
     * Health check
     */
    healthCheck: async () => {
        return api.get('/health');
    },
};

export default api;
