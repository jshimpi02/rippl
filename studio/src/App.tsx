import { useEffect, useState } from "react";

import "./App.css";
import { StatusBar } from "./layout/StatusBar";
import { StudioHeader } from "./layout/StudioHeader";
import { StudioWorkspace } from "./layout/StudioWorkspace";
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
      <StudioHeader repositoryName="Rippl" />

      <StudioWorkspace graph={graph} />

      <div className="bottom-panel-reservation">
        <span>Terminal</span>
        <span>Output</span>
        <span>Problems</span>
        <span className="bottom-panel-hint">
          Integrated terminal planned in Issue #10
        </span>
      </div>

      <StatusBar
        nodeCount={graph.nodes.length}
        edgeCount={graph.edges.length}
      />
    </main>
  );
}

export default App;