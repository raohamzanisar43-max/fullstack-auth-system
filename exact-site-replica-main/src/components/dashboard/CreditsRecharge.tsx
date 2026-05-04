import { useState, useEffect } from "react";
import { Info, AlertTriangle, CreditCard, Check, Loader2, Sparkles, TrendingUp, Shield, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { useMockCredits } from "@/hooks/useMockCredits";
import { CreditPackage as APICreditPackage } from "@/types/credit";

interface CreditPackage {
  id: number;
  price: string;
  credits: string;
  numericCredits: number;
  numericPrice: number;
  popular?: boolean;
  bonus?: string;
}

const packages: CreditPackage[] = [
  { id: 1, price: "$20.00", credits: "1,000 credits", numericCredits: 1000, numericPrice: 20 },
  { id: 2, price: "$40.00", credits: "2,000 credits", numericCredits: 2000, numericPrice: 40 },
  { id: 3, price: "$100.00", credits: "5,000 credits", numericCredits: 5000, numericPrice: 100, popular: true, bonus: "+500 bonus" },
  { id: 4, price: "$200.00", credits: "10,000 credits", numericCredits: 10000, numericPrice: 200, bonus: "+1,000 bonus" },
  { id: 5, price: "$400.00", credits: "20,000 credits", numericCredits: 20000, numericPrice: 400, bonus: "+2,500 bonus" },
  { id: 6, price: "Custom", credits: "Enter amount", numericCredits: 0, numericPrice: 0 },
];

const features = [
  { name: "Property Address", icon: "🏠" },
  { name: "Mailing Address", icon: "📧" },
  { name: "Owner Names", icon: "👤" },
  { name: "Phone Numbers (up to 5)", icon: "📱" },
  { name: "Email Addresses (up to 5)", icon: "✉️" },
];

const CreditsRecharge = () => {
  const [selected, setSelected] = useState<number | null>(null);
  const [customAmount, setCustomAmount] = useState<string>("");
  const [discountCode, setDiscountCode] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [discountApplied, setDiscountApplied] = useState<{ percentage: number; code: string } | null>(null);
  
  const { balance, packages: apiPackages, isLoading, purchaseCredits, validateDiscountCode } = useMockCredits();

  // Convert API packages to UI packages format
  const packages = [
    ...(apiPackages.map(pkg => ({
      id: pkg.id,
      price: `$${pkg.price.toFixed(2)}`,
      credits: `${pkg.credits.toLocaleString()} credits`,
      numericCredits: pkg.credits + pkg.bonus_credits,
      numericPrice: pkg.price,
      popular: pkg.credits >= 5000,
      bonus: pkg.bonus_credits > 0 ? `+${pkg.bonus_credits.toLocaleString()} bonus` : undefined,
    })) || []),
    { id: 999, price: "Custom", credits: "Enter amount", numericCredits: 0, numericPrice: 0 },
  ];

  const currentBalance = balance ? {
    credits: balance.current_credits,
    value: balance.current_credits * balance.effective_rate,
  } : { credits: 0, value: 0 };

  const handlePackageSelect = (packageId: number) => {
    setSelected(packageId);
    if (packageId !== 999) { // Not custom
      setCustomAmount("");
    }
  };

  const handleCustomAmountChange = (value: string) => {
    setCustomAmount(value);
    if (value) {
      setSelected(999);
    }
  };

  const applyDiscountCode = async () => {
    if (!discountCode.trim()) return;

    try {
      const result = await validateDiscountCode(discountCode);
      
      if (result.valid && result.percentage) {
        setDiscountApplied({ percentage: result.percentage, code: discountCode });
      } else {
        setDiscountApplied(null);
      }
    } catch (error) {
      setDiscountApplied(null);
    }
  };

  const calculateTotal = () => {
    if (selected === null) return 0;
    
    const selectedPackage = packages.find(p => p.id === selected);
    if (!selectedPackage) return 0;
    
    let total = selectedPackage.numericPrice;
    
    if (selected === 999 && customAmount) {
      const credits = parseInt(customAmount);
      if (!isNaN(credits) && credits > 0) {
        total = credits * 0.02;
      }
    }
    
    if (discountApplied) {
      total = total * (1 - discountApplied.percentage / 100);
    }
    
    return total;
  };

  const calculateCredits = () => {
    if (selected === null) return 0;
    
    const selectedPackage = packages.find(p => p.id === selected);
    if (!selectedPackage) return 0;
    
    let credits = selectedPackage.numericCredits;
    
    if (selected === 999 && customAmount) {
      credits = parseInt(customAmount) || 0;
    }
    
    // Add bonus credits (already included in numericCredits from API)
    if (selectedPackage.bonus && selected !== 999) {
      const bonusMatch = selectedPackage.bonus.match(/\+(\d+)/);
      if (bonusMatch) {
        credits += parseInt(bonusMatch[1]);
      }
    }
    
    return credits;
  };

  const handlePurchase = async () => {
    if (selected === null) {
      toast.error('Please select a credit package');
      return;
    }

    if (selected === 999 && (!customAmount || parseInt(customAmount) <= 0)) {
      toast.error('Please enter a valid custom amount');
      return;
    }

    setIsProcessing(true);

    try {
      let packageId = selected;
      let paymentMethodId = 'pm_card_visa'; // Default payment method
      
      // For custom packages, we'd need to create a custom package or handle differently
      if (selected === 999) {
        // For now, treat custom as the smallest package multiplied
        const credits = parseInt(customAmount);
        if (credits > 0) {
          toast.info('Custom packages will be available soon. Please select a predefined package.');
          return;
        }
      }
      
      await purchaseCredits(packageId, paymentMethodId);
      
      // Reset form
      setSelected(null);
      setCustomAmount("");
      setDiscountCode("");
      setDiscountApplied(null);
      
    } catch (error) {
      // Error is already handled by the hook
      console.error('Purchase failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-6 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-lg font-medium text-muted-foreground">Loading credit packages...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50/30 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-100 rounded-lg">
              <CreditCard className="h-6 w-6 text-blue-600" />
            </div>
            <h1 className="text-3xl font-bold text-foreground">Purchase Credits</h1>
          </div>
          <p className="text-muted-foreground">
            One credit balance for all tracing services and any form of upload. Web or API
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm mb-1">Current Balance</p>
                  <p className="text-2xl font-bold">{currentBalance.credits.toLocaleString()}</p>
                  <p className="text-blue-100 text-sm">${currentBalance.value.toFixed(2)}</p>
                </div>
                <div className="p-3 bg-white/20 rounded-full">
                  <TrendingUp className="h-6 w-6" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100 text-sm mb-1">Credit Rate</p>
                  <p className="text-2xl font-bold">$0.02</p>
                  <p className="text-green-100 text-sm">per credit</p>
                </div>
                <div className="p-3 bg-white/20 rounded-full">
                  <Zap className="h-6 w-6" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100 text-sm mb-1">Total Value</p>
                  <p className="text-2xl font-bold">{calculateCredits().toLocaleString()}</p>
                  <p className="text-purple-100 text-sm">credits</p>
                </div>
                <div className="p-3 bg-white/20 rounded-full">
                  <Sparkles className="h-6 w-6" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-orange-100 text-sm mb-1">Total Cost</p>
                  <p className="text-2xl font-bold">${calculateTotal().toFixed(2)}</p>
                  {discountApplied && (
                    <p className="text-orange-100 text-sm">{discountApplied.percentage}% off</p>
                  )}
                </div>
                <div className="p-3 bg-white/20 rounded-full">
                  <Shield className="h-6 w-6" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCard className="h-5 w-5" />
                  Purchase Credits
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6 space-y-6">
                <div>
                  <p className="text-sm font-semibold text-foreground mb-4 flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-yellow-500" />
                    Select Credit Package
                  </p>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {packages.map((pkg) => (
                      <div key={pkg.id} className="relative">
                        {pkg.popular && (
                          <Badge className="absolute -top-2 -right-2 z-10 bg-gradient-to-r from-yellow-400 to-orange-500 text-white text-xs px-2 py-1">
                            Popular
                          </Badge>
                        )}
                        <button
                          onClick={() => handlePackageSelect(pkg.id)}
                          className={`relative w-full border rounded-xl p-4 text-center transition-all duration-200 hover:scale-105 ${
                            selected === pkg.id
                              ? "border-blue-500 bg-blue-50 shadow-md ring-2 ring-blue-500/20"
                              : "border-border hover:border-blue-300 hover:shadow-sm"
                          }`}
                        >
                          {pkg.bonus && (
                            <div className="absolute -top-1 -right-1 bg-green-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                              +
                            </div>
                          )}
                          <p className="font-bold text-lg text-primary">{pkg.price}</p>
                          <p className="text-xs text-muted-foreground mb-1">{pkg.credits}</p>
                          {pkg.bonus && (
                            <p className="text-xs text-green-600 font-semibold">{pkg.bonus}</p>
                          )}
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                {selected === 999 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-foreground">Enter Custom Amount</p>
                    <Input
                      type="number"
                      placeholder="Enter number of credits"
                      value={customAmount}
                      onChange={(e) => handleCustomAmountChange(e.target.value)}
                      min="100"
                      step="100"
                    />
                    <p className="text-xs text-muted-foreground">Minimum 100 credits • $0.02 per credit</p>
                  </div>
                )}

                <div className="space-y-3">
                  <p className="text-sm font-medium text-foreground flex items-center gap-2">
                    Discount Code <span className="text-muted-foreground font-normal">(optional)</span>
                  </p>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Enter discount code"
                      value={discountCode}
                      onChange={(e) => setDiscountCode(e.target.value)}
                      className="flex-1"
                    />
                    <Button 
                      variant="outline" 
                      onClick={applyDiscountCode}
                      disabled={!discountCode.trim() || discountApplied !== null}
                    >
                      Apply
                    </Button>
                  </div>
                  {discountApplied && (
                    <Alert className="bg-green-50 border-green-200">
                      <Check className="h-4 w-4 text-green-600" />
                      <AlertDescription className="text-green-800">
                        Discount code {discountApplied.code} applied! {discountApplied.percentage}% off your purchase.
                      </AlertDescription>
                    </Alert>
                  )}
                </div>

                <div className="space-y-3">
                  <Alert className="bg-blue-50 border-blue-200">
                    <Info className="h-4 w-4 text-blue-600" />
                    <AlertDescription className="text-blue-800">
                      <strong>Rate:</strong> 1 credit = $0.0200 • Use credits for any service at variable rates
                    </AlertDescription>
                  </Alert>

                  <Alert className="bg-amber-50 border-amber-200">
                    <AlertTriangle className="h-4 w-4 text-amber-600" />
                    <AlertDescription className="text-amber-800">
                      <strong>Important:</strong> Credits are not refundable once purchased
                    </AlertDescription>
                  </Alert>
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Total Credits</p>
                    <p className="text-2xl font-bold text-primary">{calculateCredits().toLocaleString()}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Total Amount</p>
                    <p className="text-2xl font-bold text-primary">${calculateTotal().toFixed(2)}</p>
                    {discountApplied && (
                      <p className="text-xs text-green-600">Save ${((calculateTotal() / (1 - discountApplied.percentage / 100)) * discountApplied.percentage / 100).toFixed(2)}</p>
                    )}
                  </div>
                </div>

                <Button 
                  className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold py-3 transition-all duration-200" 
                  onClick={handlePurchase}
                  disabled={selected === null || isProcessing}
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Processing Payment...
                    </>
                  ) : selected !== null ? (
                    `Purchase ${calculateCredits().toLocaleString()} Credits - $${calculateTotal().toFixed(2)}`
                  ) : (
                    "Select a package to continue"
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-1">
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Check className="h-5 w-5 text-green-600" />
                  Service Features
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6 space-y-4">
                <div className="space-y-0">
                  <div className="flex justify-between items-center py-3 border-b">
                    <span className="text-sm font-semibold text-primary">Feature</span>
                    <span className="text-sm font-semibold text-primary">Included</span>
                  </div>
                  <div className="flex justify-between items-center py-3 border-b">
                    <span className="text-sm text-foreground">Cost per Lead</span>
                    <Badge variant="secondary" className="font-semibold">$0.0200</Badge>
                  </div>
                  {features.map((feature, index) => (
                    <div key={index} className="flex justify-between items-center py-3 border-b last:border-b-0">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{feature.icon}</span>
                        <span className="text-sm text-foreground">{feature.name}</span>
                      </div>
                      <div className="p-1 bg-green-100 rounded-full">
                        <Check className="h-3 w-3 text-green-600" />
                      </div>
                    </div>
                  ))}
                </div>

                <Separator />

                <div className="space-y-3">
                  <p className="text-sm font-semibold text-foreground">Example Usage:</p>
                  <div className="bg-slate-50 rounded-lg p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">Skip Trace Service</span>
                      <Badge variant="outline" className="text-xs">Popular</Badge>
                    </div>
                    <p className="text-sm font-bold text-primary">100 leads</p>
                    <p className="text-xs text-muted-foreground">100 credits • $2.00</p>
                  </div>
                  
                  <div className="bg-slate-50 rounded-lg p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">Bulk Upload</span>
                      <Badge variant="outline" className="text-xs">API</Badge>
                    </div>
                    <p className="text-sm font-bold text-primary">1,000 records</p>
                    <p className="text-xs text-muted-foreground">1,000 credits • $20.00</p>
                  </div>
                </div>

                <Alert className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
                  <Sparkles className="h-4 w-4 text-blue-600" />
                  <AlertDescription className="text-blue-800 text-xs">
                    <strong>Pro Tip:</strong> Larger packages offer better value with bonus credits included!
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreditsRecharge;
