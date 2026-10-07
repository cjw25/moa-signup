import { useState } from 'react'

export default function EventList({ events, loading, error, filters, onApply, onClear }) {
  const [path, setPath] = useState(filters.path || '')
  const [status, setStatus] = useState(filters.status || '')
  const errorCount = events.filter(event => event.status_code >= 400).length
  return <section className="card"><h2>요청 기록</h2>
    <form className="event-filters" onSubmit={event => { event.preventDefault(); onApply({ path: path.trim(), status }) }}>
      <label>경로 검색<input value={path} onChange={event => setPath(event.target.value)} placeholder="/board" /></label>
      <label>상태 코드<input type="number" min="100" max="599" value={status} onChange={event => setStatus(event.target.value)} placeholder="전체" /></label>
      <button disabled={loading}>검색</button><button type="button" className="secondary" onClick={() => { setPath(''); setStatus(''); onClear() }}>조건 해제</button>
    </form>
    {!loading && !error && <p className="muted">현재 조회 결과: 전체 {events.length}건 · 오류 {errorCount}건 (400 이상)</p>}
    {loading ? <p>불러오는 중...</p> : error ? <p className="error" role="alert">{error}</p> : events.length === 0 ? <p>조건에 맞는 요청 기록이 없습니다.</p> :
      <div className="table-wrap"><table><thead><tr><th>시각</th><th>메서드</th><th>경로</th><th>상태</th></tr></thead><tbody>
        {events.map(event => <tr key={event.id}><td>{new Date(event.occurred_at).toLocaleString('ko-KR')}</td><td>{event.method}</td><td>{event.path}</td><td>{event.status_code}</td></tr>)}
      </tbody></table></div>}
  </section>
}
