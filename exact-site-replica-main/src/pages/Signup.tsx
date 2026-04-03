import Layout from "@/components/Layout";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

const Signup = () => {
  const [formData, setFormData] = useState({ 
    firstName: "", 
    lastName: "", 
    email: "", 
    password: "", 
    confirmPassword: "" 
  });
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!formData.firstName || !formData.lastName || !formData.email || !formData.password || !formData.confirmPassword) {
      toast.error("Please fill in all fields");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    if (formData.password.length < 8) {
      toast.error("Password must be at least 8 characters long");
      return;
    }

    setIsLoading(true);
    
    try {
      await register(
        formData.email, 
        formData.password, 
        formData.firstName, 
        formData.lastName
      );
      toast.success("Account created successfully!");
      navigate("/dashboard");
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || "Registration failed. Please try again.";
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <section className="py-16 md:py-24">
        <div className="container mx-auto px-4 max-w-md">
          <div className="text-center mb-8">
            <div className="h-12 w-12 rounded-xl bg-primary flex items-center justify-center mx-auto mb-4">
              <span className="text-primary-foreground font-bold text-xl">T</span>
            </div>
            <h1 className="text-3xl font-bold text-foreground">Create an Account</h1>
            <p className="text-muted-foreground mt-2">Start skip tracing in minutes</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border bg-background p-8 shadow-sm">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">First Name</Label>
                <Input id="firstName" placeholder="John" value={formData.firstName} onChange={handleChange("firstName")} required />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lastName">Last Name</Label>
                <Input id="lastName" placeholder="Doe" value={formData.lastName} onChange={handleChange("lastName")} required />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="you@example.com" value={formData.email} onChange={handleChange("email")} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" placeholder="••••••••" value={formData.password} onChange={handleChange("password")} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input id="confirmPassword" type="password" placeholder="••••••••" value={formData.confirmPassword} onChange={handleChange("confirmPassword")} required />
            </div>
            <Button type="submit" className="w-full" size="lg" disabled={isLoading}>
              {isLoading ? "Creating Account..." : "Create Account"}
            </Button>
            <p className="text-xs text-center text-muted-foreground">
              By signing up, you agree to our Terms of Service and Privacy Policy.
            </p>
          </form>

          <p className="text-center text-sm text-muted-foreground mt-6">
            Already have an account?{" "}
            <Link to="/login" className="text-primary hover:underline font-medium">Sign in</Link>
          </p>
        </div>
      </section>
    </Layout>
  );
};

export default Signup;
