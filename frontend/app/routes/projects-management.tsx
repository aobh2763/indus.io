import { Navbar1 } from "~/components/navbar";
import { Protect } from "~/features/auth/components/protect";

import {
  ClipboardList,
  FolderKanban,
  Plus,
  Users,
  ArrowUpRight,
} from "lucide-react";

import { Button } from "~/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import { Separator } from "~/components/ui/separator";

export default function ProjectsManagementPage() {
  return (
    <Protect>
      <div className="min-h-screen bg-background">
        <Navbar1 />
        <div className="mx-auto space-y-6 px-6 pb-8 pt-24">
          <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div className="space-y-2">
              <div>
                <h1 className="text-3xl font-bold tracking-tight">
                  Projects Management
                </h1>

                <p className="mt-2 text-muted-foreground">
                  Track manufacturing projects, owners, deadlines, and execution
                  progress.
                </p>
              </div>
            </div>

            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              New Project
            </Button>
          </header>

          <section className="grid gap-4 md:grid-cols-3">
            <InfoCard
              icon={<FolderKanban className="h-4 w-4" />}
              title="Total Projects"
              value="24"
              change="+4 this month"
            />

            <InfoCard
              icon={<ClipboardList className="h-4 w-4" />}
              title="In Progress"
              value="9"
              change="3 nearing completion"
            />

            <InfoCard
              icon={<Users className="h-4 w-4" />}
              title="Assigned Teams"
              value="6"
              change="2 new teams added"
            />
          </section>

          <section className="grid gap-6 lg:grid-cols-[2fr_1fr]">
            <Card className="border-border/60">
              <CardHeader className="flex flex-row items-start justify-between space-y-0">
                <div>
                  <CardTitle>Active Projects</CardTitle>

                  <CardDescription>
                    Current manufacturing pipeline and delivery status.
                  </CardDescription>
                </div>

                <Button variant="outline" size="sm" className="gap-2">
                  View All
                  <ArrowUpRight className="h-4 w-4" />
                </Button>
              </CardHeader>

              <CardContent className="space-y-4">
                <ProjectRow
                  name="Assembly Line Upgrade"
                  owner="Operations Team"
                  progress={82}
                  status="In Progress"
                />

                <Separator />

                <ProjectRow
                  name="Packaging Automation"
                  owner="Automation Team"
                  progress={56}
                  status="Review"
                />

                <Separator />

                <ProjectRow
                  name="Quality Control Revamp"
                  owner="QA Department"
                  progress={94}
                  status="Completed"
                />
              </CardContent>
            </Card>

            <Card className="border-border/60">
              <CardHeader>
                <CardTitle>Overview</CardTitle>

                <CardDescription>
                  Quick snapshot of current activity.
                </CardDescription>
              </CardHeader>

              <CardContent className="space-y-5">
                <OverviewItem
                  label="Completed this week"
                  value="12"
                />

                <OverviewItem
                  label="Pending approvals"
                  value="4"
                />

                <OverviewItem
                  label="Delayed projects"
                  value="2"
                />

                <OverviewItem
                  label="Average completion"
                  value="78%"
                />
              </CardContent>
            </Card>
          </section>
        </div>
      </div>
    </Protect>
  );
}

function InfoCard({
  icon,
  title,
  value,
  change,
}: {
  icon: React.ReactNode;
  title: string;
  value: string;
  change: string;
}) {
  return (
    <Card className="border-border/60">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div className="space-y-1">
          <CardDescription>{title}</CardDescription>

          <CardTitle className="text-3xl">{value}</CardTitle>
        </div>

        <div className="rounded-xl border bg-muted p-2 text-muted-foreground">
          {icon}
        </div>
      </CardHeader>

      <CardContent>
        <p className="text-sm text-muted-foreground">{change}</p>
      </CardContent>
    </Card>
  );
}

function ProjectRow({
  name,
  owner,
  progress,
  status,
}: {
  name: string;
  owner: string;
  progress: number;
  status: string;
}) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-xl border p-4">
      <div className="min-w-0 flex-1">
        <h3 className="truncate font-medium">{name}</h3>

        <p className="text-sm text-muted-foreground">{owner}</p>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden w-40 md:block">
          <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
            <span>Progress</span>
            <span>{progress}%</span>
          </div>

          <div className="h-2 overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <Badge
          variant={
            status === "Completed"
              ? "default"
              : status === "Review"
                ? "secondary"
                : "outline"
          }
        >
          {status}
        </Badge>
      </div>
    </div>
  );
}

function OverviewItem({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg border p-3">
      <span className="text-sm text-muted-foreground">{label}</span>

      <span className="font-semibold">{value}</span>
    </div>
  );
}
