import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowUpRight, List, MapPin, Phone, Calendar, DollarSign, Shield, Star, ChevronLeft, ChevronRight, Building2, Sun, Scale, FileSearch, Home, Megaphone } from "lucide-react";
import Layout from "@/components/Layout";
import dashboardMockup from "@/assets/dashboard-mockup.png";
import { useState } from "react";

const reviews = [
  {
    text: "Exceptional skip tracing service! The data quality has been outstanding for our real estate campaigns. We've successfully connected with hundreds of property owners. Highly recommend for anyone in the industry!",
    rating: 5,
  },
  {
    text: "We've relied on this platform for over a year now. Consistent 70%+ accuracy, fast turnaround, and great customer support. The pricing can't be beat anywhere else.",
    rating: 5,
  },
  {
    text: "Fast, accurate, and professional. The data helped us reach the right leads quickly. Will definitely continue using this service for all our campaigns.",
    rating: 5,
  },
  {
    text: "Best value in skip tracing. We use it regularly for cold calling and the results speak for themselves. Great price point with solid data quality.",
    rating: 5,
  },
];

const features = [
  { icon: MapPin, title: "High Accuracy", desc: "Our system delivers the best possible results to enhance your campaigns." },
  { icon: Phone, title: "24/7 Support", desc: "Reach our support team anytime at support@tracerfy.com." },
  { icon: Shield, title: "Ease of Use", desc: "A modern interface for stress-free, speedy skip tracing." },
  { icon: Calendar, title: "Fastest Turnaround", desc: "Results delivered in minutes with 4ms per lead processing." },
  { icon: DollarSign, title: "Competitive Pricing", desc: "Starting at just $0.02 per lead — best rates in the market." },
  { icon: Building2, title: "Multi-Industry Solutions", desc: "Serving real estate, debt collection, solar, insurance, and legal professionals." },
];

const industries = [
  { icon: Home, title: "Real Estate Professionals", desc: "Wholesalers, investors, agents, and property managers use our platform for off-market deals and lead generation." },
  { icon: Sun, title: "Solar & Home Services", desc: "Solar sales teams and home service companies locate homeowners for targeted outreach campaigns." },
  { icon: Scale, title: "Collections & Legal", desc: "Debt collection agencies and legal providers rely on our tool for recovery and document serving." },
  { icon: FileSearch, title: "Insurance & Investigations", desc: "Investigators use our platform for claims processing and verifying property ownership." },
  { icon: Building2, title: "Property Management", desc: "Landlords and managers streamline operations by finding tenants and tracking property owners." },
  { icon: Megaphone, title: "Marketing Agencies", desc: "Agencies running homeowner campaigns benefit from our affordable platform with labeled contact data." },
];

const Index = () => {
  const [reviewIndex, setReviewIndex] = useState(0);

  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-0 right-0 w-[60%] h-full rounded-bl-[100px] bg-gradient-to-br from-primary/20 via-primary/10 to-accent/30" />
        </div>
        <div className="container mx-auto px-4 py-16 md:py-24">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight text-foreground">
                Professional Skip Tracing for Real Estate &{" "}
                <span className="gradient-text">Lead Generation</span>
              </h1>
              <p className="mt-6 text-lg text-muted-foreground max-w-lg">
                Find property owners, locate homeowners, and generate real estate leads with our comprehensive skip tracing platform.{" "}
                <strong>Starting at just $0.02 per lead!</strong>
              </p>
              <span className="inline-block mt-2 px-3 py-1 bg-primary text-primary-foreground text-xs font-semibold rounded-full">
                US Properties Only
              </span>
              <div className="flex flex-wrap gap-4 mt-8">
                <Link to="/signup">
                  <Button size="lg" className="gap-2">
                    <ArrowUpRight className="h-4 w-4" /> Try it Out
                  </Button>
                </Link>
                <Link to="/features">
                  <Button variant="outline" size="lg" className="gap-2">
                    <List className="h-4 w-4" /> See All Features
                  </Button>
                </Link>
              </div>
            </div>
            <div className="flex justify-center">
              <img src={dashboardMockup} alt="Skip tracing dashboard interface" width={800} height={600} className="max-w-full h-auto" />
            </div>
          </div>
        </div>
      </section>

      {/* Reviews Section */}
      <section className="py-16 bg-muted/30">
        <div className="container mx-auto px-4 text-center">
          <h2 className="section-title">Trusted by Professionals Across Industries</h2>
          <p className="section-subtitle mt-2">See what our customers say about Tracerfy</p>

          <div className="mt-8 flex items-center justify-center gap-1">
            <span className="text-5xl font-bold text-foreground">5.0</span>
            <div className="flex text-warning ml-2">
              {[...Array(5)].map((_, i) => <Star key={i} className="h-6 w-6 fill-current" />)}
            </div>
          </div>
          <p className="text-sm text-muted-foreground mt-1">Excellent Rating on Google Reviews</p>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mt-8 max-w-md mx-auto">
            <div className="text-center">
              <p className="text-2xl font-bold text-foreground">5.0/5.0</p>
              <p className="text-xs text-muted-foreground">Perfect Score</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-foreground">100%</p>
              <p className="text-xs text-muted-foreground">Satisfaction</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-foreground">&lt; 1 Hour</p>
              <p className="text-xs text-muted-foreground">Response Time</p>
            </div>
          </div>

          {/* Review Carousel */}
          <div className="mt-10 max-w-2xl mx-auto relative">
            <div className="bg-background rounded-xl border p-8 shadow-sm">
              <div className="flex text-warning justify-center mb-4">
                {[...Array(5)].map((_, i) => <Star key={i} className="h-5 w-5 fill-current" />)}
              </div>
              <blockquote className="text-muted-foreground italic">
                "{reviews[reviewIndex].text}"
              </blockquote>
            </div>
            <div className="flex justify-center gap-4 mt-4">
              <button onClick={() => setReviewIndex((reviewIndex - 1 + reviews.length) % reviews.length)} className="p-2 rounded-full border hover:bg-muted">
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button onClick={() => setReviewIndex((reviewIndex + 1) % reviews.length)} className="p-2 rounded-full border hover:bg-muted">
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm font-semibold text-primary uppercase">Features</p>
          <h2 className="section-title mt-2">Why Choose Us for Bulk Skip Tracing?</h2>
          <p className="section-subtitle mt-2">The trusted platform for processing hundreds or thousands of properties at once.</p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
            {features.map((f) => (
              <div key={f.title} className="rounded-xl border bg-background p-6 text-left hover:shadow-md transition-shadow">
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <f.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="font-semibold text-lg text-foreground">{f.title}</h3>
                <p className="text-sm text-muted-foreground mt-2">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section className="py-16 bg-muted/30">
        <div className="container mx-auto px-4 text-center">
          <h2 className="section-title">How Does It Work?</h2>
          <p className="section-subtitle mt-2">Get started in 3 simple steps</p>

          <div className="grid md:grid-cols-3 gap-8 mt-12">
            {[
              { step: "1", title: "Upload Your List", desc: "Upload a CSV file with addresses, city, state, and owner names so our system can process the data." },
              { step: "2", title: "Select Your Columns", desc: "Map the columns for property address, city, state, and owner name from your uploaded CSV file." },
              { step: "3", title: "Get Results Fast", desc: "Receive your skip traced list via email within minutes — not hours. Export anytime from your dashboard." },
            ].map((s) => (
              <div key={s.step} className="rounded-xl border bg-background p-8 text-center">
                <div className="h-14 w-14 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-2xl font-bold mx-auto mb-4">
                  {s.step}
                </div>
                <h3 className="font-semibold text-lg text-foreground">{s.title}</h3>
                <p className="text-sm text-muted-foreground mt-2">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="section-title">Your Complete Skip Tracing Platform</h2>
            <p className="section-subtitle mt-2">
              Delivering professional skip tracing services with bulk capabilities, CRM integration, and 97% data coverage across US properties.
            </p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-8 text-center">
            <div>
              <p className="stat-value">10M+</p>
              <p className="text-sm text-muted-foreground mt-1">Monthly Traces Processed</p>
            </div>
            <div>
              <p className="stat-value">432+</p>
              <p className="text-sm text-muted-foreground mt-1">Clients Served</p>
            </div>
            <div>
              <p className="stat-value">97%</p>
              <p className="text-sm text-muted-foreground mt-1">Records Available</p>
            </div>
          </div>
        </div>
      </section>

      {/* Industries Section */}
      <section className="py-16 bg-muted/30">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm font-semibold text-primary uppercase">Industries</p>
          <h2 className="section-title mt-2">Industries We Serve</h2>
          <p className="section-subtitle mt-2">Comprehensive skip tracing solutions for professionals across multiple industries</p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
            {industries.map((ind) => (
              <div key={ind.title} className="rounded-xl border bg-background p-6 text-left hover:shadow-md transition-shadow">
                <ind.icon className="h-8 w-8 text-primary mb-3" />
                <h3 className="font-semibold text-foreground">{ind.title}</h3>
                <p className="text-sm text-muted-foreground mt-2">{ind.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust Stats */}
      <section className="py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="section-title">Trusted by Thousands of Professionals</h2>
          <p className="section-subtitle mt-2">Join over 1,000+ users who rely on Tracerfy for accurate, affordable skip tracing</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-12">
            <div><p className="stat-value">1,000+</p><p className="text-sm text-muted-foreground mt-1">Active Users</p></div>
            <div><p className="stat-value">10M+</p><p className="text-sm text-muted-foreground mt-1">Monthly Traces</p></div>
            <div><p className="stat-value">97%</p><p className="text-sm text-muted-foreground mt-1">Data Coverage</p></div>
            <div><p className="stat-value">$0.02</p><p className="text-sm text-muted-foreground mt-1">Per Lead</p></div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-primary">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-primary-foreground">Ready to Start Skip Tracing?</h2>
          <p className="text-primary-foreground/80 mt-4 text-lg max-w-xl mx-auto">
            Experience the industry's best rates with no contracts. Start with just 1,000 leads for only $20!
          </p>
          <div className="flex flex-wrap justify-center gap-4 mt-8">
            <Link to="/pricing">
              <Button size="lg" variant="secondary">View Pricing</Button>
            </Link>
            <Link to="/signup">
              <Button size="lg" variant="outline" className="border-primary-foreground text-primary-foreground hover:bg-primary-foreground/10">
                Start Free
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Index;
