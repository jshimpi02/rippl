import type { USIGEdge, USIGNode } from "../types/usig";

interface NodeDetailsSidebarProps {
  node: USIGNode | null;
  incomingEdges: USIGEdge[];
  outgoingEdges: USIGEdge[];
  onClose: () => void;
}

function formatMetadataValue(value: unknown): string {
  if (typeof value === "string") {
    return value;
  }

  if (
    typeof value === "number" ||
    typeof value === "boolean" ||
    value === null
  ) {
    return String(value);
  }

  return JSON.stringify(value, null, 2);
}

export function NodeDetailsSidebar({
  node,
  incomingEdges,
  outgoingEdges,
  onClose,
}: NodeDetailsSidebarProps) {
  if (!node) {
    return null;
  }

  const metadataEntries = Object.entries(node.metadata ?? {});

  return (
    <aside className="node-sidebar" aria-label="Node details">
      <div className="node-sidebar-header">
        <div>
          <p className="node-sidebar-eyebrow">{node.type}</p>
          <h2>{node.label}</h2>
        </div>

        <button
          type="button"
          className="sidebar-close-button"
          onClick={onClose}
          aria-label="Close node details"
        >
          ×
        </button>
      </div>

      <div className="node-sidebar-content">
        <section className="node-detail-section">
          <h3>Node Information</h3>

          <dl className="node-detail-list">
            <div>
              <dt>ID</dt>
              <dd>{node.id}</dd>
            </div>

            <div>
              <dt>Type</dt>
              <dd>{node.type}</dd>
            </div>

            <div>
              <dt>Label</dt>
              <dd>{node.label}</dd>
            </div>
          </dl>
        </section>

        <section className="node-detail-section">
          <h3>Metadata</h3>

          {metadataEntries.length === 0 ? (
            <p className="empty-state">No metadata available.</p>
          ) : (
            <dl className="node-detail-list">
              {metadataEntries.map(([key, value]) => (
                <div key={key}>
                  <dt>{key}</dt>
                  <dd>
                    <pre>{formatMetadataValue(value)}</pre>
                  </dd>
                </div>
              ))}
            </dl>
          )}
        </section>

        <section className="node-detail-section">
          <h3>Incoming Relationships</h3>

          {incomingEdges.length === 0 ? (
            <p className="empty-state">No incoming relationships.</p>
          ) : (
            <ul className="relationship-list">
              {incomingEdges.map((edge, index) => (
                <li key={edge.id ?? `${edge.source}-${edge.target}-${index}`}>
                  <span className="relationship-type">{edge.type}</span>
                  <span>{edge.source}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="node-detail-section">
          <h3>Outgoing Relationships</h3>

          {outgoingEdges.length === 0 ? (
            <p className="empty-state">No outgoing relationships.</p>
          ) : (
            <ul className="relationship-list">
              {outgoingEdges.map((edge, index) => (
                <li key={edge.id ?? `${edge.source}-${edge.target}-${index}`}>
                  <span className="relationship-type">{edge.type}</span>
                  <span>{edge.target}</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </aside>
  );
}