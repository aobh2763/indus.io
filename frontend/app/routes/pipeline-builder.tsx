import { ReactFlowProvider } from "@xyflow/react";
import PipelineBuilder from "../../components/pipeline-builder";

export default function PipelineBuilderPage() {
  return (
    <ReactFlowProvider>
      <PipelineBuilder />
    </ReactFlowProvider>
  );
}
