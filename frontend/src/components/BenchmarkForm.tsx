import { useState } from "react";
import { payParityClient } from "../services/payParityClient";
import type { BenchmarkResult } from "../types/benchmark";

const DEPARTMENTS = ["Engineering", "Product"];

// Benchmark form: collects role details, calls the API through
// PayParityClient, and shows the predicted salary, interval, gap, and flag.
// Known limitations: minimal styling; job title and location are free text
// and must match the model's fixed vocabulary.

export default function BenchmarkForm() {
  const [jobTitle, setJobTitle] = useState("Senior Software Engineer");
  const [location, setLocation] = useState("Seattle, WA");
  const [yearsExperience, setYearsExperience] = useState(6);
  const [currentSalary, setCurrentSalary] = useState(145000);
  const [result, setResult] = useState<BenchmarkResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [department, setDepartment] = useState("Engineering");

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setResult(null);
    setIsLoading(true);
    try {
      const benchmark = await payParityClient.submitBenchmark({
        jobTitle,
        location,
        yearsExperience,
        currentSalary,
        department,
      });
      setResult(benchmark);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label>
          Job title
          <input value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} />
        </label>
        <label>
          Location
          <input value={location} onChange={(e) => setLocation(e.target.value)} />
        </label>
        <label>
          Years of experience
          <input
            type="number"
            value={yearsExperience}
            onChange={(e) => setYearsExperience(Number(e.target.value))}
          />
        </label>
        <label>
          Current salary
          <input
            type="number"
            value={currentSalary}
            onChange={(e) => setCurrentSalary(Number(e.target.value))}
          />
        </label>
        <label>
          Department
          <select value={department} onChange={(e) => setDepartment(e.target.value)}>
            {DEPARTMENTS.map((d) => (
              <option key={d}>{d}</option>
            ))}
          </select>
        </label>
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Checking..." : "Check fairness benchmark"}
        </button>
      </form>

      {error && <p role="alert">{error}</p>}

      {result && (
        <div>
          <p>Predicted fair salary: ${result.predictedFairSalary.toLocaleString()}</p>
          <p>
            Confidence interval: ${result.confidenceInterval[0].toLocaleString()} - $
            {result.confidenceInterval[1].toLocaleString()}
          </p>
          <p>Gap: {result.gapPercent}%</p>
          {result.flagged && <p>This role is flagged for review.</p>}
        </div>
      )}
    </div>
  );
}
