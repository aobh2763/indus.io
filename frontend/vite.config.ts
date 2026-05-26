import { reactRouter } from "@react-router/dev/vite";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

const COMPAT_FUNCTIONS = [
  "sortBy",
  "throttle",
  "isPlainObject",
  "get",
  "uniqBy",
  "range",
  "omit",
  "maxBy",
  "sumBy",
  "minBy",
  "last"
];

export default defineConfig({
  plugins: [
    tailwindcss(),
    reactRouter(),
    {
      name: "es-toolkit-compat-vite",
      resolveId(source) {
        if (source.startsWith("es-toolkit/compat/")) {
          const fn = source.split("/").pop()!;
          if (COMPAT_FUNCTIONS.includes(fn)) {
            return `\0virtual:es-toolkit-compat:${fn}`;
          }
        }
        return null;
      },
      load(id) {
        if (id.startsWith("\0virtual:es-toolkit-compat:")) {
          const fn = id.replace("\0virtual:es-toolkit-compat:", "");
          return `import { ${fn} } from "es-toolkit/compat"; export default ${fn};`;
        }
        return null;
      }
    }
  ],
  resolve: {
    tsconfigPaths: true,
  },
  optimizeDeps: {
    esbuildOptions: {
      plugins: [
        {
          name: "es-toolkit-compat-esbuild",
          setup(build) {
            build.onResolve(
              { filter: /^es-toolkit\/compat\/(sortBy|throttle|isPlainObject|get|uniqBy|range|omit|maxBy|sumBy|minBy|last)$/ },
              args => ({
                path: args.path,
                namespace: "es-toolkit-compat"
              })
            );
            build.onLoad(
              { filter: /.*/, namespace: "es-toolkit-compat" },
              args => {
                const fn = args.path.split("/").pop()!;
                return {
                  contents: `import { ${fn} } from "es-toolkit/compat"; export default ${fn};`,
                  resolveDir: "."
                };
              }
            );
          }
        }
      ]
    }
  },
  server: {
    host: true,
    port: 5173,
  },
});



