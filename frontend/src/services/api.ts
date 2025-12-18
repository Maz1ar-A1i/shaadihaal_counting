import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface Camera {
    id: number;
    name: string;
    rtsp_url: string;
    is_enabled: boolean;
    zones: Zone[];
}

export interface Zone {
    id: number;
    camera_id: number;
    name: string;
    points: number[][]; // [[x,y], [x,y], ...]
}

export const getCameras = async () => (await api.get<Camera[]>('/cameras')).data;
export const createCamera = async (data: any) => (await api.post<Camera>('/cameras', data)).data;
export const deleteCamera = async (id: number) => (await api.delete(`/cameras/${id}`)).data;

export const getZones = async (camId: number) => (await api.get<Zone[]>(`/zones/camera/${camId}`)).data;
export const createZone = async (data: any) => (await api.post<Zone>('/zones', data)).data;
export const deleteZone = async (id: number) => (await api.delete(`/zones/${id}`)).data;

export const getHistory = async () => (await api.get('/stats/history')).data;
export const exportCsv = async () => (await api.get('/stats/export', { responseType: 'blob' }));

export default api;
