import { useMemo, useState } from "react";

import type { USIGNode } from "../types/usig";

const MAX_RESULTS = 8;

export function useGraphSearch(nodes: USIGNode[]) {
  const [query, setQuery] = useState("");

  const normalizedQuery = query.trim().toLowerCase();

  const matches = useMemo(() => {
    if (!normalizedQuery) {
      return [];
    }

    return nodes
      .filter((node) => {
        const searchableText = [
          node.label,
          node.id,
          node.type,
        ]
          .join(" ")
          .toLowerCase();

        return searchableText.includes(normalizedQuery);
      })
      .slice(0, MAX_RESULTS);
  }, [nodes, normalizedQuery]);

  const matchingNodeIds = useMemo(
    () => new Set(matches.map((node) => node.id)),
    [matches]
  );

  function clearSearch() {
    setQuery("");
  }

  return {
    query,
    setQuery,
    matches,
    matchingNodeIds,
    clearSearch,
  };
}