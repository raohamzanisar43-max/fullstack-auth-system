import { Receipt, CreditCard } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const TransactionReceipts = () => {
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-foreground">Transaction History</h1>
        <Button variant="outline" onClick={() => {}}>
          ← Back to Dashboard
        </Button>
      </div>

      <Card>
        <CardContent className="p-12 flex flex-col items-center justify-center text-center">
          <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
            <Receipt className="h-8 w-8 text-primary" />
          </div>
          <h2 className="text-xl font-semibold text-foreground mb-2">No Transactions Yet</h2>
          <p className="text-sm text-muted-foreground mb-4">
            You haven't made any purchases yet. Get started by buying credits!
          </p>
          <Button>
            <CreditCard className="h-4 w-4 mr-2" />
            Buy Credits
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default TransactionReceipts;
