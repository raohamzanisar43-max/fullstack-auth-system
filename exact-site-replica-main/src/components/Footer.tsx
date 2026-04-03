import { Link } from "react-router-dom";

const Footer = () => {
  return (
    <footer className="border-t bg-muted/50">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-lg">T</span>
              </div>
              <span className="font-bold text-xl">Tracerfy</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Professional skip tracing platform for real estate professionals, debt collectors, and more.
            </p>
          </div>

          <div>
            <h4 className="font-semibold mb-3">Services</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link to="/features" className="hover:text-primary">Skip Tracing</Link></li>
              <li><Link to="/features" className="hover:text-primary">DNC Scrubbing</Link></li>
              <li><Link to="/features" className="hover:text-primary">County Lead Lists</Link></li>
              <li><Link to="/features" className="hover:text-primary">API Integration</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-3">Company</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link to="/pricing" className="hover:text-primary">Pricing</Link></li>
              <li><Link to="/features" className="hover:text-primary">Features</Link></li>
              <li><Link to="/how-it-works" className="hover:text-primary">How It Works</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold mb-3">Support</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="mailto:support@tracerfy.com" className="hover:text-primary">support@tracerfy.com</a></li>
              <li><Link to="/login" className="hover:text-primary">Login</Link></li>
              <li><Link to="/signup" className="hover:text-primary">Sign Up</Link></li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t text-center text-sm text-muted-foreground">
          © {new Date().getFullYear()} Tracerfy. All rights reserved.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
