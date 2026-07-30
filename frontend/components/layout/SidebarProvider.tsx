"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

type SidebarContextValue = {
  collapsed: boolean;
  mobileOpen: boolean;
  toggleCollapsed: () => void;
  setCollapsed: (value: boolean) => void;
  openMobile: () => void;
  closeMobile: () => void;
  toggleMobile: () => void;
};

const SidebarContext = createContext<SidebarContextValue | null>(null);

const STORAGE_KEY = "supplysight-sidebar-collapsed";

export function SidebarProvider({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsedState] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored === "true") setCollapsedState(true);
  }, []);

  useEffect(() => {
    const onResize = () => {
      if (window.innerWidth >= 1024) setMobileOpen(false);
    };
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  const setCollapsed = useCallback((value: boolean) => {
    setCollapsedState(value);
    window.localStorage.setItem(STORAGE_KEY, String(value));
  }, []);

  const toggleCollapsed = useCallback(() => {
    setCollapsed(!collapsed);
  }, [collapsed, setCollapsed]);

  const openMobile = useCallback(() => setMobileOpen(true), []);
  const closeMobile = useCallback(() => setMobileOpen(false), []);
  const toggleMobile = useCallback(() => setMobileOpen((v) => !v), []);

  const value = useMemo(
    () => ({
      collapsed,
      mobileOpen,
      toggleCollapsed,
      setCollapsed,
      openMobile,
      closeMobile,
      toggleMobile,
    }),
    [collapsed, mobileOpen, toggleCollapsed, setCollapsed, openMobile, closeMobile, toggleMobile],
  );

  return <SidebarContext.Provider value={value}>{children}</SidebarContext.Provider>;
}

export function useSidebar() {
  const ctx = useContext(SidebarContext);
  if (!ctx) {
    throw new Error("useSidebar must be used within SidebarProvider");
  }
  return ctx;
}
