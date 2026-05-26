import { useEffect } from "react";
import { useNavigate } from "react-router";
import { ReactFlowProvider } from "@xyflow/react";
import PipelineBuilder from "../../components/pipeline-builder";

export default function PipelineBuilderPage() {
  const navigate = useNavigate();

  useEffect(() => {
    if (typeof window !== "undefined" && !localStorage.getItem("indus_token")) {
      navigate("/login");
    }
  }, [navigate]);

  if (typeof window !== "undefined" && !localStorage.getItem("indus_token")) {
    return null;
  }

  return (
    <ReactFlowProvider>
      <PipelineBuilder />
    </ReactFlowProvider>
  );
}

