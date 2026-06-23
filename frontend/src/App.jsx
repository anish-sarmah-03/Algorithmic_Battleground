import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Arena from './pages/Arena';

function App() {
  return (
    <Router>
      <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
        <nav style={{ marginBottom: '20px', display: 'flex', gap: '15px' }}>
          <a href="/">Home</a>
          <a href="/login">Login</a>
          <a href="/dashboard">Dashboard</a>
          <a href="/arena">Arena</a>
        </nav>
        
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/arena" element={<Arena />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;