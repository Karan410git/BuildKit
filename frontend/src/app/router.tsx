import { createBrowserRouter } from "react-router-dom";

import RootLayout from "./layout/RootLayout";
import Home from "../pages/Home";
import ChartsPage from "../features/charts/ChartsPage";
import MapsPage from "../features/maps/MapsPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: "charts",
        element: <ChartsPage />,
      },
      {
        path: "maps",
        element: <MapsPage />,
      },
    ],
  },
]);
