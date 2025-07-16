import type { Metadata } from "next";
import { Inter, Playfair_Display, Source_Sans_3 } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});

const playfair = Playfair_Display({
  variable: "--font-serif",
  subsets: ["latin"],
  display: "swap",
});

const sourceSans = Source_Sans_3({
  variable: "--font-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "NutriGenius - AI-Powered Nutrition & Diet Management",
  description: "Personalized nutrition guidance powered by AI and medical insights. Get tailored meal plans, track your progress, and achieve your health goals.",
  keywords: ["nutrition", "AI", "diet", "meal planning", "health", "wellness", "personalized nutrition"],
  authors: [{ name: "NutriGenius Team" }],
  creator: "NutriGenius",
  publisher: "NutriGenius",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL("https://nutrigenius.app"),
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://nutrigenius.app",
    title: "NutriGenius - AI-Powered Nutrition & Diet Management",
    description: "Personalized nutrition guidance powered by AI and medical insights.",
    siteName: "NutriGenius",
    images: [
      {
        url: "/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "NutriGenius - AI-Powered Nutrition",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "NutriGenius - AI-Powered Nutrition",
    description: "Personalized nutrition guidance powered by AI and medical insights.",
    images: ["/twitter-image.jpg"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
      </head>
      <body
        className={`${inter.variable} ${playfair.variable} ${sourceSans.variable} font-sans antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
