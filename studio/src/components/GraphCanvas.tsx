import {
    Background,
    Controls,
    MiniMap,
    ReactFlow,
    type Edge,
    type Node,
  } from "@xyflow/react";
  import "@xyflow/react/dist/style.css";
  
  import { applyDagreLayout } from "../services/graphLayout";
  import type { USIGGraph } from "../types/usig";
  
  interface GraphCanvasProps {
    graph: USIGGraph;
  }
  
  export function GraphCanvas({ graph }: GraphCanvasProps) {
    const edges: Edge[] = graph.edges.map((edge, index) => ({
      id: edge.id ?? `edge-${index}`,
      source: edge.source,
      target: edge.target,
      label: edge.type,
    }));
  
    const rawNodes: Node[] = graph.nodes.map((node) => ({
      id: node.id,
      position: {
        x: 0,
        y: 0,
      },
      data: {
        label: `${node.type}: ${node.label}`,
      },
    }));
  
    const nodes = applyDagreLayout(rawNodes, edges, "TB");
  
    return (
      <div className="graph-container">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <MiniMap />
          <Controls />
          <Background />
        </ReactFlow>
      </div>
    );
  }