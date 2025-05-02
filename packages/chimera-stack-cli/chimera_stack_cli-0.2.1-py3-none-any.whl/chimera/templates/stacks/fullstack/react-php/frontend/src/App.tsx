import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

interface Post {
  id: number;
  title: string;
  content: string;
  user_id: number;
}

interface User {
  id: number;
  name: string;
  email: string;
}

function App() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

    // Fetch data from API
    const fetchData = async () => {
      try {
        setLoading(true);

        // Using Promise.all to fetch both endpoints in parallel
        const [postsResponse, usersResponse] = await Promise.all([
          axios.get(`${apiUrl}/posts`),
          axios.get(`${apiUrl}/users`)
        ]);

        setPosts(postsResponse.data);
        setUsers(usersResponse.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load data from API. Please check if the backend server is running.');
        // Set empty arrays so the UI doesn't break
        setPosts([]);
        setUsers([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <img src="https://raw.githubusercontent.com/robinmoisson/static-react-logo/master/react.svg" alt="React Logo" width={120} />
        <h1>Welcome to ChimeraStack</h1>
        <p>
          This project was scaffolded with <strong>ChimeraStack CLI</strong> and ships with a
          ready-to-code React&nbsp;+&nbsp;PHP&nbsp;+&nbsp;MySQL environment.
        </p>
        <p>Edit <code>frontend/src/App.tsx</code> and save to reload.</p>
        <div style={{ marginTop: "1rem" }}>
          {process.env.WDS_SOCKET_PORT && (
            <a
              href={`http://localhost:${process.env.WDS_SOCKET_PORT}`}
              target="_blank"
              rel="noreferrer"
              className="link"
            >
              React Dev Server
            </a>
          )}
          <span> · </span>
          <a href="/api" className="link">Backend API</a>
          <span> · </span>
          <a
            href={
              window.location.hostname === "localhost"
                ? `http://localhost:8080`
                : "/phpmyadmin"
            }
            target="_blank"
            rel="noreferrer"
            className="link"
          >
            phpMyAdmin
          </a>
        </div>
      </header>

      <div className="container">
        {loading ? (
          <div className="loading">Loading data...</div>
        ) : error ? (
          <div className="error">
            <h2>Error</h2>
            <p>{error}</p>
            <div className="connection-info">
              <h3>Connection Information</h3>
              <p>Make sure your backend API is running and accessible.</p>
              <p>Current API URL: {process.env.REACT_APP_API_URL || 'http://localhost:8000/api'}</p>
            </div>
          </div>
        ) : (
          <div className="data-container">
            <div className="data-section">
              <h2>Users</h2>
              {users.length === 0 ? (
                <p>No users found</p>
              ) : (
                <ul>
                  {users.map(user => (
                    <li key={user.id}>
                      <h3>{user.name}</h3>
                      <p>{user.email}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="data-section">
              <h2>Posts</h2>
              {posts.length === 0 ? (
                <p>No posts found</p>
              ) : (
                <ul>
                  {posts.map(post => (
                    <li key={post.id}>
                      <h3>{post.title}</h3>
                      <p>{post.content}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </div>

      <footer>
        <p>Powered by ChimeraStack</p>
      </footer>
    </div>
  );
}

export default App;
