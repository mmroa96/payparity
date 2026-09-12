// Matches Interface Contracts section 3.1 (Frontend service layer).

export interface BenchmarkRequest {
  jobTitle: string;
  location: string;
  yearsExperience: number;
  currentSalary: number;
  gender?: string;
  department?: string;
}

export interface BenchmarkResult {
  benchmarkId: string;
  predictedFairSalary: number;
  confidenceInterval: [number, number];
  gapPercent: number;
  flagged: boolean;
  generatedAt: string; // ISO 8601
}

export interface ApiError {
  error: string;
  fields?: string[];
  retryable?: boolean;
}

export interface PayParityClient {
  submitBenchmark(req: BenchmarkRequest): Promise<BenchmarkResult>;
  getBenchmark(id: string): Promise<BenchmarkResult>;
  searchRoles(query: string): Promise<string[]>;
}
