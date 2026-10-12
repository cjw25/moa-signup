import "./globals.css";

export const metadata = {
  title: "관찰 메모 | mini-watch",
  description: "Flask와 PostgreSQL에 저장되는 관찰 메모",
};

export default function RootLayout({ children }) {
  return <html lang="ko"><body>{children}</body></html>;
}
