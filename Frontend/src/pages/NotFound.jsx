import React from 'react';
import { useLocation } from "react-router-dom";
import { useEffect } from "react";

export default function NotFound() {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen items-center justify-center pt-16">
      <div className="text-center opacity-0 animate-fade-up">
        <h1 className="text-6xl font-bold font-display gold-text mb-4">404</h1>
        <p className="text-xl text-muted-foreground mb-6">Page not found</p>
        <a href="/" className="btn-primary inline-block">Return Home</a>
      </div>
    </div>
  );
}
