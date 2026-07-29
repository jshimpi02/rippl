import { useEffect, useState } from "react";

import "./App.css";
import { GraphCanvas } from "./components/GraphCanvas";
import { loadUSIGGraph } from "./services/graphLoader";
import type { USIGGraph } from "./types/usig";

function App() {
  const [graph, setGraph] = useState<USIGGraph | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadGraph() {
      try {
        const loadedGraph = await loadUSIGGraph();
        setGraph(loadedGraph);
      } catch (loadError) {
        const message =
          loadError instanceof Error
            ? loadError.message
            : "An unknown error occurred.";

        setError(message);
      }
    }

    void loadGraph();
  }, []);

  if (error) {
    return (
      <main className="status-screen">
        <h1>Rippl Studio</h1>
        <p className="error-message">{error}</p>
      </main>
    );
  }

  if (!graph) {
    return (
      <main className="status-screen">
        <h1>Rippl Studio</h1>
        <p>Loading USIG graph...</p>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Software Intelligence Graph</p>
          <h1>Rippl Studio</h1>
        </div>

        <div className="graph-summary">
          <span>{graph.nodes.length} nodes</span>
          <span>{graph.edges.length} edges</span>
        </div>
      </header>

      <GraphCanvas graph={graph} />
    </main>
  );
}

export default App;