import React, { useState } from 'react';
import './upload.css';

const Upload = ({ onSend }) => {
  const [title, setTitle] = useState('');
  const [source, setSource] = useState('');
  const [content, setContent] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [tag, setTag] = useState('news');

  const handleClear = () => {
    setTitle('');
    setSource('');
    setContent('');
    setError('');
    setSuccess('');
  };

  const handleSend = async () => {
    setError('');
    setSuccess('');
    if (!title.trim() || !content.trim()) {
      setError('Title and Content are required.');
      return;
    }
    setSending(true);
    try {
      const response = await fetch('/upload_article_service', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, source, content, tag }),
      });
      if (!response.ok) {
        throw new Error('Failed to upload article');
      }
      await response.json();
      setSuccess('Article uploaded successfully!');
      setSending(false);
      if (typeof onSend === 'function') onSend();
    } catch (e) {
      setError(e.message || 'Upload failed');
      setSending(false);
    }
  };

  return (
    <div className="upload-article-panel">
      <h2 className="upload-article-title">Upload Article</h2>
      {error && <div className="upload-article-error">{error}</div>}
      {success && tag === 'novels' ? (
        <div className="upload-article-success">
          {success}<br />
          <span style={{fontSize:'0.97rem',color:'#444'}}>fetch <code>/all_articles?tag=novels</code></span><br />
          <a href="/articles?tag=novels" style={{color:'#1976d2',fontWeight:600}}>Go to Novel List</a>
        </div>
      ) : success && (
        <div className="upload-article-success">{success}</div>
      )}
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
          <option value="novels">Novels</option>
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
