from typing import Any, Dict, List

from rdflib import Graph, URIRef
from rdflib.collection import Collection
from rdflib.namespace import RDF, SH, XSD


def _datatype_to_json_type(datatype: URIRef) -> str:
    if datatype in (XSD.string, XSD.normalizedString, XSD.token):
        return "string"
    if datatype in (XSD.integer, XSD.int, XSD.decimal, XSD.long, XSD.short):
        return "integer"
    if datatype == XSD.boolean:
        return "boolean"
    return "string"


def _get_property_label(graph: Graph, prop: URIRef) -> str:
    return str(prop).split("/")[-1]


def _get_shacl_property_shapes(graph: Graph) -> List[Dict[str, Any]]:
    shapes = []
    for shape in graph.subjects(RDF.type, SH.NodeShape):
        for prop_shape in graph.objects(shape, SH.property):
            path = graph.value(prop_shape, SH.path)
            if path is None:
                continue
            in_values = []
            for in_list in graph.objects(prop_shape, SH['in']):
                try:
                    collection = Collection(graph, in_list)
                    in_values.extend([str(item) for item in collection])
                except Exception:
                    in_values.append(str(in_list))
            shape_def = {
                "path": str(path),
                "datatype": graph.value(prop_shape, SH.datatype),
                "minCount": graph.value(prop_shape, SH.minCount),
                "maxCount": graph.value(prop_shape, SH.maxCount),
                "in": in_values,
            }
            shapes.append(shape_def)
    return shapes


def generate_form_schema(metadata: Dict[str, Any], shapes_graph: Graph) -> Dict[str, Any]:
    fields = []
    for shape in _get_shacl_property_shapes(shapes_graph):
        field_name = shape["path"].split("/")[-1]
        field_schema = {
            "name": field_name,
            "type": _datatype_to_json_type(shape["datatype"])
            if shape["datatype"] is not None
            else "string",
            "required": bool(shape["minCount"] and int(shape["minCount"]) > 0),
        }
        if shape["in"]:
            field_schema["enum"] = [str(item) for item in shape["in"]]
        if shape["maxCount"] is not None and int(shape["maxCount"]) > 1:
            field_schema["maxItems"] = int(shape["maxCount"])
            field_schema["type"] = "array"
        fields.append(field_schema)

    return {
        "id": metadata.get("dish_id"),
        "title": metadata.get("label"),
        "fields": fields,
    }
