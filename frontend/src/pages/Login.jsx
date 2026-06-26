import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../api';

export default function Login() {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    try {
      if (isRegister) {
        // Handle Registration
        const res = await API.post('/auth/register', { username, email, password });
        setMessage(res.data.message + ' Please log in.');
        setIsRegister(false); // flip to login view automatically
      } else {
        // Handle Login
        const res = await API.post('/auth/login', { email, password });
        localStorage.setItem('token', res.data.access_token);
        localStorage.setItem('username', res.data.username);
        localStorage.setItem('user_id', res.data.user_id);
        navigate('/dashboard'); // Redirect to dashboard upon success!
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An unexpected error occurred.');
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '50px auto' }}>
      <h2>{isRegister ? 'Create an Account' : 'Sign In'}</h2>
      
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {isRegister && (
          <input 
            type="text" 
            placeholder="Username" 
            value={username} 
            onChange={(e) => setUsername(e.target.value)} 
            required 
          />
        )}
        <input 
          type="email" 
          placeholder="Email Address" 
          value={email} 
          onChange={(e) => setEmail(e.target.value)} 
          required 
        />
        <input 
          type="password" 
          placeholder="Password" 
          value={password} 
          onChange={(e) => setPassword(e.target.value)} 
          required 
        />
        <button type="submit">{isRegister ? 'Register' : 'Login'}</button>
      </form>

      <button 
        onClick={() => setIsRegister(!isRegister)} 
        style={{ background: 'none', border: 'none', color: 'blue', cursor: 'pointer', marginTop: '15px' }}
      >
        {isRegister ? 'Already have an account? Sign In' : "Don't have an account? Register"}
      </button>
    </div>
  );
}