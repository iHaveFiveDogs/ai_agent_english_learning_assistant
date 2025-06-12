import React, { useEffect, useState } from 'react';

// Make sure to have FontAwesome or similar icons available in your project
// You can install FontAwesome with: npm install @fortawesome/fontawesome-free
// And import in your main index.js or App.js: import '@fortawesome/fontawesome-free/css/all.min.css';

function ArticleProcessingStatus({ articleId }) {
  const [status, setStatus] = useState('processing'); // 'processing' | 'done'

  useEffect(() => {
    if (!articleId) return;
    const ws = new window.WebSocket(`ws://localhost:8000/ws/merge_status/${articleId}`);

    ws.onopen = () => {
      setStatus('processing');
    };

    ws.onmessage = (event) => {
      setStatus('done');
      ws.close();
    };

    ws.onclose = () => {
      // Optionally handle disconnect
    };

    return () => ws.close();
  }, [articleId]);

  return (
    <div>
      {status === 'processing' ? (
        <span>
          <i className="fas fa-spinner fa-spin" style={{ color: 'gray', marginRight: 8 }} /> Processing...
        </span>
      ) : (
        <span>
          <i className="fas fa-check-circle" style={{ color: 'green', marginRight: 8 }} /> Done!
        </span>
      )}
    </div>
  );
}

export default ArticleProcessingStatus;
