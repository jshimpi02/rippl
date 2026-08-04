import type {
    USIGEdge,
    USIGNode,
  } from "../types/usig";
  
  interface InspectorPanelProps {
    selectedNode: USIGNode | null;
    edges: USIGEdge[];
    onClose: () => void;
  }
  
  export function InspectorPanel({
    selectedNode,
    edges,
    onClose,
  }: InspectorPanelProps) {
    if (!selectedNode) {
      return (
        <aside className="inspector-panel">
          <div className="panel-heading">
            <div>
              <span className="panel-eyebrow">Selection</span>
              <h2>Inspector</h2>
            </div>
          </div>
  
          <div className="inspector-empty-state">
            <div className="empty-state-icon" aria-hidden="true">
              ◇
            </div>
  
            <h3>Select a graph node</h3>
  
            <p>
              Node metadata, relationships, and impact information
              will appear here.
            </p>
          </div>
        </aside>
      );
    }
  
    const incomingEdges = edges.filter(
      (edge) => edge.target === selectedNode.id
    );
  
    const outgoingEdges = edges.filter(
      (edge) => edge.source === selectedNode.id
    );
  
    return (
      <aside className="inspector-panel">
        <div className="panel-heading inspector-heading">
          <div>
            <span className="panel-eyebrow">
              {selectedNode.type}
            </span>
            <h2>Inspector</h2>
          </div>
  
                <button
                    type="button"
                    className="inspector-close-button"
                    onClick={onClose}
                    aria-label="Clear selected node"
                >
                    ×
                </button>
        </div>
  
            <div className="inspector-content">
                <section className="inspector-section">
                    <span className="inspector-label">Name</span>

                    <h3 className="inspector-node-name">
                        {selectedNode.label}
                    </h3>
                </section>

                <section className="inspector-section">
                    <span className="inspector-label">Node ID</span>

                    <code className="inspector-code">
                        {selectedNode.id}
                    </code>
                </section>

                <section className="inspector-section">
                    <div className="inspector-section-heading">
                        <span>Relationships</span>
                        <span>{incomingEdges.length + outgoingEdges.length}</span>
                    </div>
  
            <div className="relationship-group">
              <span className="inspector-label">
                Incoming
              </span>
  
              {incomingEdges.length === 0 ? (
                <p className="inspector-muted">
                  No incoming relationships
                </p>
              ) : (
                incomingEdges.map((edge, index) => (
                  <div
                    className="relationship-card"
                    key={edge.id ?? `incoming-${index}`}
                  >
                    <strong>{edge.type}</strong>
                    <code>{edge.source}</code>
                  </div>
                ))
              )}
            </div>
  
            <div className="relationship-group">
              <span className="inspector-label">
                Outgoing
              </span>
  
              {outgoingEdges.length === 0 ? (
                <p className="inspector-muted">
                  No outgoing relationships
                </p>
              ) : (
                outgoingEdges.map((edge, index) => (
                  <div
                    className="relationship-card"
                    key={edge.id ?? `outgoing-${index}`}
                  >
                    <strong>{edge.type}</strong>
                    <code>{edge.target}</code>
                  </div>
                ))
              )}
            </div>
          </section>
        </div>
      </aside>
    );
  }