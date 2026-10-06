import { SignupForm } from "@/components/signup-form";

export default function Home() {
  return (
    <main className="shell">
      <section className="story" aria-label="모아 소개">
        <div className="brand"><span className="brand-symbol" aria-hidden="true">m.</span><span>모아<span className="brand-en">moa</span></span></div>
        <div className="story-copy">
          <span className="eyebrow"><span className="small-line" /> A LITTLE START, A NEW CHAPTER</span>
          <h1>새로운 시작을,<br /><span>함께 모아.</span></h1>
          <p>당신의 일상에 더해질 작은 가능성.<br />모아에서 첫걸음을 시작해 보세요.</p>
        </div>
        <div className="art" aria-hidden="true">
          <div className="orbit orbit-one" /><div className="orbit orbit-two" />
          <div className="art-halo" />
          <div className="petals"><i /><i /><i /><i /></div>
          <span className="art-dot dot-one" /><span className="art-dot dot-two" />
          <div className="art-note"><span>✦</span> 모든 시작에는 가능성이 있어요.</div>
        </div>
        <footer className="story-footer"><span>작은 시작. 더 넓은 내일.</span><span>EST. 2026</span></footer>
      </section>
      <section className="form-side" aria-label="회원가입">
        <div className="top-note"><span className="status-dot" /> 당신의 새로운 시작을 환영해요</div>
        <div className="form-container"><SignupForm /></div>
        <footer className="page-footer">© 2026 모아 <span>소중한 정보는 안전하게 보관해요.</span></footer>
      </section>
    </main>
  );
}
