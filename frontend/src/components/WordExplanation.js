import React from 'react';
import './WordExplanation.css';

// Renders a word explanation card
function ExplanationCard({ w, onClose }) {
  console.log('ExplanationCard received:', w);
  if (!w) return null;

  // Pronounce the word using backend audio_url
  const handlePlayPronunciation = () => {
    const audio = document.getElementById('pronounce-audio-' + w.word);
    if (audio) audio.play();
  };

  return (
    <div className="explanation-card">
      {onClose && (
        <button
          onClick={onClose}
          className="close-button"
        >
          &times;
        </button>
      )}
      <div className="explanation-card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        {w.word}
        {w.audio_url && (
          <button
            onClick={handlePlayPronunciation}
            className="pronounce-button"
            title="Play pronunciation"
            aria-label="Play pronunciation"
            style={{ marginLeft: 8, fontSize: 22, color: '#1976d2', background: 'none', border: 'none', cursor: 'pointer', verticalAlign: 'middle' }}
          >
            <span role="img" aria-label="pronunciation">🔊</span>
          </button>
        )}
        {w.audio_url && (
          <audio id={`pronounce-audio-${w.word}`} src={w.audio_url} preload="auto" />
        )}
        {w.ipa && <span className="explanation-card-ipa">({w.ipa})</span>}
      </div>
      {w.base_word && <div className="explanation-card-base-word"><strong>Base Word:</strong> {w.base_word}</div>}
      {w.explanation && <div className="explanation-card-explanation"><strong>Explanation:</strong> {w.explanation}</div>}
      {w.contextual_meaning && <div className="explanation-card-contextual-meaning"><strong>Contextual Meaning:</strong> {w.contextual_meaning}</div>}
      {w.etymology && <div className="explanation-card-etymology"><strong>Etymology:</strong> {w.etymology}</div>}
      {w.example_sentences && w.example_sentences.length > 0 && (
        <div className="explanation-card-example-sentences"><strong>Example Sentences:</strong>
          <ul>
            {w.example_sentences.map((ex, i) => <li key={i}>{ex}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}

export default function WordExplanation({ word, onClose }) {
  console.log('WordExplanation received:', word);
  // Support both single word object and array (for batch dictionary results)
  if (Array.isArray(word)) {
    return (
      <div>
        {word.map((w, i) => <ExplanationCard key={w.word || i} w={w} onClose={onClose} />)}
      </div>
    );
  } else if (word) {
    return <ExplanationCard w={word} onClose={onClose} />;
  } else {
    return <div style={{ color: '#888', padding: 24, textAlign: 'center' }}>No explanation found.</div>;
  }
}


