import { useEffect, useState } from 'react';
import { io } from 'socket.io-client';
import Editor from '@monaco-editor/react';

const socket = io('http://localhost:5000');

// Map to hold default boilerplate code for each language
const BOILERPLATES = {
  'c++': `#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    // your code goes here\n    int t;\n    cin >> t;\n    while(t--) {\n        \n    }\n    return 0;\n}`,
  python: `# your code goes here\nt = int(input())\nfor _ in range(t):\n    pass\n`,
  java: `import java.util.*;\n\npublic class Main {\n    public static void main(String[] args) {\n        // your code goes here\n    }\n}`
};

export default function Arena() {
  const [language, setLanguage] = useState('cpp');
  const [code, setCode] = useState(BOILERPLATES['cpp']);
  const [consoleOutput, setConsoleOutput] = useState('Awaiting submission...');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [roomCode, setRoomCode] = useState('');
  const [timerSetting, setTimerSetting] = useState(30);
  const [matchStatus, setMatchStatus] = useState('lobby');
  const [problems, setProblems] = useState([]);
  const [timeLeft, setTimeLeft] = useState(0);
  const [activeProblemId, setActiveProblemId] = useState(null);

  const storedId = localStorage.getItem('user_id');
  const userId = storedId ? parseInt(storedId, 10) : null;

  useEffect(() => {
    socket.on('room_status', (data) => {
      setMatchStatus('waiting');
    });

    socket.on('match_start', (data) => {
      setMatchStatus('active');
      setProblems(data.problems);
      if (data.problems && data.problems.length > 0) {
        setActiveProblemId(data.problems[0].id);
      }
      setTimeLeft(data.duration_minutes * 60);
    });

    socket.on('execution_result', (data) => {
      setConsoleOutput(data.console_output);
      setIsSubmitting(false);
      // NOTE: Here is where we will activate the "Next" button in the future 
      // if data.console_output includes "ACCEPTED"
    });

    return () => {
      socket.off('room_status');
      socket.off('match_start');
      socket.off('execution_result');
    };
  }, []);

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

  const handleSubmitCode = () => {
    if (!activeProblemId) return;
    setIsSubmitting(true);
    setConsoleOutput('Sending code to execution sandbox...');

    socket.emit('submit_code', {
      room_code: roomCode,
      user_id: userId,
      problem_id: activeProblemId,
      code: code,
      language: language
    });
  };

  const handleLanguageChange = (e) => {
    const newLang = e.target.value;
    setLanguage(newLang);
    setCode(BOILERPLATES[newLang]); // Auto-inject the boilerplate for the new language
  };

  if (matchStatus === 'lobby') {
    return (
      <div style={{ maxWidth: '500px', margin: '50px auto', textAlign: 'center' }}>
        <h2>The Arena Lobby</h2>
        <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
          <input
            type="text"
            placeholder="Enter Room Code"
            value={roomCode}
            onChange={(e) => setRoomCode(e.target.value)}
            style={{ padding: '10px', textTransform: 'uppercase', width: '80%', marginBottom: '15px' }}
          />
          <br />
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
    // Find the currently active problem object to render its details
    const activeProblem = problems.find(p => p.id === activeProblemId);

    return (
      <div style={{ width: '95%', margin: '20px auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#1e1e1e', color: 'white', padding: '10px 20px', borderRadius: '8px' }}>
          <h2>BATTLE ACTIVE!</h2>
          <h2 style={{ color: timeLeft <= 300 ? 'red' : 'lightgreen' }}>
            {Math.floor(timeLeft / 60)}m {(timeLeft % 60).toString().padStart(2, '0')}s
          </h2>
        </div>

        <div style={{ display: 'flex', gap: '20px', marginTop: '20px', height: '75vh' }}>
          
          {/* LEFT COLUMN: Single Problem View (CodeChef Style) */}
          <div style={{ flex: 1, overflowY: 'auto', backgroundColor: '#1e1e1e', padding: '20px', borderRadius: '8px', border: '1px solid #333' }}>
            {activeProblem ? (
              <>
                <div style={{ borderBottom: '1px solid #444', paddingBottom: '10px', marginBottom: '15px' }}>
                  <h1 style={{ margin: 0, color: '#fff' }}>{activeProblem.title}</h1>
                  <span style={{ color: '#aaa', fontSize: '14px' }}>Difficulty: {activeProblem.difficulty}</span>
                </div>
                {/* Render the HTML seeded from the database directly */}
                <div 
                  style={{ color: '#ddd', lineHeight: '1.6', fontSize: '15px' }}
                  dangerouslySetInnerHTML={{ __html: activeProblem.description }} 
                />
              </>
            ) : (
              <p>Loading problem...</p>
            )}
          </div>

          {/* RIGHT COLUMN: Code Editor & Console */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
              <select
                value={language}
                onChange={handleLanguageChange}
                style={{ padding: '8px', backgroundColor: '#333', color: 'white', border: '1px solid #555', borderRadius: '4px' }}
              >
                <option value="c++">C++ (GCC)</option>
                <option value="python">Python 3</option>
                <option value="java">Java</option>
              </select>

              <button
                onClick={handleSubmitCode}
                disabled={isSubmitting}
                style={{ padding: '8px 20px', backgroundColor: isSubmitting ? '#555' : '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', cursor: isSubmitting ? 'not-allowed': 'pointer', fontWeight: 'bold' }}
              >
                {isSubmitting ? 'Running...' : 'Submit Code'}
              </button>
            </div>

            <div style={{ border: '1px solid #555', borderRadius: '4px', overflow: 'hidden', flex: 1 }}>
              <Editor
                height="100%"
                theme="vs-dark"
                language={language === 'c++' ? 'cpp' : language}
                value={code}
                onChange={(value) => setCode(value)}
                options={{
                  minimap: { enabled: false },
                  fontSize: 15,
                  wordWrap: "on"
                }}
              />
            </div>

            {/* Terminal / Output Console */}
            <div style={{ marginTop: '10px', backgroundColor: '#1e1e1e', padding: '15px', borderRadius: '4px', border: '1px solid #333', minHeight: '150px', maxHeight: '150px', overflowY: 'auto' }}>
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