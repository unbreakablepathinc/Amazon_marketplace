import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Amazon.de Cluster – Dessertgläser & KONZEPT",
  description: "Thematic cluster and product table for amazon.de",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="de">
      <body>{children}</body>
    </html>
  );
}
