import Link from "next/link";
import Counter from "../components/Counter";

export default function Home() {
  return (
    <main className="page-content">
      <section className="hero panel">
        <p className="eyebrow">NEXT.JS PRACTICE</p>
        <h1>오늘의 작은 기록을 시작해요.</h1>
        <p>숫자를 세어 보고, 메모를 적고, 고쳐 보세요. 이 연습장은 브라우저의 React state로 동작합니다.</p>
        <div className="hero-actions"><Link className="button" href="/notes">메모 화면으로</Link></div>
      </section>
      <Counter />
    </main>
  );
}
