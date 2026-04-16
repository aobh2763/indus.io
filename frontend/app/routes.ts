import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/dashboard.tsx"),
  route("/pipeline-builder", "routes/pipeline-builder.tsx"),
  route("/projects-management", "routes/projects-management.tsx")
] satisfies RouteConfig;
