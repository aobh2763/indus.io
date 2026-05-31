import { toast } from "sonner";
import { simulationsApi } from "./simulations.api";
import {
  type CreateSimulationRequest,
  type UpdateSimulationRequest,
} from "./simulations.schema";

import {
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

export const simulationsKeys = {
  all: ["simulations"] as const,
  list: (lineId: string) => [...simulationsKeys.all, lineId] as const,
  detail: (id: string) => [...simulationsKeys.all, id] as const,
};

export const useGetSimulations = (lineId: string) => {
  return useQuery({
    queryKey: simulationsKeys.list(lineId),
    queryFn: () => simulationsApi.get(lineId),
    enabled: !!lineId,
  });
};

export const useGetSimulationById = (id: string) => {
  return useQuery({
    queryKey: simulationsKeys.detail(id),
    queryFn: () => simulationsApi.getById(id),
    enabled: !!id,
  });
};

export const useCreateSimulation = (lineId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateSimulationRequest) =>
      simulationsApi.create(lineId, data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: simulationsKeys.list(lineId),
      });

      toast.success("Successfully created a new simulation");
    },

    onError: () => {
      toast.error("Failed to create simulation");
    },
  });
};

export const useUpdateSimulation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: UpdateSimulationRequest;
    }) => simulationsApi.update(id, data),

    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: simulationsKeys.all,
      });

      queryClient.invalidateQueries({
        queryKey: simulationsKeys.detail(variables.id),
      });

      toast.success("Simulation updated successfully");
    },

    onError: () => {
      toast.error("Failed to update simulation");
    },
  });
};

export const useDeleteSimulation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => simulationsApi.delete(id),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: simulationsKeys.all,
      });

      toast.success("Simulation deleted successfully");
    },

    onError: () => {
      toast.error("Failed to delete simulation");
    },
  });
};

export const useGetSimulationSteps = (id: string) => {
  return useQuery({
    queryKey: [id],
    queryFn: () => simulationsApi.getSteps(id),
    enabled: !!id,
  });
};

export const useSimulationStep = (id: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => simulationsApi.step(id),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [id],
      });

      toast.success("Simulation deleted successfully");
    },

    onError: () => {
      toast.error("Failed to delete simulation");
    },
  });
};
