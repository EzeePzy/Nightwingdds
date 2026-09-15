import React, { createContext, useContext, useEffect, useState } from "react";

const ThemeContext = createContext(null);
export const useTheme = () => useContext(ThemeContext);

function autoMode() {
  const h = new Date().getHours();
  return h >= 6 && h < 18 ? "light" : "dark";
}

export function ThemeProvider({ children }) {
  const [override, setOverride] = useState(() => localStorage.getItem("rs_theme")); // 'light' | 'dark' | null
  const [mode, setMode] = useState(override || autoMode());

  useEffect(() => {
    if (override) return;
    const id = setInterval(() => setMode(autoMode()), 60000);
    return () => clearInterval(id);
  }, [override]);

  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle("rs-light", mode === "light");
    root.classList.toggle("rs-dark", mode === "dark");
  }, [mode]);

  const toggle = () => {
    const next = mode === "light" ? "dark" : "light";
    localStorage.setItem("rs_theme", next);
    setOverride(next);
    setMode(next);
  };
  const useAuto = () => {
    localStorage.removeItem("rs_theme");
    setOverride(null);
    setMode(autoMode());
  };

  const greetKey = mode === "light" ? "greet.morning" : "greet.evening";
  return (
    <ThemeContext.Provider value={{ mode, toggle, useAuto, greetKey, isAuto: !override }}>
      {children}
    </ThemeContext.Provider>
  );
}
