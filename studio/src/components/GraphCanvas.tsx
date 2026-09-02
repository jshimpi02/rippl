import {
    useEffect,
    useMemo,
    useState,
  } from "react";
  
  import {
    Background,
    Controls,
    ReactFlow,
    type Edge,
    type Node,
    type NodeMouseHandler,
    type ReactFlowInstance,
  } from "@xyflow/react";
  import "@xyflow/react/dist/style.css";
  
  import { applyDagreLayout } from "../services/graphLayout";
  import type {
    USIGGraph,
    USIGNode,
  } from "../types/usig";
  
  interface GraphCanvasProps {
    graph: USIGGraph;
    selectedNodeId: string | null;
    matchingNodeIds: Set<string>;
    onNodeSelect: (node: USIGNode | null) => void;
  }
  
  export function GraphCanvas({
    graph,
    selectedNodeId,
    matchingNodeIds,
    onNodeSelect,
  }: GraphCanvasProps) {
    const [flowInstance, setFlowInstance] =
      useState<ReactFlowInstance | null>(null);
  
    const { nodes, edges } = useMemo(() => {
      const flowEdges: Edge[] = graph.edges.map(
        (edge, index) => ({
          id: edge.id ?? `edge-${index}`,
          source: edge.source,
          target: edge.target,
          label: edge.type,
        })
      );
  
      const rawNodes: Node[] = graph.nodes.map((node) => {
        const isMatch = matchingNodeIds.has(node.id);
        const isSelected = selectedNodeId === node.id;
  
        return {
          id: node.id,
          position: { x: 0, y: 0 },
          data: {
            label: `${node.type}: ${node.label}`,
          },
          style: {
            width: 220,
            minHeight: 72,
            background: isSelected
              ? "#213a6b"
              : isMatch
                ? "#1c2d4d"
                : "#172033",
            color: "#f8fafc",
            border: isSelected
              ? "2px solid #7ea2ff"
              : isMatch
                ? "2px solid #5b8cff"
                : "1px solid #334155",
            borderRadius: "12px",
            fontWeight: 600,
            fontSize: "12px",
            padding: "12px",
            boxShadow: isSelected
              ? "0 0 0 4px rgba(91, 140, 255, 0.18), 0 10px 28px rgba(0, 0, 0, 0.35)"
              : isMatch
                ? "0 0 18px rgba(91, 140, 255, 0.3)"
                : "0 8px 20px rgba(0, 0, 0, 0.28)",
          },
        };
      });
  
      return {
        edges: flowEdges,
        nodes: applyDagreLayout(
          rawNodes,
          flowEdges,
          "TB"
        ),
      };
    }, [
      graph,
      matchingNodeIds,
      selectedNodeId,
    ]);
  
    useEffect(() => {
      if (!flowInstance || !selectedNodeId) {
        return;
      }
  
      const selectedNode = nodes.find(
        (node) => node.id === selectedNodeId
      );
  
      if (!selectedNode) {
        return;
      }
  
      const nodeWidth =
        typeof selectedNode.style?.width === "number"
          ? selectedNode.style.width
          : 220;
  
      const nodeHeight = 72;
  
      void flowInstance.setCenter(
        selectedNode.position.x + nodeWidth / 2,
        selectedNode.position.y + nodeHeight / 2,
        {
          zoom: 1.25,
          duration: 500,
        }
      );
    }, [
      flowInstance,
      nodes,
      selectedNodeId,
    ]);
  
    const handleNodeClick: NodeMouseHandler = (
      _,
      clickedNode
    ) => {
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
          onInit={setFlowInstance}
          onNodeClick={handleNodeClick}
          fitView
          fitViewOptions={{ padding: 0.2 }}
        >
          <Controls />
          <Background
            gap={32}
            size={1.2}
            color="#2a3446"
          />
        </ReactFlow>
      </div>
    );
  }