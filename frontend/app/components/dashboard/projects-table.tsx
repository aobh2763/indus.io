import { FolderKanban, Eye, Lock, ExternalLink, Calendar } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { Badge } from "../ui/badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../ui/table";
import { Separator } from "../ui/separator";
import type { Project, ProductionLine } from "../../../types/dashboard";

interface ProjectsTableProps {
  projects: Project[];
  lines: ProductionLine[];
}

const mockProjects: Project[] = [
  { id: "p1", name: "Winter T-Shirts Batch", visibility: "PRIVATE", description: "Seasonal production run", created_at: new Date(Date.now() - 864000000).toISOString(), updated_at: new Date().toISOString() },
  { id: "p2", name: "Denim Q3 Collection", visibility: "PUBLIC", description: "Quarterly denim line", created_at: new Date(Date.now() - 1728000000).toISOString(), updated_at: new Date().toISOString() },
  { id: "p3", name: "Lightweight Jackets", visibility: "PRIVATE", description: "Spring jacket production", created_at: new Date(Date.now() - 432000000).toISOString(), updated_at: new Date().toISOString() },
  { id: "p4", name: "Sports Line 2026", visibility: "PUBLIC", description: "Athletic wear prototype", created_at: new Date(Date.now() - 259200000).toISOString(), updated_at: new Date().toISOString() },
];

function formatDate(d: string) {
  return new Date(d).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export function ProjectsTable({ projects, lines }: ProjectsTableProps) {
  const data = projects.length > 0 ? projects : mockProjects;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-blue-500/10">
              <FolderKanban className="h-4 w-4 text-blue-400" />
            </div>
            <div>
              <CardTitle className="text-base">Projects</CardTitle>
              <CardDescription>{data.length} total projects</CardDescription>
            </div>
          </div>
        </div>
      </CardHeader>
      <Separator />
      <CardContent className="pt-0 px-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Visibility</TableHead>
              <TableHead>Lines</TableHead>
              <TableHead>Created</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((project) => {
              const projectLines = lines.filter((l) => l.project_id === project.id);
              return (
                <TableRow key={project.id}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-white">{project.name}</span>
                    </div>
                    {project.description && <p className="text-xs text-gray-500 mt-0.5">{project.description}</p>}
                  </TableCell>
                  <TableCell>
                    <Badge variant={project.visibility === "PUBLIC" ? "default" : "secondary"} className="text-[10px]">
                      {project.visibility === "PUBLIC" ? <Eye className="h-3 w-3 mr-1" /> : <Lock className="h-3 w-3 mr-1" />}
                      {project.visibility}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm tabular-nums">{projectLines.length || "–"}</span>
                  </TableCell>
                  <TableCell>
                    <span className="flex items-center gap-1.5 text-xs text-gray-400">
                      <Calendar className="h-3 w-3" /> {formatDate(project.created_at)}
                    </span>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
