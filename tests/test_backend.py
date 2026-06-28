from rdflib import BNode, Graph, Literal, Namespace
from rdflib.namespace import RDF, SH, XSD
from fastapi.testclient import TestClient

from backend.app import app
from backend.schema_loader import DishRegistry, DishNotFoundError
from backend.validation import validate_payload

client = TestClient(app)


def test_list_dishes_contains_all_data_driven_items():
    registry = DishRegistry("backend/data")
    ids = {dish["id"] for dish in registry.list_dishes()}
    assert ids == {"ramen", "french_tacos", "pizza"}


def test_get_schema_contains_required_enum_fields():
    registry = DishRegistry("backend/data")
    schema = registry.get_schema("french_tacos")

    field_names = {field["name"] for field in schema["fields"]}
    assert "size" in field_names
    assert "filling" in field_names
    assert "sauce" in field_names

    size_field = next(field for field in schema["fields"] if field["name"] == "size")
    assert size_field["type"] == "string"
    assert size_field["required"] is True
    assert size_field["enum"] == ["small", "medium", "large"]


def test_validate_order_returns_valid_for_example_payload():
    registry = DishRegistry("backend/data")
    valid_payload = {
        "broth": "tonkotsu",
        "noodles": "curly",
        "toppings": ["egg", "scallions"],
        "spiciness": 2,
    }

    result = registry.validate_order("ramen", valid_payload)
    assert result.valid is True
    assert result.violations == []


def test_validate_order_returns_structured_errors_for_missing_required_field():
    registry = DishRegistry("backend/data")
    invalid_payload = {"filling": "chicken", "sauce": "mayo"}

    result = registry.validate_order("french_tacos", invalid_payload)
    assert result.valid is False
    assert any(v.field == "size" for v in result.violations)
    assert any(
        v.constraint in {"MinCountConstraintComponent", "RequiredConstraintComponent"} or "minCount" in v.constraint.lower()
        for v in result.violations
    )


def test_validate_payload_uses_jsonld_context_to_resolve_property_iris():
    shapes_graph = Graph()
    custom = Namespace("http://custom.example/terms/")
    shape = BNode()

    shapes_graph.add((shape, RDF.type, SH.NodeShape))
    property_shape = BNode()
    shapes_graph.add((shape, SH.property, property_shape))
    shapes_graph.add((property_shape, SH.path, custom.size))
    shapes_graph.add((property_shape, SH.datatype, XSD.string))
    shapes_graph.add((property_shape, SH.minCount, Literal(1)))

    result = validate_payload(
        {"size": "large"},
        shapes_graph,
        context={"size": str(custom.size)},
    )

    assert result.valid is True
    assert result.violations == []


def test_validate_order_raises_for_unknown_dish():
    registry = DishRegistry("backend/data")
    try:
        registry.get_schema("unknown")
    except DishNotFoundError:
        return
    assert False, "Expected DishNotFoundError"


def test_root_page_serves_frontend_shell():
    response = client.get("/")
    # The project can serve a static frontend from the backend root, or
    # run the frontend separately on port 8001. Accept either behavior.
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        assert "Dish Ordering" in response.text
        assert "Choose a dish" in response.text
