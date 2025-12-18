import { useEffect, useState, useRef } from 'react';
import { getZones, createZone, deleteZone, getCameras } from '../services/api';

interface ZoneEditorProps {
    cameraId: number;
    onBack: () => void;
}

export default function ZoneEditor({ cameraId, onBack }: ZoneEditorProps) {
    const [zones, setZones] = useState<any[]>([]);
    const [points, setPoints] = useState<number[][]>([]);
    const [camera, setCamera] = useState<any>(null);
    const [name, setName] = useState('');
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const imageRef = useRef<HTMLImageElement>(null);

    useEffect(() => {
        loadData();
    }, [cameraId]);

    const loadData = async () => {
        const cams = await getCameras();
        const cam = cams.find((c: any) => c.id === cameraId);
        setCamera(cam);

        const z = await getZones(cameraId);
        setZones(z);
    };

    const handleCanvasClick = (e: React.MouseEvent) => {
        if (!imageRef.current) return;

        const rect = canvasRef.current!.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Normalize coordinates (0-1) based on image display size
        const width = rect.width;
        const height = rect.height;

        setPoints([...points, [x / width, y / height]]);
    };

    const handleSave = async () => {
        if (!name || points.length < 3) return;

        try {
            await createZone({
                camera_id: cameraId,
                name,
                points
            });
            setName('');
            setPoints([]);
            loadData();
        } catch (e) {
            alert("Failed to save zone");
        }
    };

    const handleDelete = async (id: number) => {
        if (confirm("Delete zone?")) {
            await deleteZone(id);
            loadData();
        }
    };

    // Draw Loop
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Clear
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        const width = canvas.width;
        const height = canvas.height;

        // Draw existing zones
        zones.forEach(zone => {
            if (zone.points.length === 0) return;
            ctx.beginPath();
            ctx.moveTo(zone.points[0][0] * width, zone.points[0][1] * height);
            for (let i = 1; i < zone.points.length; i++) {
                ctx.lineTo(zone.points[i][0] * width, zone.points[i][1] * height);
            }
            ctx.closePath();
            ctx.strokeStyle = '#10b981'; // Emerald
            ctx.lineWidth = 2;
            ctx.stroke();
            ctx.fillStyle = 'rgba(16, 185, 129, 0.2)';
            ctx.fill();
        });

        // Draw current points
        if (points.length > 0) {
            ctx.beginPath();
            ctx.moveTo(points[0][0] * width, points[0][1] * height);
            for (let i = 1; i < points.length; i++) {
                ctx.lineTo(points[i][0] * width, points[i][1] * height);
            }
            if (points.length > 2) {
                ctx.closePath();
            }
            ctx.strokeStyle = '#6366f1'; // Indigo
            ctx.lineWidth = 2;
            ctx.stroke();

            points.forEach(p => {
                ctx.beginPath();
                ctx.arc(p[0] * width, p[1] * height, 4, 0, Math.PI * 2);
                ctx.fillStyle = '#fff';
                ctx.fill();
            });
        }

    }, [points, zones]);

    if (!camera) return <div>Loading...</div>;

    return (
        <div className="max-w-6xl mx-auto">
            <div className="flex items-center gap-4 mb-6">
                <button onClick={onBack} className="text-slate-400 hover:text-white">&larr; Back</button>
                <h2 className="text-2xl font-bold">Edit Zones: {camera.name}</h2>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Editor Area */}
                <div className="lg:col-span-2 relative bg-black rounded-xl overflow-hidden border border-white/10 group">
                    {/* Image Layer */}
                    <img
                        ref={imageRef}
                        src={`http://localhost:8000/cameras/${cameraId}/preview`}
                        className="w-full h-auto block select-none"
                        alt="Preview"
                        onLoad={() => {
                            if (imageRef.current && canvasRef.current) {
                                canvasRef.current.width = imageRef.current.clientWidth;
                                canvasRef.current.height = imageRef.current.clientHeight;
                            }
                        }}
                    />

                    {/* Canvas Layer */}
                    <canvas
                        ref={canvasRef}
                        className="absolute top-0 left-0 w-full h-full cursor-crosshair z-20"
                        onClick={handleCanvasClick}
                        onMouseMove={() => {
                            // Optional: Hover effect logic could go here
                        }}
                    />

                    <div className="absolute top-4 right-4 bg-black/70 backdrop-blur px-3 py-2 rounded text-xs text-slate-300">
                        Click to add points. Save to finish.
                    </div>
                </div>

                {/* Controls */}
                <div className="space-y-6">
                    <div className="bg-slate-900 p-6 rounded-xl border border-white/10">
                        <h3 className="font-semibold mb-4 text-white">New Zone</h3>
                        <div className="text-xs text-slate-500 mb-2">Points: {points.length} (Need 3+)</div>
                        <div className="space-y-4">
                            <input
                                type="text"
                                value={name}
                                onChange={e => setName(e.target.value)}
                                placeholder="Zone Name (e.g. Entrance)"
                                className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white"
                            />
                            <div className="flex gap-2">
                                <button
                                    onClick={handleSave}
                                    disabled={points.length < 3 || !name}
                                    className="flex-1 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed py-2 rounded font-medium transition-colors"
                                >
                                    Save Zone
                                </button>
                                <button
                                    onClick={() => setPoints([])}
                                    className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded text-slate-200"
                                >
                                    Clear
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="bg-slate-900 p-6 rounded-xl border border-white/10">
                        <h3 className="font-semibold mb-4 text-white">Existing Zones</h3>
                        <div className="space-y-2">
                            {zones.map(z => (
                                <div key={z.id} className="flex justify-between items-center p-3 bg-slate-800 rounded border border-white/5">
                                    <span className="font-medium text-slate-300">{z.name}</span>
                                    <button
                                        onClick={() => handleDelete(z.id)}
                                        className="text-red-400 hover:text-red-300 text-sm"
                                    >
                                        Delete
                                    </button>
                                </div>
                            ))}
                            {zones.length === 0 && <p className="text-slate-500 text-sm">No zones defined.</p>}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
