import type { Metadata } from 'next'
import './globals.css'
import DatadogRUM from './components/DatadogRUM'

export const metadata: Metadata = {
  title: 'LLM Reliability Control Plane',
  description: 'Live Failure Theater',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <DatadogRUM />
        {children}
      </body>
    </html>
  )
}




