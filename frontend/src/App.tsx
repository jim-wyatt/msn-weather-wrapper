import { useState, useEffect } from 'react';
import CityAutocomplete from './components/CityAutocomplete';
import type { City, WeatherData, RecentSearch } from './types';
import './App.css';

type TempUnit = 'C' | 'F';

function App() {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [recentSearches, setRecentSearches] = useState<RecentSearch[]>([]);
  const [loadingLocation, setLoadingLocation] = useState<boolean>(false);
  const [unit, setUnit] = useState<TempUnit>(() => {
    const saved = localStorage.getItem('tempUnit');
    return (saved === 'C' || saved === 'F') ? saved : 'C';
  });

  // Load recent searches on mount
  useEffect(() => {
    fetchRecentSearches();
  }, []);

  const fetchRecentSearches = async (): Promise<void> => {
    try {
      const response = await fetch('/api/v1/recent-searches', {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setRecentSearches(data.recent_searches || []);
      }
    } catch (err) {
      console.error('Failed to fetch recent searches:', err);
    }
  };

  const convertTemp = (tempC: number, to: TempUnit): number => {
    return to === 'F' ? (tempC * 9 / 5) + 32 : tempC;
  };

  const fetchWeatherWithRetry = async (city: City, retries = 3): Promise<void> => {
    setLoading(true);
    setError(null);

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const response = await fetch(
          `/api/v1/weather?city=${encodeURIComponent(city.name)}&country=${encodeURIComponent(city.country)}`,
          { credentials: 'include' }
        );

        if (!response.ok) {
          const errorData = await response.json();
          
          // Don't retry on client errors (4xx)
          if (response.status >= 400 && response.status < 500) {
            throw new Error(errorData.message || 'Failed to fetch weather');
          }
          
          // Retry on server errors (5xx) or network issues
          if (attempt === retries) {
            throw new Error(errorData.message || 'Failed to fetch weather after multiple attempts');
          }
          
          // Wait before retrying (exponential backoff)
          await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
          continue;
        }

        const data: WeatherData = await response.json();
        setWeather(data);
        setError(null);
        await fetchRecentSearches(); // Refresh recent searches
        break;
      } catch (err) {
        if (attempt === retries) {
          const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
          setError(errorMessage);
          setWeather(null);
        } else {
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
        }
      }
    }

    setLoading(false);
  };

  const fetchWeatherByLocation = async (): Promise<void> => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      return;
    }

    setLoadingLocation(true);
    setError(null);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        
        try {
          const response = await fetch(
            `/api/v1/weather/coordinates?lat=${latitude}&lon=${longitude}`,
            { credentials: 'include' }
          );

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Failed to fetch weather');
          }

          const data: WeatherData = await response.json();
          setWeather(data);
          setError(null);
          await fetchRecentSearches(); // Refresh recent searches
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
          setError(errorMessage);
          setWeather(null);
        } finally {
          setLoadingLocation(false);
        }
      },
      (error) => {
        setError(`Failed to get your location: ${error.message}`);
        setLoadingLocation(false);
      }
    );
  };

  const handleRecentSearchClick = (search: RecentSearch): void => {
    fetchWeatherWithRetry({ name: search.city, country: search.country });
  };

  const clearRecentSearches = async (): Promise<void> => {
    try {
      const response = await fetch('/api/v1/recent-searches', {
        method: 'DELETE',
        credentials: 'include',
      });
      if (response.ok) {
        setRecentSearches([]);
      }
    } catch (err) {
      console.error('Failed to clear recent searches:', err);
    }
  };

  const toggleUnit = (): void => {
    const newUnit: TempUnit = unit === 'C' ? 'F' : 'C';
    setUnit(newUnit);
    localStorage.setItem('tempUnit', newUnit);
  };

  const getWeatherIcon = (condition: string): string => {
    const lowerCondition = condition.toLowerCase();
    if (lowerCondition.includes('sunny') || lowerCondition.includes('clear')) return '☀️';
    if (lowerCondition.includes('cloud')) return '☁️';
    if (lowerCondition.includes('rain')) return '🌧️';
    if (lowerCondition.includes('snow')) return '❄️';
    if (lowerCondition.includes('storm') || lowerCondition.includes('thunder')) return '⛈️';
    if (lowerCondition.includes('fog') || lowerCondition.includes('mist')) return '🌫️';
    return '🌤️';
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1 className="title">🌤️ MSN Weather</h1>
          <p className="subtitle">Get real-time weather information for any city</p>
        </header>

        <div className="search-section">
          <CityAutocomplete onCitySelect={fetchWeatherWithRetry} />
          <button 
            className="location-button" 
            onClick={fetchWeatherByLocation}
            disabled={loadingLocation}
            title="Use my location"
          >
            {loadingLocation ? '⏳' : '📍'} Use My Location
          </button>
        </div>

        {recentSearches.length > 0 && (
          <div className="recent-searches">
            <div className="recent-searches-header">
              <h3>Recent Searches</h3>
              <button 
                className="clear-button" 
                onClick={clearRecentSearches}
                title="Clear all recent searches"
              >
                Clear
              </button>
            </div>
            <div className="recent-searches-list">
              {recentSearches.map((search, index) => (
                <button
                  key={index}
                  className="recent-search-item"
                  onClick={() => handleRecentSearchClick(search)}
                >
                  {search.city}, {search.country}
                </button>
              ))}
            </div>
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Fetching weather data...</p>
          </div>
        )}

        {error && (
          <div className="error-card">
            <span className="error-icon">⚠️</span>
            <div className="error-content">
              <h3>Error</h3>
              <p>{error}</p>
            </div>
          </div>
        )}

        {weather && !loading && (
          <div className="weather-card">
            <div className="weather-header">
              <div className="location-info">
                <h2 className="location-name">{weather.location.city}</h2>
                <p className="location-country">{weather.location.country}</p>
              </div>
              <div className="weather-icon-large">
                {getWeatherIcon(weather.condition)}
              </div>
            </div>

            <div className="temperature-section">
              <div className="temperature-main">
                {Math.round(convertTemp(weather.temperature, unit))}°{unit}
                <button 
                  className="unit-toggle" 
                  onClick={toggleUnit}
                  title={`Switch to °${unit === 'C' ? 'F' : 'C'}`}
                >
                  °{unit === 'C' ? 'F' : 'C'}
                </button>
              </div>
              <div className="condition">{weather.condition}</div>
            </div>

            <div className="weather-details">
              <div className="detail-item">
                <span className="detail-icon">💧</span>
                <div className="detail-content">
                  <span className="detail-label">Humidity</span>
                  <span className="detail-value">{weather.humidity}%</span>
                </div>
              </div>

              <div className="detail-item">
                <span className="detail-icon">💨</span>
                <div className="detail-content">
                  <span className="detail-label">Wind Speed</span>
                  <span className="detail-value">{weather.wind_speed.toFixed(1)} km/h</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {!weather && !loading && !error && (
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <h3>Search for a city</h3>
            <p>Start typing in the search box above to get weather information</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
