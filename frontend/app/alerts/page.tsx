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
      // For now, we'll use mock data since backend endpoints aren't built yet
      const mockAlerts: Alert[] = [
        {
          id: 1,
          name: "Arsenal Goals",
          description: "Alert when Arsenal scores 2+ goals",
          is_active: true,
          created_at: "2025-07-19T10:00:00Z",
          alert_type: "goals",
          team: "Arsenal",
          condition: "Arsenal scores 2+ goals",
          threshold: 2
        },
        {
          id: 2,
          name: "High Scoring Matches",
          description: "Alert when any team scores 3+ goals",
          is_active: true,
          created_at: "2025-07-19T09:30:00Z",
          alert_type: "goals",
          team: "any",
          condition: "Any team scores 3+ goals",
          threshold: 3
        }
      ];

      const mockAdvancedAlerts: AdvancedAlert[] = [
        {
          id: 101,
          name: "Arsenal High Performance",
          description: "Arsenal scores 2+ goals AND has xG > 1.5",
          is_active: true,
          conditions: [
            { type: "goals", team: "Arsenal", operator: ">=", value: 2 },
            { type: "xg", team: "Arsenal", operator: ">", value: 1.5 }
          ],
          logic_operator: "AND",
          time_windows: [],
          sequences: []
        }
      ];

      setAlerts(mockAlerts);
      setAdvancedAlerts(mockAdvancedAlerts);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching alerts:', error);
      setLoading(false);
    }
  };

  const toggleAlertStatus = async (alertId: number, isActive: boolean) => {
    try {
      // TODO: Call backend API to update alert status
      console.log(`Toggling alert ${alertId} to ${isActive}`);
      
      // Update local state
      setAlerts(prev => prev.map(alert => 
        alert.id === alertId ? { ...alert, is_active: isActive } : alert
      ));
    } catch (error) {
      console.error('Error updating alert:', error);
    }
  };

  const deleteAlert = async (alertId: number) => {
    try {
      // TODO: Call backend API to delete alert
      console.log(`Deleting alert ${alertId}`);
      
      // Update local state
      setAlerts(prev => prev.filter(alert => alert.id !== alertId));
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
            <h1 className="text-3xl font-bold text-gray-900">Alert Management</h1>
            <p className="text-gray-600 mt-2">Create and manage your soccer alerts</p>
          </div>
          <div className="flex space-x-4">
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Simple Alert
            </button>
            <button
              onClick={() => setShowAdvancedForm(true)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              Create Advanced Alert
            </button>
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
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Advanced Alerts</h2>
          <div className="grid gap-4">
            {advancedAlerts.map(alert => (
              <div key={alert.id} className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{alert.name}</h3>
                    <p className="text-gray-600 mt-1">{alert.description}</p>
                    <div className="mt-3 flex items-center space-x-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        alert.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {alert.is_active ? 'Active' : 'Inactive'}
                      </span>
                      <span className="text-sm text-gray-500">
                        Logic: {alert.logic_operator}
                      </span>
                      <span className="text-sm text-gray-500">
                        Conditions: {alert.conditions.length}
                      </span>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => toggleAlertStatus(alert.id, !alert.is_active)}
                      className={`px-3 py-1 rounded text-sm ${
                        alert.is_active
                          ? 'bg-red-100 text-red-700 hover:bg-red-200'
                          : 'bg-green-100 text-green-700 hover:bg-green-200'
                      }`}
                    >
                      {alert.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button
                      onClick={() => deleteAlert(alert.id)}
                      className="px-3 py-1 rounded text-sm bg-red-100 text-red-700 hover:bg-red-200"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Simple Alerts Section */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Simple Alerts</h2>
          <div className="grid gap-4">
            {alerts.map(alert => (
              <div key={alert.id} className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{alert.name}</h3>
                    <p className="text-gray-600 mt-1">{alert.description}</p>
                    <div className="mt-3 flex items-center space-x-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        alert.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {alert.is_active ? 'Active' : 'Inactive'}
                      </span>
                      <span className="text-sm text-gray-500">
                        Team: {alert.team}
                      </span>
                      <span className="text-sm text-gray-500">
                        Threshold: {alert.threshold}
                      </span>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => toggleAlertStatus(alert.id, !alert.is_active)}
                      className={`px-3 py-1 rounded text-sm ${
                        alert.is_active
                          ? 'bg-red-100 text-red-700 hover:bg-red-200'
                          : 'bg-green-100 text-green-700 hover:bg-green-200'
                      }`}
                    >
                      {alert.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button
                      onClick={() => deleteAlert(alert.id)}
                      className="px-3 py-1 rounded text-sm bg-red-100 text-red-700 hover:bg-red-200"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Call backend API to create alert
    console.log('Creating simple alert:', formData);
    onSuccess();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">Create Simple Alert</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Alert Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Team
            </label>
            <input
              type="text"
              value={formData.team}
              onChange={(e) => setFormData({...formData, team: e.target.value})}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              placeholder="e.g., Arsenal"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Alert Type
            </label>
            <select
              value={formData.alert_type}
              onChange={(e) => setFormData({...formData, alert_type: e.target.value})}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="goals">Goals</option>
              <option value="score_difference">Score Difference</option>
              <option value="xg">Expected Goals (xG)</option>
              <option value="momentum">Momentum</option>
              <option value="pressure">Pressure Index</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Threshold
            </label>
            <input
              type="number"
              value={formData.threshold}
              onChange={(e) => setFormData({...formData, threshold: Number(e.target.value)})}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
              step="0.1"
              required
            />
          </div>
          <div className="flex space-x-3 pt-4">
            <button
              type="submit"
              className="flex-1 bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700"
            >
              Create Alert
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-md hover:bg-gray-400"
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