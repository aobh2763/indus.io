import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router";
import {
  Activity,
  ArrowUpRight,
  Edit3,
  Plus,
  RefreshCw,
  Search,
  Target,
  Trash2,
} from "lucide-react";
import { toast } from "sonner";
import { Protect } from "~/features/auth/components/protect";
import Navbar from "~/components/navbar";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
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
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "~/components/ui/sheet";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "~/components/ui/table";
import { Textarea } from "~/components/ui/textarea";
import { kpiService } from "../../lib/api";
import { useDashboardStore } from "../../store/dashboard";
import type { KPI, KPIValue } from "../../types/dashboard";

type KpiFormState = {
  lineId: string;
  machineId: string;
  name: string;
  formula: string;
  targetValue: string;
  unit: string;
};

const noMachineValue = "__line_level__";
const allLinesValue = "__all_lines__";
const lowerIsBetterTerms = ["defect", "scrap", "waste", "reject", "downtime", "error", "loss"];

const emptyForm: KpiFormState = {
  lineId: "",
  machineId: noMachineValue,
  name: "",
  formula: "",
  targetValue: "",
  unit: "",
};

function lowerIsBetter(kpi: KPI) {
  const text = `${kpi.name} ${kpi.formula ?? ""}`.toLowerCase();
  return lowerIsBetterTerms.some((term) => text.includes(term));
}

function formatNumber(value?: number | null) {
  if (value == null || Number.isNaN(value)) return "N/A";
  return new Intl.NumberFormat(undefined, {
    maximumFractionDigits: Math.abs(value) < 10 ? 2 : 0,
  }).format(value);
}

function formatDate(value?: string | null) {
  if (!value) return "N/A";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function getLatestValue(values: KPIValue[] | undefined) {
  if (!values || values.length === 0) return null;
  return [...values].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()).at(-1) ?? null;
}

function formFromKpi(kpi: KPI): KpiFormState {
  return {
    lineId: kpi.production_line_id,
    machineId: kpi.machine_id ?? noMachineValue,
    name: kpi.name,
    formula: kpi.formula ?? "",
    targetValue: kpi.target_value == null ? "" : String(kpi.target_value),
    unit: kpi.unit ?? "",
  };
}

export default function KpisPage() {
  const {
    kpis,
    kpiValues,
    lines,
    machines,
    isLoading,
    fetchDashboardData,
  } = useDashboardStore();

  const [search, setSearch] = useState("");
  const [lineFilter, setLineFilter] = useState(allLinesValue);
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [editingKpi, setEditingKpi] = useState<KPI | null>(null);
  const [form, setForm] = useState<KpiFormState>(emptyForm);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeletingId, setIsDeletingId] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const filteredKpis = useMemo(() => {
    const query = search.trim().toLowerCase();
    return [...kpis]
      .filter((kpi) => lineFilter === allLinesValue || kpi.production_line_id === lineFilter)
      .filter((kpi) => {
        if (!query) return true;
        const line = lines.find((item) => item.id === kpi.production_line_id);
        const machine = machines.find((item) => item.id === kpi.machine_id);
        return `${kpi.name} ${kpi.formula ?? ""} ${kpi.unit ?? ""} ${line?.name ?? ""} ${machine?.name ?? ""}`
          .toLowerCase()
          .includes(query);
      })
      .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
  }, [kpis, lineFilter, lines, machines, search]);

  const machineOptions = machines.filter((machine) => machine.production_line_id === form.lineId);
  const activeLine = lines.find((line) => line.id === form.lineId);
  const isEditing = Boolean(editingKpi);

  function openCreateForm() {
    setEditingKpi(null);
    setForm({ ...emptyForm, lineId: lines[0]?.id ?? "" });
    setIsSheetOpen(true);
  }

  function openEditForm(kpi: KPI) {
    setEditingKpi(kpi);
    setForm(formFromKpi(kpi));
    setIsSheetOpen(true);
  }

  function closeForm() {
    setIsSheetOpen(false);
    setEditingKpi(null);
    setForm(emptyForm);
  }

  function updateForm<K extends keyof KpiFormState>(key: K, value: KpiFormState[K]) {
    setForm((current) => {
      if (key === "lineId") {
        return { ...current, lineId: value, machineId: noMachineValue };
      }
      return { ...current, [key]: value };
    });
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const name = form.name.trim();
    if (!name) {
      toast.error("KPI name is required");
      return;
    }

    if (!isEditing && !form.lineId) {
      toast.error("Select a production line before creating a KPI");
      return;
    }

    const targetValue = form.targetValue.trim() === "" ? undefined : Number(form.targetValue);
    if (targetValue != null && Number.isNaN(targetValue)) {
      toast.error("Target value must be a valid number");
      return;
    }

    setIsSaving(true);
    try {
      if (editingKpi) {
        await kpiService.update(editingKpi.id, {
          name,
          machine_id: form.machineId === noMachineValue ? null : form.machineId,
          formula: form.formula.trim() || null,
          target_value: targetValue ?? null,
          unit: form.unit.trim() || null,
        });
        toast.success("KPI updated");
      } else {
        await kpiService.create(form.lineId, {
          name,
          machine_id: form.machineId === noMachineValue ? null : form.machineId,
          formula: form.formula.trim() || null,
          target_value: targetValue ?? null,
          unit: form.unit.trim() || null,
        });
        toast.success("KPI created");
      }

      await fetchDashboardData();
      closeForm();
    } catch {
      toast.error(isEditing ? "Failed to update KPI" : "Failed to create KPI");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDelete(kpi: KPI) {
    const confirmed = window.confirm(`Delete KPI "${kpi.name}"? Historical values will no longer appear in KPI lists.`);
    if (!confirmed) return;

    setIsDeletingId(kpi.id);
    try {
      await kpiService.delete(kpi.id);
      await fetchDashboardData();
      toast.success("KPI deleted");
    } catch {
      toast.error("Failed to delete KPI");
    } finally {
      setIsDeletingId(null);
    }
  }

  return (
    <Protect>
      <div className="min-h-screen bg-black text-neutral-200 font-sans">
        <Navbar />

        <main className="max-w-[1600px] mx-auto px-5 py-6">
          <div className="flex flex-col gap-4 mb-6 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-white">KPI Management</h1>
              <p className="text-sm text-neutral-500 mt-1">
                Define, target, inspect, and retire production KPIs by line and machine.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Button variant="outline" size="sm" onClick={() => fetchDashboardData()} disabled={isLoading}>
                <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
                Sync
              </Button>
              <Button size="sm" onClick={openCreateForm} disabled={lines.length === 0}>
                <Plus className="h-3.5 w-3.5" />
                Create KPI
              </Button>
            </div>
          </div>

          <section className="grid grid-cols-1 md:grid-cols-3 gap-px bg-neutral-800 rounded-lg overflow-hidden mb-5">
            <SummaryCell label="Tracked KPIs" value={kpis.length} />
            <SummaryCell label="Production Lines" value={lines.length} />
            <SummaryCell label="Machine-specific" value={kpis.filter((kpi) => kpi.machine_id).length} />
          </section>

          <section className="rounded-lg border border-neutral-800 bg-neutral-950/60">
            <div className="flex flex-col gap-3 border-b border-neutral-800 p-3 md:flex-row md:items-center md:justify-between">
              <div className="relative w-full md:max-w-sm">
                <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-neutral-600" />
                <Input
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  placeholder="Search KPIs, formulas, lines, machines"
                  className="pl-8 bg-black/30 border-neutral-800"
                />
              </div>
              <Select value={lineFilter} onValueChange={setLineFilter}>
                <SelectTrigger className="w-full md:w-64 bg-black/30 border-neutral-800">
                  <SelectValue placeholder="Filter by line" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={allLinesValue}>All production lines</SelectItem>
                  {lines.map((line) => (
                    <SelectItem key={line.id} value={line.id}>
                      {line.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Table>
              <TableHeader>
                <TableRow className="border-neutral-800 hover:bg-transparent">
                  <TableHead className="text-neutral-500">KPI</TableHead>
                  <TableHead className="text-neutral-500">Line</TableHead>
                  <TableHead className="text-neutral-500">Machine</TableHead>
                  <TableHead className="text-neutral-500">Target</TableHead>
                  <TableHead className="text-neutral-500">Latest</TableHead>
                  <TableHead className="text-neutral-500">Status</TableHead>
                  <TableHead className="text-neutral-500">Updated</TableHead>
                  <TableHead className="text-right text-neutral-500">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading && kpis.length === 0 ? (
                  <TableRow className="border-neutral-800">
                    <TableCell colSpan={8} className="h-28 text-center text-neutral-500">
                      Loading KPIs...
                    </TableCell>
                  </TableRow>
                ) : filteredKpis.length === 0 ? (
                  <TableRow className="border-neutral-800">
                    <TableCell colSpan={8} className="h-28 text-center text-neutral-500">
                      No KPIs match this view
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredKpis.map((kpi) => {
                    const line = lines.find((item) => item.id === kpi.production_line_id);
                    const machine = machines.find((item) => item.id === kpi.machine_id);
                    const latest = getLatestValue(kpiValues[kpi.id]);
                    const targetMet = latest?.value != null && kpi.target_value != null
                      ? lowerIsBetter(kpi) ? latest.value <= kpi.target_value : latest.value >= kpi.target_value
                      : null;

                    return (
                      <TableRow key={kpi.id} className="border-neutral-800 hover:bg-neutral-900/70">
                        <TableCell>
                          <div className="min-w-44">
                            <Link to={`/kpi/${kpi.id}`} className="font-medium text-white hover:text-emerald-300">
                              {kpi.name}
                            </Link>
                            <p className="text-xs text-neutral-500 truncate max-w-64">
                              {kpi.formula || "No formula defined"}
                            </p>
                          </div>
                        </TableCell>
                        <TableCell className="text-neutral-300">{line?.name ?? "Unknown line"}</TableCell>
                        <TableCell className="text-neutral-400">{machine?.name ?? "Line-level"}</TableCell>
                        <TableCell className="text-neutral-300 tabular-nums">
                          {formatNumber(kpi.target_value)}
                          {kpi.target_value != null && kpi.unit && <span className="ml-1 text-neutral-500">{kpi.unit}</span>}
                        </TableCell>
                        <TableCell>
                          <div className="text-neutral-300 tabular-nums">
                            {formatNumber(latest?.value)}
                            {latest?.value != null && kpi.unit && <span className="ml-1 text-neutral-500">{kpi.unit}</span>}
                          </div>
                          {latest?.simulation_id && (
                            <p className="text-[10px] text-neutral-600">Sim {latest.simulation_id.slice(0, 8)}</p>
                          )}
                        </TableCell>
                        <TableCell>
                          <span className={`text-xs font-medium ${targetMet == null ? "text-neutral-500" : targetMet ? "text-emerald-400" : "text-amber-400"}`}>
                            {targetMet == null ? "No target" : targetMet ? "On target" : "Watch"}
                          </span>
                        </TableCell>
                        <TableCell className="text-neutral-500">{formatDate(kpi.updated_at)}</TableCell>
                        <TableCell>
                          <div className="flex items-center justify-end gap-1">
                            <Button asChild variant="ghost" size="icon-sm" title="View KPI history">
                              <Link to={`/kpi/${kpi.id}`}>
                                <ArrowUpRight className="h-3.5 w-3.5" />
                              </Link>
                            </Button>
                            <Button variant="ghost" size="icon-sm" onClick={() => openEditForm(kpi)} title="Edit KPI">
                              <Edit3 className="h-3.5 w-3.5" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon-sm"
                              onClick={() => handleDelete(kpi)}
                              disabled={isDeletingId === kpi.id}
                              title="Delete KPI"
                              className="text-red-400 hover:text-red-300"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </section>
        </main>

        <Sheet open={isSheetOpen} onOpenChange={(open) => !open && closeForm()}>
          <SheetContent className="w-full sm:max-w-lg bg-neutral-950 border-neutral-800">
            <SheetHeader>
              <SheetTitle>{isEditing ? "Edit KPI" : "Create KPI"}</SheetTitle>
              <SheetDescription>
                {isEditing
                  ? "Update the KPI definition, target, formula, unit, and optional machine binding."
                  : "Create a KPI definition under a production line, with an optional machine binding."}
              </SheetDescription>
            </SheetHeader>

            <form onSubmit={handleSubmit} className="flex flex-1 flex-col gap-4 px-4 pb-4">
              <div className="grid gap-2">
                <Label htmlFor="kpi-line">Production line</Label>
                <Select
                  value={form.lineId}
                  onValueChange={(value) => updateForm("lineId", value)}
                  disabled={isSaving || isEditing}
                >
                  <SelectTrigger id="kpi-line" className="w-full bg-black/30 border-neutral-800">
                    <SelectValue placeholder="Select line" />
                  </SelectTrigger>
                  <SelectContent>
                    {lines.map((line) => (
                      <SelectItem key={line.id} value={line.id}>
                        {line.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="kpi-machine">Machine</Label>
                <Select
                  value={form.machineId}
                  onValueChange={(value) => updateForm("machineId", value)}
                  disabled={isSaving || !form.lineId}
                >
                  <SelectTrigger id="kpi-machine" className="w-full bg-black/30 border-neutral-800">
                    <SelectValue placeholder="Line-level KPI" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={noMachineValue}>Line-level KPI</SelectItem>
                    {machineOptions.map((machine) => (
                      <SelectItem key={machine.id} value={machine.id}>
                        {machine.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {isEditing && (
                  <p className="text-xs text-neutral-500">
                    Production line stays fixed: {activeLine?.name ?? "Unknown line"}
                  </p>
                )}
              </div>

              <div className="grid gap-2">
                <Label htmlFor="kpi-name">Name</Label>
                <Input
                  id="kpi-name"
                  value={form.name}
                  onChange={(event) => updateForm("name", event.target.value)}
                  placeholder="OEE, Throughput, Defect Rate"
                  disabled={isSaving}
                  className="bg-black/30 border-neutral-800"
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="kpi-formula">Calculation rule</Label>
                <Textarea
                  id="kpi-formula"
                  value={form.formula}
                  onChange={(event) => updateForm("formula", event.target.value)}
                  placeholder="availability * performance * quality"
                  disabled={isSaving}
                  className="min-h-24 bg-black/30 border-neutral-800"
                />
              </div>

              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <div className="grid gap-2">
                  <Label htmlFor="kpi-target">Target value</Label>
                  <Input
                    id="kpi-target"
                    type="number"
                    step="any"
                    value={form.targetValue}
                    onChange={(event) => updateForm("targetValue", event.target.value)}
                    placeholder="85"
                    disabled={isSaving}
                    className="bg-black/30 border-neutral-800"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="kpi-unit">Unit</Label>
                  <Input
                    id="kpi-unit"
                    value={form.unit}
                    onChange={(event) => updateForm("unit", event.target.value)}
                    placeholder="%, units/h"
                    disabled={isSaving}
                    className="bg-black/30 border-neutral-800"
                  />
                </div>
              </div>

              <SheetFooter className="px-0">
                <Button type="button" variant="outline" onClick={closeForm} disabled={isSaving}>
                  Cancel
                </Button>
                <Button type="submit" disabled={isSaving || (!isEditing && !form.lineId)}>
                  {isSaving ? "Saving..." : isEditing ? "Save changes" : "Create KPI"}
                </Button>
              </SheetFooter>
            </form>
          </SheetContent>
        </Sheet>
      </div>
    </Protect>
  );
}

function SummaryCell({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-black px-4 py-3.5 flex flex-col gap-1">
      <span className="text-[11px] text-neutral-500 uppercase tracking-wider font-medium">{label}</span>
      <span className="text-xl font-semibold tabular-nums text-white">{value}</span>
    </div>
  );
}
