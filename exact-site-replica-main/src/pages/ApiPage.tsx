import Layout from "@/components/Layout";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Code2, Key, Zap, FileJson } from "lucide-react";

const ApiPage = () => {
  return (
    <Layout>
      <section className="page-header py-20 text-center">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground">Skip Tracing API</h1>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Integrate skip tracing directly into your CRM, application, or workflow with our powerful REST API. Pay-as-you-go with no minimums.
          </p>
        </div>
      </section>

      <section className="py-16">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: Key, title: "Instant API Key", desc: "Get your API key immediately after signup. No approval process needed." },
              { icon: Zap, title: "Fast Response", desc: "Average response time of 4 milliseconds per record lookup." },
              { icon: FileJson, title: "JSON Response", desc: "Clean, structured JSON responses with phone numbers and emails." },
              { icon: Code2, title: "Easy Integration", desc: "RESTful API with comprehensive documentation and Postman examples." },
            ].map((f) => (
              <div key={f.title} className="rounded-xl border bg-background p-6 text-center">
                <f.icon className="h-10 w-10 text-primary mx-auto mb-4" />
                <h3 className="font-semibold text-foreground">{f.title}</h3>
                <p className="text-sm text-muted-foreground mt-2">{f.desc}</p>
              </div>
            ))}
          </div>

          {/* Code Example */}
          <div className="mt-16 max-w-2xl mx-auto">
            <h2 className="section-title text-center mb-8">Quick Start Example</h2>
            <div className="rounded-xl bg-foreground p-6 overflow-x-auto">
              <pre className="text-sm text-primary-foreground font-mono">
{`curl -X POST https://api.tracerfy.com/v1/trace \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "address": "123 Main St",
    "city": "Los Angeles",
    "state": "CA",
    "first_name": "John",
    "last_name": "Doe"
  }'`}
              </pre>
            </div>
          </div>

          <div className="text-center mt-12">
            <Link to="/signup">
              <Button size="lg">Get Your API Key</Button>
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default ApiPage;
