import { NavLink, Outlet } from "react-router-dom";

import { moduleNavigation } from "../moduleNavigation";
import { env } from "../../config/env";

export default function RootLayout() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <NavLink className="app-brand" to="/">{env.appName}</NavLink>
        <nav className="app-nav" aria-label="Main navigation">
          <NavLink to="/" end>Home</NavLink>
          {moduleNavigation.map((item) => (
            <NavLink key={item.to} to={item.to}>{item.label}</NavLink>
          ))}
        </nav>
      </header>
      <main className="app-main"><Outlet /></main>
    </div>
  );
}
