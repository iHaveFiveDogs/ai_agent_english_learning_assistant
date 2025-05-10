import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import TopBar from '../TopBar';
import UploadArticle from '../UploadArticle';
import ArticleCard from '../wrapper/ArticleCard';
import './Articles.css';

function Articles({ articles, loading, error, fetchArticles }) {
  const navigate = useNavigate();
  const [showUpload, setShowUpload] = useState(false);
  const [showNewArticleMsg, setShowNewArticleMsg] = useState(false);
  const location = useLocation();

  // Show 'new article coming' message if redirected from upload
  const hasFetchedAfterUpload = React.useRef(false);
  const hasFetchedInitial = React.useRef(false);
  // Track previous articles length to detect new article arrival
  const prevArticlesLength = React.useRef(articles ? articles.length : 0);

  useEffect(() => {
    // Fetch if redirected from upload (show message)
    if (
      location.state &&
      location.state.fromUpload &&
      !hasFetchedAfterUpload.current
    ) {
      setShowNewArticleMsg(true);
      if (fetchArticles) fetchArticles();
      hasFetchedAfterUpload.current = true;
    }
    // Hide message when a new article appears
    if (
      showNewArticleMsg &&
      articles &&
      articles.length > prevArticlesLength.current
    ) {
      setShowNewArticleMsg(false);
    }
    prevArticlesLength.current = articles ? articles.length : 0;
    // Fetch if articles are empty (first load or after failed fetch)
    if ((!articles || articles.length === 0) && fetchArticles && !hasFetchedInitial.current) {
      fetchArticles();
      hasFetchedInitial.current = true;
    }
  }, [fetchArticles, location.state, articles, showNewArticleMsg]);

  // Sort articles by newest upload_date first
  const sortedArticles = [...articles].sort((a, b) => {
    if (a.upload_date && b.upload_date) {
      return new Date(b.upload_date) - new Date(a.upload_date);
    }
    if (a._id && b._id) {
      return b._id - a._id;
    }
    return 0;
  });

  const handleTitleClick = (id) => {
    console.log('Article clicked, id:', id, typeof id);
    navigate(`/content/${id}`);
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
      {showUpload ? (
        <UploadArticle onSend={handleUploadSend} />
      ) : (
        <>
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
        </>
      )}
    </div>
  );
}

export default Articles;
