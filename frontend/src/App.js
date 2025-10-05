import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [transcript, setTranscript] = useState('');
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);

  const getSpeechToText = async () => {
    setLoading(true);
    setListening(true);
    setTranscript('');
    try {
      const response = await axios.get('http://127.0.0.1:5000/live-speech-to-text');
      setTranscript(response.data.transcript);
    } catch {
      setTranscript('Error fetching transcript.');
    }
    setLoading(false);
    setListening(false);
  };

  return (
    <div className="container">
      <h1 className="fade-in">🎤 Say Yours doubts..</h1>
      <button
        className={`mic-button ${listening ? 'listening' : ''}`}
        onClick={getSpeechToText}
        disabled={loading}
      >
        <span className="mic-icon" />
      </button>
      <div className={`transcript-box ${transcript ? 'visible' : ''}`}>
        {loading ? (
          <p className="blink">Listening...</p>
        ) : (
          transcript && <p>{transcript}</p>
        )}
      </div>
    </div>
  );
}

export default App;
