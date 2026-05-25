import { useNavigate } from "react-router";
import { useAuthStore } from "../auth.store";
import { useEffect, type ReactNode } from "react";

interface ProtectProps {
  children: ReactNode;
  fallback?: ReactNode;
}

export const Protect = ({ children, fallback = null }: ProtectProps) => {
  const navigate = useNavigate();
  const { isLoading, isAuthenticated, isHydrated } = useAuthStore();

  useEffect(() => {
    if (!isHydrated) return;
    if (isLoading) return;

    if (!isAuthenticated) {
      navigate("/login");
    }
  }, [isHydrated, isLoading, isAuthenticated, navigate]);

  if (!isHydrated) return null;
  if (isLoading) return fallback;
  if (!isAuthenticated) return null;

  return <>{children}</>;
};
