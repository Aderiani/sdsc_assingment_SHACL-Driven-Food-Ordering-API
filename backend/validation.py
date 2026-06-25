from dataclasses import asdict, dataclass
from typing import Any, Dict, List

from pyshacl import validate
from rdflib import BNode, Graph, Literal, Namespace
from rdflib.namespace import RDF, SH, XSD


@dataclass
class ValidationViolation:
    field: str
    constraint: str
    message: str


@dataclass
class ValidationResult:
    valid: bool
    violations: List[ValidationViolation]


@dataclass
class ValidationErrorResponse:
    valid: bool
    errors: List[Dict[str, Any]]

    @classmethod
    def from_validation_result(cls, result: ValidationResult) -> "ValidationErrorResponse":
        return cls(valid=False, errors=[asdict(v) for v in result.violations])


def _extract_violations(shacl_graph: Graph) -> List[ValidationViolation]:
    violations = []
    for result in shacl_graph.subjects(RDF.type, SH.ValidationResult):
        focus_node = str(shacl_graph.value(result, SH.focusNode) or "")
        result_path = str(shacl_graph.value(result, SH.resultPath) or "")
        message = str(shacl_graph.value(result, SH.resultMessage) or "Validation failed")
        constraint = str(shacl_graph.value(result, SH.sourceConstraintComponent) or "sh:Constraint")

        if result_path:
            field = result_path.split("/")[-1]
        else:
            field = focus_node.split("/")[-1]

        violations.append(
            ValidationViolation(field=field, constraint=constraint, message=message)
        )
    return violations


def _payload_to_graph(payload: Dict[str, Any], shapes_graph: Graph) -> Graph:
    data_graph = Graph()
    ex = Namespace("http://example.com/vocab/")
    subject = BNode()

    for key, value in payload.items():
        predicate = ex[key]
        if isinstance(value, list):
            for item in value:
                data_graph.add((subject, predicate, Literal(item)))
        elif isinstance(value, bool):
            data_graph.add((subject, predicate, Literal(value)))
        elif isinstance(value, int):
            data_graph.add((subject, predicate, Literal(value, datatype=XSD.integer)))
        else:
            data_graph.add((subject, predicate, Literal(value)))

    for shape in shapes_graph.subjects(RDF.type, SH.NodeShape):
        target_class = shapes_graph.value(shape, SH.targetClass)
        if target_class is not None:
            data_graph.add((subject, RDF.type, target_class))
            break

    return data_graph


def validate_payload(payload: Dict[str, Any], shapes_graph: Graph) -> ValidationResult:
    data_graph = _payload_to_graph(payload, shapes_graph)

    conforms, report_graph, report_text = validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',
        abort_on_first=False,
        meta_shacl=False,
        debug=False,
    )

    if conforms:
        return ValidationResult(valid=True, violations=[])

    return ValidationResult(valid=False, violations=_extract_violations(report_graph))
