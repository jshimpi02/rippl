import { useEffect, useState } from "react";

import "./App.css";
import { useGraphSearch } from "./hooks/useGraphSearch";
import { StatusBar } from "./layout/StatusBar";
import { StudioHeader } from "./layout/StudioHeader";
import { StudioWorkspace } from "./layout/StudioWorkspace";
import { loadUSIGGraph } from "./services/graphLoader";
import type {
  USIGGraph,
  USIGNode,
} from "./types/usig";

function App() {
  const [graph, setGraph] = useState<USIGGraph | null>(null);
  const [selectedNode, setSelectedNode] =
    useState<USIGNode | null>(null);
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

  const {
    query,
    setQuery,
    matches,
    matchingNodeIds,
    clearSearch,
  } = useGraphSearch(graph?.nodes ?? []);

  function handleSearchResultSelect(node: USIGNode) {
    setSelectedNode(node);
  }

  function handleSearchClear() {
    clearSearch();
  }

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
      <StudioHeader
        repositoryName="Rippl"
        query={query}
        searchResults={matches}
        onQueryChange={setQuery}
        onSearchResultSelect={handleSearchResultSelect}
        onSearchClear={handleSearchClear}
      />

      <StudioWorkspace
        graph={graph}
        selectedNode={selectedNode}
        matchingNodeIds={matchingNodeIds}
        onNodeSelect={setSelectedNode}
      />

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