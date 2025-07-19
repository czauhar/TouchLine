'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Alert {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  created_at: string;
  alert_type: string;
  team: string;
  condition: string;
  threshold: number;
}

interface AdvancedAlert {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  conditions: any[];
  logic_operator: 'AND' | 'OR';
  time_windows: any[];
  sequences: any[];
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [advancedAlerts, setAdvancedAlerts] = useState<AdvancedAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showAdvancedForm, setShowAdvancedForm] = useState(false);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/alerts');
      if (response.ok) {
        const data = await response.json();
        setAlerts(data.alerts);
        setAdvancedAlerts([]); // Advanced alerts will be added later
      } else {
        console.error('Failed to fetch alerts');
        setAlerts([]);
        setAdvancedAlerts([]);
      }
    } catch (error) {
      console.error('Error fetching alerts:', error);
      setAlerts([]);
      setAdvancedAlerts([]);
    } finally {
      setLoading(false);
    }
  };

  const toggleAlertStatus = async (alertId: number, isActive: boolean) => {
    try {
      const response = await fetch(`http://localhost:8000/api/alerts/${alertId}/toggle`, {
        method: 'PUT',
      });
      
      if (response.ok) {
        const data = await response.json();
        // Update local state
        setAlerts(prev => prev.map(alert => 
          alert.id === alertId ? { ...alert, is_active: data.is_active } : alert
        ));
      } else {
        console.error('Failed to toggle alert');
      }
    } catch (error) {
      console.error('Error updating alert:', error);
    }
  };

  const deleteAlert = async (alertId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/alerts/${alertId}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        // Update local state
        setAlerts(prev => prev.filter(alert => alert.id !== alertId));
      } else {
        console.error('Failed to delete alert');
      }
    } catch (error) {
      console.error('Error deleting alert:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-24 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-8">
            <div className="bg-gradient-to-r from-red-500 to-pink-500 p-6 rounded-3xl glow-red hover-glow-red transition-all duration-500">
              <span className="text-6xl">🚨</span>
            </div>
          </div>
          <h1 className="text-6xl font-black bg-gradient-to-r from-red-400 via-pink-400 to-purple-400 bg-clip-text text-transparent text-glow-red mb-6">
            Alert Management
          </h1>
          <p className="text-2xl text-gray-300 mb-10">Create and manage your intelligent soccer alerts</p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-10 py-5 rounded-2xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-bold text-xl glow-blue hover-glow-blue transform hover:-translate-y-2 flex items-center justify-center"
            >
              <span className="mr-3">➕</span>
              Create Alert
            </button>
            <button
              onClick={() => setShowAdvancedForm(true)}
              className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-10 py-5 rounded-2xl hover:from-purple-700 hover:to-pink-700 transition-all duration-300 font-bold text-xl glow-purple hover-glow-purple transform hover:-translate-y-2 flex items-center justify-center"
            >
              <span className="mr-3">⚡</span>
              Advanced Alerts
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700 p-8 hover:bg-gray-800/70 transition-all duration-300 hover-glow-green">
            <div className="flex items-center">
              <div className="p-4 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-500 glow-green">
                <span className="text-3xl text-white">🔔</span>
              </div>
              <div className="ml-6">
                <p className="text-sm font-medium text-gray-400">Total Alerts</p>
                <p className="text-4xl font-black text-gray-200">{alerts.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700 p-8 hover:bg-gray-800/70 transition-all duration-300 hover-glow-cyan">
            <div className="flex items-center">
              <div className="p-4 rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-500 glow-cyan">
                <span className="text-3xl text-white">🟢</span>
              </div>
              <div className="ml-6">
                <p className="text-sm font-medium text-gray-400">Active Alerts</p>
                <p className="text-4xl font-black text-gray-200">{alerts.filter(a => a.is_active).length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700 p-8 hover:bg-gray-800/70 transition-all duration-300 hover-glow-purple">
            <div className="flex items-center">
              <div className="p-4 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-500 glow-purple">
                <span className="text-3xl text-white">⚡</span>
              </div>
              <div className="ml-6">
                <p className="text-sm font-medium text-gray-400">Advanced Alerts</p>
                <p className="text-4xl font-black text-gray-200">0</p>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex flex-col sm:flex-row gap-6 justify-center mb-10">
          <Link href="/" className="bg-gradient-to-r from-gray-600 to-gray-700 text-white px-8 py-4 rounded-2xl hover:from-gray-700 hover:to-gray-800 transition-all duration-300 font-bold text-lg glow-gray hover-glow-gray transform hover:-translate-y-2">
            🏠 Dashboard
          </Link>
          <Link href="/matches" className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-8 py-4 rounded-2xl hover:from-blue-700 hover:to-cyan-700 transition-all duration-300 font-bold text-lg glow-cyan hover-glow-cyan transform hover:-translate-y-2">
            🏟️ Live Matches
          </Link>
          <span className="bg-gradient-to-r from-red-600 to-pink-600 text-white px-8 py-4 rounded-2xl font-bold text-lg glow-red">
            🚨 Alerts
          </span>
        </div>

        {/* Advanced Alerts Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4 flex items-center">
            <span className="mr-2">🚀</span>
            Advanced Alerts
            <span className="ml-2 text-sm text-gray-500 font-normal">(Coming Soon)</span>
          </h2>
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 border border-purple-200">
            <div className="text-center">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Multi-Condition Logic</h3>
              <p className="text-gray-600 mb-4">
                Create complex alerts with AND/OR logic, time windows, and sequences
              </p>
              <div className="flex justify-center space-x-4 text-sm text-gray-500">
                <span>• Multiple conditions</span>
                <span>• Time windows</span>
                <span>• Sequences</span>
              </div>
            </div>
          </div>
        </div>

        {/* Simple Alerts Section */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4 flex items-center">
            <span className="mr-2">🔔</span>
            Simple Alerts
            <span className="ml-2 text-sm text-gray-500 font-normal">({alerts.length} active)</span>
          </h2>
          
          {alerts.length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
              <div className="text-6xl mb-4">🔔</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Alerts Yet</h3>
              <p className="text-gray-600 mb-4">
                Create your first alert to start getting notified about soccer events
              </p>
              <button
                onClick={() => setShowCreateForm(true)}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create Your First Alert
              </button>
            </div>
          ) : (
            <div className="grid gap-4">
              {alerts.map(alert => (
                <div key={alert.id} className="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{alert.name}</h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          alert.is_active 
                            ? 'bg-green-100 text-green-800 animate-pulse' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {alert.is_active ? '🟢 Active' : '⚪ Inactive'}
                        </span>
                      </div>
                      <p className="text-gray-600 mb-3">{alert.description || `Alert when ${alert.team} ${alert.alert_type} >= ${alert.threshold}`}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span className="flex items-center">
                          <span className="mr-1">🏟️</span>
                          {alert.team}
                        </span>
                        <span className="flex items-center">
                          <span className="mr-1">📊</span>
                          {alert.alert_type}
                        </span>
                        <span className="flex items-center">
                          <span className="mr-1">🎯</span>
                          ≥ {alert.threshold}
                        </span>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => toggleAlertStatus(alert.id, !alert.is_active)}
                        className={`px-3 py-1 rounded text-sm transition-colors ${
                          alert.is_active
                            ? 'bg-red-100 text-red-700 hover:bg-red-200'
                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                        }`}
                      >
                        {alert.is_active ? '⏸️ Pause' : '▶️ Activate'}
                      </button>
                      <button
                        onClick={() => deleteAlert(alert.id)}
                        className="px-3 py-1 rounded text-sm bg-red-100 text-red-700 hover:bg-red-200 transition-colors"
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Create Alert Forms */}
        {showCreateForm && (
          <CreateSimpleAlertForm 
            onClose={() => setShowCreateForm(false)}
            onSuccess={() => {
              setShowCreateForm(false);
              fetchAlerts();
            }}
          />
        )}

        {showAdvancedForm && (
          <CreateAdvancedAlertForm 
            onClose={() => setShowAdvancedForm(false)}
            onSuccess={() => {
              setShowAdvancedForm(false);
              fetchAlerts();
            }}
          />
        )}
      </div>
    </div>
  );
}

// Simple Alert Form Component
function CreateSimpleAlertForm({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [formData, setFormData] = useState({
    name: '',
    team: '',
    alert_type: 'goals',
    threshold: 1,
    description: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/alerts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        onSuccess();
      } else {
        console.error('Failed to create alert');
      }
    } catch (error) {
      console.error('Error creating alert:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getAlertTypeIcon = (type: string) => {
    const icons: { [key: string]: string } = {
      goals: '⚽',
      score_difference: '📊',
      xg: '🎯',
      momentum: '📈',
      pressure: '🔥'
    };
    return icons[type] || '🔔';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900">Create New Alert</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl"
          >
            ×
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Alert Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Arsenal Goals Alert"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Team
            </label>
            <input
              type="text"
              value={formData.team}
              onChange={(e) => setFormData({...formData, team: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="e.g., Arsenal, Manchester United"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Alert Type
            </label>
            <select
              value={formData.alert_type}
              onChange={(e) => setFormData({...formData, alert_type: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="goals">⚽ Goals</option>
              <option value="score_difference">📊 Score Difference</option>
              <option value="xg">🎯 Expected Goals (xG)</option>
              <option value="momentum">📈 Momentum</option>
              <option value="pressure">🔥 Pressure Index</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Threshold
            </label>
            <input
              type="number"
              value={formData.threshold}
              onChange={(e) => setFormData({...formData, threshold: Number(e.target.value)})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              step="0.1"
              min="0"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description (Optional)
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={2}
              placeholder="Optional description of your alert"
            />
          </div>
          
          <div className="bg-blue-50 rounded-lg p-3 mt-4">
            <div className="text-sm text-blue-800">
              <strong>Preview:</strong> Alert when {formData.team || '[Team]'} {formData.alert_type} ≥ {formData.threshold}
            </div>
          </div>
          
          <div className="flex space-x-3 pt-4">
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSubmitting ? 'Creating...' : 'Create Alert'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-300 text-gray-700 py-3 rounded-lg hover:bg-gray-400 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Advanced Alert Form Component (placeholder)
function CreateAdvancedAlertForm({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
        <h3 className="text-lg font-semibold mb-4">Create Advanced Alert</h3>
        <p className="text-gray-600 mb-4">
          Advanced alerts with multi-condition logic coming soon!
        </p>
        <div className="flex space-x-3">
          <button
            onClick={onClose}
            className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-md hover:bg-gray-400"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
} 