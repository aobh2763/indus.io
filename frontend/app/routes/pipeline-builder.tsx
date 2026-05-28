import { Navbar1 } from "~/components/navbar1";
import { ReactFlowProvider } from "@xyflow/react";
import { Protect } from "~/features/auth/components/protect";
import PipelineBuilder from "~/features/pipeline/components/pipeline.canvas";

export default function PipelineBuilderPage() {
  return (
    <Protect>
      <Navbar1 />
      <ReactFlowProvider>
        <PipelineBuilder />
      </ReactFlowProvider>
    </Protect>
  );
}
