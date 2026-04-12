import type { Metadata, Viewport } from 'next';
import type { ReactNode } from 'react';
import './globals.css';

export const metadata: Metadata = {
  title: 'MSN Weather Wrapper - Real-time Weather Data',
  description:
    'A modern, production-ready Python wrapper for MSN Weather with Next.js frontend. Get weather data for 463+ cities worldwide with autocomplete and geolocation support.',
  keywords:
    'weather, MSN Weather, weather API, Python, Next.js, React, weather data, temperature, humidity, wind speed',
  authors: [{ name: 'Jim Wyatt' }],
  robots: 'index, follow',
  openGraph: {
    type: 'website',
    url: 'https://jim-wyatt.github.io/msn-weather-wrapper/',
    title: 'MSN Weather Wrapper - Real-time Weather Data',
    description:
      'A modern, production-ready Python wrapper for MSN Weather with Next.js frontend. Get weather data for 463+ cities worldwide.',
    images: ['https://jim-wyatt.github.io/msn-weather-wrapper/og-image.png'],
  },
  twitter: {
    card: 'summary_large_image',
    site: 'https://jim-wyatt.github.io/msn-weather-wrapper/',
    title: 'MSN Weather Wrapper - Real-time Weather Data',
    description:
      'A modern, production-ready Python wrapper for MSN Weather with Next.js frontend. Get weather data for 463+ cities worldwide.',
    images: ['https://jim-wyatt.github.io/msn-weather-wrapper/og-image.png'],
  },
  icons: {
    icon: '/weather.svg',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
};

export const viewport: Viewport = {
  themeColor: '#0078d4',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
