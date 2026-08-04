interface StudioHeaderProps {
    repositoryName?: string;
  }
  
  export function StudioHeader({
    repositoryName = "Sample Repository",
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
          <div className="search-placeholder" aria-hidden="true">
            <span>⌕</span>
            <span>Search graph</span>
            <kbd>⌘ K</kbd>
          </div>
  
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