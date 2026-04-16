import { Link } from "react-router";
import { Activity, AlertCircle, Briefcase, CheckCircle2, TrendingUp, Clock, Factory, ArrowRight } from "lucide-react";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";
import { ReactFlow, Background, Controls } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const kpiData = [
  { time: "08:00", oee: 65, throughput: 120 },
  { time: "10:00", oee: 72, throughput: 145 },
  { time: "12:00", oee: 68, throughput: 130 },
  { time: "14:00", oee: 78, throughput: 160 },
  { time: "16:00", oee: 82, throughput: 175 },
  { time: "18:00", oee: 85, throughput: 190 },
];

const mockNodes = [
  { id: "1", position: { x: 50, y: 50 }, data: { label: "Matière Première" }, style: { width: 100, fontSize: '10px', padding: '5px' } },
  { id: "2", position: { x: 200, y: 50 }, data: { label: "Coupe" }, style: { width: 80, fontSize: '10px', padding: '5px' } },
  { id: "3", position: { x: 350, y: 50 }, data: { label: "Assemblage" }, style: { width: 90, fontSize: '10px', padding: '5px' } },
];
const mockEdges = [
  { id: "e1-2", source: "1", target: "2" },
  { id: "e2-3", source: "2", target: "3" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 pt-24 px-8 pb-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* KPIs Row */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card title="OEE Moyen" value="78.5%" icon={<Activity className="h-4 w-4 text-emerald-500" />} trend="+2.5% depuis hier" />
          <Card title="Rendement (Unités/h)" value="1,240" icon={<TrendingUp className="h-4 w-4 text-blue-500" />} trend="+15% par rapport à l'objectif" />
          <Card title="Projets en cours" value="12" icon={<Briefcase className="h-4 w-4 text-purple-500" />} text="3 en retard" />
          <Card title="Alertes Machines" value="4" icon={<AlertCircle className="h-4 w-4 text-rose-500" />} text="Nécessite une attention immédiate" />
        </div>

        {/* Main Content Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
          
          {/* Left Column (Charts & Projects) */}
          <div className="lg:col-span-4 space-y-4">
            
            {/* Chart Block */}
            <div className="rounded-xl border border-gray-800 bg-gray-900 shadow-lg p-6">
              <div className="flex flex-col space-y-1.5 mb-4">
                <h3 className="font-semibold leading-none tracking-tight text-white">Performance Globale (OEE & Rendement)</h3>
                <p className="text-sm text-gray-400">Évolution de la production sur la journée</p>
              </div>
              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={kpiData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorOee" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#374151" />
                    <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#9ca3af' }} dy={10} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#9ca3af' }} dx={-10} />
                    <Tooltip 
                      contentStyle={{ borderRadius: '8px', border: '1px solid #374151', backgroundColor: '#1f2937', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.3)' }}
                      itemStyle={{ color: '#f3f4f6', fontWeight: 500 }}
                    />
                    <Area type="monotone" dataKey="oee" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorOee)" name="OEE (%)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Projects Block */}
            <div className="rounded-xl border border-gray-800 bg-gray-900 shadow-lg p-6">
              <div className="flex flex-col space-y-1.5 mb-4 flex-row justify-between items-start">
                <div>
                  <h3 className="font-semibold leading-none tracking-tight text-white">Projets Récents</h3>
                  <p className="text-sm text-gray-400">Suivi de l'avancement des commandes</p>
                </div>
              </div>
              <div className="space-y-4">
                <ProjectItem name="Lot T-Shirts Hiver" progress={85} expected="Aujourd'hui" status="Bon" />
                <ProjectItem name="Pantalons Denim Q3" progress={45} expected="Dans 3 jours" status="Retard" />
                <ProjectItem name="Vestes Légères" progress={15} expected="Semaine prochaine" status="Bon" />
              </div>
            </div>

          </div>

          {/* Right Column (Alerts & Pipeline) */}
          <div className="lg:col-span-3 space-y-4">
            
             {/* Pipeline Preview Window */}
             <div className="rounded-xl border border-gray-800 bg-gray-900 shadow-lg p-6 flex flex-col h-[350px]">
              <div className="flex flex-col space-y-1.5 mb-4">
                <div className="flex justify-between items-center">
                  <h3 className="font-semibold leading-none tracking-tight flex items-center gap-2 text-white">
                    <Factory className="h-4 w-4" /> 
                    Pipeline de Production
                  </h3>
                  <Link to="/pipeline-builder" className="text-xs text-blue-400 hover:text-blue-300 flex items-center">
                    Voir détails <ArrowRight className="ml-1 h-3 w-3" />
                  </Link>
                </div>
                <p className="text-sm text-gray-400">Aperçu du flux actuel</p>
              </div>
              <div className="flex-1 border border-gray-800 rounded-lg overflow-hidden bg-gray-800 relative">
                <ReactFlow 
                  nodes={mockNodes} 
                  edges={mockEdges} 
                  fitView 
                  proOptions={{ hideAttribution: true }}
                  panOnScroll={false}
                  zoomOnScroll={false}
                >
                  <Background color="#1f2937" gap={16} variant="dots" />
                </ReactFlow>
                {/* Disable interaction overlay */}
                <div className="absolute inset-0 bg-transparent cursor-pointer z-10" title="Cliquez pour modifier la pipeline" onClick={() => window.location.href = '/pipeline-builder'}></div>
              </div>
            </div>

            {/* Alerts Block */}
            <div className="rounded-xl border border-gray-800 bg-gray-900 shadow-lg p-6">
              <div className="flex flex-col space-y-1.5 mb-4">
                <h3 className="font-semibold leading-none tracking-tight flex items-center gap-2 text-white">
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  Alertes IA & Machines
                </h3>
                <p className="text-sm text-gray-400">Notifications critiques du système</p>
              </div>
              <div className="space-y-4">
                <AlertItem type="critical" time="Il y a 10 min" message="Machine Coupe-02: Baisse de performance détectée (OEE < 50%)." />
                <AlertItem type="warning" time="Il y a 1 heure" message="Goulot d'étranglement prédit sur l'Atelier Couture d'ici 2h." />
                <AlertItem type="info" time="Il y a 3 heures" message="Maintenance préventive recommandée pour Machine Tissu-01." />
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}

// Reusable micro-components for the dashboard
function Card({ title, value, icon, trend, text }: any) {
  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 shadow-lg p-6">
      <div className="flex flex-row items-center justify-between space-y-0 pb-2">
        <h3 className="tracking-tight text-sm font-medium text-gray-200">{title}</h3>
        {icon}
      </div>
      <div>
        <div className="text-2xl font-bold text-white">{value}</div>
        {(trend || text) && (
          <p className="text-xs text-gray-400 mt-1">
            {trend && <span className={trend.includes('+') ? 'text-emerald-400 font-medium' : 'text-red-400 font-medium'}>{trend}</span>}
            {trend && text && " · "}
            {text}
          </p>
        )}
      </div>
    </div>
  );
}

function ProjectItem({ name, progress, expected, status }: any) {
  return (
    <div className="flex items-center justify-between">
      <div className="space-y-1.5 flex-1">
        <p className="text-sm font-medium leading-none text-white">{name}</p>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <Clock className="h-3 w-3" /> {expected}
        </div>
      </div>
      <div className="flex items-center gap-4 w-1/3 justify-end">
        <div className="w-full bg-gray-800 rounded-full h-2 max-w-[80px]">
          <div className={`h-2 rounded-full ${status === 'Retard' ? 'bg-orange-500' : 'bg-blue-500'}`} style={{ width: `${progress}%` }}></div>
        </div>
        <span className="text-xs font-medium w-8 text-right text-gray-300">{progress}%</span>
      </div>
    </div>
  );
}

function AlertItem({ type, message, time }: any) {
  const isCritical = type === 'critical';
  const isWarning = type === 'warning';
  
  return (
    <div className={`flex items-start gap-3 p-3 rounded-lg border ${isCritical ? 'bg-red-900/30 border-red-800' : isWarning ? 'bg-orange-900/30 border-orange-800' : 'bg-blue-900/30 border-blue-800'}`}>
      <div className={`mt-0.5 ${isCritical ? 'text-red-400' : isWarning ? 'text-orange-400' : 'text-blue-400'}`}>
        {isCritical ? <AlertCircle className="h-4 w-4" /> : isWarning ? <Activity className="h-4 w-4" /> : <CheckCircle2 className="h-4 w-4" />}
      </div>
      <div className="space-y-1">
        <p className={`text-sm font-medium ${isCritical ? 'text-red-200' : isWarning ? 'text-orange-200' : 'text-blue-200'}`}>
          {message}
        </p>
        <p className={`text-xs ${isCritical ? 'text-red-400/70' : isWarning ? 'text-orange-400/70' : 'text-blue-400/70'}`}>
          {time}
        </p>
      </div>
    </div>
  );
}
