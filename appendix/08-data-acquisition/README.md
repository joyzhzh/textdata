# Large-scale data acquisition

[Webpage](https://textdata.info/toolkit/large-scale-data-acquisition/) · [All components](../README.md)

This folder contains the technical account of this component. The linked webpage provides illustrations and the materials currently available there. This addition does not include the component’s implementation files or underlying datasets.

## Purpose and scope

This workflow makes large textual sources usable for research by connecting acquisition, preparation and verification. The Federal Register collection is a data product produced through that work, distinct from the procedures and software that support its reuse.

## Design and components

The Federal Register adapter retrieves text as served by the Office of the Federal Register and the U.S. Government Publishing Office. The workflow retains original text files and prepares reading copies that preserve document headers. An inventory entry for a document offered only as a PDF records a gap. The historical collection does not contain those PDFs.

The distinction matters for sampling. A document identifier remains available even when no text was retrieved. Where a text file exists, the retrieval site and document header let the researcher check the context of a passage or reconsider a preparation decision.

## Use and outputs

The researcher defines a publication window and retrieves the documents listed in the provider’s index. The Federal Register adapter checks each document’s identifier, records its source and keeps an inventory entry even when the provider supplies no usable text. Reading copies retain document headers and can be traced back to the retrieved text. The workflow packages the files, checks them against the inventory and can compare a new retrieval with an earlier collection. For a study of agency obligations, the inventory defines the documents eligible for sampling and shows which could not be read. Missing text can then be distinguished from a document that contains no relevant obligation.

## Evidence and limitations

The historical inventory covers 806,941 document records from January 2000 through September 15, 2026. The original listing and download programs were not retained, so the historical acquisition cannot be replayed in full. For December 7–8, 2020, the rebuilt workflow returned all 191 identifiers in the historical inventory. Raw files for 169 documents matched the historical record. For the other 22 documents, neither new retrieval matched the historical record, and the historical cause remains unresolved. Comparing the two new retrievals showed that the official sites encoded email addresses differently but yielded identical reading copies for all 191 documents. The test covers one provider and a two-day window. Images remain placeholders, their count is a lower bound, and the checks do not validate content.

## Proposed development

We will extend acquisition and checking procedures to sources identified through the source review.

