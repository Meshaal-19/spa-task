import { useState } from 'react';
import { setToken } from './api';
import LoginView from './LoginView';
import Dashboard from './Dashboard';
import './App.css';

export default function App() {
  const [authed, setAuthed] = useState(false);

  function handleLogin(token) {
    setToken(token);
    setAuthed(true);
  }

  function handleLogout() {
    setAuthed(false);
  }

  return authed ? <Dashboard onLogout={handleLogout} /> : <LoginView onLogin={handleLogin} />;
}
