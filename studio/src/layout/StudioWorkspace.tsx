import { GraphCanvas } from "../components/GraphCanvas";
import type {
  USIGGraph,
  USIGNode,
} from "../types/usig";
import { InspectorPanel } from "./InspectorPanel";
import { ProjectNavigator } from "./ProjectNavigator";

interface StudioWorkspaceProps {
    graph: USIGGraph;
    selectedNode: USIGNode | null;
    matchingNodeIds: Set<string>;
    onNodeSelect: (node: USIGNode | null) => void;
  }

export function StudioWorkspace({
  graph,
  selectedNode,
  matchingNodeIds,
  onNodeSelect,
}: StudioWorkspaceProps) {
  return (
    <div className="studio-workspace">
      <ProjectNavigator nodes={graph.nodes} />

      <section className="graph-workspace">
        <div className="graph-toolbar">
          <div>
            <span className="graph-toolbar-title">
              Software Intelligence Graph
            </span>

            <span className="graph-toolbar-subtitle">
              Top-to-bottom dependency view
            </span>
          </div>

          <div className="graph-toolbar-actions">
            <button type="button" disabled>
              Fit view
            </button>
          </div>
        </div>

        <div className="graph-canvas-region">
          <GraphCanvas
            graph={graph}
            selectedNodeId={selectedNode?.id ?? null}
            matchingNodeIds={matchingNodeIds}
            onNodeSelect={onNodeSelect}
          />
        </div>
      </section>

      <InspectorPanel
        selectedNode={selectedNode}
        edges={graph.edges}
        onClose={() => onNodeSelect(null)}
      />
    </div>
  );
}