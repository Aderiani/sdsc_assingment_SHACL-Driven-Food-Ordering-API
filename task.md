## SHACL-Driven Food Ordering API

## Background

The goal of this task is to build a small but complete food-ordering application where the backend
drives the form logic usingJSON-LDdocuments andSHACL shapes. The frontend is optional
and should be minimal and simple. Its only job is to display what the backend provides. The
backend can be written in a language of your choice.

## Task

Build a prototype service that exposes a small API for configuring and ordering two dishes:
French Tacos and Ramen.
The backend should store the JSON-LD documents and SHACL shapes for each dish.
The SHACL shapes should define the relevant form constraints, such as required fields, allowed
values, cardinality, and simple validation rules.

[](https://clinicaltables.nlm.nih.gov/ "https://clinicaltables.nlm.nih.gov/")

The backend should expose the form definition in a machine-readable format consumable by a
frontend, for example JSON Forms schema + UI schema. The translation from SHACL/JSON-LD
to this format should happen exclusively on the backend.

### The backend should expose at minimum:

* an endpoint to retrieve the form schema for a given dish;
* an endpoint to submit and validate a filled-in form.
* Validation should happen on the backend.
* When the user submits the form, the backend validates the payload against the SHACL shapes and returns structured errors if constraints are violated.

### The frontend should be minimal:

* it should allow the user to select a dish, render the schema returned by the backend, submit the form data, and display either confirmation or validation errors.
* The frontend should not contain dish-specific form logic or definitions.
* No persistence is required.

### Support a third dish of your choice, added purely through a new JSON-LD

document and SHACL shape on the backend, with zero frontend changes required. This will
demonstrate the strength of the architecture.
Include a short written section explaining your SHACL/JSON-LD modelling choices, how the
translation to the frontend form schema works, and any limitations or assumptions.

## Format

* Present your work in a repository (GitHub or GitLab).
* Follow development best practices: the project must be reproducible, well-documented, and include a clear README with setup instructions.

## What We Will Be Looking At

* Backend architecture: Clean, well-structured SHACL/JSON-LD processing that is easy to extend.
* Separationofconcerns: Adding a new dish should not require frontend changes or
  hardcoded frontend form logic.
* Validation: SHACL-based validation should be meaningful, with clear structured errors.
* Approach to testing: Evidence that valid and invalid submissions were tested.
* Reproducibility:The repository can be cloned and run without guesswork
