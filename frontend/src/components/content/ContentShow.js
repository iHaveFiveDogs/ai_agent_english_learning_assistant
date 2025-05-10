import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import TopBar from '../TopBar';
import Dashboard from './Dashboard';
import ExplainableWrapper from '../wrapper/ExplainableWrapper';
import './ContentShow.css';

function Content({ articles }) {
  const { id } = useParams();
  // Use state to force a re-render when articles or id changes
  const [currentArticle, setCurrentArticle] = useState(null);
  const [highlightWord, setHighlightWord] = useState(null);
  const [dictionaryResult, setDictionaryResult] = useState(null);

  useEffect(() => {
    // Find the latest article by _id each time articles or id changes
    const found = articles.find(a => String(a._id) === String(id));
    setCurrentArticle(found || null);
    setHighlightWord(null);
    setDictionaryResult(null); // clear dictionary result on article change
    // Set article context for dictionary tab
    if (found) {
      window.__ARTICLE_CONTEXT__ = {
        articleId: found._id,
        articleContent: found.content
      };
    } else {
      window.__ARTICLE_CONTEXT__ = null;
    }
  }, [articles, id]);

  const wordExplanations = currentArticle && Array.isArray(currentArticle.word_explanations) ? currentArticle.word_explanations : [];
  const summary = currentArticle && currentArticle.summary ? currentArticle.summary : '';

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

  return (
    <div className="content-page">
      <TopBar />
      <div className="content-layout">
        {/* Article Content */}
        <div className="article-panel">
          <Link to="/articles" className="back-link">&larr; Back to Articles</Link>
          {currentArticle ? (
            <>
              <h2 className="article-title">{currentArticle.title}</h2>
              <ExplainableWrapper>
                <div className="article-body">
                  {highlightWordsInContent(currentArticle.content, highlightWord)}
                </div>
              </ExplainableWrapper>
            </>
          ) : (
            <div className="article-not-found">
              <h2 style={{ color: '#d32f2f', margin: '48px 0 18px 0', fontWeight: 700, fontSize: '2rem' }}>Article Not Found</h2>
              <p style={{ color: '#888', fontSize: '1.15rem', marginBottom: 24 }}>Sorry, the article you are looking for does not exist or was removed.</p>
              <Link to="/articles" className="back-link" style={{ color: '#1976d2' }}>&larr; Back to Articles</Link>
            </div>
          )}
        </div>

        {/* Dashboard */}
        <Dashboard wordList={wordExplanations} summary={summary} onWordClick={setHighlightWord} highlightWord={highlightWord} dictionaryResult={dictionaryResult} setDictionaryResult={setDictionaryResult} articleId={id}/>
      </div>
    </div>
  );
}

export default Content;
