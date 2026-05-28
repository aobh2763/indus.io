import { toast } from 'sonner';
import { connectionsApi } from './connections.api';
import {
  type CreateConnectionRequest,
  type UpdateConnectionRequest,
} from './connections.schema';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export const useGetConnections = (line_id: string) => {
  return useQuery({
    queryKey: ['connections'],
    queryFn: () => connectionsApi.get(line_id),
  });
};

export const useGetConnectionById = (id: string) => {
  return useQuery({
    queryKey: ['connections', id],
    queryFn: () => connectionsApi.getById(id),
  });
};

export const useCreateConnection = (line_id: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateConnectionRequest) =>
      connectionsApi.create(line_id, data),

    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['connections'] });
      toast.success('Successfully created a new connection');
      console.log(data);
    },

    onError: () => {
      toast.error('Failed to create a connection');
    },
  });
};

export const useUpdateConnection = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: UpdateConnectionRequest;
    }) => connectionsApi.update(id, data),

    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['connections'] });
      toast.success('Connection updated successfully');
      console.log(data);
    },

    onError: () => {
      toast.error('Failed to update connection');
    },
  });
};

export const useDeleteConnection = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => connectionsApi.delete(id),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['connections'] });
      toast.success('Connection deleted successfully');
    },

    onError: () => {
      toast.error('Failed to delete connection');
    },
  });
};
