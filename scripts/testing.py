# Testing OpenAlex

import requests

session = requests.Session()

# NOTE: OpenAlex does not work with bulk PMID requests
# pmid = ['34429776', '3262231', '32943485']
# pmid = '34429776'
pmid = '23042453'

hits_on_concept_ids = [34429776, 6905769, 32625953, 21962330, 24370860, 25205153, 21309226, 585583, 39456132, 24370859, 18023468, 35076356, 32626398, 25035916, 22420260, 18343389, 25461413, 1783584, 39541787, 32625585, 25844860, 17474521, 8997741, 3796654, 38845614, 17679438, 15982717, 10775335, 20223083, 19913234, 15146917, 11884232, 37196509, 33864981, 30586803, 28600808, 25149231, 19165729, 16308868, 9129300, 34425306, 26915710, 25255562, 21936321, 21410986, 20183062, 12192909, 10868593, 32045778, 26466578]
hits_on_concept_ids = hits_on_concept_ids[:10] # Cap!

# url = f"https://api.openalex.org/works?filter=pmid:{','.join(pmid)}&mailto=j.beenen@pl.hanze.nl"
# url = f"https://api.openalex.org/works?filter=pmid:{','.join(pmid)}"
url = f"https://api.openalex.org/works?filter=ids.pmid:{pmid}&mailto=j.beenen@st.hanze.nl"


# for 



response = requests.get(url).json()
results = response['results']

print(results)
# for paper in results, check if an oa_url is available.
# NOTE: `oa_url` can refer to a html or a pdf! (-> `best_oa_location` > 'pdf_url' might be better!! (Maybe combine it with `is_accepted`? https://docs.openalex.org/api-entities/works/work-object/location-object#is_accepted !! ALSO SEE https://docs.openalex.org/api-entities/works/work-object/location-object#version))
# EXAMPLE: https://pmc.ncbi.nlm.nih.gov/articles/PMC8370139/ or https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC3580294&blobtype=pdf 
# Maybe this ^ can be solved by ending a url with 
# 1) check if url ends with 'pdf',
# 2) if it does not, add '/pdf' to the url

# `has_fulltext = True` ?? NOPE: https://docs.openalex.org/api-entities/works/work-object#has_fulltext
# 'fulltext_origin' = 'ngrams'
