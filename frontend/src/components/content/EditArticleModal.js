import React, { useState, useEffect } from 'react';
import './EditArticleModal.css';
import WordMeaningPopup from '../wrapper/WordMeaningPopup';
import { editArticle, getSingleArticle } from '../../api/articleService';

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
      getSingleArticle(articleId, tag)
        .then(data => {
          setForm({
            title: data.title || '',
            tag: data.tag || '',
            summary: data.summary || '',
            content: data.content || '',
            source: data.source || '',
          });
          setLoading(false);
        })
        .catch((err) => {
          setError(err.message || 'Error loading article');
          setLoading(false);
        });
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
      await editArticle(articleId, form);
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
      <div className="edit-article-modal-content">
        <button
          onClick={onClose}
          aria-label="Close"
          className="edit-article-modal-close"
        >
          &times;
        </button>
        <h2 style={{ marginTop: 0, marginBottom: 14, color: '#1976d2', fontWeight: 700 }}>Edit Article</h2>
        {loading ? (
          <div className="edit-article-loading">Loading...</div>
        ) : (
          <form
            onSubmit={e => { e.preventDefault(); handleSend(); }}
            className="edit-article-form"
          >
            <label>
              Title:
              <input
                name="title"
                value={form.title}
                onChange={handleFormChange}
                className="edit-article-input"
                required
              />
            </label>
            <label>
              Tag:
              <select
                name="tag"
                value={form.tag}
                onChange={handleFormChange}
                className="edit-article-input"
              >
                <option value="news">News</option>
                <option value="novels">Novels</option>
                <option value="dramas">Dramas</option>
                <option value="nonfiction">Nonfiction</option>
              </select>
            </label>
            <label>
              Summary:
              <textarea
                name="summary"
                value={form.summary}
                className="edit-article-input"
                readOnly
              />
            </label>
            <label>
              Content:
              <textarea
                name="content"
                value={form.content}
                onChange={handleFormChange}
                className="edit-article-input"
              />
            </label>
            <label>
              Source:
              <input
                name="source"
                value={form.source}
                onChange={handleFormChange}
                className="edit-article-input"
              />
            </label>
            {error && <div style={{ color: 'red', marginBottom: 6 }}>{error}</div>}
            <div className="edit-article-buttons">
              <button type="button" onClick={handleClear} disabled={sending} style={{ flex: 1, background: '#eee', color: '#1976d2', border: 'none', borderRadius: 8, fontWeight: 600, fontSize: '1rem', cursor: 'pointer', padding: '10px 0' }}>Clear</button>
              <button type="submit" disabled={sending} style={{ flex: 1, background: '#1976d2', color: '#fff', border: 'none', borderRadius: 8, fontWeight: 600, fontSize: '1rem', cursor: 'pointer', padding: '10px 0' }}>{sending ? 'Sending...' : 'Send'}</button>
            </div>
          </form>
        )}
      </div>
    </WordMeaningPopup>
  );
}
