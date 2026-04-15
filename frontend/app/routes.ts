import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("/pipeline-builder", "routes/pipeline-builder.tsx")
] satisfies RouteConfig;
