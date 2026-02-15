"use client";

import { useState } from "react";
import Link from "next/link";
import { CheckSquare, LogOut, Menu, X } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth/context";

export function Navigation() {
  const { isAuthenticated, user, logout, isLoading } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    window.location.href = "/";
  };

  const closeMobile = () => setMobileOpen(false);

  return (
    <nav className="border-b bg-background/80 backdrop-blur-md sticky top-0 z-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2 font-semibold text-xl group">
            <div className="p-1.5 rounded-lg bg-gradient-to-br from-violet-500/20 to-fuchsia-500/10 group-hover:from-violet-500/30 group-hover:to-fuchsia-500/20 transition-all">
              <CheckSquare className="h-6 w-6 text-violet-600 dark:text-violet-400" />
            </div>
            <span className="bg-gradient-to-r from-violet-600 to-fuchsia-600 dark:from-violet-400 dark:to-fuchsia-400 bg-clip-text text-transparent">
              Flux
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden sm:flex items-center gap-4">
            <Link
              href="/"
              className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
            >
              Home
            </Link>

            {isLoading ? (
              <div className="h-4 w-16 bg-muted animate-pulse rounded"></div>
            ) : isAuthenticated ? (
              <>
                <Link
                  href="/tasks"
                  className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
                >
                  Tasks
                </Link>
                <span className="text-sm text-muted-foreground hidden md:inline truncate max-w-[160px]">
                  {user?.email}
                </span>
                <Button variant="ghost" size="sm" onClick={handleLogout}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="ghost" size="sm">Sign in</Button>
                </Link>
                <Link href="/register">
                  <Button size="sm">Sign up</Button>
                </Link>
              </>
            )}

            <ThemeToggle />
          </div>

          {/* Mobile hamburger */}
          <div className="flex sm:hidden items-center gap-2">
            <ThemeToggle />
            <Button variant="ghost" size="icon" onClick={() => setMobileOpen(!mobileOpen)}>
              {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="sm:hidden border-t bg-background/95 backdrop-blur-md">
          <div className="container mx-auto px-4 py-4 space-y-3">
            <Link
              href="/"
              onClick={closeMobile}
              className="block text-sm font-medium text-muted-foreground hover:text-primary transition-colors py-2"
            >
              Home
            </Link>

            {isLoading ? (
              <div className="h-4 w-16 bg-muted animate-pulse rounded"></div>
            ) : isAuthenticated ? (
              <>
                <Link
                  href="/tasks"
                  onClick={closeMobile}
                  className="block text-sm font-medium text-muted-foreground hover:text-primary transition-colors py-2"
                >
                  Tasks
                </Link>
                <p className="text-sm text-muted-foreground truncate py-2">
                  {user?.email}
                </p>
                <Button variant="ghost" size="sm" className="w-full justify-start" onClick={() => { handleLogout(); closeMobile(); }}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </Button>
              </>
            ) : (
              <div className="flex flex-col gap-2">
                <Link href="/login" onClick={closeMobile}>
                  <Button variant="ghost" size="sm" className="w-full">Sign in</Button>
                </Link>
                <Link href="/register" onClick={closeMobile}>
                  <Button size="sm" className="w-full">Sign up</Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
