export default function EventList({ events, loading, error }) {
  return <section className="card"><h2>요청 기록</h2>
    {loading ? <p>불러오는 중...</p> : error ? <p className="error" role="alert">{error}</p> : events.length === 0 ? <p>수집된 요청 기록이 없습니다.</p> :
      <div className="table-wrap"><table><thead><tr><th>시각</th><th>메서드</th><th>경로</th><th>상태</th></tr></thead><tbody>
        {events.map(event => <tr key={event.id}><td>{new Date(event.occurred_at).toLocaleString('ko-KR')}</td><td>{event.method}</td><td>{event.path}</td><td>{event.status_code}</td></tr>)}
      </tbody></table></div>}
  </section>
}
