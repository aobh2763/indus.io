import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { Factory } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { authService } from "../../lib/api";

export default function Register() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await authService.register(name, email, password);
      // Auto-login after register
      const res = await authService.login(email, password);
      localStorage.setItem("indus_token", res.data.access_token);
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black p-4">
      <div className="w-full max-w-[360px] space-y-6">
        <div className="flex flex-col items-center space-y-2 text-center">
          <div className="h-10 w-10 bg-neutral-900 border border-neutral-800 rounded-xl flex items-center justify-center mb-2 shadow-sm">
            <Factory className="h-5 w-5 text-neutral-200" />
          </div>
          <h1 className="text-xl font-semibold tracking-tight text-white">Create an account</h1>
          <p className="text-sm text-neutral-500">Sign up to access indus.io</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Full Name</Label>
            <Input
              id="name"
              placeholder="John Doe"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="m@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && <p className="text-[13px] text-red-400 font-medium">{error}</p>}

          <Button type="submit" className="w-full bg-white text-black hover:bg-neutral-200" disabled={isLoading}>
            {isLoading ? "Creating account..." : "Sign Up"}
          </Button>
        </form>

        <div className="text-center text-sm text-neutral-500">
          Already have an account?{" "}
          <Link to="/login" className="text-white hover:underline underline-offset-4">
            Log in
          </Link>
        </div>
      </div>
    </div>
  );
}
