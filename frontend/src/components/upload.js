import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './upload.css';
import { uploadArticle } from '../api/articleService';

const Upload = ({ onSend, tag: propTag }) => {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [source, setSource] = useState('');
  const [content, setContent] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [showToast, setShowToast] = useState(false);
  const [processing, setProcessing] = useState(false);

  const [tag, setTag] = useState(propTag || 'news');

  // Keep tag in sync with propTag if it changes
  React.useEffect(() => {
    if (propTag && propTag !== tag) {
      setTag(propTag);
    }
  }, [propTag, tag]);

  const handleClear = () => {
    setTitle('');
    setSource('');
    setContent('');
    setError('');
    
  };

  const handleSend = async () => {
    setError('');
    
    if (!title.trim() || !content.trim()) {
      setError('Title and Content are required.');
      return;
    }
    setSending(true);
    try {
      const uploaded = await uploadArticle({ title, source, content, tag });
      console.log('[DEBUG] upload.js: uploadArticle result:', uploaded);
      setSending(false);
      console.log('[DEBUG] typeof onSend:', typeof onSend, onSend);
      if (typeof onSend === 'function') {
        console.log('[DEBUG] upload.js: calling onSend', uploaded);
        onSend(uploaded);
      } else {
        // Standalone page: immediately redirect to articles list with uploaded param
        navigate(`/articles?uploaded=${uploaded.article_id}&tag=${encodeURIComponent(tag)}`, { replace: true });
      }
    } catch (e) {
      setError(e.message || 'Upload failed');
      setSending(false);
    }
  };

  return (
    <div className="upload-article-panel">
      <Link to="/" style={{ color: '#1976d2', textDecoration: 'underline', fontWeight: 500, marginBottom: 16, display: 'inline-block' }}>
        &larr; Back to Home
      </Link>
      <h2 className="upload-article-title">Upload Article</h2>
      {error && <div className="upload-article-error">{error}</div>}

      {showToast && (
        <div style={{
          position: 'fixed',
          top: 28,
          left: '50%',
          transform: 'translateX(-50%)',
          background: '#388e3c',
          color: '#fff',
          padding: '14px 36px',
          borderRadius: 12,
          fontWeight: 700,
          fontSize: '1.1rem',
          zIndex: 9999,
          boxShadow: '0 2px 12px rgba(56,142,60,0.13)',
          letterSpacing: '0.01em',
        }}>
          Upload successful!
        </div>
      )}
      {success && <div className="upload-article-success" style={{color:'#388e3c',background:'#e8f5e9',padding:'10px 0',marginBottom:12,borderRadius:8,fontWeight:600}}>Upload successful! Redirecting...</div>}
      <form className="upload-article-form" onSubmit={e => e.preventDefault()}>
        <input
          type="text"
          placeholder="Title"
          value={title}
          onChange={e => setTitle(e.target.value)}
          className="upload-article-input"
        />
        <input
          type="text"
          placeholder="Source (optional)"
          value={source}
          onChange={e => setSource(e.target.value)}
          className="upload-article-input"
        />
        <select
          value={tag}
          onChange={e => setTag(e.target.value)}
          className="upload-article-input"
          style={{ marginBottom: 12 }}
        >
          <option value="news">News</option>
          <option value="nonfiction">Nonfiction</option>
          <option value="novels">Novels</option>
          <option value="dramas">Dramas</option>
        </select>
        <textarea
          placeholder="Content"
          value={content}
          onChange={e => setContent(e.target.value)}
          rows={10}
          className="upload-article-textarea"
        />
        <div className="upload-article-button-group">
          <button
            type="button"
            onClick={handleClear}
            disabled={sending}
            className="upload-article-button-clear"
          >
            Clear
          </button>
          <button
            type="button"
            onClick={handleSend}
            disabled={sending}
            className="upload-article-button-send"
          >
            {sending ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Upload;
