'use client';

import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Bell, 
  Activity, 
  Target,
  Calendar,
  Clock,
  AlertTriangle,
  CheckCircle,
  RefreshCw
} from 'lucide-react';

interface AlertPerformance {
  alert_id: number;
  alert_name: string;
  total_triggers: number;
  success_rate: number;
  avg_response_time: number;
  last_triggered: string | null;
  most_common_matches: string[];
  trigger_trend: Array<{ date: string; triggers: number }>;
}

interface UserAnalytics {
  user_id: number;
  username: string;
  total_alerts: number;
  active_alerts: number;
  total_triggers: number;
  avg_alerts_per_day: number;
  most_used_alert_types: string[];
  activity_trend: Array<{ date: string; alerts_created: number }>;
}

interface SystemAnalytics {
  total_users: number;
  total_alerts: number;
  total_triggers: number;
  avg_response_time: number;
  peak_usage_hours: number[];
  most_popular_teams: string[];
  alert_type_distribution: Record<string, number>;
  system_performance_trend: Array<{ date: string; alerts_created: number }>;
}

interface PerformanceInsights {
  success_rate_24h: number;
  total_triggers_24h: number;
  most_active_alerts: Array<{ id: number; name: string; triggers: number }>;
  hourly_load: Record<string, number>;
  insights: string[];
}

interface AnalyticsDashboardProps {
  userId?: number;
  isAdmin?: boolean;
}

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ userId, isAdmin = false }) => {
  const [userAnalytics, setUserAnalytics] = useState<UserAnalytics | null>(null);
  const [systemAnalytics, setSystemAnalytics] = useState<SystemAnalytics | null>(null);
  const [performanceInsights, setPerformanceInsights] = useState<PerformanceInsights | null>(null);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'performance' | 'trends' | 'recommendations'>('overview');

  const fetchUserAnalytics = async () => {
    if (!userId) return;
    
    try {
      const response = await fetch('/api/analytics/user/profile', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setUserAnalytics(data);
      }
    } catch (error) {
      console.error('Error fetching user analytics:', error);
    }
  };

  const fetchSystemAnalytics = async () => {
    if (!isAdmin) return;
    
    try {
      const response = await fetch('/api/analytics/system/overview', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setSystemAnalytics(data);
      }
    } catch (error) {
      console.error('Error fetching system analytics:', error);
    }
  };

  const fetchPerformanceInsights = async () => {
    try {
      const response = await fetch('/api/analytics/performance/insights', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setPerformanceInsights(data);
      }
    } catch (error) {
      console.error('Error fetching performance insights:', error);
    }
  };

  const fetchRecommendations = async () => {
    if (!userId) return;
    
    try {
      const response = await fetch('/api/analytics/recommendations', {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations);
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
  };

  const fetchAllData = async () => {
    setIsLoading(true);
    await Promise.all([
      fetchUserAnalytics(),
      fetchSystemAnalytics(),
      fetchPerformanceInsights(),
      fetchRecommendations()
    ]);
    setIsLoading(false);
  };

  useEffect(() => {
    fetchAllData();
  }, [userId, isAdmin]);

  const getStatusColor = (value: number, threshold: number) => {
    if (value >= threshold * 0.8) return 'text-green-600';
    if (value >= threshold * 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusIcon = (value: number, threshold: number) => {
    if (value >= threshold * 0.8) return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (value >= threshold * 0.6) return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    return <AlertTriangle className="w-5 h-5 text-red-500" />;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600">Loading analytics...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
        <button
          onClick={fetchAllData}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'performance', label: 'Performance', icon: Activity },
            { id: 'trends', label: 'Trends', icon: TrendingUp },
            { id: 'recommendations', label: 'Recommendations', icon: Target }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* User Stats */}
          {userAnalytics && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow border">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Bell className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Alerts</p>
                    <p className="text-2xl font-bold text-gray-900">{userAnalytics.total_alerts}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow border">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Activity className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Active Alerts</p>
                    <p className="text-2xl font-bold text-gray-900">{userAnalytics.active_alerts}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow border">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Target className="w-6 h-6 text-purple-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Triggers</p>
                    <p className="text-2xl font-bold text-gray-900">{userAnalytics.total_triggers}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow border">
                <div className="flex items-center">
                  <div className="p-2 bg-orange-100 rounded-lg">
                    <Calendar className="w-6 h-6 text-orange-600" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Avg/Day</p>
                    <p className="text-2xl font-bold text-gray-900">{userAnalytics.avg_alerts_per_day.toFixed(1)}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* System Stats (Admin Only) */}
          {isAdmin && systemAnalytics && (
            <div className="bg-white p-6 rounded-lg shadow border">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">System Overview</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{systemAnalytics.total_users}</p>
                  <p className="text-sm text-gray-600">Total Users</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{systemAnalytics.total_alerts}</p>
                  <p className="text-sm text-gray-600">Total Alerts</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-600">{systemAnalytics.total_triggers}</p>
                  <p className="text-sm text-gray-600">Total Triggers</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-orange-600">{systemAnalytics.avg_response_time.toFixed(1)}s</p>
                  <p className="text-sm text-gray-600">Avg Response</p>
                </div>
              </div>
            </div>
          )}

          {/* Performance Insights */}
          {performanceInsights && (
            <div className="bg-white p-6 rounded-lg shadow border">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Insights</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    {getStatusIcon(performanceInsights.success_rate_24h, 100)}
                  </div>
                  <p className={`text-2xl font-bold ${getStatusColor(performanceInsights.success_rate_24h, 100)}`}>
                    {performanceInsights.success_rate_24h.toFixed(1)}%
                  </p>
                  <p className="text-sm text-gray-600">Success Rate (24h)</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Activity className="w-5 h-5 text-blue-500" />
                  </div>
                  <p className="text-2xl font-bold text-blue-600">{performanceInsights.total_triggers_24h}</p>
                  <p className="text-sm text-gray-600">Triggers (24h)</p>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Clock className="w-5 h-5 text-green-500" />
                  </div>
                  <p className="text-2xl font-bold text-green-600">
                    {performanceInsights.hourly_load && Object.keys(performanceInsights.hourly_load).length > 0
                      ? Math.max(...Object.values(performanceInsights.hourly_load))
                      : 0}
                  </p>
                  <p className="text-sm text-gray-600">Peak Hour Load</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Performance Tab */}
      {activeTab === 'performance' && (
        <div className="space-y-6">
          {userAnalytics && (
            <div className="bg-white p-6 rounded-lg shadow border">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Alert Performance</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Most Used Alert Types</h4>
                  <div className="space-y-2">
                    {userAnalytics.most_used_alert_types.map((type, index) => (
                      <div key={type} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">{type}</span>
                        <span className="text-sm font-medium text-gray-900">#{index + 1}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Activity Summary</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Active Alerts</span>
                      <span className="text-sm font-medium text-green-600">{userAnalytics.active_alerts}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Inactive Alerts</span>
                      <span className="text-sm font-medium text-gray-600">{userAnalytics.total_alerts - userAnalytics.active_alerts}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Success Rate</span>
                      <span className="text-sm font-medium text-blue-600">
                        {userAnalytics.total_triggers > 0 ? ((userAnalytics.active_alerts / userAnalytics.total_alerts) * 100).toFixed(1) : 0}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {performanceInsights && performanceInsights.most_active_alerts.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow border">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Most Active Alerts (24h)</h3>
              <div className="space-y-3">
                {performanceInsights.most_active_alerts.map((alert) => (
                  <div key={alert.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm font-medium text-gray-900">{alert.name}</span>
                    <span className="text-sm text-blue-600 font-medium">{alert.triggers} triggers</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Trends Tab */}
      {activeTab === 'trends' && (
        <div className="space-y-6">
          {userAnalytics && (
            <div className="bg-white p-6 rounded-lg shadow border">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity Trend (Last 30 Days)</h3>
              <div className="h-64 flex items-end justify-between space-x-1">
                {userAnalytics.activity_trend.slice(-7).map((day, index) => (
                  <div key={day.date} className="flex-1 flex flex-col items-center">
                    <div 
                      className="w-full bg-blue-500 rounded-t"
                      style={{ 
                        height: `${Math.max(10, (day.alerts_created / Math.max(...userAnalytics.activity_trend.map(d => d.alerts_created))) * 200)}px` 
                      }}
                    />
                    <span className="text-xs text-gray-500 mt-1">{day.date.split('-')[2]}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {isAdmin && systemAnalytics && (
            <div className="bg-white p-6 rounded-lg shadow border">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">System Trends</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Peak Usage Hours</h4>
                  <div className="space-y-2">
                    {systemAnalytics.peak_usage_hours.slice(0, 5).map((hour, index) => (
                      <div key={hour} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">{hour}:00</span>
                        <span className="text-sm font-medium text-gray-900">#{index + 1}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Popular Teams</h4>
                  <div className="space-y-2">
                    {systemAnalytics.most_popular_teams.slice(0, 5).map((team, index) => (
                      <div key={team} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">{team}</span>
                        <span className="text-sm font-medium text-gray-900">#{index + 1}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recommendations Tab */}
      {activeTab === 'recommendations' && (
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow border">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Personalized Recommendations</h3>
            {recommendations.length > 0 ? (
              <div className="space-y-4">
                {recommendations.map((rec, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <div>
                      <h4 className="font-medium text-gray-900">
                        {rec.type ? `Try ${rec.type} alerts` : `Follow ${rec.team}`}
                      </h4>
                      <p className="text-sm text-gray-600">{rec.reason}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-medium text-blue-600">{rec.popularity} users</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No recommendations available yet</p>
                <p className="text-sm text-gray-400">Create more alerts to get personalized suggestions</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard; 