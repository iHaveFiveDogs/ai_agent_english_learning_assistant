import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import TopBar from '../TopBar';
import ArticleCard from '../wrapper/ArticleCard';
import Upload from '../upload';
import './List.css';

function List({ list, loading, error, fetchList }) {
  const [articles, setArticles] = useState(list || []);
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

  // Keep articles state in sync with list prop
  useEffect(() => {
    setArticles(list || []);
  }, [list]);

  // Delete handler
  const handleDelete = (articleId) => {
    // For demo: Remove from UI only. Replace with API call as needed.
    setArticles(prev => prev.filter(a => a._id !== articleId));
    // Optionally: call backend delete and refetch list
    // if (fetchList) fetchList(tag);
  };

  // Fetch articles when tag changes or after upload redirect
  useEffect(() => {
    if (sessionStorage.getItem('articleListNeedsRefresh')) {
      if (fetchList) fetchList(tag);
      sessionStorage.removeItem('articleListNeedsRefresh');
    }
  }, [fetchList, tag]);

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
    // Restore scroll position if available
    const savedScroll = sessionStorage.getItem('articleListScroll');
    if (savedScroll) {
      window.scrollTo(0, parseInt(savedScroll, 10));
      sessionStorage.removeItem('articleListScroll');
    }
    if (
      showNewArticleMsg &&
      list &&
      list.length > prevArticlesLength.current
    ) {
      setShowNewArticleMsg(false);
    }
    prevArticlesLength.current = list ? list.length : 0;
  }, [list, loading, error, tag, showNewArticleMsg]);

  // Sort articles by newest upload_date first
  const sortedArticles = [...(articles || [])].sort((a, b) => {
    if (a.upload_date && b.upload_date) {
      return new Date(b.upload_date) - new Date(a.upload_date);
    }
    if (a._id && b._id) {
      return b._id - a._id;
    }
    return 0;
  });

  const handleTitleClick = (id) => {
    // Save scroll position before navigating
    sessionStorage.setItem('articleListScroll', window.scrollY.toString());
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

  const handleUploadSend = async (article) => {
    // TODO: Implement the actual upload logic (API call)
    // Example: await api.uploadArticle(article);
    setShowUpload(false);
    if (fetchList) fetchList(tag); // Refresh list for the current tag
    navigate(`/articles?tag=${encodeURIComponent(tag)}`); // Switch to list view for the tag
  };

  return (
    <div className="articles-page" style={{marginTop:0,paddingTop:0}}>
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
            onDelete={handleDelete}
          />
        ))}
      </div>
      {showUpload && (
        <Upload
          onSend={handleUploadSend}
          onClose={() => setShowUpload(false)}
          tag={tag}
        />
      )}
    </div>
  );
}

export default List;
