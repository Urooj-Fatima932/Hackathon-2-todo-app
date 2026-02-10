import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Toaster } from "react-hot-toast";
import { Navigation } from "@/components/Navigation";
import { ThemeProvider } from "@/components/theme-provider";
import { AuthProvider } from "@/lib/auth/context";
import { ChatProvider } from "@/components/chat";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: {
    default: "Flux",
    template: "%s | Flux",
  },
  description: "A modern task management application built with Next.js",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <AuthProvider>
          <ThemeProvider
            attribute="class"
            defaultTheme="light"
            enableSystem
            disableTransitionOnChange
          >
            <ChatProvider>
              <Navigation />
              <main className="min-h-screen">{children}</main>
              <Toaster position="top-right" />
            </ChatProvider>
          </ThemeProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
