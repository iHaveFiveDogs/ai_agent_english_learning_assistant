import React, { useState, useCallback } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import List from "./components/content/List";
import TopBar from './components/TopBar';
import ContentShow from './components/content/ContentShow';
import FloatingChatButton from './components/FloatingChatButton';

import Upload from './components/upload';


function App() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchList = useCallback((tag = 'news') => {
    setLoading(true);
    fetch(`/all_articles?tag=${encodeURIComponent(tag)}`)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch articles');
        return res.json();
      })
      .then((data) => {
        setList(data.articles || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [setList, setLoading, setError]);

  

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
    <>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/articles" element={<List list={list} loading={loading} error={error} fetchList={fetchList} />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/content/:id" element={<ContentShow list={list} loading={loading} tag={new URLSearchParams(window.location.search).get('tag') || 'news'} fetchList={fetchList} />} />
        </Routes>
      </Router>
      <FloatingChatButton />
    </>
  );
}

export default App;
