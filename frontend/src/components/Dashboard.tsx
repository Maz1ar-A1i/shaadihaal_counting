import { useEffect, useState } from 'react';
import { getCameras, getHistory } from '../services/api';
import type { Camera } from '../services/api';

export default function Dashboard() {
    const [cameras, setCameras] = useState<Camera[]>([]);
    const [refreshKey, setRefreshKey] = useState(Date.now());
    const [lastCount, setLastCount] = useState<number | null>(null);
    const [lastUpdated, setLastUpdated] = useState<string | null>(null);

    useEffect(() => {
        loadData();
        const interval = setInterval(() => {
            setRefreshKey(Date.now());
            loadData(); // Also refresh stats
        }, 5000); // 5 seconds refresh
        return () => clearInterval(interval);
    }, []);

    const loadData = async () => {
        try {
            const cams = await getCameras();
            setCameras(cams);

            // Get latest history for stats
            const history = await getHistory();

            // Also fetch live stats (new endpoint)
            try {
                // We need to add this to api.ts service first, but for now specific fetch:
                const res = await fetch('http://localhost:8000/stats/live');
                const liveData = await res.json();
                setLastCount(liveData.live_count);
                if (liveData.last_updated) setLastUpdated(liveData.last_updated);
            } catch (e) {
                // Fallback to history if live fails
                if (history.length > 0) {
                    setLastCount(history[0].total_hall_count);
                }
            }
        } catch (e) {
            console.error("Failed to load dashboard", e);
        }
    };

    return (
        <div className="space-y-6">
            {/* Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900/50 backdrop-blur border border-white/5 p-6 rounded-2xl">
                    <h3 className="text-slate-400 text-sm font-medium">Total Hall Occupancy</h3>
                    <div className="mt-2 text-4xl font-bold bg-gradient-to-tr from-indigo-400 to-white bg-clip-text text-transparent">
                        {lastCount !== null ? Math.round(lastCount) : '--'} <span className="text-lg text-slate-500 font-normal">people</span>
                    </div>
                    {lastUpdated && (
                        <div className="mt-2 text-xs text-slate-500 flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                            Updated: {new Date(lastUpdated).toLocaleTimeString()}
                        </div>
                    )}
                </div>

                <div className="bg-slate-900/50 backdrop-blur border border-white/5 p-6 rounded-2xl">
                    <h3 className="text-slate-400 text-sm font-medium">Active Cameras</h3>
                    <div className="mt-2 text-4xl font-bold text-white">
                        {cameras.filter(c => c.is_enabled).length} <span className="text-lg text-slate-500 font-normal">/ {cameras.length}</span>
                    </div>
                </div>

                <div className="bg-slate-900/50 backdrop-blur border border-white/5 p-6 rounded-2xl">
                    <h3 className="text-slate-400 text-sm font-medium">System Status</h3>
                    <div className="mt-2 flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
                        <span className="text-xl font-bold text-emerald-500">Live</span>
                    </div>
                </div>
            </div>

            {/* Camera Grid */}
            <h2 className="text-xl font-semibold text-white mt-8">Live Feeds</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {cameras.map((cam) => (
                    <div key={cam.id} className="group relative bg-slate-900 rounded-2xl overflow-hidden border border-white/5 hover:border-indigo-500/50 transition-all duration-300">
                        <div className="aspect-video bg-black relative">
                            {/* Live Preview Image */}
                            <img
                                src={`http://localhost:8000/cameras/${cam.id}/preview?t=${refreshKey}`}
                                alt={cam.name}
                                className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
                                onError={(e) => (e.currentTarget.src = 'https://placehold.co/640x360/1e293b/475569?text=No+Signal')}
                            />

                            {/* Overlay Info */}
                            <div className="absolute top-3 left-3 px-2 py-1 bg-black/60 backdrop-blur rounded text-xs font-mono text-white flex items-center gap-2">
                                <div className={`w-2 h-2 rounded-full ${cam.is_enabled ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
                                {cam.name}
                            </div>
                        </div>
                    </div>
                ))}

                {cameras.length === 0 && (
                    <div className="col-span-full py-12 text-center text-slate-500 bg-slate-900/30 rounded-2xl border border-dashed border-white/10">
                        No cameras added yet. Go to Cameras tab to setup.
                    </div>
                )}
            </div>
        </div>
    );
}
