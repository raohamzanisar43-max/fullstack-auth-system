import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from "@/components/ui/table";
import { apiClient, TraceJob } from "@/lib/api";
import { toast } from "sonner";
import { format } from "date-fns";

const MyTraces = () => {
  const [traces, setTraces] = useState<TraceJob[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchTraces = async () => {
      try {
        setIsLoading(true);
        const data = await apiClient.getTraceJobs();
        setTraces(data);
      } catch (error) {
        console.error("Failed to fetch trace jobs:", error);
        toast.error("Failed to load your trace jobs");
      } finally {
        setIsLoading(false);
      }
    };

    fetchTraces();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
        return "bg-emerald-500";
      case "processing":
        return "bg-blue-500";
      case "failed":
        return "bg-red-500";
      default:
        return "bg-slate-500";
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-4"></div>
        <p className="text-muted-foreground">Loading your traces...</p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-foreground mb-4">My Traces</h1>

      <div className="rounded-lg border overflow-hidden bg-background">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/50">
              <TableHead className="font-semibold text-foreground">Queue ID</TableHead>
              <TableHead className="font-semibold text-foreground">List Tag</TableHead>
              <TableHead className="font-semibold text-foreground">Trace Type</TableHead>
              <TableHead className="font-semibold text-foreground">Rows Uploaded</TableHead>
              <TableHead className="font-semibold text-foreground">Created At</TableHead>
              <TableHead className="font-semibold text-foreground">Credits Deducted</TableHead>
              <TableHead className="font-semibold text-foreground">Status</TableHead>
              <TableHead className="font-semibold text-foreground text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {traces.length > 0 ? (
              traces.map((trace) => (
                <TableRow key={trace.id}>
                  <TableCell className="font-medium text-foreground">#{trace.id}</TableCell>
                  <TableCell>{trace.name}</TableCell>
                  <TableCell>
                    <Badge className={`${getStatusColor(trace.status)} text-white text-xs gap-1 border-0`}>
                      <span className="h-1.5 w-1.5 rounded-full bg-white inline-block" />
                      {trace.type}
                    </Badge>
                  </TableCell>
                  <TableCell>{trace.total_records.toLocaleString()}</TableCell>
                  <TableCell className="text-muted-foreground text-xs">
                    {format(new Date(trace.created_at), "MMM d, yyyy, h:mm a")}
                  </TableCell>
                  <TableCell>{trace.credits_used.toLocaleString()}</TableCell>
                  <TableCell>
                    <span className="capitalize text-sm font-medium">{trace.status}</span>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button 
                        size="sm" 
                        disabled={trace.status !== "completed"}
                        className="bg-emerald-500 hover:bg-emerald-600 text-white text-xs h-7 px-3"
                        onClick={() => apiClient.downloadTraceResults(trace.id)}
                      >
                        Export
                      </Button>
                      <Button size="sm" variant="outline" className="bg-orange-500 hover:bg-orange-600 text-white border-orange-500 text-xs h-7 px-3">
                        DNC Scrub
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={8} className="h-32 text-center text-muted-foreground">
                  No trace jobs found. Start by uploading a new list!
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};

export default MyTraces;
