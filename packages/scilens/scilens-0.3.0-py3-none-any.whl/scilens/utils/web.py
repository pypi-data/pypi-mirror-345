import requests
from urllib.parse import urlparse
BASE_HEADERS={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
class Web:
	def download(E,url,filename,headers=None):
		A=headers;B=BASE_HEADERS.copy()
		if A:B.update(A)
		C=requests.get(url,headers=B);C.raise_for_status()
		with open(filename,'wb')as D:D.write(C.content)
	def download_progress(L,url,filename,headers=None,callback100=None):
		D=callback100;C=headers;E=BASE_HEADERS.copy()
		if C:E.update(C)
		F=requests.get(url,headers=E,stream=True);I=int(F.headers.get('Content-Length',0));G=0;J=I//100;A=0
		with open(filename,'wb')as K:
			for B in F.iter_content(chunk_size=1024):
				if B:
					K.write(B);G+=len(B);H=G//J
					if H>A:
						A=H
						if D:D(A)