import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RealEstate AI — инструменты для риелторов",
  description: "Генерация описаний, постов и скриптов для риелторов с помощью Claude AI",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
