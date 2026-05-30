import { toast } from "sonner";
import { projectsApi } from "./projects.api";

import {
  type CreateProjectRequest,
  type UpdateProjectRequest,
} from "./projects.schema";

import {
  useQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

export const projectsKeys = {
  all: ["projects"] as const,
  list: (lineId: string) => [...projectsKeys.all, lineId] as const,
  detail: (id: string) => [...projectsKeys.all, id] as const,
};

export const useGetProjects = () => {
  return useQuery({
    queryKey: projectsKeys.all,
    queryFn: () => projectsApi.get(),
  });
};

export const useGetProjectById = (id: string) => {
  return useQuery({
    queryKey: projectsKeys.detail(id),
    queryFn: () => projectsApi.getById(id),
    enabled: !!id,
  });
};

export const useCreateProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateProjectRequest) =>
      projectsApi.create(data),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: projectsKeys.all,
      });

      toast.success("Successfully created a new project");
    },

    onError: () => {
      toast.error("Failed to create project");
    },
  });
};

export const useUpdateProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: UpdateProjectRequest;
    }) => projectsApi.update(id, data),

    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: projectsKeys.all,
      });

      queryClient.invalidateQueries({
        queryKey: projectsKeys.detail(variables.id),
      });

      toast.success("Project updated successfully");
    },

    onError: () => {
      toast.error("Failed to update project");
    },
  });
};

export const useDeleteProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => projectsApi.delete(id),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: projectsKeys.all,
      });

      toast.success("Project deleted successfully");
    },

    onError: () => {
      toast.error("Failed to delete project");
    },
  });
};
