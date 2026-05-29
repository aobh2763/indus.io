import Navbar from "~/components/navbar";
import { ReactFlowProvider } from "@xyflow/react";
import { Protect } from "~/features/auth/components/protect";
import PipelineBuilder from "~/features/pipeline/components/pipeline.canvas";

export default function PipelineBuilderPage() {
  return (
    <Protect>
      <Navbar />
      <ReactFlowProvider>
        <PipelineBuilder />
      </ReactFlowProvider>
    </Protect>
  );
}
