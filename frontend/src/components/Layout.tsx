import { Link, useNavigate } from 'react-router-dom';
import { logout } from '../services/api';

export default function Layout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="text-xl font-bold text-green-700">Diet Driven Health</Link>
          <div className="flex gap-4 text-sm">
            <Link to="/" className="text-gray-600 hover:text-green-700">Dashboard</Link>
            <Link to="/meal-plans" className="text-gray-600 hover:text-green-700">Meal Plans</Link>
            <Link to="/recipes" className="text-gray-600 hover:text-green-700">Recipes</Link>
            <Link to="/upload" className="text-gray-600 hover:text-green-700">Upload</Link>
            <Link to="/history" className="text-gray-600 hover:text-green-700">History</Link>
            <Link to="/profile" className="text-gray-600 hover:text-green-700">Profile</Link>
            <button onClick={handleLogout} className="text-red-500 hover:text-red-700">Logout</button>
          </div>
        </div>
      </nav>
      <main className="max-w-6xl mx-auto px-4 py-6">{children}</main>
    </div>
  );
}
