
Background
==========

The growth of which scientific papers are being published every year still keeps on growing 1–3. With the rise of generative artificial intelligence (genAI) in the scientific community 4–6, it is expected that the growth in publication will not decrease for the coming years – even though using genAI for writing papers is currently a taboo in the scientific community 7. This growth makes it each year harder for an interested audience to get a grip of what the current state of knowledge is. Therefore our developed pipeline which can capture scientific publications based on keywords and further process full open access papers into a summary where references to sources are maintained, would be of high value. 
TODO: It can help …. Law makers…

FAQ
---

**Are all academic papers processed?**
    Unfortunately no. Only open access papers are processed that are hosted on websites that do not check for bot activity. 
    Though it is possible for a user to include their pdf papers of interest that they have downloaded themselves, just by placing the paper in `data/pdf_papers`. 
.. warning:: The pipeline is specialized on academic papers only. It cannot be guaranteed that manually added pdf documents of other media types will be processed correctly.

**What part of a paper is being processed?**
    The total full paper is processed, including the abstracts. This makes it possible to query "material and method" related questions as well.

**I'm only interested in peer-reviewed papers. Is there an easy way to apply this as an filter?**
    <in progress..>
