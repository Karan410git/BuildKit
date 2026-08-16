import { apiRequest } from "../../lib/api";

export type User = { id: number; email: string; is_active: boolean };
export type Credentials = { email: string; password: string };
type TokenResponse = { access_token: string; token_type: string };
const tokenStorageKey = "buildkit_access_token";

export function register(credentials: Credentials) {
  return apiRequest<User>("/auth/register", { method: "POST", body: credentials });
}
export function login(credentials: Credentials) {
  return apiRequest<TokenResponse>("/auth/login", { method: "POST", body: credentials });
}
export function getProfile(token: string) {
  return apiRequest<User>("/auth/me", { headers: { Authorization: `Bearer ${token}` } });
}
export function storeAccessToken(token: string) { sessionStorage.setItem(tokenStorageKey, token); }
export function readAccessToken() { return sessionStorage.getItem(tokenStorageKey); }
export function clearAccessToken() { sessionStorage.removeItem(tokenStorageKey); }
