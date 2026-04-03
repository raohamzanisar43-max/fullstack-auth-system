import { useState } from "react";
import { Info, AlertTriangle, CreditCard, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const packages = [
  { price: "$20.00", credits: "1,000 credits" },
  { price: "$40.00", credits: "2,000 credits" },
  { price: "$100.00", credits: "5,000 credits" },
  { price: "$200.00", credits: "10,000 credits" },
  { price: "$400.00", credits: "20,000 credits" },
  { price: "Custom", credits: "Enter amount" },
];

const features = [
  "Property Address",
  "Mailing Address",
  "Owner Names",
  "Phone Numbers (up to 5)",
  "Email Addresses (up to 5)",
];

const CreditsRecharge = () => {
  const [selected, setSelected] = useState<number | null>(null);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-foreground">Buy Credits</h1>
        <p className="text-sm text-muted-foreground">
          One credit balance for all tracing services and any form of upload. Web or API
        </p>
      </div>

      <div className="flex items-center gap-2 bg-primary/10 text-primary rounded-lg px-4 py-3 text-sm mb-6">
        <CreditCard className="h-4 w-4 flex-shrink-0" />
        <span>Current Balance: 118 credits ($2.36)</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div className="lg:col-span-3">
          <Card>
            <CardContent className="p-6 space-y-5">
              <h2 className="text-lg font-semibold text-foreground">Purchase Credits</h2>

              <div>
                <p className="text-sm font-medium text-foreground mb-3">Select Amount</p>
                <div className="grid grid-cols-3 gap-3">
                  {packages.map((pkg, i) => (
                    <button
                      key={i}
                      onClick={() => setSelected(i)}
                      className={`border rounded-lg p-4 text-center transition-colors ${
                        selected === i
                          ? "border-primary bg-primary/5"
                          : "border-border hover:border-primary/50"
                      }`}
                    >
                      <p className="font-semibold text-primary">{pkg.price}</p>
                      <p className="text-xs text-muted-foreground">{pkg.credits}</p>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-sm font-medium text-foreground mb-1">
                  Discount Code <span className="text-muted-foreground">(optional)</span>
                </p>
                <Input placeholder="Enter discount code" />
              </div>

              <div className="flex items-center gap-2 bg-primary/10 text-primary rounded-lg px-4 py-3 text-sm">
                <Info className="h-4 w-4 flex-shrink-0" />
                <span>1 credit = $0.0200 • Use credits for any service at variable rates</span>
              </div>

              <div className="flex items-center gap-2 bg-destructive/10 text-destructive rounded-lg px-4 py-3 text-sm">
                <AlertTriangle className="h-4 w-4 flex-shrink-0" />
                <span><strong>Important:</strong> Credits are not refundable</span>
              </div>

              <Button className="w-full" disabled={selected === null}>
                {selected !== null ? "Continue to Payment" : "Select an amount to continue"}
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2">
          <Card>
            <CardContent className="p-6">
              <h2 className="text-lg font-semibold text-foreground mb-4">Service Comparison</h2>
              <div className="space-y-0 divide-y">
                <div className="flex justify-between py-2">
                  <span className="text-sm font-medium text-primary">Feature</span>
                  <span className="text-sm font-medium text-primary">Included</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-sm text-foreground">Cost per Lead</span>
                  <span className="text-sm text-foreground">$0.0200</span>
                </div>
                {features.map((f) => (
                  <div key={f} className="flex justify-between py-2">
                    <span className="text-sm text-foreground">{f}</span>
                    <Check className="h-4 w-4 text-primary" />
                  </div>
                ))}
              </div>

              <div className="mt-6">
                <p className="text-sm font-semibold text-foreground mb-1">Example Costs:</p>
                <p className="text-xs text-muted-foreground line-through">Skip Trace</p>
                <p className="text-sm font-bold text-foreground">100 leads</p>
                <p className="text-xs text-muted-foreground">100 credits</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CreditsRecharge;
