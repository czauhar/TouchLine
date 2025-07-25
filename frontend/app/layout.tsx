import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import SessionProviderWrapper from './SessionProviderWrapper'
import RealTimeNotifications from '../components/ui/RealTimeNotifications'
import UserMenu from '../components/ui/UserMenu'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'TouchLine - Sports Alerts',
  description: 'Real-time sports alerts and notifications',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <SessionProviderWrapper>
          <div className="min-h-screen bg-gray-50">
            <div className="w-full flex justify-end items-center px-8 py-4">
              <RealTimeNotifications userId={1} />
              <UserMenu />
            </div>
            {children}
          </div>
        </SessionProviderWrapper>
      </body>
    </html>
  )
} 