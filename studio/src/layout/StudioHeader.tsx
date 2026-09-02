import { GraphSearch } from "../components/GraphSearch";
import type { USIGNode } from "../types/usig";

interface StudioHeaderProps {
  repositoryName?: string;
  query: string;
  searchResults: USIGNode[];
  onQueryChange: (query: string) => void;
  onSearchResultSelect: (node: USIGNode) => void;
  onSearchClear: () => void;
}

export function StudioHeader({
  repositoryName = "Sample Repository",
  query,
  searchResults,
  onQueryChange,
  onSearchResultSelect,
  onSearchClear,
}: StudioHeaderProps) {
  return (
    <header className="studio-header">
      <div className="studio-brand">
        <div className="studio-logo" aria-hidden="true">
          R
        </div>

        <div>
          <h1>Rippl Studio</h1>
          <p>{repositoryName}</p>
        </div>
      </div>

      <div className="studio-header-actions">
        <GraphSearch
          query={query}
          results={searchResults}
          onQueryChange={onQueryChange}
          onResultSelect={onSearchResultSelect}
          onClear={onSearchClear}
        />

        <button
          type="button"
          className="icon-button"
          aria-label="Open settings"
          disabled
        >
          ⚙
        </button>
      </div>
    </header>
  );
}