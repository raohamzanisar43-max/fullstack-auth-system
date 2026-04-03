import { Link, useLocation } from "react-router-dom";
import { useState } from "react";
import { Menu, X, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";

const Navbar = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [servicesOpen, setServicesOpen] = useState(false);
  const location = useLocation();

  const navLinks = [
    { label: "HOME", path: "/" },
    { label: "HOW IT WORKS", path: "/how-it-works" },
    { label: "API", path: "/api" },
    { label: "PRICING", path: "/pricing" },
    { label: "DASHBOARD", path: "/dashboard" },
  ];

  const serviceLinks = [
    { label: "Skip Tracing (Residential)", path: "/features" },
    { label: "Business Skip Tracing", path: "/features" },
    { label: "County Lead Lists", path: "/features" },
    { label: "Reverse Email Append", path: "/features" },
    { label: "Reverse Phone Append", path: "/features" },
    { label: "Reverse Name Append", path: "/features" },
    { label: "DNC Scrubbing", path: "/features" },
    { label: "Bulk Data", path: "/features" },
  ];

  return (
    <nav className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link to="/" className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-lg">T</span>
          </div>
          <span className="font-bold text-xl text-foreground hidden sm:inline">Tracerfy</span>
        </Link>

        {/* Desktop Nav */}
        <div className="hidden lg:flex items-center gap-1">
          {navLinks.slice(0, 1).map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`px-4 py-2 text-sm font-medium transition-colors hover:text-primary ${
                location.pathname === link.path ? "text-primary" : "text-muted-foreground"
              }`}
            >
              {link.label}
            </Link>
          ))}

          {/* Services Dropdown */}
          <div className="relative" onMouseEnter={() => setServicesOpen(true)} onMouseLeave={() => setServicesOpen(false)}>
            <button className="flex items-center gap-1 px-4 py-2 text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
              SERVICES <ChevronDown className="h-3 w-3" />
            </button>
            {servicesOpen && (
              <div className="absolute top-full left-0 mt-1 w-48 rounded-md border bg-background shadow-lg py-1">
                {serviceLinks.map((link) => (
                  <Link key={link.label} to={link.path} className="block px-4 py-2 text-sm text-muted-foreground hover:bg-muted hover:text-primary">
                    {link.label}
                  </Link>
                ))}
              </div>
            )}
          </div>

          {navLinks.slice(1).map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`px-4 py-2 text-sm font-medium transition-colors hover:text-primary ${
                location.pathname === link.path ? "text-primary" : "text-muted-foreground"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </div>

        <div className="hidden lg:flex items-center gap-3">
          <Link to="/login">
            <Button variant="ghost" size="sm">LOGIN</Button>
          </Link>
          <Link to="/signup">
            <Button size="sm">SIGN UP</Button>
          </Link>
        </div>

        {/* Mobile toggle */}
        <button className="lg:hidden" onClick={() => setMobileOpen(!mobileOpen)}>
          {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileOpen && (
        <div className="lg:hidden border-t bg-background px-4 py-4 space-y-2">
          {navLinks.map((link) => (
            <Link key={link.path} to={link.path} onClick={() => setMobileOpen(false)} className="block py-2 text-sm font-medium text-muted-foreground hover:text-primary">
              {link.label}
            </Link>
          ))}
          <Link to="/features" onClick={() => setMobileOpen(false)} className="block py-2 text-sm font-medium text-muted-foreground hover:text-primary">
            FEATURES
          </Link>
          <div className="flex gap-2 pt-2">
            <Link to="/login" className="flex-1"><Button variant="outline" className="w-full" size="sm">LOGIN</Button></Link>
            <Link to="/signup" className="flex-1"><Button className="w-full" size="sm">SIGN UP</Button></Link>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
