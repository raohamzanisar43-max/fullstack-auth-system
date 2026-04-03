import { useState } from "react";
import { Search, MapPin, CreditCard, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog";

const steps = [
  { num: 1, title: "Select County", desc: "Click on a county on the map or use search" },
  { num: 2, title: "Choose List Type", desc: "Select from 32 lead list categories" },
  { num: 3, title: "Place Order", desc: "We'll prepare your list (24hrs-5+ days)" },
  { num: 4, title: "Card Authorized", desc: "Hold placed at order, charged on delivery only" },
];

const CountyLeadLists = () => {
  const [paymentOpen, setPaymentOpen] = useState(false);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-foreground">County Lead Lists</h1>
        <p className="text-sm text-muted-foreground">
          Get fresh, up-to-date property records pulled directly from county sources — no stale data
        </p>
      </div>

      {/* How It Works */}
      <Card className="mb-6 bg-[hsl(222,47%,16%)] text-white border-0">
        <CardContent className="p-4">
          <p className="text-xs font-semibold mb-3 flex items-center gap-1">
            <span className="text-primary">⊕</span> How It Works
          </p>
          <div className="grid grid-cols-4 gap-4">
            {steps.map((s) => (
              <div key={s.num} className="flex items-start gap-3">
                <div className="h-7 w-7 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold flex-shrink-0">
                  {s.num}
                </div>
                <div>
                  <p className="text-sm font-semibold">{s.title}</p>
                  <p className="text-xs text-white/60">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Search + Map placeholder */}
      <div className="relative mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Search className="h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search for a county (e.g., 'Los Angeles' or 'California')..."
            className="flex-1"
          />
        </div>
        <div className="h-72 rounded-xl bg-muted/50 border flex items-center justify-center">
          <div className="text-center text-muted-foreground">
            <MapPin className="h-10 w-10 mx-auto mb-2" />
            <p className="text-sm font-medium">Interactive Map</p>
            <p className="text-xs">Click on a county to select it</p>
          </div>
        </div>
      </div>

      {/* Recent Orders */}
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-semibold text-foreground flex items-center gap-1">
          ↻ Recent Orders
        </p>
        <Button size="sm" variant="outline" onClick={() => setPaymentOpen(true)}>
          <CreditCard className="h-3.5 w-3.5 mr-1" /> Add Payment Method
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50">
                <TableHead>Order #</TableHead>
                <TableHead>County</TableHead>
                <TableHead>List Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Download</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell colSpan={6} className="text-center py-12">
                  <p className="text-muted-foreground text-sm">
                    No orders yet. Select a county on the map to{" "}
                    <button className="text-primary underline hover:no-underline">get started!</button>
                  </p>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Payment Method Dialog */}
      <Dialog open={paymentOpen} onOpenChange={setPaymentOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <CreditCard className="h-5 w-5" /> Add Payment Method
            </DialogTitle>
          </DialogHeader>

          <div className="flex items-center gap-2 bg-destructive/10 text-destructive rounded-lg px-4 py-3 text-sm mb-4">
            <span>
              <strong>Payment Required:</strong> Add a payment method to place orders. A hold will be placed on your card when you place an order and charged upon delivery.
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-foreground">Name on Card</label>
              <Input placeholder="John Doe" className="mt-1" />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground">Billing Address</label>
              <Input placeholder="123 Main St" className="mt-1" />
            </div>
            <div>
              <label className="text-sm font-medium text-foreground">City</label>
              <Input placeholder="Los Angeles" className="mt-1" />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-sm font-medium text-foreground">State</label>
                <Input placeholder="CA" className="mt-1" />
              </div>
              <div>
                <label className="text-sm font-medium text-foreground">ZIP Code</label>
                <Input placeholder="90001" className="mt-1" />
              </div>
            </div>
          </div>

          <div className="mt-2">
            <label className="text-sm font-medium text-foreground">Country</label>
            <Input placeholder="US" className="mt-1 w-1/2" />
          </div>

          <div className="mt-2">
            <label className="text-sm font-medium text-foreground">Credit Card Details</label>
            <Input placeholder="Card number    MM / YY   CVC" className="mt-1" />
          </div>

          <div className="flex items-center gap-2 bg-destructive/10 text-destructive rounded-lg px-4 py-3 text-xs mt-2">
            <strong>Billing Terms:</strong> By adding your card, you agree that a hold will be placed on your card when you place an order. You will be charged when your order is delivered (delivery time varies based on order size).
          </div>

          <DialogFooter className="mt-4">
            <Button variant="outline" onClick={() => setPaymentOpen(false)}>Cancel</Button>
            <Button>
              <CreditCard className="h-4 w-4 mr-1" /> Save Payment Method
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CountyLeadLists;
