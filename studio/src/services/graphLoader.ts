import type { USIGGraph } from "../types/usig";

export async function loadUSIGGraph(
  path = "/usig.json",
): Promise<USIGGraph> {
  const response = await fetch(path);

  if (!response.ok) {
    throw new Error(
      `Failed to load USIG graph: ${response.status} ${response.statusText}`,
    );
  }

  const data: unknown = await response.json();

  if (!isUSIGGraph(data)) {
    throw new Error("The loaded file is not a valid USIG graph.");
  }

  return data;
}

function isUSIGGraph(data: unknown): data is USIGGraph {
  if (typeof data !== "object" || data === null) {
    return false;
  }

  const graph = data as Partial<USIGGraph>;

  return Array.isArray(graph.nodes) && Array.isArray(graph.edges);
}