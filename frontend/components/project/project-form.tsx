
import type { CreateProjectDTO } from "../../types/project";
import { useNavigate } from "react-router";

type Props = {
  form: CreateProjectDTO;
  setForm: (form: CreateProjectDTO) => void;
  onSubmit: () => void;
};

export default function ProjectForm({ form, setForm, onSubmit }: Props) {
  const navigate = useNavigate();

  const handleCreateProductionLine = () => {
    navigate("/pipeline-builder", {
      state: { projectName: form.name },
    });
  };

  const handleImportProductionLine = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    console.log("Importing:", file.name);
    e.target.value = "";
  };

  return (
    <div className="bg-gray-900 p-6 rounded-2xl space-y-5">
      <input
        placeholder="Project name"
        value={form.name}
        onChange={(e) => setForm({ ...form, name: e.target.value })}
        className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-gray-600 transition-colors"
      />
      <div className="space-y-2">
        <label className="block text-sm text-gray-400 font-medium">
          Production Lines
        </label>

        <div className="flex gap-3">
          <button
            type="button"
            onClick={handleCreateProductionLine}
            className="flex-1 bg-gray-800 hover:bg-gray-700 border border-gray-700 hover:border-gray-600 px-5 py-3 rounded-xl text-sm font-medium transition-all duration-200"
          >
            Create Production Line
          </button>
          <label className="flex-1 cursor-pointer">
            <div className="bg-gray-800 hover:bg-gray-700 border border-gray-700 hover:border-gray-600 px-5 py-3 rounded-xl text-sm font-medium text-center transition-all duration-200">
              Import Production Line
            </div>
            <input
              type="file"
              accept=".json,.yaml,.yml,.csv"
              onChange={handleImportProductionLine}
              className="hidden"
            />
          </label>
        </div>
        {form.production_lines?.length > 0 && (
          <p className="text-xs text-gray-500 pl-1">
            {form.production_lines.length} production line(s) configured
          </p>
        )}
      </div>
      <input
        placeholder="Shift supervisors"
        value={(form.shift_supervisors || []).join(", ")}
        onChange={(e) =>
          setForm({
            ...form,
            shift_supervisors: e.target.value.split(",").map((v) => v.trim()),
          })
        }
        className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-gray-600 transition-colors"
      />
      <div>
        <label className="block text-sm text-gray-400 font-medium mb-1.5">
          Visibility
        </label>
        <select
          value={form.visibility}
          onChange={(e) =>
            setForm({
              ...form,
              visibility: e.target.value as "private" | "public",
            })
          }
          className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-gray-600 transition-colors"
        >
          <option value="private">Private</option>
          <option value="public">Public</option>
        </select>
      </div>
      <button
        onClick={onSubmit}
        className="w-full bg-indigo-600 hover:bg-indigo-700 py-3.5 rounded-xl text-sm font-semibold transition-all duration-200 mt-4"
      >
        Create Project
      </button>
    </div>
  );
}