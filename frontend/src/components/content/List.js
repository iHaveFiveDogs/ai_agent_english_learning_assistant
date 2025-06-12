// ArticleCard dimensions (height: 456px, width: 330px) are set in ArticleCard.css
// Grid layout for cards is set in List.css (.articles-grid)
import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import TopBar from '../TopBar';
import ArticleCard from '../wrapper/ArticleCard';
import Upload from '../upload';
import './List.css';
import { uploadArticle, deleteArticle, getSingleArticle } from '../../api/articleService';

function List({ list, loading, error, fetchList }) {
  const [articles, setArticles] = useState(list || []);
  // Track processing state for each article: { [articleId]: 'idle' | 'processing' | 'prepared' }
  const [processingStatus, setProcessingStatus] = useState({});
  const navigate = useNavigate();
  const [showUpload, setShowUpload] = useState(false);
  const [showNewArticleMsg, setShowNewArticleMsg] = useState(false);
  const location = useLocation();

  // Get tag from URL
  const query = new URLSearchParams(location.search);
  const tag = query.get('tag') || 'news';

  // Show upload modal if ?upload=1 is in the URL
  useEffect(() => {
    const query = new URLSearchParams(location.search);
    setShowUpload(query.get('upload') === '1');
  }, [location.search]);

  // Helper to close modal and remove upload=1 from URL
  const handleCloseUpload = () => {
    setShowUpload(false);
    const newQuery = new URLSearchParams(location.search);
    newQuery.delete('upload');
    navigate({ search: newQuery.toString() }, { replace: true });
  };


  // Show 'new article coming' message if redirected from upload
  const hasFetchedAfterUpload = React.useRef(false);
  // Track previous articles length to detect new article arrival
  const prevArticlesLength = React.useRef(list ? list.length : 0);

  // Keep articles state in sync with list prop
  useEffect(() => {
    setArticles(list || []);
    // Reset processing status for new articles
    if (list) {
      setProcessingStatus(prev => {
        const updated = { ...prev };
        list.forEach(article => {
          if (!updated[article._id]) updated[article._id] = 'idle';
        });
        return updated;
      });
    }
  }, [list]);

  // Handle ?uploaded= in query string for post-upload redirect
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const uploadedId = params.get('uploaded');
    const uploadedTag = params.get('tag') || 'news';
    if (uploadedId) {
      // Set processing status and open WebSocket
      setProcessingStatus(prev => ({ ...prev, [uploadedId]: 'processing' }));
      const ws = new window.WebSocket(`ws://localhost:8000/ws/merge_status/${uploadedId}`);
      ws.onopen = () => console.log('[WS] WebSocket opened for uploaded article', uploadedId);
      ws.onmessage = function(event) {
        console.log('[WS] Message received for uploaded article', uploadedId, 'event:', event);
        setProcessingStatus(prev => ({ ...prev, [uploadedId]: 'prepared' }));
        ws.close();
      };
      ws.onclose = () => console.log('[WS] WebSocket closed for uploaded article', uploadedId);
      ws.onerror = (err) => console.error('[WS] WebSocket error for uploaded article', uploadedId, err);
      // Optionally scroll to or highlight the uploaded article
      setTimeout(() => {
        const el = document.getElementById(`article-card-${uploadedId}`);
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
          el.classList.add('highlight-uploaded');
          setTimeout(() => el.classList.remove('highlight-uploaded'), 1600);
        }
      }, 700);
      // Remove ?uploaded=... from the URL after handling
      params.delete('uploaded');
      const newUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
      window.history.replaceState({}, '', newUrl);
    }
  }, []);

  // Delete handler
  const handleDelete = async (articleId) => {
    // For demo: Remove from UI only. Replace with API call as needed.
    try {
      await deleteArticle(articleId, tag);
      setArticles(prev => prev.filter(a => a._id !== articleId));
      // Optionally: call backend delete and refetch list
      if (fetchList) fetchList(tag);
    } catch (e) {
      // Optionally handle error
    }
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



  const handleUploadSend = (uploaded) => {
    try {
      console.log('[DEBUG] uploadArticle result:', uploaded);
      if (uploaded && uploaded.article_id) {
        setProcessingStatus(prev => ({ ...prev, [uploaded.article_id]: 'processing' }));
        // Open WebSocket for this article
        const ws = new window.WebSocket(`ws://localhost:8000/ws/merge_status/${uploaded.article_id}`);
        ws.onopen = () => console.log('[WS] WebSocket opened for article', uploaded.article_id);
        ws.onmessage = async function(event) {
          console.log('[WS] Message received for article', uploaded.article_id, 'event:', event);
          // Fetch article once before showing 'prepared'
          try {
            await getSingleArticle(uploaded.article_id, tag);
            // Always refresh the article list after preparation
            if (fetchList) {
              fetchList(tag);
            }
          } catch (fetchErr) {
            console.error('[Fetch after upload] Failed to fetch single article:', fetchErr);
          }
          setProcessingStatus(prev => ({ ...prev, [uploaded.article_id]: 'prepared' }));
          ws.close();
        };
        ws.onclose = () => console.log('[WS] WebSocket closed for article', uploaded.article_id);
        ws.onerror = (err) => console.error('[WS] WebSocket error for article', uploaded.article_id, err);
      }
    } catch (e) {
      // Optionally handle error
    }
    setShowUpload(false);
    if (fetchList) {
      fetchList(tag);
    }
    //navigate(`/articles?tag=${encodeURIComponent(tag)}`);
  };


  return (
    <div className="articles-page" style={{marginTop:0,paddingTop:0}}>
      <TopBar />
      <div style={{ display: 'flex', justifyContent: 'flex-end', margin: '18px 24px 0 0' }}>
        <Link to="/upload" className="upload-link-btn" style={{ background: '#1976d2', color: '#fff', padding: '8px 22px', borderRadius: 8, fontWeight: 600, fontSize: '1rem', textDecoration: 'none', boxShadow: '0 1px 4px rgba(25, 118, 210, 0.08)' }}>
          + Upload Article
        </Link>
      </div>
      {showNewArticleMsg && (
        <p style={{ textAlign: 'center', fontWeight: 600, color: '#1976d2', fontSize: '1.18rem', margin: '24px 0' }}>
          New article is coming, please wait...
        </p>
      )}
      {loading && <p style={{ textAlign: 'center' }}>Loading...</p>}
      {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}
      <div className="articles-grid">
        {sortedArticles.map(article => (
          <ArticleCard
            key={article._id}
            article={article}
            onClick={handleTitleClick}
            onDelete={handleDelete}
            processingStatus={processingStatus[article._id] || 'idle'}
          />
        ))}
      </div>
      {showUpload && (
        <Upload
          onSend={handleUploadSend}
          onClose={handleCloseUpload}
          tag={tag}
        />
      )}
    </div>
  );
}

export default List;
