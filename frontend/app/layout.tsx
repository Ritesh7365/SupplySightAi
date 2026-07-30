import type { Metadata } from "next";
import { Geist, Instrument_Serif } from "next/font/google";

import { ThemeProvider } from "@/components/layout/ThemeProvider";

import "./globals.css";

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
  display: "swap",
});

const instrument = Instrument_Serif({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-instrument",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "SupplySight AI",
    template: "%s · SupplySight AI",
  },
  description: "Enterprise Supply Chain Analytics Platform",
  applicationName: "SupplySight AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html:
              "(function(){try{var t=localStorage.getItem('supplysight-theme');var d=t==='dark'||(t!=='light'&&window.matchMedia('(prefers-color-scheme: dark)').matches);if(d)document.documentElement.classList.add('dark');document.documentElement.style.colorScheme=d?'dark':'light';}catch(e){}})();",
          }}
        />
      </head>
      <body className={`${geistSans.variable} ${instrument.variable} font-sans`}>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
