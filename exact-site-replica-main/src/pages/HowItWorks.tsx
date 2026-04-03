import Layout from "@/components/Layout";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

const HowItWorks = () => {
  const steps = [
    { step: "1", title: "Create Your Account", desc: "Sign up for free and get instant access to the platform. No credit card required to get started." },
    { step: "2", title: "Upload Your CSV File", desc: "Upload a CSV file containing property addresses, city, state, and owner first and last name. Minimum 1,000 records for bulk processing." },
    { step: "3", title: "Map Your Columns", desc: "Our system auto-detects your columns. Simply confirm the mapping for property address, city, state, and owner name fields." },
    { step: "4", title: "Submit & Pay", desc: "Review your list, confirm the trace, and pay. You only pay for successful matches at $0.02 per credit." },
    { step: "5", title: "Get Results in Minutes", desc: "Your skip traced list with phone numbers and emails is delivered to your inbox and dashboard within minutes." },
    { step: "6", title: "Export & Take Action", desc: "Download your results, import into your CRM, and start reaching out to property owners immediately." },
  ];

  return (
    <Layout>
      <section className="page-header py-20 text-center">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground">How Tracerfy Works</h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            From upload to results in minutes. Our streamlined process makes skip tracing effortless.
          </p>
        </div>
      </section>

      <section className="py-16">
        <div className="container mx-auto px-4 max-w-3xl">
          <div className="space-y-8">
            {steps.map((s) => (
              <div key={s.step} className="flex gap-6 items-start">
                <div className="h-12 w-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl font-bold shrink-0">
                  {s.step}
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-foreground">{s.title}</h3>
                  <p className="text-muted-foreground mt-1">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center mt-16">
            <Link to="/signup">
              <Button size="lg">Get Started Now</Button>
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default HowItWorks;
