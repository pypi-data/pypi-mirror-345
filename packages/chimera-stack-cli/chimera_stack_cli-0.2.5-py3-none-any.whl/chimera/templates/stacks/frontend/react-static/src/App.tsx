import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">
          🪄 ChimeraStack React starter
        </h1>

        <p className="text-gray-600 text-center mb-8">
          Edit <code className="bg-gray-100 px-2 py-1 rounded font-mono">src/App.tsx</code> and save to reload.
        </p>

        <div className="flex justify-center">
          <button
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
            onClick={() => setCount((count) => count + 1)}
          >
            Count is {count}
          </button>
        </div>

        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>Built with Vite, React, and Tailwind CSS</p>
        </div>
      </div>
    </div>
  )
}

export default App
