import { layout } from "./layout.js";
import { registerRoute, router } from "./router.js";

const app = document.getElementById("app");

async function mount(loader) {
  const module = await loader();
  const page = await module.default();
  app.replaceChildren(layout(page));
}

registerRoute("/", () => mount(() => import("../../pages/home.js")));
registerRoute("/students", () => mount(() => import("../../pages/students.js")));
registerRoute("/professors", () => mount(() => import("../../pages/professors.js")));
registerRoute("/courses", () => mount(() => import("../../pages/courses.js")));
registerRoute("/selection", () => mount(() => import("../../pages/selection.js")));

router().catch(console.error);
