import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import { useAuthStore } from '~/features/auth/auth.store';
import { projectsApi, projectAccessApi, projectNotificationsApi } from './project.api';
import type {
  CreateProjectRequest,
  UpdateProjectRequest,
  CreateProjectAccessRequest,
  UpdateProjectAccessRequest,
} from './project.schema';

export const projectKeys = {
  all: ['projects'] as const,
  detail: (id: string) => ['projects', id] as const,
  access: (projectId: string) => ['projects', projectId, 'access'] as const,
  invitationsRoot: ['projects', 'me', 'invitations'] as const,
  invitations: (userId?: string | null) => ['projects', 'me', 'invitations', userId ?? 'anonymous'] as const,
  notificationsRoot: ['projects', 'notifications'] as const,
  notifications: (userId?: string | null) => ['projects', 'notifications', userId ?? 'anonymous'] as const,
};

export const useGetProjects = () => {
  return useQuery({
    queryKey: projectKeys.all,
    queryFn: () => projectsApi.getAll(),
  });
};

export const useGetProjectById = (id: string) => {
  return useQuery({
    queryKey: projectKeys.detail(id),
    queryFn: () => projectsApi.getById(id),
    enabled: !!id,
  });
};

export const useCreateProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateProjectRequest) => projectsApi.create(data),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.all });
      toast.success('Project created successfully');
    },

    onError: () => {
      toast.error('Failed to create project');
    },
  });
};

export const useCloneProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => projectsApi.clone(id),

    onSuccess: (project) => {
      queryClient.invalidateQueries({ queryKey: projectKeys.all });
      toast.success(`Cloned ${project.name}`);
    },

    onError: () => {
      toast.error('Failed to clone project');
    },
  });
};

export const useUpdateProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateProjectRequest }) =>
      projectsApi.update(id, data),

    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: projectKeys.all });
      queryClient.invalidateQueries({ queryKey: projectKeys.detail(id) });
      toast.success('Project updated successfully');
    },

    onError: () => {
      toast.error('Failed to update project');
    },
  });
};

export const useDeleteProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => projectsApi.delete(id),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.all });
      toast.success('Project deleted successfully');
    },

    onError: () => {
      toast.error('Failed to delete project');
    },
  });
};

export const useGetProjectAccess = (projectId: string) => {
  return useQuery({
    queryKey: projectKeys.access(projectId),
    queryFn: () => projectAccessApi.getList(projectId),
    enabled: !!projectId,
  });
};

export const useGetProjectInvitations = () => {
  const userId = useAuthStore((state) => state.user?.id);

  return useQuery({
    queryKey: projectKeys.invitations(userId),
    queryFn: () => projectAccessApi.invitations(),
    enabled: !!userId,
    refetchInterval: 15000,
  });
};

export const useGetProjectNotifications = () => {
  const userId = useAuthStore((state) => state.user?.id);

  return useQuery({
    queryKey: projectKeys.notifications(userId),
    queryFn: () => projectNotificationsApi.getList(),
    enabled: !!userId,
    refetchInterval: 15000,
  });
};

export const useGrantProjectAccess = (projectId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateProjectAccessRequest) =>
      projectAccessApi.grant(projectId, data),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.access(projectId) });
      queryClient.invalidateQueries({ queryKey: projectKeys.notificationsRoot });
      toast.success('Invitation sent. It stays pending until accepted.');
    },

    onError: () => {
      toast.error('Failed to grant access');
    },
  });
};

export const useAcceptProjectInvitation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (accessId: string) => projectAccessApi.accept(accessId),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.all });
      queryClient.invalidateQueries({ queryKey: projectKeys.invitationsRoot });
      queryClient.invalidateQueries({ queryKey: projectKeys.notificationsRoot });
      toast.success('Invitation accepted');
    },

    onError: () => {
      toast.error('Failed to accept invitation');
    },
  });
};

export const useDeclineProjectInvitation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (accessId: string) => projectAccessApi.decline(accessId),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.invitationsRoot });
      queryClient.invalidateQueries({ queryKey: projectKeys.notificationsRoot });
      toast.success('Invitation declined');
    },

    onError: () => {
      toast.error('Failed to decline invitation');
    },
  });
};

export const useMarkProjectNotificationRead = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (notificationId: string) => projectNotificationsApi.markRead(notificationId),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.notificationsRoot });
    },
  });
};

export const useUpdateProjectAccess = (projectId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ accessId, data }: { accessId: string; data: UpdateProjectAccessRequest }) =>
      projectAccessApi.update(accessId, data),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.access(projectId) });
      toast.success('Access updated');
    },

    onError: () => {
      toast.error('Failed to update access');
    },
  });
};

export const useRevokeProjectAccess = (projectId: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (accessId: string) => projectAccessApi.revoke(accessId),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: projectKeys.access(projectId) });
      toast.success('Access revoked');
    },

    onError: () => {
      toast.error('Failed to revoke access');
    },
  });
};
