import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Live Failure Theater - LLM Reliability Control Plane',
  description: 'One-click failure scenarios for LLM observability demo',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}



