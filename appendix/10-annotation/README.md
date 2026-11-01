# LLM-annotation workflow

[Webpage](https://textdata.info/toolkit/llm-annotation-workflow/) · [All components](../README.md)

This folder contains the technical account of this component. The linked webpage provides illustrations and the materials currently available there. This addition does not include the component’s implementation files or underlying datasets.

## Purpose and scope

This prototype connects a defined coding task to source-linked candidate annotations. It supports questions about who is assigned to do what in organizational documents, while keeping a stated responsibility distinct from observed behavior.

## Design and components

The package combines a codebook, preserved passages, versioned requests, retained model responses and tools for checking and exporting results. The model proposes actors, actions and qualifications; software checks whether quotations and passage identities match the source. The researcher assesses the interpretation.

The codebook distinguishes mandatory, discretionary, prohibited, recommended and unresolved relations. It records responsible actors separately from actors who are consulted or receive an output, and retains conditions, deadlines and exceptions. A passage with no assignment receives a substantive negative classification, distinct from an unresolved interpretation or a failed model response.

## Use and outputs

To study how organizations assign responsibility, the researcher selects passages and supplies the document and codebook. The software prepares a request for each passage with the full document as context. Candidate responses are supplied separately. The export checks quotations against the source, records the selected occurrence when words recur, and distinguishes a missing response from a judgment that the passage assigns nothing. In section 5(c)(ii) of Executive Order 13960, agencies must “strive to implement the approved plans” within 180 days of approval, “subject to existing resource levels.” The feature table distinguishes the agencies responsible for acting from the body that coordinates their work and preserves both qualifications.

## Evidence and limitations

The demonstration covers five selected passages of the order. The export reproduces four candidate mandatory relations and one no-assignment record from the saved responses. The assistant that developed the codebook and software produced the responses in the same interactive session. The software itself makes no model calls, and the backend model and settings are unknown. Two synthetic error cases show why source checks cannot establish coding accuracy. One substitutes a consulted party for the responsible actor. The other omits an assignment. Both pass the checks. No independent reference coding or repeated model run exists. Evaluating whole passages, including omitted relations, remains proposed.

## Proposed development

We will obtain independent reference annotations and evaluate accuracy and consistency before scaling.

