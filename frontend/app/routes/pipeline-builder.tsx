import { Navbar1 } from "~/components/navbar";
import { ReactFlowProvider } from "@xyflow/react";
import PipelineBuilder from "~/features/pipeline/components/pipeline";
import { Protect } from "~/features/auth/components/protect";

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
