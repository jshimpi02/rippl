import dagre from "@dagrejs/dagre";
import type { Edge, Node } from "@xyflow/react";

const DEFAULT_NODE_WIDTH = 220;
const DEFAULT_NODE_HEIGHT = 72;

export function applyDagreLayout(
  nodes: Node[],
  edges: Edge[],
  direction: "TB" | "LR" = "TB"
): Node[] {
  const graph = new dagre.graphlib.Graph();

  graph.setDefaultEdgeLabel(() => ({}));

  graph.setGraph({
    rankdir: direction,
    ranksep: 140,
    nodesep: 80,
  });

  nodes.forEach((node) => {
    graph.setNode(node.id, {
      width: DEFAULT_NODE_WIDTH,
      height: DEFAULT_NODE_HEIGHT,
    });
  });

  edges.forEach((edge) => {
    graph.setEdge(edge.source, edge.target);
  });

  dagre.layout(graph);

  return nodes.map((node) => {
    const positionedNode = graph.node(node.id);

    return {
      ...node, // Important: preserves data, style, type, etc.
      position: {
        x: positionedNode.x - DEFAULT_NODE_WIDTH / 2,
        y: positionedNode.y - DEFAULT_NODE_HEIGHT / 2,
      },
    };
  });
}