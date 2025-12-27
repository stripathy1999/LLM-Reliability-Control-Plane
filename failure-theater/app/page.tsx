'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, AlertTriangle, CheckCircle, Zap, Activity, DollarSign, Clock, Target, ExternalLink } from 'lucide-react'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

interface HealthStatus {
  health_score: number
  status: 'healthy' | 'degraded' | 'critical'
  last_incident: boolean
  top_recommendation: string
}

interface MetricPoint {
  time: string
  health_score: number
  latency: number
  cost: number
  errors: number
}

interface Incident {
  id: string
  type: string
  timestamp: Date
  severity: 'low' | 'medium' | 'high' | 'critical'
  description: string
}

export default function FailureTheater() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus>({
    health_score: 85,
    status: 'healthy',
    last_incident: false,
    top_recommendation: 'System operating normally',
  })
  const [loading, setLoading] = useState(false)
  const [lastTriggered, setLastTriggered] = useState<string | null>(null)
  const [incidentCount, setIncidentCount] = useState(0)
  const [metricsHistory, setMetricsHistory] = useState<MetricPoint[]>([])
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [activeRequests, setActiveRequests] = useState(0)
  const [totalRequests, setTotalRequests] = useState(0)
  const [realTimeMetrics, setRealTimeMetrics] = useState({
    latency: 0,
    cost: 0,
    errors: 0,
    requests: 0,
  })

  // Initialize metrics history
  useEffect(() => {
    const initialMetrics: MetricPoint[] = Array.from({ length: 20 }, (_, i) => ({
      time: new Date(Date.now() - (19 - i) * 1000).toLocaleTimeString(),
      health_score: 85,
      latency: 500 + Math.random() * 200,
      cost: 0.001 + Math.random() * 0.002,
      errors: 0,
    }))
    setMetricsHistory(initialMetrics)
  }, [])

  // Animate health score changes
  useEffect(() => {
    const interval = setInterval(() => {
      if (metricsHistory.length > 0) {
        const newPoint: MetricPoint = {
          time: new Date().toLocaleTimeString(),
          health_score: healthStatus.health_score,
          latency: realTimeMetrics.latency || 500 + Math.random() * 200,
          cost: realTimeMetrics.cost || 0.001 + Math.random() * 0.002,
          errors: realTimeMetrics.errors,
        }
        setMetricsHistory(prev => [...prev.slice(-19), newPoint])
      }
    }, 1000)
    return () => clearInterval(interval)
  }, [healthStatus.health_score, realTimeMetrics])

  const triggerScenario = async (scenario: string, endpoint: string, params: Record<string, string>) => {
    setLoading(true)
    setLastTriggered(scenario)
    setActiveRequests(15)
    
    const startTime = Date.now()
    const requests = []
    
    try {
      // Send multiple requests with progress tracking
      for (let i = 0; i < 15; i++) {
        const requestPromise = axios.post(`${API_BASE_URL}${endpoint}`, getRequestBody(endpoint), { params })
          .then(response => {
            setTotalRequests(prev => prev + 1)
            setActiveRequests(prev => Math.max(0, prev - 1))
            
            // Update real-time metrics from response
            if (response.data.metadata) {
              const meta = response.data.metadata
              setRealTimeMetrics(prev => ({
                latency: meta.latency_ms || prev.latency,
                cost: meta.cost_usd || prev.cost,
                errors: meta.error ? prev.errors + 1 : prev.errors,
                requests: prev.requests + 1,
              }))
            }
            return response
          })
          .catch(error => {
            setActiveRequests(prev => Math.max(0, prev - 1))
            setRealTimeMetrics(prev => ({
              ...prev,
              errors: prev.errors + 1,
            }))
            throw error
          })
        
        requests.push(requestPromise)
        
        // Stagger requests slightly for visual effect
        await new Promise(resolve => setTimeout(resolve, 50))
      }
      
      await Promise.all(requests)
      
      // Create incident
      const incident: Incident = {
        id: `incident-${Date.now()}`,
        type: scenario,
        timestamp: new Date(),
        severity: scenario === 'cost' || scenario === 'security' ? 'critical' : scenario === 'latency' ? 'high' : 'medium',
        description: getIncidentDescription(scenario),
      }
      
      setIncidents(prev => [incident, ...prev].slice(0, 10))
      setIncidentCount(prev => prev + 1)
      
      // Update health status with animation
      updateHealthStatus(scenario)
      
      // Simulate incident creation
      setTimeout(() => {
        setHealthStatus(prev => ({ ...prev, last_incident: true }))
      }, 1000)
      
    } catch (error) {
      console.error(`Error triggering ${scenario}:`, error)
    } finally {
      setLoading(false)
      setActiveRequests(0)
    }
  }

  const getIncidentDescription = (scenario: string): string => {
    switch (scenario) {
      case 'cost':
        return 'Cost anomaly detected: Token usage exceeded 2x baseline'
      case 'latency':
        return 'Latency SLO breach: p95 latency exceeded 1500ms threshold'
      case 'quality':
        return 'Quality degradation: Semantic similarity score dropped below 0.4'
      case 'security':
        return 'Security alert: Multiple safety blocks detected'
      default:
        return 'Incident detected'
    }
  }

  const getRequestBody = (endpoint: string) => {
    switch (endpoint) {
      case '/qa':
        return { question: 'What is Datadog?', document: 'Datadog is an observability platform.' }
      case '/reason':
        return { prompt: 'Explain the golden signals of SRE and why they matter for LLMs.' }
      case '/stress':
        return { prompt: 'Summarize production incidents.', repetitions: 50 }
      default:
        return {}
    }
  }

  const updateHealthStatus = (scenario: string) => {
    const newStatus = (() => {
      switch (scenario) {
        case 'cost':
          return {
            health_score: 45,
            status: 'critical' as const,
            last_incident: false,
            top_recommendation: 'Cost spike detected! Consider downgrading model or enabling caching to save 30%',
          }
        case 'latency':
          return {
            health_score: 55,
            status: 'degraded' as const,
            last_incident: false,
            top_recommendation: 'Latency SLO breach! Check APM traces and consider model optimization',
          }
        case 'quality':
          return {
            health_score: 50,
            status: 'critical' as const,
            last_incident: false,
            top_recommendation: 'Quality degradation detected! Review prompt engineering and model version',
          }
        case 'security':
          return {
            health_score: 40,
            status: 'critical' as const,
            last_incident: false,
            top_recommendation: 'Security alert! Prompt injection risk detected. Review and block suspicious patterns',
          }
        default:
          return healthStatus
      }
    })()
    
    setHealthStatus(newStatus)
  }

  const resetSystem = () => {
    setHealthStatus({
      health_score: 85,
      status: 'healthy',
      last_incident: false,
      top_recommendation: 'System operating normally',
    })
    setLastTriggered(null)
    setIncidentCount(0)
    setIncidents([])
    setRealTimeMetrics({ latency: 0, cost: 0, errors: 0, requests: 0 })
    setTotalRequests(0)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-400'
      case 'degraded':
        return 'text-yellow-400'
      case 'critical':
        return 'text-red-400'
      default:
        return 'text-gray-400'
    }
  }

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500/20 border-green-500'
      case 'degraded':
        return 'bg-yellow-500/20 border-yellow-500'
      case 'critical':
        return 'bg-red-500/20 border-red-500 animate-pulse'
      default:
        return 'bg-gray-500/20 border-gray-500'
    }
  }

  const scenarioConfig = {
    cost: {
      icon: '🔴',
      color: 'red',
      gradient: 'from-red-600 to-red-800',
      shadow: 'shadow-red-500/50',
      endpoint: '/stress',
      params: { simulate_long_context: 'true' },
    },
    latency: {
      icon: '🟠',
      color: 'orange',
      gradient: 'from-orange-600 to-orange-800',
      shadow: 'shadow-orange-500/50',
      endpoint: '/reason',
      params: { simulate_latency: 'true', simulate_retry: 'true' },
    },
    quality: {
      icon: '🔵',
      color: 'blue',
      gradient: 'from-blue-600 to-blue-800',
      shadow: 'shadow-blue-500/50',
      endpoint: '/qa',
      params: { simulate_bad_prompt: 'true' },
    },
    security: {
      icon: '⚫',
      color: 'purple',
      gradient: 'from-purple-600 to-purple-800',
      shadow: 'shadow-purple-500/50',
      endpoint: '/qa',
      params: { simulate_bad_prompt: 'true' },
    },
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-red-500 via-orange-500 to-yellow-500 bg-clip-text text-transparent">
            🎭 Live Failure Theater
          </h1>
          <p className="text-xl text-gray-400 mb-2">
            One-Click Production Failure Scenarios
          </p>
          <p className="text-sm text-gray-500">
            Watch incidents get created in real-time with Datadog observability
          </p>
        </motion.div>

        {/* Real-time Stats Bar */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="max-w-6xl mx-auto mb-8 grid grid-cols-2 md:grid-cols-4 gap-4"
        >
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
              <Activity className="w-4 h-4" />
              Active Requests
            </div>
            <div className="text-2xl font-bold text-blue-400">{activeRequests}</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
              <Target className="w-4 h-4" />
              Total Requests
            </div>
            <div className="text-2xl font-bold text-green-400">{totalRequests}</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
              <Clock className="w-4 h-4" />
              Avg Latency
            </div>
            <div className="text-2xl font-bold text-yellow-400">
              {realTimeMetrics.latency > 0 ? `${Math.round(realTimeMetrics.latency)}ms` : 'N/A'}
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
              <DollarSign className="w-4 h-4" />
              Total Cost
            </div>
            <div className="text-2xl font-bold text-purple-400">
              ${realTimeMetrics.cost > 0 ? realTimeMetrics.cost.toFixed(4) : '0.0000'}
            </div>
          </div>
        </motion.div>

        {/* Health Status Panel */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="max-w-6xl mx-auto mb-8"
        >
          <div className={`rounded-2xl p-8 border-2 ${getStatusBg(healthStatus.status)} backdrop-blur-sm`}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Health Score with Animation */}
              <div className="text-center">
                <div className="text-sm text-gray-400 mb-2">Health Score</div>
                <motion.div
                  key={healthStatus.health_score}
                  initial={{ scale: 1.2, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ type: 'spring', stiffness: 200 }}
                  className={`text-7xl font-bold ${getStatusColor(healthStatus.status)} mb-2`}
                >
                  {healthStatus.health_score}
                </motion.div>
                <motion.div
                  className={`inline-block px-4 py-2 rounded-full mt-2 ${getStatusBg(healthStatus.status)} border`}
                  whileHover={{ scale: 1.05 }}
                >
                  {healthStatus.status.toUpperCase()}
                </motion.div>
              </div>

              {/* Incident Status */}
              <div className="text-center">
                <div className="text-sm text-gray-400 mb-2">Last Incident</div>
                <motion.div
                  key={healthStatus.last_incident ? 'yes' : 'no'}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className={`text-5xl font-bold mb-2 ${healthStatus.last_incident ? 'text-red-500' : 'text-green-500'}`}
                >
                  {healthStatus.last_incident ? <AlertTriangle className="inline w-12 h-12" /> : <CheckCircle className="inline w-12 h-12" />}
                </motion.div>
                <div className="text-sm text-gray-500">
                  Total: <span className="font-bold text-white">{incidentCount}</span> incidents
                </div>
              </div>

              {/* Top Recommendation */}
              <div className="text-center md:text-left">
                <div className="text-sm text-gray-400 mb-2">Top Recommendation</div>
                <motion.div
                  key={healthStatus.top_recommendation}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="text-lg font-semibold text-yellow-400"
                >
                  {healthStatus.top_recommendation}
                </motion.div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Real-time Metrics Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-6xl mx-auto mb-8 bg-gray-800/50 rounded-2xl p-6 border border-gray-700"
        >
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Real-time Health Score Trend
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={metricsHistory}>
              <defs>
                <linearGradient id="colorHealth" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" domain={[0, 100]} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                labelStyle={{ color: '#fff' }}
              />
              <Area
                type="monotone"
                dataKey="health_score"
                stroke="#10b981"
                fillOpacity={1}
                fill="url(#colorHealth)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Failure Buttons */}
        <div className="max-w-6xl mx-auto mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {Object.entries(scenarioConfig).map(([scenario, config]) => (
              <motion.button
                key={scenario}
                onClick={() => triggerScenario(scenario, config.endpoint, config.params)}
                disabled={loading}
                whileHover={{ scale: 1.05, y: -5 }}
                whileTap={{ scale: 0.95 }}
                className={`group relative overflow-hidden rounded-2xl bg-gradient-to-br ${config.gradient} p-8 text-white transform transition-all duration-300 hover:shadow-2xl hover:${config.shadow} disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0"
                  initial={{ x: '-100%' }}
                  whileHover={{ x: '100%' }}
                  transition={{ duration: 1, repeat: Infinity, repeatDelay: 2 }}
                />
                <div className="relative z-10">
                  <motion.div
                    className="text-5xl mb-4"
                    animate={loading && lastTriggered === scenario ? { rotate: [0, 10, -10, 0] } : {}}
                    transition={{ duration: 0.5, repeat: Infinity }}
                  >
                    {config.icon}
                  </motion.div>
                  <div className="text-2xl font-bold mb-2 capitalize">{scenario}</div>
                  <div className="text-sm opacity-90">
                    {scenario === 'cost' && 'Triggers cost anomaly monitor'}
                    {scenario === 'latency' && 'Breaches SLO threshold'}
                    {scenario === 'quality' && 'Degrades similarity score'}
                    {scenario === 'security' && 'Triggers safety blocks'}
                  </div>
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Recent Incidents */}
        {incidents.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="max-w-6xl mx-auto mb-8 bg-gray-800/50 rounded-2xl p-6 border border-gray-700"
          >
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              Recent Incidents
            </h3>
            <div className="space-y-2">
              <AnimatePresence>
                {incidents.slice(0, 5).map((incident, index) => (
                  <motion.div
                    key={incident.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="bg-gray-900/50 rounded-lg p-4 border border-gray-700 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${
                        incident.severity === 'critical' ? 'bg-red-500' :
                        incident.severity === 'high' ? 'bg-orange-500' :
                        incident.severity === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                      }`} />
                      <div>
                        <div className="font-semibold capitalize">{incident.type}</div>
                        <div className="text-sm text-gray-400">{incident.description}</div>
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      {incident.timestamp.toLocaleTimeString()}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </motion.div>
        )}

        {/* Reset Button */}
        <div className="text-center mb-8">
          <motion.button
            onClick={resetSystem}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="px-8 py-4 bg-gray-700 hover:bg-gray-600 rounded-xl font-semibold transition-all duration-300 transform flex items-center gap-2 mx-auto"
          >
            <Zap className="w-5 h-5" />
            Reset System
          </motion.button>
        </div>

        {/* Loading Indicator */}
        <AnimatePresence>
          {loading && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="fixed top-4 right-4 bg-yellow-500 text-black px-6 py-3 rounded-lg font-bold shadow-lg z-50"
            >
              <div className="flex items-center gap-2">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                  ⚡
                </motion.div>
                Triggering {lastTriggered} scenario...
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Success Indicator */}
        <AnimatePresence>
          {lastTriggered && !loading && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg font-bold shadow-lg z-50"
            >
              ✅ {lastTriggered} scenario triggered!
            </motion.div>
          )}
        </AnimatePresence>

        {/* Footer Info */}
        <div className="max-w-4xl mx-auto mt-12 text-center text-gray-400 text-sm">
          <p>💡 Check Datadog dashboard to see monitors trigger and incidents get created automatically</p>
          <p className="mt-2">🔗 API: {API_BASE_URL}</p>
          <div className="mt-4 flex items-center justify-center gap-4">
            <a
              href={`${API_BASE_URL}/docs`}
              target="_blank"
              className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/30 rounded-lg text-blue-400 transition-colors flex items-center gap-2"
            >
              <ExternalLink className="w-4 h-4" />
              View Swagger UI
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
