import type { Metadata } from "next";
import "./globals.css";
import Providers from "./providers";

export const metadata: Metadata = {
  title: "HeatShield: ShadeStop — Hartford Bus Stop Prioritization",
  description:
    "Prioritize shade structures and cooling interventions for Hartford bus stops based on heat risk, shade deficit, vulnerability, and ridership.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 antialiased min-h-screen flex flex-col">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
