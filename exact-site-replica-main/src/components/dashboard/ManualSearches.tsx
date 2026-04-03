import { useState } from "react";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent } from "@/components/ui/card";

const ManualSearches = () => {
  const [findOwner, setFindOwner] = useState(true);
  const [address, setAddress] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [zip, setZip] = useState("");

  return (
    <div>
      <h1 className="text-2xl font-bold text-foreground mb-1">Manual Searches</h1>
      <p className="text-sm text-muted-foreground mb-6">
        Look up a single address instantly. You can identify the owner or search for someone else at that property by toggling{" "}
        <span className="text-primary font-medium">Find Property</span>
      </p>

      <Card className="max-w-2xl">
        <CardContent className="p-6">
          <h2 className="text-lg font-semibold text-foreground mb-4">Search</h2>

          <div className="space-y-4">
            <div>
              <Label className="text-sm font-medium">
                Address <span className="text-destructive">*</span>
              </Label>
              <Input
                placeholder="123 Main St"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label className="text-sm font-medium">
                  City <span className="text-destructive">*</span>
                </Label>
                <Input placeholder="Miami" value={city} onChange={(e) => setCity(e.target.value)} />
              </div>
              <div>
                <Label className="text-sm font-medium">
                  State <span className="text-destructive">*</span>
                </Label>
                <Input placeholder="FL" value={state} onChange={(e) => setState(e.target.value)} />
              </div>
              <div>
                <Label className="text-sm font-medium">
                  Zip <span className="text-destructive">*</span>
                </Label>
                <Input placeholder="33101" value={zip} onChange={(e) => setZip(e.target.value)} />
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Switch checked={findOwner} onCheckedChange={setFindOwner} />
              <div>
                <p className="text-sm font-semibold text-foreground">Find Property Owner</p>
                <p className="text-xs text-muted-foreground">Search by address only to find the current property owner</p>
              </div>
            </div>

            <Button className="w-full gap-2" size="lg">
              <Search className="h-4 w-4" /> Search
            </Button>

            <p className="text-sm text-primary font-medium">Your Balance: <span className="font-bold">118</span> credits</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ManualSearches;
