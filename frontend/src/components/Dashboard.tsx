import { useEffect, useState } from 'react';
import { getCameras, getHistory } from '../services/api';
import type { Camera } from '../services/api';

export default function Dashboard() {
    const [cameras, setCameras] = useState<Camera[]>([]);
    const [refreshKey, setRefreshKey] = useState(Date.now());
    const [lastCount, setLastCount] = useState<number | null>(null);
    const [lastUpdated, setLastUpdated] = useState<string | null>(null);
    const [isPaused, setIsPaused] = useState<boolean>(false);

    useEffect(() => {
        loadData();
        fetchSystemStatus();
        const interval = setInterval(() => {
            setRefreshKey(Date.now());
            loadData(); // Also refresh stats
        }, 5000); // 5 seconds refresh
        return () => clearInterval(interval);
    }, []);

    const fetchSystemStatus = async () => {
        try {
            const res = await fetch('http://localhost:8000/system/status');
            const data = await res.json();
            setIsPaused(data.is_paused);
        } catch (e) {
            console.error("Failed to fetch system status", e);
        }
    };

    const toggleSystemPause = async () => {
        const endpoint = isPaused ? 'resume' : 'pause';
        try {
            await fetch(`http://localhost:8000/system/${endpoint}`, { method: 'POST' });
            setIsPaused(!isPaused);
        } catch (e) {
            console.error("Failed to toggle pause", e);
        }
    };

    const toggleCamera = async (cam: Camera) => {
        try {
            await fetch(`http://localhost:8000/cameras/${cam.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_enabled: !cam.is_enabled })
            });
            loadData(); // Refresh list
        } catch (e) {
            console.error("Failed to toggle camera", e);
        }
    };

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
            {/* Header & Controls */}
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                        Dashboard
                    </h1>
                    <p className="text-slate-400">Live occupancy monitoring</p>
                </div>

                <button
                    onClick={toggleSystemPause}
                    className={`px-6 py-3 rounded-xl font-bold transition-all duration-300 transform active:scale-95 shadow-lg flex items-center gap-2 ${isPaused
                        ? 'bg-emerald-500 hover:bg-emerald-400 text-white shadow-emerald-500/20'
                        : 'bg-rose-500 hover:bg-rose-400 text-white shadow-rose-500/20'
                        }`}
                >
                    {isPaused ? (
                        <>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            RESUME SYSTEM
                        </>
                    ) : (
                        <>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" /></svg>
                            STOP ALL CAMERAS
                        </>
                    )}
                </button>
            </div>

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
                        <div className={`w-3 h-3 rounded-full ${isPaused ? 'bg-amber-500' : 'bg-emerald-500 animate-pulse'}`}></div>
                        <span className={`text-xl font-bold ${isPaused ? 'text-amber-500' : 'text-emerald-500'}`}>
                            {isPaused ? 'Paused' : 'Live'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Camera Grid */}
            <h2 className="text-xl font-semibold text-white mt-8">Live Feeds</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {cameras.map((cam) => {
                    // If system is paused, everything looks disabled/inactive
                    const displayEnabled = isPaused ? false : cam.is_enabled;

                    return (
                        <div key={cam.id} className={`group relative bg-slate-900 rounded-2xl overflow-hidden border transition-all duration-300 ${displayEnabled ? 'border-white/5 hover:border-indigo-500/50' : 'border-rose-500/20 grayscale opacity-60'}`}>
                            <div className="aspect-video bg-black relative">
                                {/* Live Preview Image */}
                                <img
                                    src={`http://localhost:8000/cameras/${cam.id}/preview?t=${refreshKey}`}
                                    alt={cam.name}
                                    className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
                                    onError={(e) => (e.currentTarget.src = 'https://placehold.co/640x360/1e293b/475569?text=No+Signal')}
                                />

                                {/* Overlay Info */}
                                <div className="absolute top-0 left-0 right-0 p-3 flex justify-between items-start bg-gradient-to-b from-black/80 to-transparent">
                                    <div className="px-2 py-1 bg-black/40 backdrop-blur rounded text-xs font-mono text-white flex items-center gap-2">
                                        <div className={`w-2 h-2 rounded-full ${displayEnabled ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
                                        {cam.name}
                                    </div>

                                    <button
                                        onClick={() => toggleCamera(cam)}
                                        disabled={isPaused}
                                        className={`px-3 py-1 rounded-md text-xs font-bold shadow-lg transition-colors ${isPaused
                                                ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
                                                : displayEnabled
                                                    ? 'bg-rose-500/80 hover:bg-rose-600 text-white'
                                                    : 'bg-emerald-500/80 hover:bg-emerald-600 text-white'
                                            }`}
                                    >
                                        {isPaused ? 'PAUSED' : (displayEnabled ? 'STOP' : 'START')}
                                    </button>
                                </div>
                            </div>
                        </div>
                    );
                })}

                {cameras.length === 0 && (
                    <div className="col-span-full py-12 text-center text-slate-500 bg-slate-900/30 rounded-2xl border border-dashed border-white/10">
                        No cameras added yet. Go to Cameras tab to setup.
                    </div>
                )}
            </div>
        </div>
    );
}
