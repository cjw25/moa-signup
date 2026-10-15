"use client";

import { useState } from "react";
import { getAnalysis, startObservation } from "../lib/api";

export default function AnalysisClient() {
  const [threshold, setThreshold] = useState("10");
  const [afterId, setAfterId] = useState(null);
  const [referenceTime, setReferenceTime] = useState(null);
  const [report, setReport] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function start() {
    setBusy(true); setError("");
    try {
      const boundary = await startObservation();
      setAfterId(boundary.after_id);
      setReferenceTime(null);
      setReport(null);
    } catch (failure) { setError(failure.message); }
    finally { setBusy(false); }
  }

  async function load() {
    setBusy(true); setError("");
    try {
      const result = await getAnalysis(afterId, threshold, referenceTime);
      setReferenceTime(result.reference_time);
      setReport(result);
    } catch (failure) { setError(failure.message); }
    finally { setBusy(false); }
  }

  return <section className="panel analysis">
    <h2>실제 HTTP 요청 분석</h2>
    <p className="sub">새 관찰은 현재 마지막 DB ID를 경계로 잡습니다. 첫 결과를 불러온 시각부터 과거 60초의 기록을 읽습니다.</p>
    <div className="analysis-controls">
      <button onClick={start} disabled={busy}>새 관찰 시작</button>
      <label>비교 기준<input type="number" min="1" max="1000" value={threshold} onChange={event => setThreshold(event.target.value)} /></label>
      <button onClick={load} disabled={busy || afterId === null}>결과 불러오기</button>
    </div>
    {afterId !== null && <p className="sub">시작 ID 경계: {afterId}{referenceTime && ` · 기준시각: ${new Date(referenceTime).toLocaleString("ko-KR")}`}</p>}
    {error && <p className="notice error" role="alert">{error}</p>}
    {report && <article className="analysis-report">
      <h3>{report.rule}</h3>
      <p className="analysis-verdict">관찰값 <strong>{report.observed_count}</strong>회 · 기준 <strong>{report.threshold}</strong>회 · <strong>{report.verdict}</strong></p>
      <p>{report.reason}</p>
      <p className="sub">조회 근거 {report.view_ids.length}행 · 뒤따른 404 {report.following_error_ids.length}행 · 전체 근거 {report.evidence.length}행</p>
      <details><summary>근거 보기</summary>
        {report.records.length ? <div className="event-table"><table><thead><tr><th>ID</th><th>수신시각</th><th>방법</th><th>경로</th><th>상태</th><th>종류</th></tr></thead><tbody>
          {report.records.map(record => <tr key={record.id}><td>{record.id}</td><td>{new Date(record.occurred_at).toLocaleString("ko-KR")}</td><td>{record.method}</td><td>{record.path}</td><td>{record.status_code}</td><td>{record.kind}</td></tr>)}
        </tbody></table></div> : <p className="empty">해당 관찰 구간의 근거가 없습니다.</p>}
      </details>
    </article>}
  </section>;
}
