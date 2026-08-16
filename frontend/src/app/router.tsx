import { createBrowserRouter } from "react-router-dom";

import RootLayout from "./layout/RootLayout";
import Home from "../pages/Home";
import ChartsPage from "../features/charts/ChartsPage";
import MapsPage from "../features/maps/MapsPage";
import LoginPage from "../features/auth/LoginPage";
import ProfilePage from "../features/auth/ProfilePage";
import RegisterPage from "../features/auth/RegisterPage";
import UploadPage from "../features/upload/UploadPage";

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
      {
        path: "upload",
        element: <UploadPage />,
      },
      {
        path: "auth/register",
        element: <RegisterPage />,
      },
      {
        path: "auth/login",
        element: <LoginPage />,
      },
      {
        path: "auth/profile",
        element: <ProfilePage />,
      },
    ],
  },
]);
