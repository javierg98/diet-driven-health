import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { login } from '../services/api';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(username, password);
      navigate('/');
      window.location.reload();
    } catch {
      setError('Invalid username or password');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-md w-full max-w-sm">
        <h1 className="text-2xl font-bold text-green-700 mb-6 text-center">Diet Driven Health</h1>
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
        <input
          type="text" placeholder="Username" value={username}
          onChange={e => setUsername(e.target.value)}
          className="w-full border rounded px-3 py-2 mb-4"
        />
        <input
          type="password" placeholder="Password" value={password}
          onChange={e => setPassword(e.target.value)}
          className="w-full border rounded px-3 py-2 mb-4"
        />
        <button type="submit" className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700">
          Login
        </button>
        <p className="text-center text-sm mt-4">
          No account? <Link to="/register" className="text-green-600 hover:underline">Register</Link>
        </p>
      </form>
    </div>
  );
}
