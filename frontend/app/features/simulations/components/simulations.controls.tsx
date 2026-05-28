import {
  List,
  Plus,
} from "lucide-react";

import { Button } from "~/components/ui/button";

import {
  Card,
  CardContent,
} from "~/components/ui/card";

import { usePipelineStore } from "~/features/pipeline/pipeline.store";

import { useCreateSimulation } from "../simulations.hooks";
import { SimulationStatus } from "../simulations.schema";

export function SimulationsControls() {
  const {
    lineId,
    isMachineLibraryOpen,
    isSimulationPanelOpen,
    setMachineLibraryOpen,
    setSimulationPanelOpen,
  } = usePipelineStore();

  const createSimulation = useCreateSimulation(lineId);

  const handleCreate = () => {
    createSimulation.mutate({
      status: SimulationStatus.STOPPED,
    });
  };

  const handleToggleHistory = () => {
    setSimulationPanelOpen(!isSimulationPanelOpen);
  }

  const handleToggleMachineLibrary = () => {
    setMachineLibraryOpen(!isMachineLibraryOpen);
  }

  return (
    <div className="flex gap-3">
      <Card className="overflow-hidden">
        <CardContent className="flex flex-wrap gap-3">
          <Button variant="outline" className="gap-2" onClick={handleToggleMachineLibrary}>
            <List className="h-4 w-4" />

            {!isMachineLibraryOpen ? <>Show Machine Library</> : <>Hide Machine Library</>}
          </Button>
        </CardContent>
      </Card>
      <Card className="overflow-hidden">
        <CardContent className="flex flex-wrap gap-3">
          <Button
            className="gap-2"
            onClick={handleCreate}
            disabled={createSimulation.isPending}
          >
            <Plus className="h-4 w-4" />

            Create Simulation
          </Button>

          <Button variant="outline" className="gap-2" onClick={handleToggleHistory}>
            <List className="h-4 w-4" />

            {!isSimulationPanelOpen ? <>View Simulation History</> : <>Hide Simulation History</>}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
