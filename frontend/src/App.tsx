import BenchmarkForm from "./components/BenchmarkForm";

// Alpha scope: this proves the frontend module mounts and renders the
// working benchmark flow end to end against the live API. Page shell,
// routing, and navigation are out of scope until Beta.
export default function App() {
  return (
    <main>
      <h1>PayParity — Fairness Benchmark</h1>
      <BenchmarkForm />
    </main>
  );
}
