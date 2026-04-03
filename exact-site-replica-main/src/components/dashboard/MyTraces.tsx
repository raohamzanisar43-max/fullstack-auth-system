import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from "@/components/ui/table";

const tracesData = [
  { id: "#55553", type: "Normal", rows: 188, date: "Feb. 26, 2026, 5:30 p.m.", credits: 77, status: "Ready" },
  { id: "#30369", type: "Normal", rows: 2820, date: "Sept. 22, 2025, 8:39 a.m.", credits: 2785, status: "Ready" },
  { id: "#30368", type: "Normal", rows: 4092, date: "Sept. 22, 2025, 8:37 a.m.", credits: 4035, status: "Ready" },
  { id: "#30367", type: "Normal", rows: 2859, date: "Sept. 22, 2025, 8:35 a.m.", credits: 2809, status: "Ready" },
  { id: "#28564", type: "Normal", rows: 6312, date: "Aug. 18, 2025, 10:34 p.m.", credits: 6234, status: "Ready" },
  { id: "#28556", type: "Normal", rows: 1299, date: "Aug. 18, 2025, 6:54 p.m.", credits: 1280, status: "Ready" },
  { id: "#28411", type: "Normal", rows: 4221, date: "Aug. 15, 2025, 1:53 p.m.", credits: 4149, status: "Ready" },
  { id: "#28011", type: "Normal", rows: 6671, date: "Aug. 5, 2025, 10:32 p.m.", credits: 6549, status: "Ready" },
];

const MyTraces = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold text-foreground mb-4">My Traces</h1>

      <div className="rounded-lg border overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/50">
              <TableHead className="font-semibold text-foreground">Queue ID</TableHead>
              <TableHead className="font-semibold text-foreground">List Tag</TableHead>
              <TableHead className="font-semibold text-foreground">Trace Type</TableHead>
              <TableHead className="font-semibold text-foreground">Rows Uploaded</TableHead>
              <TableHead className="font-semibold text-foreground">Created At</TableHead>
              <TableHead className="font-semibold text-foreground">Credits Deducted</TableHead>
              <TableHead className="font-semibold text-foreground">Approx. Processing Time</TableHead>
              <TableHead className="font-semibold text-foreground text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {tracesData.map((trace) => (
              <TableRow key={trace.id}>
                <TableCell className="font-medium text-foreground">{trace.id}</TableCell>
                <TableCell></TableCell>
                <TableCell>
                  <Badge className="bg-emerald-500 text-white text-xs gap-1">
                    <span className="h-1.5 w-1.5 rounded-full bg-white inline-block" />
                    {trace.type}
                  </Badge>
                </TableCell>
                <TableCell>{trace.rows.toLocaleString()}</TableCell>
                <TableCell className="text-muted-foreground">{trace.date}</TableCell>
                <TableCell>{trace.credits.toLocaleString()}</TableCell>
                <TableCell>{trace.status}</TableCell>
                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-2">
                    <Button size="sm" className="bg-emerald-500 hover:bg-emerald-600 text-white text-xs h-7 px-3">
                      Export
                    </Button>
                    <Button size="sm" variant="outline" className="bg-orange-500 hover:bg-orange-600 text-white border-orange-500 text-xs h-7 px-3">
                      DNC Scrub
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};

export default MyTraces;
