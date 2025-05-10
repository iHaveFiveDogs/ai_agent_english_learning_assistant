import React, { useState, useCallback } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import Articles from './components/content/Articles';
import TopBar from './components/TopBar';
import ContentShow from './components/content/ContentShow';

import UploadArticle from './components/UploadArticle';

// Hegel SVG Icon
// const HegelHead = () => (
//   <Link to="/" className="hegel-link" aria-label="Home">
//     <svg width="32" height="32" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
//       <circle cx="32" cy="32" r="32" fill="#222" />
//       <ellipse cx="32" cy="40" rx="18" ry="12" fill="#fff" />
//       <ellipse cx="24" cy="28" rx="6" ry="8" fill="#fff" />
//       <ellipse cx="40" cy="28" rx="6" ry="8" fill="#fff" />
//       <ellipse cx="24" cy="28" rx="2.5" ry="3.5" fill="#222" />
//       <ellipse cx="40" cy="28" rx="2.5" ry="3.5" fill="#222" />
//       <rect x="28" y="44" width="8" height="3" rx="1.5" fill="#222" />
//     </svg>
//   </Link>
// );

function App() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchArticles = useCallback(() => {
    setLoading(true);
    fetch('/all_articles')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch articles');
        return res.json();
      })
      .then((data) => {
        setArticles(data.articles || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [setArticles, setLoading, setError]);

  

  function Home() {
    return (
      <div className="App ollama-style">
        <TopBar />
        <section className="hero">
          <h1 className="hero-title">Article AI Agent</h1>
          <p className="hero-subtitle">Your personal assistant for understanding and summarizing articles. Select any text to get instant explanations powered by AI.</p>
          <button className="cta-button">Get Started</button>
        </section>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/articles" element={<Articles articles={articles} loading={loading} error={error} fetchArticles={fetchArticles} />} />
        <Route path="/content/:id" element={<ContentShow articles={articles} />} />
        <Route path="/upload" element={<UploadArticle onSend={fetchArticles} />} />

      </Routes>
    </Router>
  );
}

export default App;
