import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_URL,
});

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload', formData);
  return response.data;
};

export const getTaskStatus = async (taskId) => {
  const response = await api.get(`/task/${taskId}`);
  return response.data;
};

export const getQueueStatus = async () => {
    try {
      const response = await api.get('/queue_status');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch queue status:', error);
      throw error;
    }
};

export const downloadFile = (taskId) => {
  return `${API_URL}/download/${taskId}`;
};

export const getHistoricalRequet = async (page, page_size=10) =>{
  const response = await axios.get(`/tasks?page=${page}&per_page=${page_size}`);
  return response.data;
}