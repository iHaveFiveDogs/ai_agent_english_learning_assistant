// Article-related API calls

// Send a chat message to the agent and get a response
export async function sendChatMessage({ tag, articleId, query }) {
  if (!tag) throw new Error('No tag provided');
  const res = await fetch(`http://localhost:8000/agent_langraph_answer?tag=${encodeURIComponent(tag)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ article_id: articleId, query })
  });
  if (!res.ok) throw new Error('Failed to get response');
  return res.json();
}

// Fetch dictionary result for words in an article
export async function fetchDictionary({ article_id, article, words }) {
  const res = await fetch('http://localhost:8000/dictionary', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ article_id, article, words })
  });
  if (!res.ok) throw new Error('Failed to fetch dictionary');
  return res.json();
}


// Explain text
export async function explainText(text) {
  const response = await fetch('/explain', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  if (!response.ok) throw new Error('Failed to fetch explanation');
  return response.json();
}

// Get all articles by tag
export async function getAllArticles(tag = 'news') {
  const response = await fetch(`/all_articles?tag=${encodeURIComponent(tag)}`);
  if (!response.ok) throw new Error('Failed to fetch articles');
  return response.json();
}

// Upload a new article
export async function uploadArticle({ title, source, content, tag }) {
  const payload = { title, source, content, tag };
  console.log('[DEBUG] uploadArticle payload:', payload);
  const response = await fetch('/upload_article_service', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  console.log('[DEBUG] uploadArticle raw response:', response);
  if (!response.ok) throw new Error('Failed to upload article');
  const json = await response.json();
  console.log('[DEBUG] uploadArticle parsed JSON:', json);
  return json;
}

// Edit an existing article
export async function editArticle(articleId, form) {
  const response = await fetch(`/edit_article?article_id=${encodeURIComponent(articleId)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form),
  });
  const data = await response.json();
  if (!response.ok || data.error) throw new Error(data.error || 'Failed to update article');
  return data;
}

// Delete an article
export async function deleteArticle(articleId, tag) {
  const response = await fetch(`/delete_article?article_id=${encodeURIComponent(articleId)}&tag=${encodeURIComponent(tag)}`, {
    method: 'DELETE',
  });
  const data = await response.json();
  if (!data.success) throw new Error(data.message || 'Delete failed');
  return data;
}

// Get a single article
export async function getSingleArticle(articleId, tag) {
  const response = await fetch(`/single_article?article_id=${encodeURIComponent(articleId)}&tag=${encodeURIComponent(tag)}`);
  if (!response.ok) throw new Error('Failed to fetch article');
  return response.json();
}

// (Optional) List articles by tag
export async function listArticlesByTag(tag) {
  const response = await fetch(`/list_articles?tag=${encodeURIComponent(tag)}`);
  if (!response.ok) throw new Error('Failed to fetch articles');
  return response.json();
}
