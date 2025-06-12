import React, { useState, useEffect } from 'react';

import { useNavigate, useParams, Link } from 'react-router-dom';
import './ContentShow.css';
import { useLocation } from 'react-router-dom';
import { deleteArticle, getSingleArticle } from '../../api/articleService';
import TopBar from '../TopBar';
import EditArticleModal from './EditArticleModal';
import ExplainableWrapper from '../wrapper/ExplainableWrapper';
import Dashboard from './Dashboard';
import ChunkQuestionPagination from './ChunkQuestionPagination';
import { getChunkQuestions } from '../../api/questionService';

function Content({ list, loading, fetchList, dictionaryResult, setDictionaryResult, highlightWord, setHighlightWord }) {
  const [showContent, setShowContent] = useState(false);
  const location = useLocation();
  const query = new URLSearchParams(location.search);
  const tag = query.get('tag') || 'news';
  const { id } = useParams();
  const [currentArticle, setCurrentArticle] = useState(null);

  const [fetchingSingle, setFetchingSingle] = useState(false);
  const [notFound, setNotFound] = useState(false);
  // --- ADDED: State and hooks for modal, navigation, and deleting ---
  const [showEdit, setShowEdit] = useState(false);
  const [shouldNavigateAfterEdit, setShouldNavigateAfterEdit] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const navigate = useNavigate();

  // State for chunk questions
  const [chunkQuestions, setChunkQuestions] = useState([]);
  const [chunkQuestionsLoading, setChunkQuestionsLoading] = useState(false);
  const [chunkQuestionsError, setChunkQuestionsError] = useState(null);
  const [chunkQuestionsFetched, setChunkQuestionsFetched] = useState(false);

  // Button-triggered fetch for chunk questions
  const handleFetchChunkQuestions = async () => {
    if (!currentArticle || !currentArticle._id || !tag) return;
    setChunkQuestionsLoading(true);
    setChunkQuestionsError(null);
    setChunkQuestions([]);
    setChunkQuestionsFetched(false);
    try {
      const list = await getChunkQuestions(currentArticle._id, tag);
      setChunkQuestions(list);
      setChunkQuestionsFetched(true);
    } catch (err) {
      setChunkQuestionsError(err.message || 'Failed to fetch chunk questions');
    } finally {
      setChunkQuestionsLoading(false);
    }
  }

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
      
      getSingleArticle(id, tag)
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
        });
      return;
    }

    // If not found and not loading and id exists (fallback for other cases)
    if (!loading && id) {
      setFetchingSingle(true);
      
      getSingleArticle(id, tag)
        .then(data => {
          if (!data || data.error) {
            setNotFound(true);
            window.__ARTICLE_CONTEXT__ = null;
          } else {
            setCurrentArticle(data);
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
      await deleteArticle(id, tag);
      if (typeof fetchList === 'function') {
        fetchList(tag);
      }
      setTimeout(() => {
        navigate(`/articles?tag=${encodeURIComponent(tag)}`);
      }, 300);
    } catch (e) {
      alert('Delete failed: ' + (e.message || e));
    }
    setDeleting(false);
  };

  return (
    <>
      <div className="content-page" style={{marginTop:0,paddingTop:0}}>
        <TopBar />
        <div className="content-layout">
          {/* Article Content */}
          <div className="article-panel">
              {currentArticle && (
                <div className="article-panel-actions">
                  <button
                    className={`delete-article-btn${deleting ? ' deleting' : ''}`}
                    disabled={deleting}
                    title="Delete article"
                    onClick={handleDelete}
                  >
                    {deleting ? <span style={{fontSize:14}}>...</span> : '×'}
                  </button>
                  {/* Edit icon - always visible for detail view */}
                  <button
                    className="edit-article-btn"
                    title="Edit article"
                    onClick={() => setShowEdit(true)}
                    style={{
                      marginLeft: 8,
                      background: '#fff',
                      border: '1px solid #1976d2',
                      color: '#1976d2',
                      borderRadius: 5,
                      padding: '0 10px',
                      fontSize: '18px',
                      fontWeight: 600,
                      cursor: deleting ? 'not-allowed' : 'pointer',
                      opacity: deleting ? 0.5 : 1,
                      transition: 'background 0.2s',
                      outline: 'none',
                      height: 32
                    }}
                    disabled={deleting}
                  >
                    <span title="Edit">✎</span>
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
                        const data = await getSingleArticle(id, tag);
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
                        {!showContent ? (
                          <div style={{ margin: '14px 0', color: '#444', fontStyle: 'italic' }}>
                            <strong>Summary:</strong> {currentArticle.summary || 'No summary.'}
                            <div>
                              <span
                                onClick={() => setShowContent(true)}
                                style={{ color: '#1976d2', cursor: 'pointer', textDecoration: 'underline', marginLeft: 8 }}
                                  title="Show full content"
                                >
                                  Show Content
                                </span>
                                <span style={{ color: '#b71c1c', marginLeft: 14, fontSize: '0.98em', opacity: 0.7 }}>
                                  (will be deleted if exceed 7 days)
                                </span>
                              </div>
                            </div>
                          ) : (
                            <div style={{ margin: '14px 0' }}>
                              <strong>Content:</strong>
                              <div
                                style={{ color: '#222', background: '#f8f8fa', borderRadius: 6, padding: '14px 12px', marginTop: 6 }}
                              >
                                {highlightWordsInContent(currentArticle.content, highlightWord)}
                              </div>
                              <div>
                                <span
                                  onClick={() => setShowContent(false)}
                                  style={{ color: '#1976d2', cursor: 'pointer', textDecoration: 'underline', marginLeft: 8 }}
                                  title="Hide content"
                                >
                                  Hide Content
                                </span>
                              </div>
                            </div>
                          ) }
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
      {/* Chunk-Question Pagination - moved below article and dashboard area */}
      <div style={{ marginTop: 24 }}>
        {!chunkQuestionsFetched ? (
          <button
            onClick={handleFetchChunkQuestions}
            disabled={chunkQuestionsLoading || !currentArticle}
            style={{
              padding: '10px 22px',
              borderRadius: 8,
              border: 'none',
              background: '#1976d2',
              color: '#fff',
              fontWeight: 600,
              fontSize: '1.08rem',
              cursor: chunkQuestionsLoading || !currentArticle ? 'not-allowed' : 'pointer',
              margin: '8px 0'
            }}>
            {chunkQuestionsLoading ? 'Loading...' : 'Load Questions'}
          </button>
        ) : chunkQuestionsError ? (
          <div style={{ color: '#d32f2f', margin: '16px 0' }}>Error: {chunkQuestionsError}</div>
        ) : (
          <ChunkQuestionPagination chunkQuestionsList={chunkQuestions} />
        )}
      </div>
    </>
  );
}

export default Content;
