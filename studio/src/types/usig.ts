export interface USIGNode {
    id: string;
    type: string;
    label: string;
    metadata?: Record<string, unknown>;
  }
  
  export interface USIGEdge {
    id?: string;
    source: string;
    target: string;
    type: string;
    metadata?: Record<string, unknown>;
  }
  
  export interface USIGGraph {
    nodes: USIGNode[];
    edges: USIGEdge[];
  }