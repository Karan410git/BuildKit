import { createBrowserRouter } from "react-router-dom";

import RootLayout from "./layout/RootLayout";
import { moduleRoutes } from "./moduleRoutes";
import Home from "../pages/Home";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [{ index: true, element: <Home /> }, ...moduleRoutes],
  },
]);
