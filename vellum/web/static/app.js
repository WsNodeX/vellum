const results = document.getElementById('results');

function esc(s) {
  return (s || '').replace(/[&<>]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;'}[c]));
}
function card(n, score) {
  const sc = score != null ? `<span class="score">${score}</span>` : '';
  const snippet = (n.snippet || n.content || '').slice(0, 160);
  const tags = (n.tags || []).map(t => `#${esc(t)}`).join(' ');
  return `<article><h3>${esc(n.title)} ${sc}</h3><p>${esc(snippet)}</p><small>${tags}</small></article>`;
}

async function loadNotes() {
  const r = await fetch('/api/notes');
  const notes = await r.json();
  results.innerHTML = notes.length
    ? notes.map(n => card(n)).join('')
    : '<p class="empty">还没有笔记，先在上方添加一条吧。</p>';
}

async function search(q) {
  if (!q.trim()) return loadNotes();
  const r = await fetch('/api/search?q=' + encodeURIComponent(q));
  const hits = await r.json();
  results.innerHTML = hits.length
    ? hits.map(h => card(h, h.score)).join('')
    : '<p class="empty">没有匹配的笔记。</p>';
}

document.getElementById('addBtn').onclick = async () => {
  const title = titleEl.value.trim();
  if (!title) return alert('请填写标题');
  const tags = tagsEl.value.split(',').map(s => s.trim()).filter(Boolean);
  await fetch('/api/notes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content: contentEl.value, tags })
  });
  titleEl.value = contentEl.value = tagsEl.value = '';
  loadNotes();
};

document.getElementById('searchBtn').onclick = () => search(qEl.value);
document.getElementById('resetBtn').onclick = () => { qEl.value = ''; loadNotes(); };
qEl.addEventListener('keydown', e => { if (e.key === 'Enter') search(qEl.value); });

const titleEl = document.getElementById('title');
const contentEl = document.getElementById('content');
const tagsEl = document.getElementById('tags');
const qEl = document.getElementById('q');

loadNotes();
