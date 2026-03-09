import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { getMe, logout as apiLogout } from "../api";

interface User {
  id: string;
  handle: string;
  display_name: string;
  email: string;
  gravity_level: number;
}

interface AuthCtx {
  user: User | null;
  loading: boolean;
  logout: () => Promise<void>;
  setUser: (u: User) => void;
}

const AuthContext = createContext<AuthCtx>({
  user: null,
  loading: true,
  logout: async () => {},
  setUser: () => {},
});

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    getMe()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!loading && !user && location.pathname !== "/login") {
      navigate("/login");
    }
  }, [loading, user, location.pathname, navigate]);

  const logout = async () => {
    await apiLogout();
    setUser(null);
    navigate("/login");
  };

  return (
    <AuthContext.Provider value={{ user, loading, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}
