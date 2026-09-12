import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import BenchmarkForm from "./BenchmarkForm";
import { payParityClient } from "../services/payParityClient";

// Alpha scope: proves the component -> service layer wiring works without
// needing a live backend. The real end-to-end round trip (component ->
// HttpPayParityClient -> FastAPI -> model) is exercised manually against
// `uvicorn app.main:app --reload` per README_ALPHA.md, and by the backend's
// own pytest suite.
vi.mock("../services/payParityClient", () => ({
  payParityClient: {
    submitBenchmark: vi.fn(),
    getBenchmark: vi.fn(),
    searchRoles: vi.fn(),
  },
}));

describe("BenchmarkForm", () => {
  beforeEach(() => {
    vi.mocked(payParityClient.submitBenchmark).mockReset();
  });

  it("renders the form with default values", () => {
    render(<BenchmarkForm />);
    expect(
      screen.getByRole("button", { name: /check fairness benchmark/i })
    ).toBeInTheDocument();
  });

  it("submits the form and displays the result", async () => {
    vi.mocked(payParityClient.submitBenchmark).mockResolvedValueOnce({
      benchmarkId: "b_test123",
      predictedFairSalary: 150000,
      confidenceInterval: [142000, 158000],
      gapPercent: -3.3,
      flagged: false,
      generatedAt: "2026-01-01T00:00:00Z",
    });

    render(<BenchmarkForm />);
    fireEvent.click(screen.getByRole("button", { name: /check fairness benchmark/i }));

    await waitFor(() => {
      expect(screen.getByText(/predicted fair salary/i)).toBeInTheDocument();
    });
    expect(payParityClient.submitBenchmark).toHaveBeenCalledTimes(1);
  });

  it("shows an error message when the request fails", async () => {
    vi.mocked(payParityClient.submitBenchmark).mockRejectedValueOnce(
      new Error("model_unavailable")
    );

    render(<BenchmarkForm />);
    fireEvent.click(screen.getByRole("button", { name: /check fairness benchmark/i }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("model_unavailable");
    });
  });
});
