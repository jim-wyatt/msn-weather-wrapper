# MSN Weather Frontend

A modern Next.js frontend for the MSN Weather Wrapper API.

## Features

- 🔍 **Smart City Autocomplete** - Instant search through 463+ cities worldwide
- 🎨 **Beautiful UI** - Modern gradient design with smooth animations
- 📱 **Fully Responsive** - Perfect on desktop, tablet, and mobile
- ⚡ **Lightning Fast** - Powered by Next.js App Router with server-side rendering
- 🌐 **API Proxy** - Seamless integration with FastAPI backend via Next.js rewrites
- ♿ **Accessible** - Keyboard navigation support for autocomplete

## Quick Start

### Prerequisites

- Node.js 24+ and npm
- FastAPI server running on `http://localhost:5000`

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Open `http://localhost:3000` in your browser.

### Production Build

```bash
npm run build
npm run preview
```

## How It Works

1. **City Search** - Type in the search box to see matching cities
2. **Autocomplete** - Navigate suggestions with arrow keys or mouse
3. **Weather Display** - Select a city to fetch and display weather data
4. **Real-time Updates** - Data is fetched fresh from MSN Weather via the API

## API Integration

The frontend uses Next.js rewrites to proxy API requests to the FastAPI backend:

```typescript
// In next.config.ts
async rewrites() {
  const apiUrl = process.env.API_URL ?? 'http://localhost:5000';
  return [
    {
      source: '/api/:path*',
      destination: `${apiUrl}/api/:path*`,
    },
  ];
},
```

This means frontend code can make requests to `/api/v1/weather` and they'll be automatically routed to `http://localhost:5000/api/v1/weather`. In production, nginx handles this proxying instead.

## Project Structure

```
frontend/
├── app/                 # Next.js App Router directory
│   ├── layout.tsx       # Root layout with metadata and global CSS
│   ├── page.tsx         # Main weather app page (client component)
│   ├── globals.css      # Global styles
│   ├── types.ts         # TypeScript interfaces
│   ├── components/      # Reusable UI components
│   │   ├── CityAutocomplete.tsx
│   │   └── CityAutocomplete.css
│   └── data/
│       └── cities.ts    # Static city list (463 cities)
├── public/              # Static assets (SVG, manifest)
├── tests/e2e/           # Playwright browser tests
├── next.config.ts       # Next.js configuration (rewrites, standalone output)
├── playwright.config.ts # Playwright test configuration
├── tsconfig.json        # TypeScript configuration
└── package.json         # Dependencies and scripts
```

## Components

### CityAutocomplete

A smart autocomplete input component with:
- Fuzzy search through city names
- Keyboard navigation (arrow keys, Enter, Escape)
- Click-outside to close
- Visual selection indicator

### App (page.tsx)

Main weather application with:
- Weather data fetching and display
- Loading states
- Error handling with retry logic
- Weather icons based on conditions
- Temperature, humidity, and wind speed display
- Temperature unit toggle (°C / °F) with localStorage persistence

## Customization

### Adding More Cities

Edit `app/data/cities.ts` to add more cities:

```typescript
export const cities = [
  { name: "Your City", country: "Your Country" },
  // ... more cities
];
```

### Styling

- Global styles: `app/globals.css`
- Autocomplete styles: `app/components/CityAutocomplete.css`

## Tech Stack

- **Next.js 16** - React framework with App Router and standalone output
- **React 19** - UI library
- **TypeScript** - Type safety
- **Vanilla CSS** - No CSS framework needed, custom styles included

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

MIT
