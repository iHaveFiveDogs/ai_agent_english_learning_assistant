import React, { useState, useEffect } from 'react';
import WordMeaningPopup from '../wrapper/WordMeaningPopup';

// Simple Edit icon SVG
export const EditIcon = ({ style = {}, ...props }) => (
  <svg style={{ width: 20, height: 20, cursor: 'pointer', ...style }} viewBox="0 0 24 24" fill="none" stroke="#1976d2" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M12 20h9" />
    <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19.5 3 21l1.5-4L16.5 3.5z" />
  </svg>
);

export default function EditArticleModal({ open, onClose, articleId, tag, onSend }) {
  const [form, setForm] = useState({ title: '', tag: '', summary: '', content: '', source: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (open && articleId && tag) {
      setLoading(true);
      setError('');
      fetch(`/single_article?article_id=${encodeURIComponent(articleId)}&tag=${encodeURIComponent(tag)}`)
        .then(res => {
          if (!res.ok) throw new Error('Failed to fetch article');
          return res.json();
        })
        .then(data => {
          const a = data.article || data;
          setForm({
            title: a.title || '',
            tag: a.tag || tag || '',
            summary: a.summary || '',
            content: a.content || '',
            source: a.source || '',
          });
        })
        .catch(err => setError(err.message || 'Error fetching article'))
        .finally(() => setLoading(false));
    }
  }, [open, articleId, tag]);

  const handleFormChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleClear = () => {
    setForm({ title: '', tag: tag || '', summary: '', content: '', source: '' });
    setError('');
  };

  const handleSend = async () => {
    setSending(true);
    setError('');
    try {
      const res = await fetch(`/edit_article?article_id=${encodeURIComponent(articleId)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: form.title,
          tag: form.tag,
          summary: form.summary,
          content: form.content,
          source: form.source,
        }),
      });
      const data = await res.json();
      if (!res.ok || data.error) {
        throw new Error(data.error || 'Failed to update article');
      }
      if (onSend) await onSend(form);
      sessionStorage.setItem('articleListNeedsRefresh', '1');
      onClose();
    } catch (err) {
      setError(err.message || 'Error sending update');
    }
    setSending(false);
  };


  return (
    <WordMeaningPopup open={open} onClose={onClose}>
      <div style={{ minWidth: 340, position: 'relative' }}>
        <button
          onClick={onClose}
          aria-label="Close"
          style={{
            position: 'absolute',
            top: 10,
            right: 10,
            background: 'none',
            border: 'none',
            fontSize: 22,
            color: '#888',
            cursor: 'pointer',
            zIndex: 9999
          }}
        >
          &times;
        </button>
        <h2 style={{ marginTop: 0, marginBottom: 14, color: '#1976d2', fontWeight: 700 }}>Edit Article</h2>
        {loading ? (
          <div style={{ color: '#888' }}>Loading...</div>
        ) : (
          <form
            onSubmit={e => { e.preventDefault(); handleSend(); }}
            style={{ display: 'flex', flexDirection: 'column', gap: 12 }}
          >
            <label>
              Title:
              <input
                name="title"
                value={form.title}
                onChange={handleFormChange}
                style={{ width: '100%', padding: 6, borderRadius: 6, border: '1px solid #ccc', marginBottom: 6 }}
                required
              />
            </label>
            <label>
              Tag:
              <select
                name="tag"
                value={form.tag}
                onChange={handleFormChange}
                style={{ width: '100%', padding: 6, borderRadius: 6, border: '1px solid #ccc', marginBottom: 6 }}
              >
                <option value="news">News</option>
                <option value="novels">Novels</option>
              </select>
            </label>
            <label>
              Summary:
              <textarea
                name="summary"
                value={form.summary}
                style={{ width: '100%', padding: 6, borderRadius: 6, border: '1px solid #ccc', minHeight: 80, marginBottom: 6 }}
                readOnly
              />
            </label>
            <label>
              Content:
              <textarea
                name="content"
                value={form.content}
                onChange={handleFormChange}
                style={{ width: '100%', padding: 6, borderRadius: 6, border: '1px solid #ccc', minHeight: 80, marginBottom: 6 }}
              />
            </label>
            <label>
              Source:
              <input
                name="source"
                value={form.source}
                onChange={handleFormChange}
                style={{ width: '100%', padding: 6, borderRadius: 6, border: '1px solid #ccc', marginBottom: 6 }}
              />
            </label>
            {error && <div style={{ color: 'red', marginBottom: 6 }}>{error}</div>}
            <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
              <button type="button" onClick={handleClear} disabled={sending} style={{ flex: 1, background: '#eee', color: '#1976d2', border: 'none', borderRadius: 8, fontWeight: 600, fontSize: '1rem', cursor: 'pointer', padding: '10px 0' }}>Clear</button>
              <button type="submit" disabled={sending} style={{ flex: 1, background: '#1976d2', color: '#fff', border: 'none', borderRadius: 8, fontWeight: 600, fontSize: '1rem', cursor: 'pointer', padding: '10px 0' }}>{sending ? 'Sending...' : 'Send'}</button>
            </div>
          </form>
        )}
      </div>
    </WordMeaningPopup>
  );
}
