import { useEffect, useState } from 'react';
import { getCameras, createCamera, deleteCamera } from '../services/api';
import type { Camera } from '../services/api';

interface CameraManagerProps {
    onEditZones: (id: number) => void;
}

export default function CameraManager({ onEditZones }: CameraManagerProps) {
    const [cameras, setCameras] = useState<Camera[]>([]);
    const [isAdding, setIsAdding] = useState(false);
    const [newCam, setNewCam] = useState({ name: '', rtsp_url: '', is_enabled: true });

    useEffect(() => {
        loadCameras();
    }, []);

    const loadCameras = async () => {
        const data = await getCameras();
        setCameras(data);
    };

    const handleAdd = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await createCamera(newCam);
            setNewCam({ name: '', rtsp_url: '', is_enabled: true });
            setIsAdding(false);
            loadCameras();
        } catch (error) {
            console.error(error);
            alert("Failed to add camera");
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm("Are you sure?")) return;
        await deleteCamera(id);
        loadCameras();
    };

    return (
        <div className="max-w-4xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">Camera Management</h2>
                <button
                    onClick={() => setIsAdding(!isAdding)}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg font-medium transition-colors"
                >
                    {isAdding ? 'Cancel' : '+ Add Camera'}
                </button>
            </div>

            {isAdding && (
                <form onSubmit={handleAdd} className="mb-8 bg-slate-900 p-6 rounded-xl border border-white/10 animate-fade-in-down">
                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Camera Name</label>
                            <input
                                type="text"
                                required
                                className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
                                value={newCam.name}
                                onChange={e => setNewCam({ ...newCam, name: e.target.value })}
                                placeholder="e.g. Main Hall Entrance"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">RTSP / Stream URL</label>
                            <input
                                type="text"
                                required
                                className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
                                value={newCam.rtsp_url}
                                onChange={e => setNewCam({ ...newCam, rtsp_url: e.target.value })}
                                placeholder="rtsp://..."
                            />
                        </div>
                    </div>
                    <div className="mt-4 flex justify-end">
                        <button type="submit" className="px-6 py-2 bg-indigo-600 rounded-lg hover:bg-indigo-500">Save Camera</button>
                    </div>
                </form>
            )}

            <div className="bg-slate-900 rounded-xl border border-white/10 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-slate-800 text-slate-400 text-xs uppercase font-semibold">
                        <tr>
                            <th className="px-6 py-4">Name</th>
                            <th className="px-6 py-4">URL</th>
                            <th className="px-6 py-4">Status</th>
                            <th className="px-6 py-4 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {cameras.map(cam => (
                            <tr key={cam.id} className="hover:bg-white/5 transition-colors">
                                <td className="px-6 py-4 font-medium">{cam.name}</td>
                                <td className="px-6 py-4 font-mono text-sm text-slate-400 truncate max-w-xs">{cam.rtsp_url}</td>
                                <td className="px-6 py-4">
                                    <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${cam.is_enabled ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
                                        }`}>
                                        {cam.is_enabled ? 'Active' : 'Disabled'}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-right flex justify-end gap-3">
                                    <button
                                        onClick={() => onEditZones(cam.id)}
                                        className="bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-400 hover:text-indigo-300 px-3 py-1.5 rounded-md text-sm font-medium transition-colors border border-indigo-500/20"
                                    >
                                        Edit Zones
                                    </button>
                                    <button
                                        onClick={() => handleDelete(cam.id)}
                                        className="text-slate-400 hover:text-red-400 text-sm"
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                        {cameras.length === 0 && (
                            <tr>
                                <td colSpan={4} className="px-6 py-8 text-center text-slate-500">No cameras found.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
