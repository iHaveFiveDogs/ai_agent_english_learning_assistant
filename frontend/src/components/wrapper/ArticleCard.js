import React from 'react';

function ArticleCard({ article, onClick, onDelete }) {
  return (
    <div
      className="article-card"
      style={{ position: 'relative', cursor: 'pointer', transition: 'box-shadow 0.2s', boxShadow: '0 2px 12px rgba(0,0,0,0.10)', height: '480px', overflow: 'hidden', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
      onClick={e => {
        // Prevent click if delete or edit button was pressed
        if (e.target.classList.contains('article-delete-btn') || e.target.classList.contains('article-edit-btn')) return;
        onClick && onClick(article._id);
      }}
    >
      {/* Top right control: Delete button (X) only */}
      <div style={{ position: 'absolute', top: 12, right: 12, zIndex: 10 }}>
        <button
          className="article-delete-btn"
          style={{ background: 'none', border: 'none', fontSize: 20, color: '#888', cursor: 'pointer', padding: 0 }}
          onClick={e => {
            e.stopPropagation();
            if (onDelete) onDelete(article._id);
          }}
          title="Delete this article"
        >
          &times;
        </button>
      </div>

      <div className="article-card-title" style={{ fontWeight: 700, fontSize: '1.18rem', marginBottom: 8 }}>
        {article.title}
      </div>
      {article.tag && (
        <span className="article-tag-chip" style={{
          display: 'inline-block',
          background: '#e3f2fd',
          color: '#1976d2',
          borderRadius: '12px',
          padding: '2px 12px',
          fontSize: '0.92rem',
          fontWeight: 600,
          marginBottom: 8
        }}>{article.tag}</span>
      )}
      <div className="article-card-summary" style={{ color: '#444', fontSize: '1.01rem', marginBottom: 10, maxHeight: '220px', overflowY: 'auto' }}>
        {article.summary || (article.content?.slice(0, 120) + (article.content?.length > 120 ? '...' : ''))}
      </div>
      <div className="article-card-meta" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.96rem', color: '#888' }}>
        <span className="article-card-time">{article.upload_date ? new Date(article.upload_date).toLocaleString() : ''}</span>
        <span className="article-card-source">{article.source || ''}</span>
      </div>

    </div>
  );
}


export default ArticleCard;
