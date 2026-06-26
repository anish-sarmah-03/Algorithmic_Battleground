import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';
import Editor from '@monaco-editor/react' ;
const socket = io('http://localhost:5000');

export default function Arena() {
  const [language, setLanguage]= useState('c++');
  const [code, setCode] = useState('# Write your solution here...\n');
  const [consoleOutput, setConsoleOutput] = useState('Awaiting submission...');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [roomCode, setRoomCode] = useState('');
  const [timerSetting, setTimerSetting] = useState(30);
  const [matchStatus, setMatchStatus] = useState('lobby'); 
  const [problems, setProblems] = useState([]);
  const [timeLeft, setTimeLeft] = useState(0);


const storedId = localStorage.getItem('user_id');
const userId = storedId ? parseInt(storedId, 10) : null;

  useEffect(() => {
    // Listen for room status updates (Player 1 waiting)
    socket.on('room_status', (data) => {
      setMatchStatus('waiting');
      console.log(data.message);
    });

    // Listen for the match start broadcast (Player 2 joined)
    socket.on('match_start', (data) => {
      setMatchStatus('active');
      setProblems(data.problems);
      setTimeLeft(data.duration_minutes * 60); 
    });

    return () => {
      socket.off('room_status');
      socket.off('match_start');
    };
  }, []);

  // Timer Countdown Logic
  useEffect(() => {
    if (matchStatus !== 'active' || timeLeft <= 0) return;

    const timerInterval = setInterval(() => {
      setTimeLeft((prevTime) => {
        if (prevTime <= 1) {
          clearInterval(timerInterval);
          setMatchStatus('completed');
          return 0;
        }
        return prevTime - 1;
      });
    }, 1000);

    return () => clearInterval(timerInterval);
  }, [matchStatus, timeLeft]);

  const handleStartMatch = () => {
    if (!roomCode) return alert("Please enter a room code.");
    socket.emit('join_arena', {
      room_code: roomCode.toUpperCase(),
      user_id: userId,
      timer_setting: timerSetting
    });
  };

 
  if (matchStatus === 'lobby') {
    return (
      <div style={{ maxWidth: '500px', margin: '50px auto', textAlign: 'center' }}>
        <h2>The Arena Lobby</h2>
        <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
          <input 
            type="text" 
            placeholder="Enter Room Code (e.g., BATTLE1)" 
            value={roomCode} 
            onChange={(e) => setRoomCode(e.target.value)} 
            style={{ padding: '10px', textTransform: 'uppercase', width: '80%', marginBottom: '15px' }}
          />
          <br/>
          <label>Match Duration: </label>
          <select value={timerSetting} onChange={(e) => setTimerSetting(e.target.value)} style={{ padding: '5px' }}>
            <option value={30}>30 Minutes</option>
            <option value={60}>60 Minutes</option>
            <option value={90}>90 Minutes</option>
          </select>
          <br/><br/>
          <button onClick={handleStartMatch} style={{ padding: '10px 20px', cursor: 'pointer', backgroundColor: '#4CAF50', color: 'white', border: 'none' }}>
            Create / Join Room
          </button>
        </div>
      </div>
    );
  }

  if (matchStatus === 'waiting') {
    return (
      <div style={{ textAlign: 'center', marginTop: '50px' }}>
        <h2>Room Code: {roomCode}</h2>
        <p>Waiting for an opponent to enter this room code...</p>
        <div className="spinner">⏳</div>
      </div>
    );
  }

  if (matchStatus === 'active') {
    return (
      <div style={{ maxWidth: '800px', margin: '30px auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#1e1e1e', color: 'white', padding: '10px 20px', borderRadius: '8px' }}>
          <h2>BATTLE ACTIVE!</h2>
          <h2 style={{ color: timeLeft <= 300 ? 'red' : 'lightgreen' }}>
            {Math.floor(timeLeft / 60)}m {timeLeft % 60}s
          </h2>
        </div>
    <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
          {/* LEFT COLUMN: Problems */}
          <div style={{ flex: 1, maxHeight: '600px', overflowY: 'auto' }}>
            <h3>Problems:</h3>
            {problems.map((prob, index) => (
              <div key={prob.id} style={{ border: '1px solid #ccc', padding: '15px', marginBottom: '10px', borderRadius: '4px', backgroundColor: '#2a2a2a' }}>
                <h4>{index + 1}. {prob.title} <span style={{ fontSize: '12px', color: '#aaa' }}>({prob.difficulty})</span></h4>
                <p style={{ fontSize: '14px', lineHeight: '1.5' }}>{prob.description}</p>
              </div>
            ))}
          </div>

          {/* RIGHT COLUMN: Code Editor */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <select 
                value={language} 
                onChange={(e) => setLanguage(e.target.value)}
                style={{ padding: '8px', backgroundColor: '#333', color: 'white', border: '1px solid #555', borderRadius: '4px' }}
              >
                <option value="python">Python</option>
                <option value="cpp">C++</option>
                <option value="java">Java</option>
              </select>
              
              <button 
                onClick={() => console.log("Submit clicked!", code)}
                disabled={isSubmitting}
                style={{ padding: '8px 20px', backgroundColor: isSubmitting ? '#555' : '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', cursor: isSubmitting ? 'not-allowed' : 'pointer', fontWeight: 'bold' }}
              >
                {isSubmitting ? 'Running...' : 'Submit Code'}
              </button>
            </div>

            <div style={{ border: '1px solid #555', borderRadius: '4px', overflow: 'hidden' }}>
              <Editor
                height="400px"
                theme="vs-dark"
                language={language}
                value={code}
                onChange={(value) => setCode(value)}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  wordWrap: "on"
                }}
              />
            </div>

            {/* Terminal / Output Console */}
            <div style={{ marginTop: '10px', backgroundColor: '#1e1e1e', padding: '10px', borderRadius: '4px', border: '1px solid #333', minHeight: '100px' }}>
              <h4 style={{ margin: '0 0 5px 0', color: '#888' }}>Console Output:</h4>
              <pre style={{ margin: 0, color: '#00ff00', whiteSpace: 'pre-wrap', fontSize: '13px' }}>
                {consoleOutput}
              </pre>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (matchStatus === 'completed') {
    return <h2 style={{ textAlign: 'center', marginTop: '50px', color: 'red' }}>Time is up! The match has ended.</h2>;
  }
}