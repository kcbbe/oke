# Testing OpenAlex

"""
The limits are:

max 100,000 calls every day, and also

max 10 requests every second.

We can raise the limit: as an academic researcher it's free. Just send an email to support@openalex.org
https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication
"""

import requests

session = requests.Session()

# NOTE: OpenAlex does not work with bulk PMID requests
# pmid = ['34429776', '3262231', '32943485']
# pmid = '34429776'
pmid = '23042453'

hits_on_concept_ids = [34429776, 6905769, 32625953, 21962330, 24370860, 25205153, 21309226, 585583, 39456132, 24370859, 18023468, 35076356, 32626398, 25035916, 22420260, 18343389, 25461413, 1783584, 39541787, 32625585, 25844860, 17474521, 8997741, 3796654, 38845614, 17679438, 15982717, 10775335, 20223083, 19913234, 15146917, 11884232, 37196509, 33864981, 30586803, 28600808, 25149231, 19165729, 16308868, 9129300, 34425306, 26915710, 25255562, 21936321, 21410986, 20183062, 12192909, 10868593, 32045778, 26466578]
hits_on_concept_ids = [str(i) for i in hits_on_concept_ids]
hits_on_concept_ids = hits_on_concept_ids[:3] # Cap!

# TODO: Refactor!
# NOTE: Query up to 50 ids per request. (we could try more with `&per-page=200`) 200 is the max. per-page. https://blog.ourresearch.org/fetch-multiple-dois-in-one-openalex-api-request/
# If you need more pages, use cursor paging https://docs.openalex.org/how-to-use-the-api/get-lists-of-entities/paging#cursor-paging
# url = f"https://api.openalex.org/works?filter=pmid:{'|'.join(hits_on_concept_ids)},best_open_version:acceptedOrPublished&select=ids,best_oa_location,open_access&mailto=j.beenen@pl.hanze.nl"
url = f"https://api.openalex.org/works?filter=pmid:{'|'.join(hits_on_concept_ids)},best_open_version:acceptedOrPublished&mailto=j.beenen@pl.hanze.nl"

# &filter=best_open_version:acceptedOrPublished



response = session.get(url).json()
results = response['results']


# TODO: turn this into a function
collector = dict()

for r in results:
    pmid = r["ids"]["pmid"].split("/")[-1]

    if r["best_oa_location"]["pdf_url"] is not None:
        collector[pmid] = r["best_oa_location"]["pdf_url"]

    # TODO: Troubleshoot when `pdf_url` is None, how to extract a pdf in an alternative way:
    # # if pdf_url is empty, try landing_page_url by appending "/pdf" to it
    # elif r["best_oa_location"]["pdf_url"] is None:
    #     # try:
    #     collector[pmid] = f'{r["best_oa_location"]["landing_page_url"]}/pdf'
    #     # check if pdf


print(f"Proportion of PMIDs that returned an open access paper: {round(len(results) / len(hits_on_concept_ids) * 100, 2)}%")

print(results)
# for paper in results, check if an oa_url is available.
# NOTE: `oa_url` can refer to a html or a pdf! (-> `best_oa_location` > 'pdf_url' might be better!! But is not always available.. Then try to include `landing_page_url`)
# (Maybe combine it with `is_accepted`? https://docs.openalex.org/api-entities/works/work-object/location-object#is_accepted !! ALSO SEE https://docs.openalex.org/api-entities/works/work-object/location-object#version))
# (^^ this can be done in the API: https://docs.openalex.org/api-entities/works/filter-works#best_open_version)
# `?filter=best_open_version:acceptedOrPublished`
# `?select=best_oa_location`
# EXAMPLE: https://pmc.ncbi.nlm.nih.gov/articles/PMC8370139/ or https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC3580294&blobtype=pdf 
# Maybe this ^ can be solved by ending a url with 
# 1) check if url ends with 'pdf',
# 2) if it does not, add '/pdf' to the url

# `has_fulltext = True` ?? NOPE: https://docs.openalex.org/api-entities/works/work-object#has_fulltext
# 'fulltext_origin' = 'ngrams'
