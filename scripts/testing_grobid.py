
# import urllib.request # the things this library does, should also be doable with `requests` ...
from urllib.request import Request, urlopen
import requests


# Had a look at 

# Start GROBID by running:
# docker run --rm --init --ulimit core=0 -p 8670:8070 lfoppiano/grobid:0.8.1

# TODO: let Python provide GROBID with multiple papers with multiprocessing

# TODO: check if server is live at http://assemblix:8670/api/isalive
# If not, make it alive!

# https://grobid.readthedocs.io/en/latest/Grobid-service/#pdf-to-tei-conversion-services

# Used code structure from https://github.com/TenWise-Dev/jrc-public/blob/main/lib/PDF2Tei.py (commit# b90181a805bd7dc5277c5d650bd5b7ffa4fe97be)
pdf_urls = {'23042453' : 'https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC3580294&blobtype=pdf', '25461413': 'https://www.sciencedirect.com/science/article/am/pii/S0160412014003213', '17474521': 'https://academic.oup.com/jaoac/article-pdf/90/2/485/32438101/jaoac0485.pdf', '21410986': 'https://ehjournal.biomedcentral.com/counter/pdf/10.1186/1476-069X-10-19', '15982717': 'https://ir.rcees.ac.cn/bitstream/311016/23222/1/Screening%2031%20endocrine-disrupting...0from%20Beijing%20Guanting%20reservoir.pdf', '22420260': 'https://academic.oup.com/jee/article-pdf/105/1/92/19289243/jee105-0092.pdf', '10868593': 'https://academic.oup.com/jaoac/article-pdf/83/3/680/32415208/jaoac0680.pdf', '32626398': 'https://efsa.onlinelibrary.wiley.com/doi/pdfdirect/10.2903/j.efsa.2019.5797', '39456132': 'https://ntp.niehs.nih.gov/ntp/roc/content/process_508.pdf', '20223083': 'https://academic.oup.com/chromsci/article-pdf/48/3/183/928301/48-3-183.pdf', '21309226': 'https://academic.oup.com/jee/article-pdf/103/6/2061/19244845/jee103-2061.pdf', '32625953': 'https://efsa.onlinelibrary.wiley.com/doi/pdfdirect/10.2903/j.efsa.2018.5306', '25255562': 'https://www.chrom-china.com/CN/article/downloadArticleFile.do?attachType=PDF&id=13653'}
pdf_urls_values = ['https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC3580294&blobtype=pdf','https://www.sciencedirect.com/science/article/am/pii/S0160412014003213', 'https://academic.oup.com/jaoac/article-pdf/90/2/485/32438101/jaoac0485.pdf', 'https://ehjournal.biomedcentral.com/counter/pdf/10.1186/1476-069X-10-19', 'https://ir.rcees.ac.cn/bitstream/311016/23222/1/Screening%2031%20endocrine-disrupting...0from%20Beijing%20Guanting%20reservoir.pdf', 'https://academic.oup.com/jee/article-pdf/105/1/92/19289243/jee105-0092.pdf', 'https://academic.oup.com/jaoac/article-pdf/83/3/680/32415208/jaoac0680.pdf', 'https://efsa.onlinelibrary.wiley.com/doi/pdfdirect/10.2903/j.efsa.2019.5797', 'https://ntp.niehs.nih.gov/ntp/roc/content/process_508.pdf', 'https://academic.oup.com/chromsci/article-pdf/48/3/183/928301/48-3-183.pdf', 'https://academic.oup.com/jee/article-pdf/103/6/2061/19244845/jee103-2061.pdf', 'https://efsa.onlinelibrary.wiley.com/doi/pdfdirect/10.2903/j.efsa.2018.5306', 'https://www.chrom-china.com/CN/article/downloadArticleFile.do?attachType=PDF&id=13653']

pdf_file = ['./papers/paper2.pdf']


# with urllib.request.urlopen(pdf_urls_values[0]) as file:
input_json = {"input" : open(pdf_file[0], "rb").read()}



# pdf_urls_values = ["https://bioinf.nl/~jbeenen/data/paper1.pdf"]
# input_json = {"input" : urllib.request.urlopen(pdf_urls_values[0]).read()}


# # This also works, but is maybe not necessary
# req = Request(
#     url = pdf_urls_values[0],
#     headers = {"User-Agent": "Mozilla/6.0"}
# )
# input_json = {"input" : urlopen(req).read()}

base_url = f'http://assemblix:8670/api'
response = requests.post(base_url + '/processFulltextDocument', files=input_json)

print(response.status_code)