import Layout from "@/components/Layout";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Check, Database, CheckCircle, Phone, DollarSign } from "lucide-react";

const plans = [
  {
    label: "MOST POPULAR",
    name: "Normal Trace",
    credits: "1 Credit",
    per: "per successful result",
    price: "Each credit is 2 cents",
    desc: "Perfect for basic contact information — phones and emails. Ideal for real estate professionals and lead generation.",
    features: [
      "Unlimited Uploads",
      "Bulk Processing",
      "Lead Storage",
      "Email Delivery",
      "Real-Time Analytics",
      "Property Owner Data — Phones & Emails",
      "24/7 Support",
    ],
    highlight: true,
  },
  {
    label: "NEW",
    name: "Advanced Trace",
    credits: "2 Credits",
    per: "per successful result",
    price: "Each credit is 2 cents ($0.04/result)",
    desc: "Don't have the property owner's name? Upload just addresses and we'll identify the owner and return their contact info.",
    features: [
      "Everything in Normal Trace",
      "Owner Name Identification",
      "Address-Only Processing",
      "Enhanced Data Matching",
      "Priority Processing",
      "Advanced Analytics",
      "Dedicated Support",
    ],
    highlight: false,
  },
];

const stats = [
  { icon: Database, value: "10M+", label: "Monthly Records Processed" },
  { icon: CheckCircle, value: "75-90%", label: "Industry-Leading Match Rate" },
  { icon: Phone, value: "8+5", label: "Phones + Emails Per Match" },
  { icon: DollarSign, value: "$0.02", label: "Per Credit" },
];

const Pricing = () => {
  return (
    <Layout>
      {/* Hero */}
      <section className="page-header py-20 text-center">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground">
            Enterprise Data Solutions: Pricing Built for Scale
          </h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Process millions of records monthly with enterprise-grade skip tracing and data enrichment. Trusted by high-volume data operations processing 10M+ records.
          </p>
          <div className="mt-6 inline-flex items-center gap-2 rounded-full border bg-background px-4 py-2 text-sm text-muted-foreground">
            HOME <span>›</span> <span className="font-medium text-primary">PRICING</span>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((s) => (
              <div key={s.label} className="rounded-xl border bg-background p-6 text-center">
                <s.icon className="h-8 w-8 mx-auto mb-3 text-primary" />
                <p className="text-2xl md:text-3xl font-bold text-primary">{s.value}</p>
                <p className="text-sm text-muted-foreground mt-1">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="section-title">Simple, Transparent Pricing</h2>
          <p className="section-subtitle mt-2">Choose the right plan for your volume. Flexible skip tracing with competitive per-lead pricing.</p>

          <div className="grid md:grid-cols-2 gap-8 mt-12 max-w-4xl mx-auto">
            {plans.map((plan) => (
              <div key={plan.name} className={`rounded-2xl border-2 p-8 text-left ${plan.highlight ? "border-primary shadow-lg" : "border-border"}`}>
                <span className={`inline-block px-3 py-1 text-xs font-semibold rounded-full mb-4 ${plan.highlight ? "bg-primary text-primary-foreground" : "bg-accent text-accent-foreground"}`}>
                  {plan.label}
                </span>
                <h3 className="text-xl font-semibold text-foreground">{plan.name}</h3>
                <p className="text-4xl font-bold text-primary mt-2">{plan.credits}</p>
                <p className="text-sm text-muted-foreground">{plan.per}</p>
                <p className="text-sm text-muted-foreground mt-1">{plan.price}</p>
                <p className="text-sm text-muted-foreground mt-4">{plan.desc}</p>

                <ul className="mt-6 space-y-3">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm text-foreground">
                      <Check className="h-4 w-4 text-primary shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>

                <Link to="/signup">
                  <Button className="w-full mt-8" variant={plan.highlight ? "default" : "outline"}>
                    Start Skip Tracing Now
                  </Button>
                </Link>
                <p className="text-xs text-muted-foreground text-center mt-2">No credit card required to start</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 bg-primary">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-primary-foreground">Start Your Free Trial Today</h2>
          <p className="text-primary-foreground/80 mt-4 max-w-lg mx-auto">
            No contracts, no hidden fees. Pay only for successful matches.
          </p>
          <Link to="/signup">
            <Button size="lg" variant="secondary" className="mt-8">Get Started Free</Button>
          </Link>
        </div>
      </section>
    </Layout>
  );
};

export default Pricing;
