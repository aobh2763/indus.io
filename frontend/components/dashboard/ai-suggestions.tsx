import { Brain, Sparkles, CheckCircle2, Clock } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../ui/card";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Progress } from "../ui/progress";
import { ScrollArea } from "../ui/scroll-area";
import { Separator } from "../ui/separator";
import type { Suggestion } from "../../types/dashboard";

interface AiSuggestionsProps {
  suggestions: Suggestion[];
}

const mockSuggestions: Suggestion[] = [
  { id: "s1", production_line_id: "", type: "optimization", description: "Reduce spindle speed on CNC-03 by 15% to prevent overheating", confidence: 0.92, applied: false, created_at: new Date(Date.now() - 1800000).toISOString() },
  { id: "s2", production_line_id: "", type: "scheduling", description: "Reschedule batch #247 to night shift for 12% energy savings", confidence: 0.87, applied: false, created_at: new Date(Date.now() - 7200000).toISOString() },
  { id: "s3", production_line_id: "", type: "maintenance", description: "Replace wear plate on Press-01 within next 48 hours", confidence: 0.78, applied: true, created_at: new Date(Date.now() - 86400000).toISOString() },
];

const typeIcons: Record<string, string> = {
  optimization: "⚡",
  scheduling: "📅",
  maintenance: "🔧",
  quality: "✨",
};

export function AiSuggestions({ suggestions }: AiSuggestionsProps) {
  const data = suggestions.length > 0 ? suggestions : mockSuggestions;

  return (
    <Card className="flex flex-col h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <div className="flex items-center justify-center h-8 w-8 rounded-lg bg-purple-500/10">
            <Brain className="h-4 w-4 text-purple-400" />
          </div>
          <div>
            <CardTitle className="text-base">AI Suggestions</CardTitle>
            <CardDescription>Recommendations from AI agents</CardDescription>
          </div>
        </div>
      </CardHeader>
      <Separator />
      <CardContent className="flex-1 pt-4">
        <ScrollArea maxHeight="350px" className="pr-1">
          <div className="space-y-3">
            {data.map((suggestion) => (
              <div key={suggestion.id} className="p-3.5 rounded-lg border border-gray-800/60 bg-gray-800/20 hover:bg-gray-800/40 transition-all duration-200 space-y-3">
                <div className="flex items-start gap-2">
                  <span className="text-base shrink-0 mt-0.5">{typeIcons[suggestion.type || ""] || "💡"}</span>
                  <p className="text-sm text-gray-200 leading-snug">{suggestion.description}</p>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {suggestion.type && <Badge variant="outline" className="text-[10px] capitalize">{suggestion.type}</Badge>}
                    {suggestion.applied ? (
                      <Badge variant="success" className="text-[10px]"><CheckCircle2 className="h-3 w-3 mr-1" />Applied</Badge>
                    ) : (
                      <Badge variant="secondary" className="text-[10px]"><Clock className="h-3 w-3 mr-1" />Pending</Badge>
                    )}
                  </div>
                  {suggestion.confidence != null && (
                    <div className="flex items-center gap-2 min-w-[100px]">
                      <Progress value={suggestion.confidence * 100} className="h-1.5 flex-1" indicatorClassName={suggestion.confidence > 0.8 ? "bg-emerald-500" : suggestion.confidence > 0.6 ? "bg-amber-500" : "bg-rose-500"} />
                      <span className="text-[11px] text-gray-400 font-mono w-9 text-right">{Math.round(suggestion.confidence * 100)}%</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
