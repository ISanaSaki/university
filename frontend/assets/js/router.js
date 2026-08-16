const routes = new Map();

export function registerRoute(path, handler) {
  routes.set(path, handler);
}

export function navigate(path) {
  window.location.hash = `#${path}`;
}

export function currentPath() {
  const raw = window.location.hash.slice(1) || "/";
  return raw.split("?")[0] || "/";
}

export async function router() {
  const handler = routes.get(currentPath()) || routes.get("/");
  await handler?.();
}

window.addEventListener("hashchange", router);
