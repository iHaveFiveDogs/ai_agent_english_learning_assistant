import React, { useState, useEffect } from 'react';
import { sendChatMessage, fetchDictionary } from '../../api/articleService';
import './Dashboard.css';
import WordMeaningPopup from '../wrapper/WordMeaningPopup.js';

function Dashboard({ wordList = [], summary = '', onWordClick, highlightWord, dictionaryResult, setDictionaryResult, articleId, tag, expression_explanation = [], sentence_explanation = [] }) {
  // Use tag prop passed from ContentShow.js
  const chatHistoryRef = React.useRef(null);
  const chatEndRef = React.useRef(null);
  const [sentenceMeaning, setSentenceMeaning] = useState(null);
  const [activeTab, setActiveTab] = useState('words');
  // For dictionary input in Words tab
  const [dictInput, setDictInput] = useState('');
  const [dictLoading, setDictLoading] = useState(false);
  const [dictError, setDictError] = useState(null);
  // For chat input in Chat tab
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState(null);
  const [messages, setMessages] = useState(() => {
    try {
      const saved = localStorage.getItem('dashboard_chat_history');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  // Ref for notification audio
  const chatNotificationAudioRef = React.useRef(null);

  // Auto-scroll chat to bottom when messages or tab change
  React.useEffect(() => {
    if (activeTab === 'chat' && chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'auto' });
      setTimeout(() => {
        if (chatEndRef.current) {
          chatEndRef.current.scrollIntoView({ behavior: 'auto' });
        }
      }, 100);
    }
  }, [messages, activeTab]);
  const [selectedWord, setSelectedWord] = useState(null);
  const [showMeaningPopup, setShowMeaningPopup] = useState(false);
  // For expression explanations
  const [selectedExpression, setSelectedExpression] = useState(null);
  // For sentence explanations
  const [selectedSentence, setSelectedSentence] = useState(null);

  // When a word is clicked, highlight it in the article and show explanation
  const handleWordClick = (w) => {
    setSelectedWord(w);
    setShowMeaningPopup(true);
    if (onWordClick) onWordClick(w.word);
  };

  // Handler for receiving chat messages from backend
  const handleReceiveChatMessage = (msg) => {
    setMessages(prev => [...prev, msg]);
    // Play notification sound for backend messages
    if (msg && msg.role === 'assistant' && chatNotificationAudioRef.current) {
      chatNotificationAudioRef.current.currentTime = 0;
      chatNotificationAudioRef.current.play();
    }
  };

  return (
    <div className="dashboard-panel">
      {/* Notification sound for chat */}
      <audio ref={chatNotificationAudioRef} src="/chat-notification.mp3" preload="auto" style={{ display: 'none' }} />

      {/* Tab navigation and content here */}
      {/* Example: */}
      <div className="dashboard-tabs">
        <button className={`tab${activeTab === 'words' ? ' active' : ''}`} onClick={() => setActiveTab('words')}>Words</button>
        <button className={`tab${activeTab === 'chat' ? ' active' : ''}`} onClick={() => setActiveTab('chat')}>Chat</button>
      </div>
      <div className="tab-content">
        {activeTab === 'words' && (
          <div className="dashboard-wordlist" style={{display:'flex',flexDirection:'column',height:'100%',minHeight:320}}>
            <div style={{flex:1,overflowY:'auto'}}>
              {/* Sentence Explanation List */}
              {sentence_explanation && Array.isArray(sentence_explanation) && sentence_explanation.length > 0 && (
                <div style={{ marginTop: 0 }}>
                  <div style={{ fontWeight: 600, marginBottom: 6 }}>Sentences:</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {sentence_explanation.map((sent, idx) => (
                      <button
                        key={sent.sentence || idx}
                        className="dashboard-wordlink"
                        style={{ background: '#dff9fb', color: '#30336b', border: '1px solid #7ed6df', textAlign: 'left', whiteSpace: 'normal' }}
                        onClick={() => { setSelectedSentence(sent); setShowMeaningPopup(true); }}
                      >
                        {sent.sentence}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Word list display */}
              {wordList && wordList.length > 0 ? wordList.map((w, i) => (
                <button
                  key={w.word || i}
                  className={`dashboard-wordlink${highlightWord === w.word ? ' dashboard-wordlink-active' : ''}`}
                  onClick={() => handleWordClick(w)}
                >
                  {w.word}
                </button>
              )) : <div style={{ color: '#888', padding: 18 }}>No words available.</div>}

              {/* Expression Explanation List */}
              {expression_explanation && Array.isArray(expression_explanation) && expression_explanation.length > 0 && (
                <div style={{ marginTop: 18 }}>
                  <div style={{ fontWeight: 600, marginBottom: 6 }}>Expressions:</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                    {expression_explanation.map((exp, idx) => (
                      <button
                        key={exp.expression || idx}
                        className="dashboard-wordlink"
                        style={{ background: '#ffeaa7', color: '#636e72', border: '1px solid #fdcb6e' }}
                        onClick={() => { setSelectedExpression(exp); setShowMeaningPopup(true); }}
                      >
                        {exp.expression}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* WordMeaningPopup for selected word */}
              {/* WordMeaningPopup for selected word or expression */}
              <WordMeaningPopup open={showMeaningPopup && (!!selectedWord || !!dictionaryResult || !!selectedExpression || !!selectedSentence)} onClose={() => { setShowMeaningPopup(false); setDictionaryResult(null); setSelectedExpression(null); setSelectedSentence(null); }}>
                {(selectedWord || dictionaryResult || selectedExpression || selectedSentence) && (
                  <div style={{padding: 8, position: 'relative'}}>
                    <button
                      onClick={() => { setShowMeaningPopup(false); setDictionaryResult(null); setSelectedExpression(null); setSelectedSentence(null); }}
                      style={{
                        position: 'absolute',
                        top: 8,
                        right: 8,
                        background: 'transparent',
                        border: 'none',
                        fontSize: 22,
                        fontWeight: 'bold',
                        cursor: 'pointer',
                        color: '#888',
                        lineHeight: 1
                      }}
                      aria-label="Close"
                      title="Close"
                    >
                      ×
                    </button>
                    {(() => {
                      if (selectedSentence) {
                        const sent = selectedSentence;
                        return <>
                          <h2 style={{marginTop:0}}>Sentence</h2>
                          <div style={{marginTop:8}}><b>Text:</b> {sent.sentence}</div>
                          {sent.paraphrase && <div style={{marginTop:8}}><b>Paraphrase:</b> {sent.paraphrase}</div>}
                          {sent.grammar && <div style={{marginTop:8}}><b>Grammar:</b> {sent.grammar}</div>}
                          {sent.meaning && <div style={{marginTop:8}}><b>Meaning:</b> {sent.meaning}</div>}
                        </>;
                      }
                      if (selectedExpression) {
                        const exp = selectedExpression;
                        return <>
                          <h2 style={{marginTop:0}}>{exp.expression}</h2>
                          {exp.meaning && <div style={{marginTop:8}}><b>Meaning:</b> {exp.meaning}</div>}
                          {exp.etymology && <div style={{marginTop:8}}><b>Etymology:</b> {exp.etymology}</div>}
                          {exp.contextual_meaning && <div style={{marginTop:8}}><b>Contextual Meaning:</b> {exp.contextual_meaning}</div>}
                          {exp.example_sentences && exp.example_sentences.length > 0 && (
                            <div style={{marginTop:8}}>
                              <b>Example Sentences:</b>
                              <ul style={{marginTop:4}}>
                                {exp.example_sentences.map((ex, idx) => <li key={idx}>{ex}</li>)}
                              </ul>
                            </div>
                          )}
                        </>;
                      }
                      const wordObj = selectedWord || (Array.isArray(dictionaryResult) ? dictionaryResult[0] : dictionaryResult);
                      if (!wordObj) return null;
                      return <>
                        <h2 style={{marginTop:0, display:'flex', alignItems:'center', gap:8}}>
  {wordObj.word}
  {wordObj.audio_url && (
    <button
      style={{ border: 'none', background: 'none', cursor: 'pointer', fontSize: 22, color: '#1976d2', padding: 0 }}
      title="Play pronunciation"
      aria-label="Play pronunciation"
      onClick={() => {
        const audio = document.getElementById('pronounce-audio-' + wordObj.word);
        if (audio) audio.play();
      }}
    >
      <span role="img" aria-label="pronunciation">🔊</span>
    </button>
  )}
  {wordObj.audio_url && (
    <audio id={`pronounce-audio-${wordObj.word}`} src={wordObj.audio_url} preload="auto" />
  )}
</h2>
                        {wordObj.ipa && <div><b>IPA:</b> {wordObj.ipa}</div>}
                        {wordObj.etymology && <div><b>Etymology:</b> {wordObj.etymology}</div>}
                        {wordObj.explanation && <div style={{marginTop:8}}><b>Explanation:</b> {wordObj.explanation}</div>}
                        {wordObj.contextual_meaning && <div style={{marginTop:8}}><b>Contextual Meaning:</b> {wordObj.contextual_meaning}</div>}
                        {wordObj.example_sentences && wordObj.example_sentences.length > 0 && (
                          <div style={{marginTop:8}}>
                            <b>Example Sentences:</b>
                            <ul style={{marginTop:4}}>
                              {wordObj.example_sentences.map((ex, idx) => <li key={idx}>{ex}</li>)}
                            </ul>
                          </div>
                        )}
                      </>;
                    })()}
                  </div>
                )}
              </WordMeaningPopup>
              <form
                className="dashboard-dictionary-input"
                onSubmit={async e => {
                  e.preventDefault();
                  if (!dictInput.trim()) return;
                  setDictLoading(true);
                  setDictError(null);
                  try {
                    const payload = { article_id: articleId, article: (typeof summary === 'string' ? summary : ''), words: [dictInput.trim()] };
                    const data = await fetchDictionary(payload);
                    setDictionaryResult(Array.isArray(data) ? data[0] : data);
                    setSelectedWord(null);
                    setSelectedExpression(null);
                    setSelectedSentence(null);
                    setShowMeaningPopup(true);
                    setDictInput('');
                  } catch (err) {
                    setDictError(err.message);
                  } finally {
                    setDictLoading(false);
                  }
                }}
              >
                <input
                  className="dashboard-dictionary-inputbox"
                  value={dictInput}
                  onChange={e => setDictInput(e.target.value)}
                  disabled={dictLoading}
                  placeholder="Type a word to look up..."
                />
                <button
                  className="dashboard-dictionary-sendbtn"
                  type="submit"
                  disabled={dictLoading || !dictInput.trim()}
                >
                  {dictLoading ? 'Checking...' : 'Check'}
                </button>
              </form>
              {dictionaryResult && (
                <div className="dashboard-dictionary-result" style={{ marginTop: 10 }}>
                  <pre style={{ whiteSpace: 'pre-wrap', fontSize: 13 }}>{JSON.stringify(dictionaryResult, null, 2)}</pre>
                </div>
              )}
            </div>
          </div>
        )}
        {activeTab === 'chat' && (
          <div className="dashboard-chat-sheet" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div className="dashboard-chat-history" style={{ flex: 1, overflowY: 'auto', marginBottom: 10 }} ref={chatHistoryRef}>
              {messages.length === 0 && <div style={{ color: '#888', padding: 18 }}>No messages yet.</div>}
              {messages.map((msg, i) => (
                <div key={i} className={`dashboard-chat-msg dashboard-chat-msg-${msg.role}`.trim()} style={{ marginBottom: 8 }}>
                  <span style={{ fontWeight: 600, color: msg.role === 'user' ? '#1976d2' : '#333' }}>{msg.role === 'user' ? 'You:' : 'Agent:'}</span>
                  <span style={{ marginLeft: 8 }}>{msg.content}</span>
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>
            <form
              className="dashboard-chat-input"
              onSubmit={async e => {
                e.preventDefault();
                if (!chatInput.trim()) return;
                const userMsg = { role: 'user', content: chatInput };
                setMessages(msgs => {
                  const updated = [...msgs, userMsg];
                  try {
                    localStorage.setItem('dashboard_chat_history', JSON.stringify(updated));
                  } catch {}
                  return updated;
                });
                setChatInput('');
                setChatLoading(true);
                setChatError(null);
                try {
                  const data = await sendChatMessage({ tag, articleId, query: userMsg.content });
                  setMessages(msgs => {
                    const updated = [...msgs, { role: 'agent', content: data.answer || JSON.stringify(data) }];
                    try { localStorage.setItem('dashboard_chat_history', JSON.stringify(updated)); } catch {}
                    return updated;
                  });
                } catch (err) {
                  setChatError(err.message);
                } finally {
                  setChatLoading(false);
                }
              }}
            >
              <input
                className="dashboard-chat-inputbox"
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                disabled={chatLoading}
                placeholder="Ask the agent..."
              />
              <button
                className="dashboard-chat-sendbtn"
                type="submit"
                disabled={chatLoading || !chatInput.trim()}
              >
                {chatLoading ? 'Sending...' : 'Send'}
              </button>
            </form>
            {chatError && <div style={{ color: 'red', marginTop: 8 }}>{chatError}</div>}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
