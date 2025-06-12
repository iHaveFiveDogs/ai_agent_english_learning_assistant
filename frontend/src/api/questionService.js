// Service for calling /generate_question endpoint
export async function getChunkQuestions(articleId, tag) {
  const res = await fetch('/generate_question', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ article_id: articleId, tag })
  });
  if (!res.ok) {
    throw new Error('Failed to fetch chunk questions');
  }
  const data = await res.json();

  let list = [];
  const chunkArr = data.chunks || [];
  const nested = data.chunk_questions_list || [];

  let chunkMap = {};
  if (Array.isArray(chunkArr)) {
    chunkArr.forEach(obj => {
      if (obj.chunk_id && typeof obj.chunk_text === 'string') {
        chunkMap[obj.chunk_id] = obj.chunk_text;
      }
    });
  }

  if (Array.isArray(nested)) {
    // Flatten: each question becomes its own entry with chunk_id and chunk text
    nested.forEach(chunkObj => {
      const chunk_id = chunkObj.chunk_id;
      const chunk = chunkMap[chunk_id] || '';
      (chunkObj.questions || []).forEach(question => {
        list.push({ chunk_id, chunk, question });
      });
    });
  }
  return list;
}

// Send user answer and feedback for a chunk-question-answer triplet
export async function answerQuestionFeedback(chunk, question, answer) {
  const res = await fetch('/answer_question_feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chunk, question, answer })
  });
  if (!res.ok) {
    throw new Error('Failed to send answer feedback');
  }
  return await res.json();
}
