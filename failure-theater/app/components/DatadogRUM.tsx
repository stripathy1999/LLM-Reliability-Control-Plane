'use client'

import { useEffect } from 'react'

/**
 * Datadog RUM (Real User Monitoring) Integration
 * 
 * This component initializes Datadog RUM to track user interactions,
 * performance metrics, and errors in the Failure Theater UI.
 * 
 * This demonstrates frontend observability for the hackathon submission.
 */
export default function DatadogRUM() {
  useEffect(() => {
    // Only initialize in browser
    if (typeof window === 'undefined') return

    // Get RUM configuration from environment variables
    const ddApplicationId = process.env.NEXT_PUBLIC_DD_APPLICATION_ID
    const ddClientToken = process.env.NEXT_PUBLIC_DD_CLIENT_TOKEN
    const ddSite = process.env.NEXT_PUBLIC_DD_SITE || 'datadoghq.com'
    const ddService = process.env.NEXT_PUBLIC_DD_SERVICE || 'failure-theater-ui'
    const ddEnv = process.env.NEXT_PUBLIC_DD_ENV || 'local'
    const ddVersion = process.env.NEXT_PUBLIC_DD_VERSION || '1.0.0'

    // Skip if not configured
    if (!ddApplicationId || !ddClientToken) {
      console.warn('Datadog RUM not configured: Missing DD_APPLICATION_ID or DD_CLIENT_TOKEN')
      return
    }

    // Dynamically load Datadog RUM script
    const script = document.createElement('script')
    script.src = `https://www.datadoghq-browser-agent.com/${ddSite}/v5/datadog-rum.js`
    script.async = true
    script.onload = () => {
      // Initialize RUM after script loads
      if ((window as any).DD_RUM) {
        ;(window as any).DD_RUM.init({
          applicationId: ddApplicationId,
          clientToken: ddClientToken,
          site: ddSite,
          service: ddService,
          env: ddEnv,
          version: ddVersion,
          sessionSampleRate: 100, // 100% of sessions for demo
          sessionReplaySampleRate: 100, // 100% for demo
          trackResources: true,
          trackLongTasks: true,
          defaultPrivacyLevel: 'allow',
          beforeSend: (event: any) => {
            // Add custom context
            event.context = {
              ...event.context,
              ui_component: 'failure-theater',
              feature: 'llm-reliability-control-plane',
            }
            return true
          },
        })

        // Add custom actions
        ;(window as any).DD_RUM.addAction('failure_scenario_triggered', {
          component: 'failure-theater',
        })

        console.log('Datadog RUM initialized successfully')
      }
    }
    script.onerror = () => {
      console.error('Failed to load Datadog RUM script')
    }

    document.head.appendChild(script)

    // Cleanup
    return () => {
      if (script.parentNode) {
        script.parentNode.removeChild(script)
      }
    }
  }, [])

  return null
}

/**
 * Helper function to track custom RUM events
 */
export function trackRUMEvent(name: string, context?: Record<string, any>) {
  if (typeof window !== 'undefined' && (window as any).DD_RUM) {
    ;(window as any).DD_RUM.addAction(name, {
      ...context,
      timestamp: new Date().toISOString(),
    })
  }
}

/**
 * Helper function to track RUM errors
 */
export function trackRUMError(error: Error, context?: Record<string, any>) {
  if (typeof window !== 'undefined' && (window as any).DD_RUM) {
    ;(window as any).DD_RUM.addError(error, {
      ...context,
      source: 'failure-theater-ui',
    })
  }
}

