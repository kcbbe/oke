
# import urllib.request # the things this library does, should also be doable with `requests` ...
from urllib.request import Request, urlopen
import requests

# Start GROBID by running:
# docker run --rm --init --ulimit core=0 -p 8670:8070 lfoppiano/grobid:0.8.1

# TODO: let Python provide GROBID with multiple papers with multiprocessing

# TODO: check if server is live at http://assemblix:8670/api/isalive NOTE: <- Is dit gevoelige informatie?????
# If not, make it alive!

# https://grobid.readthedocs.io/en/latest/Grobid-service/#pdf-to-tei-conversion-services


# Used code structure from https://github.com/TenWise-Dev/jrc-public/blob/main/lib/PDF2Tei.py (commit# b90181a805bd7dc5277c5d650bd5b7ffa4fe97be)
pdf_urls = {'39456132': 'https://ntp.niehs.nih.gov/ntp/roc/content/process_508.pdf', '21309226': 'https://academic.oup.com/jee/article-pdf/103/6/2061/19244845/jee103-2061.pdf', '32625953': 'https://efsa.onlinelibrary.wiley.com/doi/pdfdirect/10.2903/j.efsa.2018.5306'}
pdf_urls = [pdf_urls[k]for k in pdf_urls]
# NOTE: pdf_url incl. urls that do not refer to a pdf.....
# with urllib.request.urlopen(pdf_urls_values[0]) as file:
# input_json = {"input" : open(pdf_file[0], "rb").read()}



# pdf_urls_values = ["https://bioinf.nl/~jbeenen/data/paper1.pdf"]
# input_json = {"input" : urllib.request.urlopen(pdf_urls_values[0]).read()}

# TODO: pickle all input_json, `filename` = `pmid` (So that the documents remain accessible if it is ever removed from online)

# This also works, but is maybe not necessary
req = Request(
    url = pdf_urls[0],
    headers = {"User-Agent": "Mozilla/6.0"}
)
input_json = {"input" : urlopen(req).read()}

response = requests.post('http://assemblix:8670/api/processFulltextDocument', files=input_json)

print(response.status_code)
