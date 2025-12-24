'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface HealthStatus {
  health_score: number
  status: 'healthy' | 'degraded' | 'critical'
  last_incident: boolean
  top_recommendation: string
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

  const fetchHealthStatus = async () => {
    try {
      // In production, this would call your /insights endpoint
      // For demo, we'll simulate based on triggered scenarios
      const response = await axios.get(`${API_BASE_URL}/insights/health-score`)
      // Simulate health score based on recent triggers
      return healthStatus
    } catch (error) {
      console.error('Error fetching health status:', error)
    }
  }

  const triggerScenario = async (scenario: string, endpoint: string, params: Record<string, string>) => {
    setLoading(true)
    setLastTriggered(scenario)
    
    try {
      // Send multiple requests to trigger the scenario
      const requests = []
      for (let i = 0; i < 15; i++) {
        requests.push(axios.post(`${API_BASE_URL}${endpoint}`, getRequestBody(endpoint), { params }))
      }
      
      await Promise.all(requests)
      
      // Update health status based on scenario
      updateHealthStatus(scenario)
      setIncidentCount(prev => prev + 1)
      
      // Simulate incident creation
      setTimeout(() => {
        setHealthStatus(prev => ({ ...prev, last_incident: true }))
      }, 2000)
      
    } catch (error) {
      console.error(`Error triggering ${scenario}:`, error)
    } finally {
      setLoading(false)
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
    switch (scenario) {
      case 'cost':
        setHealthStatus({
          health_score: 45,
          status: 'critical',
          last_incident: false,
          top_recommendation: 'Cost spike detected! Consider downgrading model or enabling caching to save 30%',
        })
        break
      case 'latency':
        setHealthStatus({
          health_score: 55,
          status: 'degraded',
          last_incident: false,
          top_recommendation: 'Latency SLO breach! Check APM traces and consider model optimization',
        })
        break
      case 'quality':
        setHealthStatus({
          health_score: 50,
          status: 'critical',
          last_incident: false,
          top_recommendation: 'Quality degradation detected! Review prompt engineering and model version',
        })
        break
      case 'security':
        setHealthStatus({
          health_score: 40,
          status: 'critical',
          last_incident: false,
          top_recommendation: 'Security alert! Prompt injection risk detected. Review and block suspicious patterns',
        })
        break
    }
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
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-500'
      case 'degraded':
        return 'text-yellow-500'
      case 'critical':
        return 'text-red-500'
      default:
        return 'text-gray-500'
    }
  }

  const getStatusBg = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500'
      case 'degraded':
        return 'bg-yellow-500'
      case 'critical':
        return 'bg-red-500 animate-pulse'
      default:
        return 'bg-gray-500'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-red-500 via-orange-500 to-yellow-500 bg-clip-text text-transparent">
            🎭 Live Failure Theater
          </h1>
          <p className="text-xl text-gray-400 mb-2">
            One-Click Production Failure Scenarios
          </p>
          <p className="text-sm text-gray-500">
            Watch incidents get created in real-time with Datadog observability
          </p>
        </div>

        {/* Health Status Panel */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className={`rounded-2xl p-8 border-4 ${healthStatus.status === 'critical' ? 'border-red-500 animate-glow' : healthStatus.status === 'degraded' ? 'border-yellow-500' : 'border-green-500'}`}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Health Score */}
              <div className="text-center">
                <div className="text-sm text-gray-400 mb-2">Health Score</div>
                <div className={`text-6xl font-bold ${getStatusColor(healthStatus.status)}`}>
                  {healthStatus.health_score}
                </div>
                <div className={`inline-block px-4 py-2 rounded-full mt-2 ${getStatusBg(healthStatus.status)}`}>
                  {healthStatus.status.toUpperCase()}
                </div>
              </div>

              {/* Incident Status */}
              <div className="text-center">
                <div className="text-sm text-gray-400 mb-2">Last Incident</div>
                <div className={`text-4xl font-bold mb-2 ${healthStatus.last_incident ? 'text-red-500 animate-pulse' : 'text-green-500'}`}>
                  {healthStatus.last_incident ? '🚨 YES' : '✅ NO'}
                </div>
                <div className="text-sm text-gray-500">
                  Total: {incidentCount} incidents
                </div>
              </div>

              {/* Top Recommendation */}
              <div className="text-center md:text-left">
                <div className="text-sm text-gray-400 mb-2">Top Recommendation</div>
                <div className="text-lg font-semibold text-yellow-400">
                  {healthStatus.top_recommendation}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Failure Buttons */}
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* Cost Explosion */}
            <button
              onClick={() => triggerScenario('cost', '/stress', { simulate_long_context: 'true' })}
              disabled={loading}
              className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-red-600 to-red-800 p-8 text-white transform transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-red-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-red-400/0 via-red-400/20 to-red-400/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
              <div className="relative z-10">
                <div className="text-5xl mb-4">🔴</div>
                <div className="text-2xl font-bold mb-2">Cost Explosion</div>
                <div className="text-sm text-red-200">
                  Triggers cost anomaly monitor
                </div>
              </div>
            </button>

            {/* Latency Spike */}
            <button
              onClick={() => triggerScenario('latency', '/reason', { simulate_latency: 'true', simulate_retry: 'true' })}
              disabled={loading}
              className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-orange-600 to-orange-800 p-8 text-white transform transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-orange-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-orange-400/0 via-orange-400/20 to-orange-400/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
              <div className="relative z-10">
                <div className="text-5xl mb-4">🟠</div>
                <div className="text-2xl font-bold mb-2">Latency Spike</div>
                <div className="text-sm text-orange-200">
                  Breaches SLO threshold
                </div>
              </div>
            </button>

            {/* Quality Drop */}
            <button
              onClick={() => triggerScenario('quality', '/qa', { simulate_bad_prompt: 'true' })}
              disabled={loading}
              className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-600 to-blue-800 p-8 text-white transform transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-blue-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-blue-400/0 via-blue-400/20 to-blue-400/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
              <div className="relative z-10">
                <div className="text-5xl mb-4">🔵</div>
                <div className="text-2xl font-bold mb-2">Quality Drop</div>
                <div className="text-sm text-blue-200">
                  Degrades similarity score
                </div>
              </div>
            </button>

            {/* Security Attack */}
            <button
              onClick={() => triggerScenario('security', '/qa', { simulate_bad_prompt: 'true' })}
              disabled={loading}
              className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-purple-600 to-purple-800 p-8 text-white transform transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-purple-400/0 via-purple-400/20 to-purple-400/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
              <div className="relative z-10">
                <div className="text-5xl mb-4">⚫</div>
                <div className="text-2xl font-bold mb-2">Security Attack</div>
                <div className="text-sm text-purple-200">
                  Triggers safety blocks
                </div>
              </div>
            </button>
          </div>

          {/* Reset Button */}
          <div className="text-center">
            <button
              onClick={resetSystem}
              className="px-8 py-4 bg-gray-700 hover:bg-gray-600 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105"
            >
              🔄 Reset System
            </button>
          </div>

          {/* Loading Indicator */}
          {loading && (
            <div className="fixed top-4 right-4 bg-yellow-500 text-black px-6 py-3 rounded-lg font-bold animate-pulse">
              ⚡ Triggering {lastTriggered} scenario...
            </div>
          )}

          {/* Last Triggered Indicator */}
          {lastTriggered && !loading && (
            <div className="fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg font-bold">
              ✅ {lastTriggered} scenario triggered!
            </div>
          )}
        </div>

        {/* Footer Info */}
        <div className="max-w-4xl mx-auto mt-12 text-center text-gray-400 text-sm">
          <p>💡 Check Datadog dashboard to see monitors trigger and incidents get created automatically</p>
          <p className="mt-2">🔗 API: {API_BASE_URL}</p>
        </div>
      </div>
    </div>
  )
}



