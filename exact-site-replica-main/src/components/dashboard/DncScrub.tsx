import { useState, useRef } from "react";
import { Upload, Info, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const dncChecks = [
  "Federal DNC Registry",
  "State DNC Lists",
  "DMA (Do Not Mail)",
  "TCPA Litigators",
];

const DncScrub = () => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]?.name.endsWith(".csv")) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setFile(e.target.files[0]);
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-foreground">DNC Scrub</h1>
        <p className="text-sm text-muted-foreground">
          Scrub your phone list against Federal DNC, State DNC, DMA, and TCPA Litigator databases
        </p>
      </div>

      <div className="max-w-3xl mx-auto space-y-4">
        <div className="flex items-center gap-2 bg-primary/10 text-primary rounded-lg px-4 py-3 text-sm">
          <Info className="h-4 w-4 flex-shrink-0" />
          <span>
            <strong>1 credit per phone number.</strong> Upload a CSV containing a column with phone numbers.
          </span>
        </div>

        <p className="text-sm text-foreground">
          Your Balance: <span className="text-amber-600 font-semibold">118 credits</span>
        </p>

        <div>
          <p className="text-sm font-medium text-foreground mb-2">What's included in each DNC check:</p>
          <div className="grid grid-cols-2 gap-px bg-border rounded-lg overflow-hidden">
            {dncChecks.map((check) => (
              <div key={check} className="bg-card px-4 py-3 text-sm text-foreground">
                {check}
              </div>
            ))}
          </div>
        </div>

        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
            dragActive ? "border-primary bg-primary/5" : "border-border bg-muted/30"
          }`}
        >
          <Upload className="h-10 w-10 mx-auto mb-3 text-primary" />
          <p className="font-semibold text-foreground">Drag & Drop your CSV file here</p>
          <p className="text-sm text-muted-foreground mt-1">
            or{" "}
            <button
              onClick={() => inputRef.current?.click()}
              className="text-primary underline hover:no-underline"
            >
              click to browse
            </button>
          </p>
          <p className="text-xs text-muted-foreground mt-2 flex items-center justify-center gap-1">
            <AlertCircle className="h-3 w-3" /> Accepts .csv files only
          </p>
          <input
            ref={inputRef}
            type="file"
            accept=".csv"
            className="hidden"
            onChange={handleChange}
          />
          {file && (
            <p className="mt-3 text-sm text-primary font-medium">{file.name}</p>
          )}
        </div>

        <Button className="bg-primary text-primary-foreground">Upload</Button>
      </div>
    </div>
  );
};

export default DncScrub;
