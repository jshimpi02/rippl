import {
    useEffect,
    useRef,
    useState,
    type KeyboardEvent,
  } from "react";
  
  import type { USIGNode } from "../types/usig";
  
  interface GraphSearchProps {
    query: string;
    results: USIGNode[];
    onQueryChange: (query: string) => void;
    onResultSelect: (node: USIGNode) => void;
    onClear: () => void;
  }
  
  export function GraphSearch({
    query,
    results,
    onQueryChange,
    onResultSelect,
    onClear,
  }: GraphSearchProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [activeIndex, setActiveIndex] = useState(0);
  
    const containerRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
  
    useEffect(() => {
      function handleShortcut(event: globalThis.KeyboardEvent) {
        const isSearchShortcut =
          (event.metaKey || event.ctrlKey) &&
          event.key.toLowerCase() === "k";
  
        if (!isSearchShortcut) {
          return;
        }
  
        event.preventDefault();
        inputRef.current?.focus();
        setIsOpen(true);
      }
  
      window.addEventListener("keydown", handleShortcut);
  
      return () => {
        window.removeEventListener("keydown", handleShortcut);
      };
    }, []);
  
    useEffect(() => {
      function handleOutsideClick(event: MouseEvent) {
        if (
          containerRef.current &&
          !containerRef.current.contains(event.target as Node)
        ) {
          setIsOpen(false);
        }
      }
  
      document.addEventListener("mousedown", handleOutsideClick);
  
      return () => {
        document.removeEventListener(
          "mousedown",
          handleOutsideClick
        );
      };
    }, []);
  
    useEffect(() => {
      setActiveIndex(0);
    }, [query]);
  
    function selectResult(node: USIGNode) {
      onResultSelect(node);
      setIsOpen(false);
    }
  
    function handleKeyDown(
      event: KeyboardEvent<HTMLInputElement>
    ) {
      if (event.key === "Escape") {
        setIsOpen(false);
        return;
      }
  
      if (results.length === 0) {
        return;
      }
  
      if (event.key === "ArrowDown") {
        event.preventDefault();
  
        setActiveIndex((currentIndex) =>
          currentIndex >= results.length - 1
            ? 0
            : currentIndex + 1
        );
      }
  
      if (event.key === "ArrowUp") {
        event.preventDefault();
  
        setActiveIndex((currentIndex) =>
          currentIndex <= 0
            ? results.length - 1
            : currentIndex - 1
        );
      }
  
      if (event.key === "Enter") {
        event.preventDefault();
        selectResult(results[activeIndex]);
      }
    }
  
    return (
      <div className="graph-search" ref={containerRef}>
        <div className="graph-search-input-wrapper">
          <span
            className="graph-search-icon"
            aria-hidden="true"
          >
            ⌕
          </span>
  
          <input
            ref={inputRef}
            type="search"
            value={query}
            placeholder="Search graph"
            aria-label="Search graph nodes"
            onFocus={() => setIsOpen(true)}
            onChange={(event) => {
              onQueryChange(event.target.value);
              setIsOpen(true);
            }}
            onKeyDown={handleKeyDown}
          />
  
          {query ? (
            <button
              type="button"
              className="graph-search-clear"
              onClick={() => {
                onClear();
                inputRef.current?.focus();
              }}
              aria-label="Clear graph search"
            >
              ×
            </button>
          ) : (
            <kbd>⌘ K</kbd>
          )}
        </div>
  
        {isOpen && query.trim() && (
          <div className="graph-search-results">
            {results.length === 0 ? (
              <div className="graph-search-empty">
                No matching nodes found
              </div>
            ) : (
              <ul>
                {results.map((node, index) => (
                  <li key={node.id}>
                    <button
                      type="button"
                      className={
                        index === activeIndex
                          ? "graph-search-result is-active"
                          : "graph-search-result"
                      }
                      onMouseEnter={() => setActiveIndex(index)}
                      onClick={() => selectResult(node)}
                    >
                      <span className="search-result-type">
                        {node.type}
                      </span>
  
                      <span className="search-result-label">
                        {node.label}
                      </span>
  
                      <span className="search-result-id">
                        {node.id}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    );
  }