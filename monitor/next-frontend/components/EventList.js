"use client";

import { useState } from "react";

const labels = { login_failure: "로그인 실패", login_success: "로그인 성공", http_request: "일반 요청" };

export default function EventList({ events, onRefresh }) {
  const [path, setPath] = useState("");
  const [status, setStatus] = useState("");
  const shown = events.filter(event =>
    event.path.toLowerCase().includes(path.trim().toLowerCase()) &&
    (!status || String(event.status_code) === status.trim())
  );
  return <section className="panel events">
    <div className="section-head"><h2>요청 기록</h2><button className="ghost" onClick={onRefresh}>기록 불러오기</button></div>
    <p className="sub">조회 {shown.length}건 · 오류 {shown.filter(event => event.status_code >= 400).length}건</p>
    <div className="event-filters"><label>경로 검색<input value={path} onChange={event => setPath(event.target.value)} placeholder="/login" /></label><label>상태 코드<input value={status} onChange={event => setStatus(event.target.value)} inputMode="numeric" placeholder="401" /></label><button className="ghost" onClick={() => { setPath(""); setStatus(""); }}>조건 해제</button></div>
    {shown.length ? <div className="event-table"><table><thead><tr><th>종류</th><th>상태</th><th>메서드</th><th>경로</th><th>시각</th></tr></thead><tbody>{shown.map(event => <tr key={event.id}><td>{labels[event.event_type] || event.event_type}</td><td>{event.status_code}</td><td>{event.method}</td><td>{event.path}</td><td>{new Date(event.occurred_at).toLocaleString("ko-KR")}</td></tr>)}</tbody></table></div> : <p className="empty">조건에 맞는 기록이 없습니다.</p>}
  </section>;
}
