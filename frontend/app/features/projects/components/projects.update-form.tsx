import { useEffect } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { useUpdateProject } from "../projects.hooks";
import {
  updateProjectRequestSchema,
  type UpdateProjectRequest,
  type ProjectResponse,
  ProjectVisibility,
} from "../projects.schema";

import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Field, FieldLabel, FieldError } from "~/components/ui/field";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetFooter,
} from "~/components/ui/sheet";

export interface ProjectsUpdateFormProps {
  project: ProjectResponse | null;
  isOpen: boolean;
  onClose: () => void;
}

export function ProjectsUpdateForm({
  project,
  isOpen,
  onClose,
}: ProjectsUpdateFormProps) {
  const { mutateAsync: updateProject, isPending } = useUpdateProject();

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors },
  } = useForm<UpdateProjectRequest>({
    resolver: zodResolver(updateProjectRequestSchema),
    defaultValues: {
      name: "",
      description: "",
      visibility: ProjectVisibility.PRIVATE,
    },
  });

  useEffect(() => {
    if (project && isOpen) {
      reset({
        name: project.name,
        description: project.description,
        visibility: project.visibility,
      });
    }
  }, [project, isOpen, reset]);

  const onSubmit = async (data: UpdateProjectRequest) => {
    if (!project) return;
    try {
      await updateProject({ id: project.id, data });
      onClose();
    } catch (error) {
      // Error handled by hook
    }
  };

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      onClose();
    }
  };

  return (
    <Sheet open={isOpen} onOpenChange={handleOpenChange}>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Update Project</SheetTitle>
          <SheetDescription>
            Modify the details of your project.
          </SheetDescription>
        </SheetHeader>

        <form
          onSubmit={handleSubmit(onSubmit)}
          className="mt-6 flex flex-col gap-4 flex-1"
        >
          <Field>
            <FieldLabel>Name</FieldLabel>
            <Input
              {...register("name")}
              placeholder="Project Name"
              disabled={isPending}
            />
            <FieldError errors={[errors.name as any]} />
          </Field>

          <Field>
            <FieldLabel>Description</FieldLabel>
            <Input
              {...register("description")}
              placeholder="Project Description"
              disabled={isPending}
            />
            <FieldError errors={[errors.description as any]} />
          </Field>

          <Controller
            control={control}
            name="visibility"
            render={({ field }) => (
              <Field>
                <FieldLabel>Visibility</FieldLabel>
                <Select
                  disabled={isPending}
                  onValueChange={field.onChange}
                  value={field.value}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select visibility" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={ProjectVisibility.PRIVATE}>
                      Private
                    </SelectItem>
                    <SelectItem value={ProjectVisibility.PUBLIC}>
                      Public
                    </SelectItem>
                  </SelectContent>
                </Select>
                <FieldError errors={[errors.visibility as any]} />
              </Field>
            )}
          />

          <SheetFooter className="mt-auto pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? "Saving..." : "Save Changes"}
            </Button>
          </SheetFooter>
        </form>
      </SheetContent>
    </Sheet>
  );
}
