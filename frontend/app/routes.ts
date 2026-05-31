import * as routeHelpers from "@react-router/dev/routes";
import { type RouteConfig } from "@react-router/dev/routes";

const { route } = "route" in routeHelpers && typeof routeHelpers.route === "function"
  ? routeHelpers
  : (routeHelpers as unknown as { default: typeof routeHelpers }).default;

export default [
  route("/", "routes/dashboard.tsx"),
  route("/login", "routes/login.tsx"),
  route("/signup", "routes/signup.tsx"),
  route("/register", "routes/register.tsx"),
  route("/pipeline-builder", "routes/pipeline-builder.tsx"),
  route("/projects-management", "routes/projects-management.tsx"),
  route("/kpis", "routes/kpis.tsx"),
  route("/kpi/:kpiId", "routes/kpi-details.tsx"),
  route("/scanner", "routes/scanner.tsx")
] satisfies RouteConfig;
