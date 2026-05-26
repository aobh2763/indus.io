import { toast } from 'sonner';
import { productionLinesApi } from './pipeline.api';
import { type CreateProductionLineRequest, type UpdateProductionLineRequest } from './pipeline.schema';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export const useGetProductionLines = (project_id: string) => {
  return useQuery({
    queryKey: ['productionLines'],
    queryFn: () => productionLinesApi.get(project_id),
  });
};

export const useGetProductionLineById = (id: string) => {
  return useQuery({
    queryKey: ['productionLines'],
    queryFn: () => productionLinesApi.getById(id),
  });
};

export const useCreateProductionLine = (project_id: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateProductionLineRequest) => productionLinesApi.create(project_id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['productionLines'] });
      toast.success('successfully created a new production line');
      console.log(data);
    },
    onError: () => {
      toast.error('Failed to create a production line');
    },
  });
};

export const useUpdateProductionLine = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateProductionLineRequest }) => productionLinesApi.update(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['productionLines'] });
      toast.success('Production line updated successfully');
      console.log(data);
    },
    onError: () => {
      toast.error('Failed to update sprint');
    },
  });
};

export const useDeleteProductionLine = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => productionLinesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['productionLines'] });
      toast.success('Production line deleted successfully');
    },
    onError: () => {
      toast.error('Failed to delete production line');
    },
  });
};
