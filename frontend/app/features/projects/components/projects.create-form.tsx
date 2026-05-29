import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { useCreateProject } from "../projects.hooks";
import {
  createProjectRequestSchema,
  type CreateProjectRequest,
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

export interface ProjectsCreateFormProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ProjectsCreateForm({
  isOpen,
  onClose,
}: ProjectsCreateFormProps) {
  const { mutateAsync: createProject, isPending } = useCreateProject();

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors },
  } = useForm<CreateProjectRequest>({
    resolver: zodResolver(createProjectRequestSchema),
    defaultValues: {
      name: "",
      description: "",
      visibility: ProjectVisibility.PRIVATE,
    },
  });

  const onSubmit = async (data: CreateProjectRequest) => {
    try {
      await createProject(data);
      reset();
      onClose();
    } catch (error) {
      // Error handled by hook
    }
  };

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      reset();
      onClose();
    }
  };

  return (
    <Sheet open={isOpen} onOpenChange={handleOpenChange}>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Create Project</SheetTitle>
          <SheetDescription>
            Add a new project to this line. Click save when you're done.
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
                  defaultValue={field.value}
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
              {isPending ? "Saving..." : "Save Project"}
            </Button>
          </SheetFooter>
        </form>
      </SheetContent>
    </Sheet>
  );
}
