import { useState } from 'react';
import Dashboard from './components/Dashboard';
import CameraManager from './components/CameraManager';
import History from './components/History';
import ZoneEditor from './components/ZoneEditor';

function App() {
  /* Navigation State */
  const [activeTab, setActiveTab] = useState('dashboard');
  const [editingCameraId, setEditingCameraId] = useState<number | null>(null);

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans selection:bg-indigo-500 selection:text-white">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/50 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center">
              <span className="font-bold text-lg">S</span>
            </div>
            <span className="font-bold text-xl tracking-tight">ShadiHaal Analytics</span>
          </div>

          <div className="flex gap-1 bg-slate-800/50 p-1 rounded-full border border-white/5">
            {['dashboard', 'cameras', 'history'].map((tab) => (
              <button
                key={tab}
                onClick={() => { setActiveTab(tab); setEditingCameraId(null); }}
                className={`px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-300 ${activeTab === tab && !editingCameraId
                  ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/25'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
                  }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="pt-24 pb-12 px-6 max-w-7xl mx-auto">
        <div className="animate-fade-in">
          {editingCameraId ? (
            <ZoneEditor
              cameraId={editingCameraId}
              onBack={() => setEditingCameraId(null)}
            />
          ) : (
            <>
              {activeTab === 'dashboard' && <Dashboard />}
              {activeTab === 'cameras' && (
                <CameraManager
                  onEditZones={(id) => setEditingCameraId(id)}
                />
              )}
              {activeTab === 'history' && <History />}
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
