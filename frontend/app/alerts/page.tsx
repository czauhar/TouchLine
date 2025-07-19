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
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <span className="mr-3">🚨</span>
              Alert Management
            </h1>
            <p className="text-gray-600 mt-2">Create and manage your soccer alerts</p>
          </div>
          <div className="flex space-x-4">
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
            >
              <span className="mr-2">➕</span>
              Create Alert
            </button>
            <button
              onClick={() => setShowAdvancedForm(true)}
              className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all flex items-center"
            >
              <span className="mr-2">⚡</span>
              Advanced
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <span className="text-2xl">🔔</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Alerts</p>
                <p className="text-2xl font-bold text-gray-900">{alerts.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <span className="text-2xl">🟢</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Alerts</p>
                <p className="text-2xl font-bold text-gray-900">{alerts.filter(a => a.is_active).length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <span className="text-2xl">⚡</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Advanced Alerts</p>
                <p className="text-2xl font-bold text-gray-900">0</p>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex space-x-8 mb-8">
          <Link href="/" className="text-gray-600 hover:text-gray-900">
            Dashboard
          </Link>
          <Link href="/matches" className="text-gray-600 hover:text-gray-900">
            Live Matches
          </Link>
          <span className="text-blue-600 font-medium">Alerts</span>
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