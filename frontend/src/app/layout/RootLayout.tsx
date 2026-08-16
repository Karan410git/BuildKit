import { NavLink, Outlet } from "react-router-dom";

import { env } from "../../config/env";

export default function RootLayout() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <NavLink className="app-brand" to="/">
          {env.appName}
        </NavLink>
        <nav className="app-nav" aria-label="Main navigation">
          <NavLink to="/" end>
            Home
          </NavLink>
          <NavLink to="/charts">Charts</NavLink>
          <NavLink to="/maps">Maps</NavLink>
        </nav>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
