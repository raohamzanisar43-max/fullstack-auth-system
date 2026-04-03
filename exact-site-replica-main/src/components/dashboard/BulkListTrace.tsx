import { useState, useRef, useEffect } from "react";
import { Upload, Star, Info, FileText, Download, AlertCircle, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { apiClient, TraceJob, CreditBalance } from "@/lib/api";
import { toast } from "sonner";

const BulkListTrace = () => {
  const [traceType, setTraceType] = useState<"normal" | "enhanced">("normal");
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [recentJobs, setRecentJobs] = useState<TraceJob[]>([]);
  const [creditBalance, setCreditBalance] = useState<CreditBalance | null>(null);
  const [jobName, setJobName] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [jobs, credits] = await Promise.all([
        apiClient.getTraceJobs(0, 5),
        apiClient.getCreditBalance()
      ]);
      setRecentJobs(jobs);
      setCreditBalance(credits);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file?.name.endsWith(".csv")) {
      setSelectedFile(file);
      setJobName(file.name.replace(/\.[^/.]+$/, ""));
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setJobName(file.name.replace(/\.[^/.]+$/, ""));
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error("Please select a file to upload");
      return;
    }

    if (!jobName.trim()) {
      toast.error("Please enter a job name");
      return;
    }

    setIsUploading(true);
    
    try {
      const traceJob = await apiClient.createTraceJob({
        name: jobName,
        type: traceType,
        file: selectedFile
      });
      
      toast.success("Trace job created successfully!");
      setSelectedFile(null);
      setJobName("");
      
      // Refresh jobs
      const jobs = await apiClient.getTraceJobs(0, 5);
      setRecentJobs(jobs);
      
    } catch (error: any) {
      console.error('Failed to create trace job:', error);
      toast.error(error.response?.data?.detail || "Failed to create trace job");
    } finally {
      setIsUploading(false);
    }
  };

  const downloadResults = async (jobId: number) => {
    try {
      const blob = await apiClient.downloadTraceResults(jobId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `trace_results_${jobId}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success("Results downloaded successfully!");
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to download results");
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: string; icon: React.ReactNode }> = {
      pending: { variant: "secondary", icon: <AlertCircle className="h-3 w-3" /> },
      processing: { variant: "default", icon: <div className="h-3 w-3 animate-spin rounded-full border-2 border-current border-t-transparent" /> },
      completed: { variant: "default", icon: <CheckCircle className="h-3 w-3" /> },
      failed: { variant: "destructive", icon: <AlertCircle className="h-3 w-3" /> }
    };
    
    const config = variants[status] || variants.pending;
    
    return (
      <Badge variant={config.variant as any} className="flex items-center gap-1">
        {config.icon}
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const getProgressPercentage = (job: TraceJob) => {
    if (job.total_records === 0) return 0;
    return (job.processed_records / job.total_records) * 100;
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-primary mb-1">Quick Trace</h1>
      <p className="text-sm text-muted-foreground mb-1">
        Need help? Click here for our walk-through video -&gt;:{" "}
        <a href="#" className="text-primary underline">Video</a>
      </p>
      <p className="text-sm text-muted-foreground mb-6">Choose a CSV file to upload</p>

      {/* Tracer Status & Trace Type */}
      <div className="max-w-3xl mx-auto mb-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="font-semibold text-foreground">Tracer Status</span>
          <Badge className="bg-emerald-500 text-white text-xs">Online</Badge>
        </div>
        <p className="text-sm font-semibold text-foreground mb-3">Select Trace Type</p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          <Card
            className={`cursor-pointer transition-all ${traceType === "normal" ? "ring-2 ring-primary" : "hover:border-primary/50"}`}
            onClick={() => setTraceType("normal")}
          >
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-1">
                <div className={`h-4 w-4 rounded-full border-2 flex items-center justify-center ${traceType === "normal" ? "border-primary" : "border-muted-foreground"}`}>
                  {traceType === "normal" && <div className="h-2 w-2 rounded-full bg-primary" />}
                </div>
                <span className="font-semibold text-foreground">Normal Trace</span>
              </div>
              <p className="text-xs text-primary ml-6">1 credit per result</p>
              <p className="text-xs text-muted-foreground ml-6">Standard contact info, phones and emails</p>
            </CardContent>
          </Card>

          <Card
            className={`cursor-pointer transition-all ${traceType === "enhanced" ? "ring-2 ring-primary" : "hover:border-primary/50"}`}
            onClick={() => setTraceType("enhanced")}
          >
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-1">
                <div className={`h-4 w-4 rounded-full border-2 flex items-center justify-center ${traceType === "enhanced" ? "border-primary" : "border-muted-foreground"}`}>
                  {traceType === "enhanced" && <div className="h-2 w-2 rounded-full bg-primary" />}
                </div>
                <span className="font-semibold text-foreground">Enhanced Trace</span>
              </div>
              <p className="text-xs text-primary ml-6">3 credits per result</p>
              <p className="text-xs text-muted-foreground ml-6">Advanced data including property values and mortgage info</p>
            </CardContent>
          </Card>
        </div>

        <p className="text-sm text-primary font-medium mb-4">
          Your Balance: <span className="font-bold">{creditBalance?.credits || 0}</span> credits
        </p>

        {/* Job Name Input */}
        <div className="mb-4">
          <label className="text-sm font-medium text-foreground mb-2 block">Job Name</label>
          <input
            type="text"
            value={jobName}
            onChange={(e) => setJobName(e.target.value)}
            placeholder="Enter job name"
            className="w-full p-2 border rounded-md bg-background"
          />
        </div>

        {/* Google Review Banner */}
        <div className="bg-emerald-600 text-white rounded-lg px-4 py-3 flex items-center justify-between mb-4">
          <p className="text-sm font-medium">If you love our service, Leave us a Google review here</p>
          <Button size="sm" variant="secondary" className="gap-1.5">
            <Star className="h-3.5 w-3.5" /> Review
          </Button>
        </div>

        {/* CSV Requirements */}
        <p className="text-sm text-muted-foreground mb-3">
          Your CSV file must have the columns <span className="font-medium text-foreground">Address</span>, <span className="font-medium text-foreground">City</span>, <span className="font-medium text-foreground">State</span>, <span className="font-medium text-foreground">First Name</span> and <span className="font-medium text-foreground">Last Name</span>
        </p>

        {/* Drop Zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors mb-4 ${
            dragOver ? "border-primary bg-primary/5" : "border-muted-foreground/30 bg-muted/30 hover:border-primary/50"
          }`}
        >
          <Upload className="h-10 w-10 text-primary mx-auto mb-3" />
          <p className="text-lg font-semibold text-foreground mb-1">
            {selectedFile ? selectedFile.name : "Drag & Drop your CSV file here"}
          </p>
          <p className="text-sm text-muted-foreground">
            or <span className="text-primary underline">click to browse</span>
          </p>
          <p className="text-xs text-muted-foreground mt-2 flex items-center justify-center gap-1">
            <Info className="h-3 w-3" /> Accepts .csv files only
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={handleFileSelect}
          />
        </div>

        {/* Info Banner */}
        <div className="bg-blue-50 border border-blue-200 text-blue-700 rounded-lg px-4 py-3 flex items-center gap-2 mb-4">
          <Info className="h-4 w-4 flex-shrink-0" />
          <p className="text-sm">For maximized accuracy please ensure that your list contains correct Addresses and the Owner's name.</p>
        </div>

        <Button className="px-8" onClick={handleUpload} disabled={isUploading || !selectedFile}>
          {isUploading ? "Uploading..." : "Upload"}
        </Button>
      </div>

      {/* Recent Jobs Section */}
      {recentJobs.length > 0 && (
        <div className="max-w-3xl mx-auto mt-8">
          <h3 className="text-lg font-semibold text-foreground mb-4">Recent Trace Jobs</h3>
          <div className="space-y-4">
            {recentJobs.map((job) => (
              <Card key={job.id} className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <h4 className="font-medium">{job.name}</h4>
                    {getStatusBadge(job.status)}
                    <Badge variant="outline">{job.type}</Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">
                      {job.processed_records}/{job.total_records} records
                    </span>
                    {job.status === "completed" && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => downloadResults(job.id)}
                      >
                        <Download className="h-4 w-4 mr-1" />
                        Download
                      </Button>
                    )}
                  </div>
                </div>
                
                {job.status === "processing" && (
                  <Progress value={getProgressPercentage(job)} className="w-full mb-3" />
                )}
                
                <div className="text-sm text-muted-foreground">
                  Credits used: {job.credits_used} | Created: {new Date(job.created_at).toLocaleDateString()}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default BulkListTrace;
