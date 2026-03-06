export const TOKEN_COOKIE_NAME = "imdb_api_token";

export function getCookie(name: string): string {
  const prefix = `${encodeURIComponent(name)}=`;
  const found = document.cookie
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith(prefix));

  if (!found) {
    return "";
  }

  return decodeURIComponent(found.slice(prefix.length));
}

export function setTokenCookie(value: string): void {
  const secureFlag = window.location.protocol === "https:" ? "; Secure" : "";
  document.cookie = `${encodeURIComponent(TOKEN_COOKIE_NAME)}=${encodeURIComponent(value)}; Max-Age=${60 * 60 * 24 * 30}; Path=/; SameSite=Strict${secureFlag}`;
}

export function clearTokenCookie(): void {
  const base = `${encodeURIComponent(TOKEN_COOKIE_NAME)}=; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/; SameSite=Strict`;
  document.cookie = base;
  document.cookie = `${base}; Secure`;
}
