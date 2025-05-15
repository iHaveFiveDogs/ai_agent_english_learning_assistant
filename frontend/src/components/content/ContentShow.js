import React, { useState, useEffect } from 'react';

import { useNavigate, useParams, Link } from 'react-router-dom';
import TopBar from '../TopBar';
import EditArticleModal, { EditIcon } from './EditArticleModal';
import List from './List';
import Dashboard from './Dashboard';
import ExplainableWrapper from '../wrapper/ExplainableWrapper';
import './ContentShow.css';
import { useLocation } from 'react-router-dom';

function Content({ list, loading, fetchList }) {
  const location = useLocation();
  const query = new URLSearchParams(location.search);
  const tag = query.get('tag') || 'news';
  const { id } = useParams();
  const [currentArticle, setCurrentArticle] = useState(null);
  const [highlightWord, setHighlightWord] = useState(null);
  const [dictionaryResult, setDictionaryResult] = useState(null);
  const [fetchingSingle, setFetchingSingle] = useState(false);
  const [notFound, setNotFound] = useState(false);
  // --- ADDED: State and hooks for modal, navigation, and deleting ---
  const [showEdit, setShowEdit] = useState(false);
  const [shouldNavigateAfterEdit, setShouldNavigateAfterEdit] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    
    setNotFound(false);
    

    // If list are loaded, use the array
    const found = list.find(a => String(a._id) === String(id));
    if (found) {
      setCurrentArticle(found);
      window.__ARTICLE_CONTEXT__ = {
        articleId: found._id,
        articleContent: found.content,
        tag: found.tag || tag
      };
      return;
    }

    // If list are empty and id exists, fetch single article immediately (on refresh)
    if (list.length === 0 && id) {
      setFetchingSingle(true);
      
      fetch(`/single_article?article_id=${encodeURIComponent(id)}&tag=${encodeURIComponent(tag || 'news')}`)
        .then(res => {
          if (!res.ok) throw new Error('not found');
          return res.json();
        })
        .then(data => {
          setCurrentArticle(data.article || null);
          setFetchingSingle(false);
          if (data.article) {
            window.__ARTICLE_CONTEXT__ = {
              articleId: data.article._id,
              articleContent: data.article.content,
              tag: data.article.tag || tag
            };
          } else {
            setNotFound(true);
            window.__ARTICLE_CONTEXT__ = null;
          }
        })
        .catch((err) => {
          console.error('Error fetching single article:', err);
          setCurrentArticle(null);
          setFetchingSingle(false);
          setNotFound(true);
          window.__ARTICLE_CONTEXT__ = null;
        });
      return;
    }

    // If not found and not loading and id exists (fallback for other cases)
    if (!loading && id) {
      setFetchingSingle(true);
      
      fetch(`/single_article?article_id=${encodeURIComponent(id)}&tag=${encodeURIComponent(tag || 'news')}`)
        .then(res => {
          if (!res.ok) throw new Error('not found');
          return res.json();
        })
        .then(data => {
          setCurrentArticle(data.article || null);
          setFetchingSingle(false);
          if (data.article) {
            window.__ARTICLE_CONTEXT__ = {
              articleId: data.article._id,
              articleContent: data.article.content,
              tag: data.article.tag || tag
            };
          } else {
            setNotFound(true);
            window.__ARTICLE_CONTEXT__ = null;
          }
        })
        .catch((err) => {
          console.error('Error fetching single article:', err);
          setCurrentArticle(null);
          setFetchingSingle(false);
          setNotFound(true);
          window.__ARTICLE_CONTEXT__ = null;
        });
    }
  }, [list, id, loading]);

  const wordExplanations = currentArticle && Array.isArray(currentArticle.word_explanations) ? currentArticle.word_explanations : [];
  const summary = currentArticle && currentArticle.summary ? currentArticle.summary : '';


  // Navigate after edit and modal close
  useEffect(() => {
    if (!showEdit && shouldNavigateAfterEdit) {
      setShouldNavigateAfterEdit(false);
      navigate(`/articles?tag=${encodeURIComponent(tag || 'news')}`);
    }
  }, [showEdit, shouldNavigateAfterEdit, navigate, tag]);

  // Helper: highlight all occurrences of the word in the article content
  function highlightWordsInContent(content, word) {
    if (!word || typeof content !== 'string') return content;
    // Regex: match word boundaries, case-insensitive
    const regex = new RegExp(`(\\b${word.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\$&')}\\b)`, 'gi');
    return content.split(regex).map((part, i) => {
      if (part.toLowerCase() === word.toLowerCase()) {
        return <span key={i} className="article-highlighted-word">{part}</span>;
      }
      return part;
    });
  }

  

  const handleDelete = async () => {
    if (!id || !tag) return;
    if (!window.confirm('Are you sure you want to delete this article?')) return;
    setDeleting(true);
    try {
      const res = await fetch(`/delete_article?article_id=${encodeURIComponent(id)}&tag=${encodeURIComponent(tag)}`, {
        method: 'DELETE',
      });
      const data = await res.json();
      if (data.success) {
        if (typeof fetchList === 'function') {
          fetchList(tag);
        }
        setTimeout(() => {
          navigate(`/articles?tag=${encodeURIComponent(tag)}`);
        }, 300);
      } else {
        alert(data.message || 'Delete failed');
      }
    } catch (e) {
      alert('Delete failed: ' + (e.message || e));
    }
    setDeleting(false);
  };

  return (
    <div className="content-page" style={{marginTop:0,paddingTop:0}}>
      <TopBar />
      <div className="content-layout">
        {/* Article Content */}
        <div className="article-panel" style={{ position: 'relative' }}>
           {currentArticle && (
            <div style={{ position: 'absolute', top: 12, right: 12, display: 'flex', gap: 8, zIndex: 10 }}>
              <button
                className="delete-article-btn"
                style={{
                  background: 'none',
                  color: '#222',
                  border: 'none',
                  borderRadius: '50%',
                  width: 32,
                  height: 32,
                  fontWeight: 'bold',
                  fontSize: 22,
                  cursor: deleting ? 'wait' : 'pointer',
                  opacity: deleting ? 0.5 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'background 0.15s',
                }}
                disabled={deleting}
                title="Delete article"
                onClick={handleDelete}
              >
                {deleting ? <span style={{fontSize:14}}>...</span> : '×'}
              </button>
              {/* Edit icon */}
              <button
                className="edit-article-btn"
                style={{ background: 'none', border: 'none', padding: 0, cursor: 'pointer', display: 'flex', alignItems: 'center' }}
                title="Edit article"
                onClick={() => setShowEdit(true)}
                disabled={deleting}
              >
                <EditIcon />
              </button>
            </div>
          )}
          {/* Edit Modal */}
          {showEdit && (
            <EditArticleModal
              open={showEdit}
              onClose={() => setShowEdit(false)}
              articleId={id}
              tag={tag}
              onSend={async () => {
                // Refetch article after edit
                try {
                  const res = await fetch(`/single_article?article_id=${encodeURIComponent(id)}&tag=${encodeURIComponent(tag || 'news')}`);
                  if (!res.ok) throw new Error('Failed to fetch article');
                  const data = await res.json();
                  setCurrentArticle(data.article || data);
                  setShouldNavigateAfterEdit(true); // set flag to trigger navigation after modal closes
                } catch (e) {
                  // Optionally handle error
                }
              }}
            />
          )}
          <Link to={`/articles?tag=${encodeURIComponent(tag || 'news')}`} className="back-link">&larr; Back to List</Link>
          {fetchingSingle ? (
            <div className="article-loading">
              <p style={{ color: '#888', fontSize: '1.15rem', margin: '48px 0 18px 0' }}>Loading article...</p>
            </div>
          ) : notFound ? (
            <div className="article-not-found">
              <h2 style={{ color: '#d32f2f', margin: '48px 0 18px 0', fontWeight: 700, fontSize: '2rem' }}>Article Not Found</h2>
              <p style={{ color: '#888', fontSize: '1.15rem', marginBottom: 24 }}>Sorry, the article you are looking for does not exist or was removed.</p>
              <Link to={`/articles?tag=${encodeURIComponent(tag || 'news')}`} className="back-link" style={{ color: '#1976d2' }}>&larr; Back to List</Link>
            </div>
          ) : currentArticle ? (
            <>
              <h2 className="article-title">{currentArticle.title}</h2>
              <div style={{ display: 'flex', gap: 24, alignItems: 'center', margin: '6px 0 18px 0' }}>
                <span style={{ color: '#1976d2', fontWeight: 500, fontSize: '1.08rem' }}>Tag: {tag}</span>
                {currentArticle.source && (
                  <span style={{ color: '#1976d2', fontWeight: 500, fontSize: '1.08rem' }}>Source: {currentArticle.source}</span>
                )}
              </div>
              <ExplainableWrapper>
                <div className="article-body">
                  {highlightWordsInContent(currentArticle.content, highlightWord)}
                </div>
              </ExplainableWrapper>
            </>
          ) : null}
        </div>

        {/* Dashboard */}
        <Dashboard
          wordList={wordExplanations}
          summary={summary}
          onWordClick={w => setHighlightWord(w.word)}
          highlightWord={highlightWord}
          dictionaryResult={dictionaryResult}
          setDictionaryResult={setDictionaryResult}
          articleId={currentArticle ? currentArticle._id : null}
          tag={tag}
          expression_explanation={currentArticle && Array.isArray(currentArticle.expression_explanation) ? currentArticle.expression_explanation : []}
          sentence_explanation={currentArticle && Array.isArray(currentArticle.sentence_explanation) ? currentArticle.sentence_explanation : []}
        />
      </div>
    </div>
  );
}

export default Content;
