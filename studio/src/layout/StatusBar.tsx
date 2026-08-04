interface StatusBarProps {
    nodeCount: number;
    edgeCount: number;
  }
  
  export function StatusBar({
    nodeCount,
    edgeCount,
  }: StatusBarProps) {
    return (
      <footer className="status-bar">
        <div className="status-group">
          <span className="status-ready">
            <span className="status-dot" />
            Ready
          </span>
  
          <span>{nodeCount} nodes</span>
          <span>{edgeCount} edges</span>
        </div>
  
        <div className="status-group">
          <span>USIG</span>
          <span>Local workspace</span>
        </div>
      </footer>
    );
  }