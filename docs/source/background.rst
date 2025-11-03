
Background
==========

The growth of which scientific papers are being published every year still keeps on growing 1–3. With the rise of generative artificial intelligence (genAI) in the scientific community 4–6, it is expected that the growth in publication will not decrease for the coming years – even though using genAI for writing papers being a taboo in the scientific community 7. This growth makes it each year harder for an interested audience to get a grip of what the current state of knowledge is. Therefore our developed pipeline called Open Knowledge Explorer (OKE), which can capture scientific publications based on keywords and further process full open access papers into a summary where references to sources are maintained, would be of high value. It can provide insight to general interested public, scholars, and law makers, by helping them to navigate the fast amount of knowledge in an intuitive way (how?).
OKE expands on the knowledge map from TenWise (KMAP) which is a network database containing its own biological/chemical keywords (i.e. concept identifiers) that are all connected via scientific papers in form of PubMed identifiers (PMID) 8. Searching on concept identifiers in KMAP through an application programming interface (KMINE API) therefore yields PMIDs where concepts were mentioned in the abstract.

FAQ
---

.. dropdown:: Dropdown title
    :chevron: down-up

    Dropdown content
    

**Are all academic papers processed?**
    Unfortunately, no. Only open access papers are automatically processed that are hosted on websites that do not check for bot activity. If you like to include other sources as well, then you'll like the answer to the next question. |:wink:|

**Can I manually add my favorite papers?**
    Yes! You will need to have the PDF, its PubMed ID, and associated meta data. Follow this protocol and be successful:
    * Rename the pdf to its PubMed ID.
    * Place the pdf in `data/pdf_papers`.
    * Add the PubMed ID to the pmid experiment file (`pmid_<experiment_name>.csv`) in `data/pmids/`.
    * Add a line to the meta experiment file (`meta_<experiment_name>.csv`) in `data/meta/`, with the associated meta data.

    .. warning:: The pipeline is specialized on academic papers only. It cannot be guaranteed that manually added PDF documents of other media types will be processed correctly.

**What part of a paper is being processed?**
    The full paper is processed, including the abstracts. This makes it possible to query "material and method" related questions as well!

**I'm only interested in peer-reviewed papers. Is there an easy way to apply this as an filter?**
    Yes! Within the exploratory python notebooks it is possible to filter on peer-reviewed paper thanks to the meta data file located in `data/meta`. Whenever we thought is would be applicable, we already added the code for you to do so.

.. dropdown:: **I'm only interested in peer-reviewed papers. Is there an easy way to apply this as an filter?**
    :animated: fade-in
    :chevron: down-up

    Yes! Within the exploratory python notebooks it is possible to filter on peer-reviewed paper thanks to the meta data file located in `data/meta`. Whenever we thought is would be applicable, we already added the code for you to do so.
