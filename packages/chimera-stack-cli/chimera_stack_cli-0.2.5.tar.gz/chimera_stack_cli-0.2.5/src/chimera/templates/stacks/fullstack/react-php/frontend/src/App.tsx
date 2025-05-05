import { useState, useEffect } from 'react'
import axios from 'axios'

function App() {
  const [apiStatus, setApiStatus] = useState<string>('Loading...')
  const [apiData, setApiData] = useState<any>(null)

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || '/api'

    axios.get(`${apiUrl}/status`)
      .then(response => {
        setApiStatus('Connected')
        setApiData(response.data)
      })
      .catch(error => {
        console.error('API connection error:', error)
        setApiStatus('Error connecting to API')
      })
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-8">
          React + PHP Fullstack
        </h1>

        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2 text-gray-700">API Status</h2>
          <div className={`px-4 py-3 rounded ${
            apiStatus === 'Connected'
              ? 'bg-green-100 text-green-800'
              : apiStatus === 'Loading...'
                ? 'bg-blue-100 text-blue-800'
                : 'bg-red-100 text-red-800'
          }`}>
            {apiStatus}
          </div>
        </div>

        {apiData && (
          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-2 text-gray-700">API Response</h2>
            <pre className="bg-gray-100 p-3 rounded overflow-auto text-sm">
              {JSON.stringify(apiData, null, 2)}
            </pre>
          </div>
        )}

        <div className="text-center text-gray-500 text-sm">
          <p>Built with Vite, React, Tailwind, and PHP</p>
        </div>
      </div>
    </div>
  )
}

export default App
