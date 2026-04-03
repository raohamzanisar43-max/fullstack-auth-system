import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  BarChart3, Grid3X3, Search, Crosshair, Scissors, List, FileText,
  CreditCard, Receipt, Building2, MapPin, Menu, User, ChevronRight
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow
} from "@/components/ui/table";
import { apiClient, DashboardStats, CreditBalance } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import BulkListTrace from "@/components/dashboard/BulkListTrace";
import ManualSearches from "@/components/dashboard/ManualSearches";
import MyTraces from "@/components/dashboard/MyTraces";
import DncScrub from "@/components/dashboard/DncScrub";
import MyDncScrubs from "@/components/dashboard/MyDncScrubs";
import CreditsRecharge from "@/components/dashboard/CreditsRecharge";
import TransactionReceipts from "@/components/dashboard/TransactionReceipts";
import CountyLeadLists from "@/components/dashboard/CountyLeadLists";
import { toast } from "sonner";

const sidebarItems = [
  { label: "Analytics", icon: BarChart3, path: "/dashboard" },
  { label: "Bulk List Trace", icon: Grid3X3, path: "/dashboard" },
  { label: "Manual Searches", icon: Search, path: "/dashboard", badge: "New" },
  { label: "My Traces", icon: Crosshair, path: "/dashboard" },
  { label: "DNC Scrub", icon: Scissors, path: "/dashboard" },
  { label: "My DNC Scrubs", icon: List, path: "/dashboard" },
  { label: "API Docs", icon: FileText, path: "/dashboard", badge: "Updates" },
  { label: "Credits Recharge", icon: CreditCard, path: "/dashboard" },
  { label: "Transaction Receipts", icon: Receipt, path: "/dashboard" },
  { label: "Business Skip Tracing", icon: Building2, path: "/dashboard" },
  { label: "County Lead Lists", icon: MapPin, path: "/dashboard", badge: "New" },
];

const Dashboard = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeItem, setActiveItem] = useState("Analytics");
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [creditBalance, setCreditBalance] = useState<CreditBalance | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { user, logout } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const [stats, credits] = await Promise.all([
          apiClient.getDashboardStats(),
          apiClient.getCreditBalance()
        ]);
        setDashboardStats(stats);
        setCreditBalance(credits);
      } catch (error: any) {
        console.error('Failed to fetch dashboard data:', error);
        toast.error('Failed to load dashboard data');
        if (error.response?.status === 401) {
          logout();
        }
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      fetchData();
    }
  }, [user, logout]);

  const credits = creditBalance?.credits || 0;
  const creditRate = creditBalance?.credit_rate || 0.02;

  return (
    <div className="min-h-screen flex bg-muted/30">
      {/* Loading State */}
      {isLoading && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex items-center gap-3">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
            <span>Loading dashboard...</span>
          </div>
        </div>
      )}

      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-0 overflow-hidden"
        } transition-all duration-300 bg-[hsl(222,47%,16%)] text-white flex-shrink-0`}
      >
        <div className="p-4">
          <Link to="/" className="flex items-center gap-2 mb-8">
            <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-lg">t</span>
            </div>
            <span className="font-bold text-xl">Tracerfy</span>
          </Link>

          <nav className="space-y-1">
            {sidebarItems.map((item) => (
              <button
                key={item.label}
                onClick={() => setActiveItem(item.label)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  activeItem === item.label
                    ? "bg-white/10 text-white"
                    : "text-white/70 hover:bg-white/5 hover:text-white"
                }`}
              >
                <item.icon className="h-4 w-4 flex-shrink-0" />
                <span>{item.label}</span>
                {item.badge && (
                  <Badge className="ml-auto bg-primary text-primary-foreground text-[10px] px-1.5 py-0">
                    {item.badge}
                  </Badge>
                )}
              </button>
            ))}
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="h-14 border-b bg-background flex items-center justify-between px-4">
          <button onClick={() => setSidebarOpen(!sidebarOpen)}>
            <Menu className="h-5 w-5 text-muted-foreground" />
          </button>
          <div className="flex items-center gap-3">
            <Badge variant="outline" className="bg-primary text-primary-foreground border-0 text-xs">
              {credits} Credits available
            </Badge>
            <Badge variant="outline" className="text-xs">
              1 credit = ${creditRate.toFixed(4)}
            </Badge>
            <User className="h-5 w-5 text-muted-foreground" />
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="flex-1 p-6 overflow-auto">
          {activeItem === "Bulk List Trace" ? (
            <BulkListTrace />
          ) : activeItem === "Manual Searches" ? (
            <ManualSearches />
          ) : activeItem === "My Traces" ? (
            <MyTraces />
          ) : activeItem === "DNC Scrub" ? (
            <DncScrub />
          ) : activeItem === "My DNC Scrubs" ? (
            <MyDncScrubs />
          ) : activeItem === "Credits Recharge" ? (
            <CreditsRecharge />
          ) : activeItem === "Transaction Receipts" ? (
            <TransactionReceipts />
          ) : activeItem === "County Lead Lists" ? (
            <CountyLeadLists />
          ) : (
            <>
              <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
                <Button>Buy Credits</Button>
              </div>

              <Card className="mb-6">
                <CardContent className="p-6 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center">
                      <CreditCard className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Credit Balance</p>
                      <p className="text-2xl font-bold text-foreground">{credits} credits</p>
                      <p className="text-sm text-muted-foreground">${(credits * creditRate).toFixed(2)}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Use for any service:</p>
                    <p className="text-sm text-foreground">
                      <span className="font-bold">{credits}</span> normal traces OR{" "}
                      <span className="font-bold">{Math.floor(credits / 3)}</span> enhanced traces
                    </p>
                  </div>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                {[
                  { label: "Lists Uploaded", value: dashboardStats?.lists_uploaded || 0, icon: Crosshair },
                  { label: "Properties Uploaded", value: dashboardStats?.properties_uploaded || 0, icon: Building2 },
                  { label: "Successful Traces", value: dashboardStats?.successful_traces || 0, icon: ChevronRight },
                ].map((stat) => (
                  <Card key={stat.label}>
                    <CardContent className="p-6 flex items-center gap-4">
                      <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                        <stat.icon className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">{stat.label}</p>
                        <p className="text-2xl font-bold text-foreground">{stat.value.toLocaleString()}</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {[
                  { label: "Total Credits Used", value: dashboardStats?.total_credits_used || 0, icon: FileText },
                  { label: "Account's Effective Rate", value: `$${(dashboardStats?.effective_rate || 0.02).toFixed(4)} per credit`, icon: Receipt },
                ].map((stat) => (
                  <Card key={stat.label}>
                    <CardContent className="p-6 flex items-center gap-4">
                      <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                        <stat.icon className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">{stat.label}</p>
                        <p className="text-2xl font-bold text-foreground">{typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <Card>
                <CardContent className="p-6">
                  <h2 className="text-lg font-semibold text-foreground mb-4">Usage Breakdown</h2>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Trace Type</TableHead>
                        <TableHead>Queues</TableHead>
                        <TableHead>Credits Used</TableHead>
                        <TableHead>Rate</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow>
                        <TableCell className="flex items-center gap-2">
                          <span className="h-2 w-2 rounded-full bg-emerald-500" />
                          Normal
                        </TableCell>
                        <TableCell>{dashboardStats?.usage_breakdown?.normal?.queues || 0}</TableCell>
                        <TableCell>{dashboardStats?.usage_breakdown?.normal?.credits_used || 0}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-emerald-600 border-emerald-200 bg-emerald-50 text-xs">
                            1 credit/lead
                          </Badge>
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell className="flex items-center gap-2">
                          <span className="h-2 w-2 rounded-full bg-blue-500" />
                          Enhanced
                        </TableCell>
                        <TableCell>{dashboardStats?.usage_breakdown?.enhanced?.queues || 0}</TableCell>
                        <TableCell>{dashboardStats?.usage_breakdown?.enhanced?.credits_used || 0}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-blue-600 border-blue-200 bg-blue-50 text-xs">
                            3 credits/lead
                          </Badge>
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
