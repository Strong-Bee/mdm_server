import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://mdm-server.vercel.app"),
  title: {
    default: "Apple MDM Server — Eksperimen Device Management",
    template: "%s | Apple MDM Server",
  },
  description:
    "Fondasi eksperimental Apple iOS/iPadOS Mobile Device Management berbasis Python Flask. Untuk pembelajaran protokol dan pengelolaan perangkat yang sah.",
  applicationName: "Apple MDM Server",
  openGraph: {
    title: "Apple MDM Server",
    description:
      "Eksplorasi protokol Apple Device Management dengan pendekatan yang transparan, terdokumentasi, dan berorientasi keamanan.",
    type: "website",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  themeColor: "#08111f",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}
