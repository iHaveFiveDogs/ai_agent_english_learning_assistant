import React from 'react';

function ArticleCard({ article, onClick }) {
  return (
    <div
      className="article-card"
      onClick={() => onClick && onClick(article._id)}
      style={{ cursor: 'pointer' }}
    >
      <div className="article-card-title">{article.title}</div>
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
