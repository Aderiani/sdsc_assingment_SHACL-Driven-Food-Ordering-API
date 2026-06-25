import json
import os
from pathlib import Path
from typing import Any, Dict, List

from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.namespace import SH, RDF as RDFNS

from .form_generator import generate_form_schema
from .validation import validate_payload, ValidationResult


class DishNotFoundError(Exception):
    pass


class DishRegistry:
    def __init__(self, data_root: str):
        self.data_root = Path(data_root)
        self.dishes = self._discover_dishes()

    def _discover_dishes(self) -> Dict[str, Dict[str, Any]]:
        dishes = {}
        for folder in sorted(self.data_root.iterdir()):
            if not folder.is_dir():
                continue
            dish_id = folder.name
            dish_file = folder / "dish.jsonld"
            shape_file = folder / "shape.ttl"
            if dish_file.exists() and shape_file.exists():
                dish_metadata = json.loads(dish_file.read_text(encoding="utf-8"))
                dishes[dish_id] = {
                    "id": dish_id,
                    "metadata": dish_metadata,
                    "shape_path": shape_file,
                    "shape_graph": self._load_shape(shape_file),
                }
        return dishes

    def _load_shape(self, shape_path: Path) -> Graph:
        graph = Graph()
        graph.parse(str(shape_path), format="turtle")
        return graph

    def list_dishes(self) -> List[Dict[str, str]]:
        return [
            {"id": dish_id, "name": data["metadata"].get("label", dish_id)}
            for dish_id, data in self.dishes.items()
        ]

    def get_dish(self, dish_id: str) -> Dict[str, Any]:
        try:
            return self.dishes[dish_id]
        except KeyError:
            raise DishNotFoundError(dish_id)

    def get_schema(self, dish_id: str) -> Dict[str, Any]:
        dish = self.get_dish(dish_id)
        return generate_form_schema(dish["metadata"], dish["shape_graph"])

    def validate_order(self, dish_id: str, payload: Dict[str, Any]) -> ValidationResult:
        dish = self.get_dish(dish_id)
        return validate_payload(payload, dish["shape_graph"])
