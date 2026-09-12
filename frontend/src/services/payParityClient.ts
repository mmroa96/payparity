import type { ApiError, BenchmarkRequest, BenchmarkResult, PayParityClient } from "../types/benchmark";

// TECH DEBT: base URL is read from an env var with a localhost fallback
// rather than a proper per-environment config module. Fine for Alpha
// (one dev backend, one dev frontend); revisit once there's a staging
// deploy on AWS.
const BASE_URL = import.meta.env?.VITE_API_BASE_URL ?? "http://localhost:8000";

interface BenchmarkResultWire {
  benchmark_id: string;
  predicted_fair_salary: number;
  confidence_interval: [number, number];
  gap_percent: number;
  flagged: boolean;
  generated_at: string;
}

function toWireRequest(req: BenchmarkRequest) {
  return {
    job_title: req.jobTitle,
    location: req.location,
    years_experience: req.yearsExperience,
    current_salary: req.currentSalary,
    gender: req.gender,
    department: req.department,
  };
}

function fromWireResult(wire: BenchmarkResultWire): BenchmarkResult {
  return {
    benchmarkId: wire.benchmark_id,
    predictedFairSalary: wire.predicted_fair_salary,
    confidenceInterval: wire.confidence_interval,
    gapPercent: wire.gap_percent,
    flagged: wire.flagged,
    generatedAt: wire.generated_at,
  };
}

async function parseErrorOrThrow(response: Response): Promise<never> {
  let body: ApiError = { error: "unknown_error" };
  try {
    body = await response.json();
  } catch {
    // Response had no JSON body; keep the default.
  }
  throw new Error(body.error ?? `Request failed with status ${response.status}`);
}

export class HttpPayParityClient implements PayParityClient {
  async submitBenchmark(req: BenchmarkRequest): Promise<BenchmarkResult> {
    const response = await fetch(`${BASE_URL}/api/v1/benchmark`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(toWireRequest(req)),
    });
    if (!response.ok) return parseErrorOrThrow(response);
    return fromWireResult(await response.json());
  }

  async getBenchmark(id: string): Promise<BenchmarkResult> {
    const response = await fetch(`${BASE_URL}/api/v1/benchmark/${encodeURIComponent(id)}`);
    if (!response.ok) return parseErrorOrThrow(response);
    return fromWireResult(await response.json());
  }

  async searchRoles(query: string): Promise<string[]> {
    const response = await fetch(`${BASE_URL}/api/v1/roles?query=${encodeURIComponent(query)}`);
    if (!response.ok) return parseErrorOrThrow(response);
    const body: { roles: string[] } = await response.json();
    return body.roles;
  }
}

export const payParityClient: PayParityClient = new HttpPayParityClient();
