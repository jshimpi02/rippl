import {
    Background,
    Controls,
    MiniMap,
    ReactFlow,
    type Edge,
    type Node,
  } from "@xyflow/react";
  import "@xyflow/react/dist/style.css";
  
  import type { USIGGraph } from "../types/usig";
  
  interface GraphCanvasProps {
    graph: USIGGraph;
  }
  
  export function GraphCanvas({ graph }: GraphCanvasProps) {
    const nodes: Node[] = graph.nodes.map((node, index) => ({
      id: node.id,
      position: {
        x: (index % 3) * 260,
        y: Math.floor(index / 3) * 160,
      },
      data: {
        label: `${node.type}: ${node.label}`,
      },
    }));
  
    const edges: Edge[] = graph.edges.map((edge, index) => ({
      id: edge.id ?? `edge-${index}`,
      source: edge.source,
      target: edge.target,
      label: edge.type,
    }));
  
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