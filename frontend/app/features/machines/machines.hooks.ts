import { toast } from 'sonner';
import { machinesApi } from './machines.api';
import {
  type CreateMachineRequest,
  type UpdateMachineRequest,
} from './machines.schema';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export const useGetMachines = (line_id: string) => {
  return useQuery({
    queryKey: ['machines'],
    queryFn: () => machinesApi.get(line_id),
  });
};

export const useGetMachineById = (id: string) => {
  return useQuery({
    queryKey: ['machines', id],
    queryFn: () => machinesApi.getById(id),
  });
};

export const useCreateMachine = (line_id: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateMachineRequest) =>
      machinesApi.create(line_id, data),

    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['machines'] });
      toast.success('Successfully created a new machine');
      console.log(data);
    },

    onError: () => {
      toast.error('Failed to create a machine');
    },
  });
};

export const useUpdateMachine = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: UpdateMachineRequest;
    }) => machinesApi.update(id, data),

    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['machines'] });
      toast.success('Machine updated successfully');
      console.log(data);
    },

    onError: () => {
      toast.error('Failed to update machine');
    },
  });
};

export const useDeleteMachine = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => machinesApi.delete(id),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['machines'] });
      toast.success('Machine deleted successfully');
    },

    onError: () => {
      toast.error('Failed to delete machine');
    },
  });
};
