import Layout from "@/components/Layout";
import { Check, Zap, Target, DollarSign, FileUp, Link2, BarChart3, Shield, Globe, Clock } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

const featureCards = [
  {
    icon: Zap, title: "Lightning-Fast Processing",
    items: ["Process leads in just 4 seconds per record", "Handle millions of traces per month without delays", "Scalable infrastructure trusted by 1,000+ active users"],
    tagline: "Close deals faster with instant, bulk data results.",
  },
  {
    icon: Target, title: "Accuracy You Can Trust",
    items: ["75%–90% match rate across every batch", "97% U.S. residential property coverage", "Consistently updated data sources for precision"],
    tagline: "Skip tracing results you can count on, every time.",
  },
  {
    icon: DollarSign, title: "Affordable Pricing at Scale",
    items: ["Only $0.02 per lead — industry-leading cost", "No hidden fees or complicated credit systems", "API: pay-as-you-go, no minimums"],
    tagline: "Enterprise-level data at startup-friendly pricing.",
  },
  {
    icon: FileUp, title: "Simple Bulk Uploads",
    items: ["Upload your CSV list in seconds", "Auto-map your columns for fast setup", "Results delivered to your dashboard and inbox"],
    tagline: "Skip tracing made easy, even for non-technical users.",
  },
  {
    icon: Link2, title: "Powerful API Integration",
    items: ["Instant API key access", "Postman walkthroughs for easy setup", "Flexible pay-per-response model"],
    tagline: "Integrate skip tracing directly into your CRM or workflow.",
  },
  {
    icon: BarChart3, title: "Real-Time Analytics",
    items: ["Track match rates and performance", "Monitor credit usage and ROI", "Detailed reporting dashboard"],
    tagline: "Full visibility into your skip tracing performance.",
  },
  {
    icon: Shield, title: "DNC Scrubbing",
    items: ["Federal and State DNC databases", "DMA and TCPA Litigator databases", "Available via web or API at 1 credit per phone"],
    tagline: "Stay compliant with comprehensive DNC scrubbing.",
  },
  {
    icon: Globe, title: "County Lead Lists",
    items: ["32 list types across US counties", "Tax delinquent, foreclosure, vacant, probate leads", "Pulled fresh when you order — not cached data"],
    tagline: "Fresh leads direct from county records.",
  },
  {
    icon: Clock, title: "24/7 Platform Access",
    items: ["Upload and process anytime, anywhere", "Email delivery of results within minutes", "Dedicated support team available round the clock"],
    tagline: "Your skip tracing platform never sleeps.",
  },
];

const Features = () => {
  return (
    <Layout>
      {/* Hero */}
      <section className="page-header py-20 text-center">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground">Tracerfy Features</h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            The <span className="text-warning font-semibold">fastest, most affordable, and accurate</span> skip tracing software built for real estate investors, debt collection agencies, legal teams, and more.
          </p>
          <p className="mt-2 text-muted-foreground max-w-2xl mx-auto">
            Whether you're uploading thousands of records or connecting via our API, Tracerfy delivers verified homeowner data in <span className="text-warning font-semibold">milliseconds</span>.
          </p>
          <div className="flex flex-wrap justify-center gap-4 mt-8">
            <Link to="/signup">
              <Button size="lg">Start Your First Upload</Button>
            </Link>
            <Link to="/api">
              <Button variant="outline" size="lg">Learn About Our API</Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Feature Cards */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featureCards.map((f) => (
              <div key={f.title} className="rounded-xl border bg-background p-6 hover:shadow-lg transition-shadow">
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <f.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="font-semibold text-lg text-foreground mb-3">{f.title}</h3>
                <ul className="space-y-2">
                  {f.items.map((item) => (
                    <li key={item} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <Check className="h-4 w-4 text-primary mt-0.5 shrink-0" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
                <p className="mt-4 text-sm italic text-muted-foreground">{f.tagline}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 bg-primary">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-primary-foreground">Ready to Get Started?</h2>
          <p className="text-primary-foreground/80 mt-4 max-w-lg mx-auto">
            Join thousands of professionals who trust Tracerfy for their skip tracing needs.
          </p>
          <Link to="/signup">
            <Button size="lg" variant="secondary" className="mt-8">Create Free Account</Button>
          </Link>
        </div>
      </section>
    </Layout>
  );
};

export default Features;
