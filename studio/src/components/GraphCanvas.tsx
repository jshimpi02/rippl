import { useMemo } from "react";

import {
  Background,
  Controls,
  ReactFlow,
  type Edge,
  type Node,
  type NodeMouseHandler,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { applyDagreLayout } from "../services/graphLayout";
import type { USIGGraph, USIGNode } from "../types/usig";

interface GraphCanvasProps {
  graph: USIGGraph;
  onNodeSelect: (node: USIGNode) => void;
}

export function GraphCanvas({
  graph,
  onNodeSelect,
}: GraphCanvasProps) {
  const { nodes, edges } = useMemo(() => {
    const flowEdges: Edge[] = graph.edges.map((edge, index) => ({
      id: edge.id ?? `edge-${index}`,
      source: edge.source,
      target: edge.target,
      label: edge.type,
    }));

    const rawNodes: Node[] = graph.nodes.map((node) => ({
      id: node.id,
      position: { x: 0, y: 0 },
      data: {
        label: `${node.type}: ${node.label}`,
      },
      style: {
        width: 220,
        minHeight: 72,
        background: "#172033",
        color: "#f8fafc",
        border: "1px solid #334155",
        borderRadius: "12px",
        fontWeight: 600,
        fontSize: "12px",
        padding: "12px",
        boxShadow: "0 8px 20px rgba(0, 0, 0, 0.28)",
      },
    }));

    return {
      edges: flowEdges,
      nodes: applyDagreLayout(rawNodes, flowEdges, "TB"),
    };
  }, [graph]);

  const handleNodeClick: NodeMouseHandler = (_, clickedNode) => {
    const selectedNode = graph.nodes.find(
      (node) => node.id === clickedNode.id
    );

    if (selectedNode) {
      onNodeSelect(selectedNode);
    }
  };

  return (
    <div className="graph-container">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodeClick={handleNodeClick}
        fitView
        fitViewOptions={{ padding: 0.2 }}
      >
        <Controls />
        <Background gap={32} size={1.2} color="#2a3446" />
      </ReactFlow>
    </div>
  );
}