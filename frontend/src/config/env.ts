const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

if (!apiBaseUrl) {
  throw new Error("VITE_API_BASE_URL is required");
}

export const env = {
  apiBaseUrl: apiBaseUrl.replace(/\/$/, ""),
  appName: import.meta.env.VITE_APP_NAME || "BuildKit",
} as const;
