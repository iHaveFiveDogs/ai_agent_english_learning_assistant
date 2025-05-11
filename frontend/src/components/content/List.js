import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import TopBar from '../TopBar';
import ArticleCard from '../wrapper/ArticleCard';
import './List.css';

function List({ list, loading, error, fetchList }) {
  const navigate = useNavigate();
  const [showUpload, setShowUpload] = useState(false);
  const [showNewArticleMsg, setShowNewArticleMsg] = useState(false);
  const location = useLocation();

  // Get tag from URL
  const query = new URLSearchParams(location.search);
  const tag = query.get('tag') || 'news';

  // Show 'new article coming' message if redirected from upload
  const hasFetchedAfterUpload = React.useRef(false);
  const hasFetchedInitial = React.useRef(false);
  // Track previous articles length to detect new article arrival
  const prevArticlesLength = React.useRef(list ? list.length : 0);

  // Fetch articles when tag changes or after upload redirect
  useEffect(() => {
    if (location.state && location.state.fromUpload && !hasFetchedAfterUpload.current) {
      setShowNewArticleMsg(true);
      if (fetchList) fetchList(tag);
      hasFetchedAfterUpload.current = true;
    } else if (fetchList) {
      fetchList(tag);
    }
    // eslint-disable-next-line
  }, [fetchList, location.state, tag]);

  // Hide new article message when a new article arrives
  useEffect(() => {
    if (
      showNewArticleMsg &&
      list &&
      list.length > prevArticlesLength.current
    ) {
      setShowNewArticleMsg(false);
    }
    prevArticlesLength.current = list ? list.length : 0;
  }, [list, showNewArticleMsg]);

  // Sort articles by newest upload_date first
  const sortedArticles = [...(list || [])].sort((a, b) => {
    if (a.upload_date && b.upload_date) {
      return new Date(b.upload_date) - new Date(a.upload_date);
    }
    if (a._id && b._id) {
      return b._id - a._id;
    }
    return 0;
  });

  const handleTitleClick = (id) => {
    navigate(`/content/${id}?tag=${encodeURIComponent(tag)}`);
  };

  React.useEffect(() => {
    // Use popstate to handle browser navigation and menu clicks
    const updateUpload = () => {
      setShowUpload(window.location.pathname === '/upload');
    };
    window.addEventListener('popstate', updateUpload);
    updateUpload();
    return () => window.removeEventListener('popstate', updateUpload);
  }, []);

  const handleUploadSend = (article) => {
    // TODO: Implement the actual upload logic (API call)
    alert(`Article uploaded!\nTitle: ${article.title}\nSource: ${article.source}\nContent: ${article.content.slice(0, 40)}...`);
    setShowUpload(false);
    window.history.replaceState({}, '', '/articles');
  };

  return (
    <div className="articles-page">
      <TopBar />
      {showNewArticleMsg && (
        <p style={{ textAlign: 'center', fontWeight: 600, color: '#1976d2', fontSize: '1.18rem', margin: '24px 0' }}>
          New article is coming, please wait...
        </p>
      )}
      {loading && <p style={{ textAlign: 'center' }}>Loading...</p>}
      {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}
      <div className="articles-grid">
        {sortedArticles.map((article, idx) => (
          <ArticleCard
            key={article._id ? String(article._id) : idx}
            article={article}
            onClick={handleTitleClick}
          />
        ))}
      </div>
      )}
    </div>
  );
}

export default List;
