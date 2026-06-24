import { useState } from 'react';
import API from '../api';

export default function Arena() {
  const [roomCode, setRoomCode] = useState('');
  const [joinCode, setJoinCode] = useState('');
  const [inRoom, setInRoom] = useState(false);
  
  const [code, setCode] = useState('def solve():\n    # Write your logic here\n    pass');
  const [verdict, setVerdict] = useState('');
  const [loading, setLoading] = useState(false);

  // --- LOBBY ACTIONS ---
  const handleCreateRoom = async () => {
    try {
      const res = await API.post('/room/create');
      setRoomCode(res.data.room_code);
      setInRoom(true);
    } catch (err) {
      alert('Failed to create room. Are you logged in?');
    }
  };

  const handleJoinRoom = async () => {
    if (!joinCode) return;
    try {
      await API.post('/room/join', { room_code: joinCode });
      setRoomCode(joinCode);
      setInRoom(true);
    } catch (err) {
      alert('Room not found or invalid code.');
    }
  };

  // --- BATTLEGROUND ACTIONS ---
  const handleSubmitCode = async () => {
    setLoading(true);
    setVerdict('Evaluating on hidden test cases...');
    
    try {
      const res = await API.post('/room/submit', {
        problem_name: 'Valid Anagram',
        topic_tag: 'Strings',
        difficulty: 'Easy',
        code: code
      });

      setTimeout(() => {
        setVerdict(`Verdict: ${res.data.verdict}`);
        setLoading(false);
      }, 800);
      
    } catch (err) {
      setVerdict('Execution Failed. Server Error.');
      setLoading(false);
    }
  };

  // --- VIEW 1: THE LOBBY ---
  if (!inRoom) {
    return (
      <div style={{ maxWidth: '500px', margin: '50px auto', textAlign: 'center' }}>
        <h2>The Arena Lobby</h2>
        <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px', marginTop: '20px' }}>
          <h3>Start a Match</h3>
          <button onClick={handleCreateRoom} style={{ padding: '10px 20px', cursor: 'pointer' }}>
            Create New Room
          </button>
          
          <hr style={{ margin: '30px 0' }} />
          
          <h3>Join a Match</h3>
          <input 
            type="text" 
            placeholder="Enter 5-digit Room Code" 
            value={joinCode}
            onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
            style={{ padding: '10px', marginRight: '10px', textTransform: 'uppercase' }}
          />
          <button onClick={handleJoinRoom} style={{ padding: '10px 20px', cursor: 'pointer' }}>
            Join
          </button>
        </div>
      </div>
    );
  }

  // --- VIEW 2: THE BATTLEGROUND ---
  return (
    <div style={{ maxWidth: '800px', margin: '30px auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Battle Arena</h2>
        <h3 style={{ color: 'blue' }}>Room Code: {roomCode}</h3>
      </div>
      
      <div style={{ marginTop: '20px' }}>
        <p><strong>Problem:</strong> Valid Anagram (Strings - Easy)</p>
        
        <textarea 
          value={code}
          onChange={(e) => setCode(e.target.value)}
          style={{ 
            width: '100%', 
            height: '300px', 
            fontFamily: 'monospace', 
            padding: '15px', 
            backgroundColor: '#1e1e1e', 
            color: '#d4d4d4',
            borderRadius: '4px'
          }}
        />
        
        <div style={{ marginTop: '20px', display: 'flex', alignItems: 'center', gap: '20px' }}>
          <button 
            onClick={handleSubmitCode} 
            disabled={loading}
            style={{ 
              padding: '10px 20px', 
              backgroundColor: loading ? '#ccc' : '#4CAF50', 
              color: 'white', 
              border: 'none', 
              cursor: loading ? 'not-allowed' : 'pointer' 
            }}
          >
            {loading ? 'Running...' : 'Submit Code'}
          </button>
          
          <h3 style={{ 
            color: verdict.includes('AC') ? 'green' : verdict.includes('WA') || verdict.includes('TLE') ? 'red' : 'black' 
          }}>
            {verdict}
          </h3>
        </div>
      </div>
    </div>
  );
}