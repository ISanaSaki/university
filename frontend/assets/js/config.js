const localHosts = new Set(["localhost", "127.0.0.1"]);

export const API_BASE_URL = window.UNIREG_API_URL || (
  localHosts.has(window.location.hostname)
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : `${window.location.origin}/api`
);
