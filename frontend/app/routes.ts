import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("/hello", "routes/hello.tsx")
] satisfies RouteConfig;
