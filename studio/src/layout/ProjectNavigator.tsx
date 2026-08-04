import type { USIGNode } from "../types/usig";

interface ProjectNavigatorProps {
  nodes: USIGNode[];
}

interface NodeCategory {
  type: string;
  label: string;
  icon: string;
}

const NODE_CATEGORIES: NodeCategory[] = [
  { type: "Repository", label: "Repositories", icon: "◫" },
  { type: "File", label: "Files", icon: "▤" },
  { type: "Class", label: "Classes", icon: "◇" },
  { type: "Method", label: "Methods", icon: "ƒ" },
  { type: "API", label: "APIs", icon: "◎" },
  { type: "Database", label: "Databases", icon: "▦" },
  { type: "BusinessRule", label: "Business Rules", icon: "◆" },
];

export function ProjectNavigator({
  nodes,
}: ProjectNavigatorProps) {
  const getNodeCount = (type: string) =>
    nodes.filter(
      (node) => node.type.toLowerCase() === type.toLowerCase()
    ).length;

  return (
    <aside className="project-navigator">
      <div className="panel-heading">
        <div>
          <span className="panel-eyebrow">Workspace</span>
          <h2>Explorer</h2>
        </div>
      </div>

      <nav aria-label="Graph node categories">
        <ul className="navigator-list">
          {NODE_CATEGORIES.map((category) => (
            <li key={category.type}>
              <button type="button" className="navigator-item">
                <span className="navigator-icon" aria-hidden="true">
                  {category.icon}
                </span>

                <span className="navigator-label">
                  {category.label}
                </span>

                <span className="navigator-count">
                  {getNodeCount(category.type)}
                </span>
              </button>
            </li>
          ))}
        </ul>
      </nav>

      <div className="navigator-section">
        <span className="panel-eyebrow">Graph Overview</span>

        <dl className="overview-list">
          <div>
            <dt>Total nodes</dt>
            <dd>{nodes.length}</dd>
          </div>

          <div>
            <dt>Node types</dt>
            <dd>
              {
                new Set(
                  nodes.map((node) => node.type.toLowerCase())
                ).size
              }
            </dd>
          </div>
        </dl>
      </div>
    </aside>
  );
}