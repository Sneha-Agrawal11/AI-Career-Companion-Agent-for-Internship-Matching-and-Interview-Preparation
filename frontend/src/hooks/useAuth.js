import { createContext, useContext, useEffect, useMemo, useState } from "react";
import {
  clearToken,
  getStoredToken,
  loginWithTokenFlow,
  registerUser,
  storeToken,
} from "../services/authService";
import { fetchProfile } from "../services/profileService";
import { saveJson, storageKeys } from "../utils/storage";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(getStoredToken());
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const profile = await fetchProfile();
        setUser(profile);
        saveJson(storageKeys.profile, profile);
      } catch {
        clearToken();
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    init();
  }, [token]);

  const login = async ({ email, password }) => {
    const data = await loginWithTokenFlow({ email, password });
    storeToken(data.access_token);
    setToken(data.access_token);
    const profile = await fetchProfile();
    setUser(profile);
    saveJson(storageKeys.profile, profile);
    return profile;
  };

  const register = async (payload) => registerUser(payload);

  const logout = () => {
    clearToken();
    setToken(null);
    setUser(null);
    localStorage.removeItem(storageKeys.lastMatches);
    localStorage.removeItem(storageKeys.latestResumeRaw);
    localStorage.removeItem(storageKeys.latestResumeCandidate);
  };

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      isAuthenticated: Boolean(token),
      setUser,
      login,
      logout,
      register,
    }),
    [user, token, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
