import { Outlet } from "react-router-dom";

import { env } from "../../config/env";

export default function RootLayout() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <a className="app-brand" href="/">
          {env.appName}
        </a>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
