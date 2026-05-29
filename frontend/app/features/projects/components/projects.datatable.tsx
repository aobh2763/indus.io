import { useState } from "react";
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnDef,
} from "@tanstack/react-table";
import { Plus, Pencil, Trash } from "lucide-react";

import { useGetProjects, useDeleteProject } from "../projects.hooks";
import { type ProjectResponse } from "../projects.schema";

import { Button } from "~/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table";
import { Badge } from "~/components/ui/badge";

import { ProjectsCreateForm } from "./projects.create-form";
import { ProjectsUpdateForm } from "./projects.update-form";
import { usePipelineStore } from "~/features/pipeline/pipeline.store";
import { productionLinesApi } from "~/features/pipeline/pipeline.api";
import { useNavigate } from "react-router";
import { PipelineStatus } from "~/features/pipeline/pipeline.schema";

export function ProjectsDataTable() {
  const navigate = useNavigate();
  const { setLineId } = usePipelineStore();

  const { data: projects = [], isLoading } = useGetProjects();
  const { mutateAsync: deleteProject } = useDeleteProject();

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [updateProjectState, setUpdateProjectState] = useState<ProjectResponse | null>(null);

  async function handleOpenInPipelineEditor(project: ProjectResponse) {
    let pId: string | null = null;
    const productionLines = await productionLinesApi.get(project.id);

    if (productionLines.length === 0) {
      const productionLine = await productionLinesApi.create(project.id, {
        name: "default",
        status: PipelineStatus.DRAFT,
      });

      pId = productionLine.id;
    } else {
      const sorted = productionLines.sort((a, b) => Number(a.id > b.id));
      pId = sorted[0].id;
    }

    if (pId) {
      setLineId(pId);
      navigate('/pipeline-builder');
    }
  }

  const columns: ColumnDef<ProjectResponse>[] = [
    {
      accessorKey: "name",
      header: "Name",
    },
    {
      accessorKey: "description",
      header: "Description",
    },
    {
      accessorKey: "visibility",
      header: "Visibility",
      cell: ({ row }) => {
        const visibility = row.getValue("visibility") as string;
        return (
          <Badge variant={visibility === "PUBLIC" ? "default" : "secondary"}>
            {visibility}
          </Badge>
        );
      },
    },
    {
      accessorKey: "created_at",
      header: "Created At",
      cell: ({ row }) => {
        const date = row.getValue("created_at") as Date;
        return new Date(date).toLocaleDateString();
      },
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const project = row.original;
        return (
          <div className="flex items-center gap-2 justify-end">
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleOpenInPipelineEditor(project)}
            >
              Open in pipeline editor
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setUpdateProjectState(project)}
            >
              <Pencil className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                if (window.confirm("Are you sure you want to delete this project?")) {
                  deleteProject(project.id);
                }
              }}
              className="text-destructive hover:text-destructive"
            >
              <Trash className="w-4 h-4" />
            </Button>
          </div>
        );
      },
    },
  ];

  const table = useReactTable({
    data: projects,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold tracking-tight">Projects</h2>
        <Button onClick={() => setIsCreateOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Project
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <ProjectsCreateForm
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
      />

      <ProjectsUpdateForm
        project={updateProjectState}
        isOpen={!!updateProjectState}
        onClose={() => setUpdateProjectState(null)}
      />
    </div>
  );
}
