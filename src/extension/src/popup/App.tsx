import React, { useState, useEffect } from 'react';
import { fetchUserData, logout } from '../api/client';

const App: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'home' | 'settings'>('home');
    const [status, setStatus] = useState<string>("Checking API Connection...");
    const [connected, setConnected] = useState(false);

    useEffect(() => {
        const checkConnection = async () => {
            try {
                const user = await fetchUserData();
                if (user && user.email) {
                    setStatus(`✅ Connected to Backend as ${user.email}`);
                    setConnected(true);
                } else {
                    setStatus("❌ Backend Connection Failed (Invalid User)");
                }
            } catch (err) {
                setStatus("🔴 Offline / Unauthenticated. Please sign in to the web platform.");
            }
        };
        checkConnection();
    }, []);

    const handleAutofill = async () => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const currentTab = tabs[0];
            if (currentTab.id) {
                chrome.scripting.executeScript({
                    target: { tabId: currentTab.id },
                    func: () => {
                        alert("Forcing extension to rescan this page...");
                        window.dispatchEvent(new Event('load'));
                        return true;
                    }
                });
            }
        });
    };

    const handleLogout = async () => {
        await logout();
        setConnected(false);
        setStatus("🔴 Unauthenticated. Please enter proper token.");
    };

    return (
        <div style={{ width: '400px', padding: '16px', fontFamily: 'system-ui, sans-serif', backgroundColor: '#F9FAFB', color: '#111827' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #E5E7EB', paddingBottom: '12px', marginBottom: '16px' }}>
                <h2 style={{ fontSize: '18px', fontWeight: 'bold', margin: 0 }}>🧠 AI Job Assistant</h2>
                <div style={{ display: 'flex', gap: '8px' }}>
                    <button onClick={() => setActiveTab('home')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontWeight: activeTab === 'home' ? 'bold' : 'normal', color: activeTab === 'home' ? '#3B82F6' : '#6B7280' }}>Home</button>
                    <button onClick={() => setActiveTab('settings')} style={{ background: 'none', border: 'none', cursor: 'pointer', fontWeight: activeTab === 'settings' ? 'bold' : 'normal', color: activeTab === 'settings' ? '#3B82F6' : '#6B7280' }}>Settings</button>
                </div>
            </div>

            {activeTab === 'home' && (
                <div>
                    <div style={{ padding: '12px', backgroundColor: connected ? '#DEF7EC' : '#FDE8E8', borderRadius: '6px', fontSize: '14px', marginBottom: '16px' }}>
                        {status}
                    </div>

                    <p style={{ fontSize: '14px', color: '#4B5563', marginBottom: '16px' }}>
                        Navigate to an ATS platform like Workday, Greenhouse, or Lever. A floating widget will appear on supported fields natively.
                    </p>

                    <button 
                        onClick={handleAutofill}
                        disabled={!connected}
                        style={{ width: '100%', padding: '12px', backgroundColor: connected ? '#2563EB' : '#9CA3AF', color: 'white', border: 'none', borderRadius: '6px', fontSize: '16px', fontWeight: 'bold', cursor: connected ? 'pointer' : 'not-allowed', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                        Trigger Manual Page Rescan
                    </button>
                </div>
            )}

            {activeTab === 'settings' && (
                <div>
                    <h3 style={{ fontSize: '16px', margin: '0 0 12px 0' }}>Security Settings</h3>
                    <p style={{ fontSize: '14px', color: '#4B5563', marginBottom: '16px' }}>
                        API Tokens are securely stored within <code>chrome.storage.local</code>. Logging out will instantly purge local backend keys.
                    </p>
                    <button 
                        onClick={handleLogout}
                        style={{ width: '100%', padding: '10px', backgroundColor: 'white', color: '#DC2626', border: '1px solid #DC2626', borderRadius: '6px', fontSize: '14px', fontWeight: 'bold', cursor: 'pointer' }}>
                        Purge Backend Tokens
                    </button>
                </div>
            )}
        </div>
    );
};

export default App;
