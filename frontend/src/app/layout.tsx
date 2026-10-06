import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "회원가입 · 모아",
  description: "나의 일상에 새로운 가능성을 더하는 모아. 지금 시작해 보세요.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="ko"><body>{children}</body></html>;
}
