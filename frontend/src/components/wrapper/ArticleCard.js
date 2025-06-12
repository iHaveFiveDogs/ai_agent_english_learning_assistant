import React from 'react';
import './ArticleCard.css';

// ArticleCard: Card dimensions controlled via CSS (see ArticleCard.css)
// Height: 456px, Width: 330px (as of last update)
function ArticleCard({ article, onClick, onDelete, processingStatus = 'idle' }) {
  // Main card div. Height and width set in ArticleCard.css
  return (
    <div
      id={`article-card-${article._id}`}
      className="article-card"
      style={{ position: 'relative' }}
      onClick={e => {
        // Prevent click if delete or edit button was pressed
        if (e.target.classList.contains('article-delete-btn') || e.target.classList.contains('article-edit-btn')) return;
        onClick && onClick(article._id);
      }}
    >
      {/* Processing/Prepared status overlay */}
      {processingStatus === 'processing' && (
        <div className="article-processing-overlay">
          <span className="article-processing-spinner" /> Processing...
        </div>
      )}
      {processingStatus === 'prepared' && (
        <div className="article-prepared-badge">Ready!</div>
      )}
      {/* Overlay when processing */}
      {processingStatus === 'processing' && (
        <div className="article-processing-overlay">
          <div className="article-processing-spinner"></div>
          <span style={{ marginLeft: 10 }}>Processing...</span>
        </div>
      )}
      {/* Prepared badge */}
      {processingStatus === 'prepared' && (
        <div className="article-prepared-badge">Prepared</div>
      )}
      {/* Top right control: Delete button (X) only */}
      <div className="article-card-delete-btn-wrap">
        <button
          className="article-delete-btn"
          onClick={e => {
            e.stopPropagation();
            if (onDelete) onDelete(article._id);
          }}
          title="Delete this article"
        >
          &times;
        </button>
      </div>

      <div className="article-card-title">
        {article.title}
      </div>
      {article.tag && (
        <span className="article-tag-chip">{article.tag}</span>
      )}
      <div className="article-card-summary">
        {article.summary || (article.content?.slice(0, 120) + (article.content?.length > 120 ? '...' : ''))}
      </div>
      <div className="article-card-meta">
        <span className="article-card-time">{article.upload_date ? new Date(article.upload_date).toLocaleString() : ''}</span>
        <span className="article-card-source">{article.source || ''}</span>
      </div>
    </div>
  );
}


export default ArticleCard;
