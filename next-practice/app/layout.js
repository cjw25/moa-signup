import Link from "next/link";
import "./globals.css";

export const metadata = {
  title: "작은 메모 연습장",
  description: "Next.js와 React state로 만든 메모 연습장",
};

export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <body>
        <div className="site-shell">
          <header className="site-header">
            <Link className="brand" href="/">작은 메모 연습장</Link>
            <nav aria-label="주 메뉴"><Link href="/">홈</Link><Link href="/notes">메모</Link></nav>
          </header>
          {children}
          <footer className="site-footer">Next.js App Router · React state 실습</footer>
        </div>
      </body>
    </html>
  );
}
