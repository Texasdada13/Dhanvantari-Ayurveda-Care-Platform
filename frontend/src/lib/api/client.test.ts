import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import axios from "axios";

// We test the shape and configuration of the api client and the helper objects.
// Network calls are not made — we spy on the axios instance methods.

describe("API client module", () => {
  beforeEach(() => {
    // Ensure a clean localStorage for each test
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("creates an axios instance with correct baseURL and headers", async () => {
    const { api } = await import("./client");
    expect(api.defaults.baseURL).toBe("http://localhost:8747");
    expect(api.defaults.headers["Content-Type"]).toBe("application/json");
  });

  it("authApi exposes register, login, and me methods", async () => {
    const { authApi } = await import("./client");
    expect(typeof authApi.register).toBe("function");
    expect(typeof authApi.login).toBe("function");
    expect(typeof authApi.me).toBe("function");
  });

  it("patientsApi exposes CRUD methods", async () => {
    const { patientsApi } = await import("./client");
    expect(typeof patientsApi.list).toBe("function");
    expect(typeof patientsApi.get).toBe("function");
    expect(typeof patientsApi.create).toBe("function");
    expect(typeof patientsApi.update).toBe("function");
    expect(typeof patientsApi.deactivate).toBe("function");
  });

  it("plansApi exposes plan management methods", async () => {
    const { plansApi } = await import("./client");
    expect(typeof plansApi.get).toBe("function");
    expect(typeof plansApi.create).toBe("function");
    expect(typeof plansApi.addSupplement).toBe("function");
    expect(typeof plansApi.removeSupplement).toBe("function");
    expect(typeof plansApi.addRecipe).toBe("function");
    expect(typeof plansApi.removeRecipe).toBe("function");
  });

  it("portalApi exposes public portal methods", async () => {
    const { portalApi } = await import("./client");
    expect(typeof portalApi.home).toBe("function");
    expect(typeof portalApi.plan).toBe("function");
    expect(typeof portalApi.history).toBe("function");
    expect(typeof portalApi.checkin).toBe("function");
    expect(typeof portalApi.followups).toBe("function");
  });

  it("request interceptor attaches Bearer token from localStorage", async () => {
    const { api } = await import("./client");
    localStorage.setItem("access_token", "test-token-123");

    // Simulate the request interceptor by running it manually
    const config = {
      headers: new axios.AxiosHeaders(),
    } as import("axios").InternalAxiosRequestConfig;

    // The interceptor is the first handler on the request chain
    const interceptor = api.interceptors.request as unknown as {
      handlers: Array<{ fulfilled: (config: import("axios").InternalAxiosRequestConfig) => import("axios").InternalAxiosRequestConfig }>;
    };
    const handler = interceptor.handlers[0];
    const result = handler.fulfilled(config);

    expect(result.headers.Authorization).toBe("Bearer test-token-123");
  });

  it("request interceptor does not attach token when none exists", async () => {
    const { api } = await import("./client");

    const config = {
      headers: new axios.AxiosHeaders(),
    } as import("axios").InternalAxiosRequestConfig;

    const interceptor = api.interceptors.request as unknown as {
      handlers: Array<{ fulfilled: (config: import("axios").InternalAxiosRequestConfig) => import("axios").InternalAxiosRequestConfig }>;
    };
    const handler = interceptor.handlers[0];
    const result = handler.fulfilled(config);

    expect(result.headers.Authorization).toBeUndefined();
  });

  it("supplementsApi.uploadImage sends FormData", async () => {
    const { api, supplementsApi } = await import("./client");
    const postSpy = vi.spyOn(api, "post").mockResolvedValue({ data: {} });

    const file = new File(["img"], "test.png", { type: "image/png" });
    await supplementsApi.uploadImage(1, file);

    expect(postSpy).toHaveBeenCalledWith(
      "/api/supplements/1/image",
      expect.any(FormData),
      { headers: { "Content-Type": "multipart/form-data" } }
    );
  });

  it("all API namespaces are exported", async () => {
    const mod = await import("./client");
    const expectedExports = [
      "api", "authApi", "practitionersApi", "patientsApi", "plansApi",
      "supplementsApi", "recipesApi", "checkinsApi", "followupsApi",
      "aiApi", "portalApi", "notesApi", "assessmentsApi", "yogaApi",
      "videosApi", "planYogaApi", "pranayamaApi", "planPranayamaApi",
      "therapiesApi", "packagesApi", "planTherapyApi", "planPackageApi",
      "intakeApi", "billingApi",
    ];
    for (const name of expectedExports) {
      expect(mod).toHaveProperty(name);
    }
  });
});
