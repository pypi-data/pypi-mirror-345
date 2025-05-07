from typing import Any, Dict, List
import pandas as pd

class ResourceRegistry:
    def __init__(self):
        # { resource_type: { name: (resource_obj, details) } }
        self._registry: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, resource: Any, *,
                 resource_type: str, details: Dict[str, Any] = None):
        """Register a resource under a given type."""
        if resource_type == "frequency_list":
            if not (
                isinstance(resource, pd.DataFrame)
                and resource.shape[1] == 2
                and resource.columns[1] == "f"
            ):
                raise ValueError("Frequency lists must be a DataFrame with exactly two columns, the second being 'f'")

        self._registry.setdefault(resource_type, {})[name] = (resource, details or {})

    def list(self, resource_type: str = None) -> List[str] | Dict[str, List[str]]:
        """List resource names, optionally filtered by type."""
        if resource_type:
            return list(self._registry.get(resource_type, {}).keys())
        return {rtype: list(entries.keys()) for rtype, entries in self._registry.items()}

    def get(self, resource_type: str, name: str) -> Any:
        """Retrieve a specific resource."""
        return self._registry[resource_type][name][0]

    def details(self, resource_type: str, name: str) -> Dict[str, Any]:
        """Get metadata about a resource."""
        return self._registry[resource_type][name][1]
