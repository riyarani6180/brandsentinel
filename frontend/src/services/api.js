
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("brandsentinel_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Handle file uploads.
    if (config.data instanceof FormData) {
      delete config.headers["Content-Type"];
    }
    // Handle OAuth2 login form data.
    else if (config.data instanceof URLSearchParams) {
      config.headers["Content-Type"] =
        "application/x-www-form-urlencoded";
    }
    // Handle normal JSON requests.
    else if (config.data) {
      config.headers["Content-Type"] = "application/json";
    }

    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
