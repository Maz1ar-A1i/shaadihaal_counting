import { useEffect, useState } from 'react';
import { getHistory, exportCsv } from '../services/api';

interface SessionStat {
    session_id: number;
    start_time: string;
    end_time: string | null;
    total_hall_count: number;
}

export default function History() {
    const [history, setHistory] = useState<SessionStat[]>([]);

    useEffect(() => {
        loadHistory();
        const interval = setInterval(loadHistory, 3000); // Refresh every 3 seconds
        return () => clearInterval(interval);
    }, []);

    const loadHistory = async () => {
        try {
            const data = await getHistory();
            setHistory(data);
        } catch (e) {
            console.error("Failed to load history", e);
        }
    };

    const handleExport = async () => {
        try {
            const response = await exportCsv();
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'occupancy_report.csv');
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (e) {
            console.error("Export failed", e);
        }
    };

    return (
        <div className="max-w-5xl mx-auto">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-2xl font-bold">Historical Records</h2>
                    <p className="text-slate-400 text-sm">View past occupancy sessions.</p>
                </div>
                <button
                    onClick={handleExport}
                    className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-white/10 rounded-lg transition-colors"
                >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Export CSV
                </button>
            </div>

            <div className="bg-slate-900 rounded-xl border border-white/10 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-slate-800 text-slate-400 text-xs uppercase font-semibold">
                        <tr>
                            <th className="px-6 py-4">Date</th>
                            <th className="px-6 py-4">Time Window</th>
                            <th className="px-6 py-4">Total Count</th>
                            <th className="px-6 py-4">Status</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {history.map(item => (
                            <tr key={item.session_id} className="hover:bg-white/5 transition-colors">
                                <td className="px-6 py-4 text-white font-medium">
                                    {new Date(item.start_time).toLocaleDateString()}
                                </td>
                                <td className="px-6 py-4 text-slate-400">
                                    {new Date(item.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    {' - '}
                                    {item.end_time ? new Date(item.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '...'}
                                </td>
                                <td className="px-6 py-4 font-bold text-indigo-400">
                                    {Math.round(item.total_hall_count)}
                                </td>
                                <td className="px-6 py-4">
                                    {item.end_time ? (
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-500">
                                            Completed
                                        </span>
                                    ) : (
                                        <div className="flex items-center gap-2">
                                            <span className="relative flex h-3 w-3">
                                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                                                <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
                                            </span>
                                            <span className="text-indigo-400 text-xs font-medium tracking-wide">Recording...</span>
                                        </div>
                                    )}
                                </td>
                            </tr>
                        ))}
                        {history.length === 0 && (
                            <tr>
                                <td colSpan={4} className="px-6 py-12 text-center text-slate-500">
                                    No records found.
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
