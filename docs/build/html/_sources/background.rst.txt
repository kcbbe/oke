
Background
==========

The annual growth in scientific publications continues to accelerate making it an exemplary case of big data (Bornmann & Mutz, 2015; González-Márquez et al., 2024; Larsen & von Ins, 2010). With the increasing use of generative artificial intelligence (genAI) within the scientific community (Gray, 2024; Kobak et al., 2024; Liang et al., 2024), this trend is unlikely to decline in the coming years – despite the ongoing debate and perceived taboo surrounding the use of genAI for scientific writing (Kwon, 2025). As the body of literature expands, maintaining a coherent overview of current knowledge becomes progressively more challenging and time consuming for researchers, clinicians, policymakers, and other stakeholders. Text mining approaches offer a means to provide structure in the overwhelming scientific landscape (Gonzalez et al., 2015).
To address this issue, the Open Knowledge Explorer (OKE) was developed as a modular text-mining pipeline designed to capture full open-access scientific publications by extracting and embedding their sentences, preserving provenance, and constructing a cosine similarity graph for downstream analysis. The OKE pipeline accepts user defined query terms, identifies relevant papers through the TenWise Knowledge Map (KMAP), retrieves full texts by locating PDF URLs through the OpenAlex database (Priem et al., 2022), converts PDF to XML using GROBID, and embeds sentences using a biomedical SBERT model. These representations can in turn be explored via semantic search, clustering methods, and similarity-based visualisations. Importantly, the OKE preserves traceability by linking each sentence to its original location within the source paper, thereby enabling transparent analytical workflows (see infographic in Figure 1). Metadata-based filtering is supported throughout the pipeline.

.. image:: ./docs/source/infographic.png

*Figure 1: Infographic providing an overview of the workflow. Keywords are supplied by the user, after which full open-access papers are downloaded and sentences processed into a corpus, that are embedded by SBERT to generate semantic representations where provenance of sentences is preserved.*

Frequently Asked Questions
--------------------------

.. dropdown:: **Are all academic papers processed?**
    :open:

    Unfortunately, no. Only open access papers are automatically processed that are hosted on websites and do not check for bot activity. If you like to include other sources as well, then you'll like the answer to the next question. |:wink:|

.. dropdown:: **Can I manually feed papers to the pipeline?**

    Yes! You will need to have the PDF, its PubMed ID, and associated meta data. Please follow this protocol and be successful:
        
        - Rename the PDF to its PubMed ID.
        - Place the PDF in `data/pdf_papers`.
        - Add the PubMed ID to the PMID experiment file (`pmid_<experiment_name>.csv`) in `data/pmids/`.
        - Add a line to the meta experiment file (`meta_<experiment_name>.csv`) in `data/meta/`, with the associated meta data.

    .. warning:: The pipeline is specialized on academic papers only. It cannot be guaranteed that manually added PDF documents of other media types will be processed correctly.

.. dropdown:: **What part of a paper is being processed?**

    The full paper is processed, including the abstracts. This makes it possible to query "material and method" related questions as well!

.. dropdown:: **I'm only interested in peer-reviewed papers. Is there an easy way to apply this as an filter?**

    Yes! Within the exploratory python notebooks it is possible to filter on peer-reviewed paper thanks to the meta data file located in `data/meta`. Whenever we thought is would be applicable, we already added the code for you to do so.
