import { ReactFlowProvider } from "@xyflow/react";
import PipelineBuilder from "~/features/pipeline/components/pipeline";

export default function PipelineBuilderPage() {
  return (
    <ReactFlowProvider>
      <PipelineBuilder />
    </ReactFlowProvider>
  );
}
