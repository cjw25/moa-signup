"use client";

import { useState } from "react";

export default function Counter() {
  const [count, setCount] = useState(0);
  return (
    <section className="panel counter-panel" aria-label="숫자 세기">
      <div><p className="eyebrow">COUNTER</p><h2>숫자를 세어 보세요</h2><p className="muted">버튼을 누르면 이 화면의 값이 바뀝니다.</p></div>
      <div className="count-box" aria-live="polite">{count}</div>
      <div className="actions"><button onClick={() => setCount(value => value + 1)}>숫자 증가</button><button className="secondary" onClick={() => setCount(0)}>초기화</button></div>
    </section>
  );
}
