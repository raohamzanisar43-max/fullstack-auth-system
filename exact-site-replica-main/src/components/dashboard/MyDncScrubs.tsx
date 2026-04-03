import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Download } from "lucide-react";

const MyDncScrubs = () => {
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-foreground">My DNC Scrubs</h1>
        <Button>New DNC Scrub</Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50">
                <TableHead>ID</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>Phones Uploaded</TableHead>
                <TableHead>Checked</TableHead>
                <TableHead>Clean</TableHead>
                <TableHead>Credits Used</TableHead>
                <TableHead>Created At</TableHead>
                <TableHead>Est. Time</TableHead>
                <TableHead className="text-right">
                  <span className="flex items-center justify-end gap-1">
                    Downloads <Download className="h-3.5 w-3.5" />
                  </span>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell colSpan={9} className="text-center py-16">
                  <p className="text-muted-foreground text-sm">
                    No DNC scrubs yet.{" "}
                    <button className="text-primary underline hover:no-underline">
                      Start one now.
                    </button>
                  </p>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default MyDncScrubs;
