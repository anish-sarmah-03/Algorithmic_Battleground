import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import API from '../api';

export default function Dashboard() {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();
  const username = localStorage.getItem('username') || 'Coder';

  // useEffect runs automatically as soon as this page loads
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        // Hit the Day 4 backend endpoint! Our api.js auto-attaches the token.
        const res = await API.get('/analytics/dashboard');
        setChartData(res.data.chart_data);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setError('Failed to fetch analytics. Please log in again.');
        setLoading(false);
        
        // If the token is expired or invalid (401 Unauthorized), kick them back to login
        if (err.response?.status === 401) {
            localStorage.removeItem('token');
            navigate('/login');
        }
      }
    };

    fetchAnalytics();
  }, [navigate]);

  // Handle wiping the session
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    navigate('/login');
  };

  // Show a loading screen while we wait for the backend
  if (loading) {
    return <h2 style={{ textAlign: 'center', marginTop: '50px' }}>Loading your battle stats...</h2>;
  }

  return (
    <div style={{ maxWidth: '800px', margin: '40px auto', padding: '20px' }}>
      
      {/* Header Section */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Welcome back, {username}!</h2>
        <button 
          onClick={handleLogout} 
          style={{ padding: '8px 16px', backgroundColor: '#ff4d4f', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          Logout
        </button>
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {/* Analytics Section */}
      <div style={{ marginTop: '40px', backgroundColor: '#f9f9f9', padding: '30px', borderRadius: '8px' }}>
        <h3 style={{ textAlign: 'center', marginBottom: '30px' }}>Your Topic Performance</h3>

        {chartData.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666' }}>No submissions yet. Head to the Arena to start coding!</p>
        ) : (
          <div style={{ width: '100%', height: 400 }}>
            {/* ResponsiveContainer makes the chart scale to fit the screen */}
            <ResponsiveContainer>
              <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                {/* These dataKeys exactly match the JSON keys from Day 4! */}
                <Bar dataKey="total" fill="#8884d8" name="Total Submissions" />
                <Bar dataKey="ac" fill="#82ca9d" name="Accepted (AC)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

    </div>
  );
}