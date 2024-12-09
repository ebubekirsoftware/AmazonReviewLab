"""
FastAPI Testing
"""
import requests
link = "https://www.amazon.com.tr/United-Colors-Benetton-Canotta-Schwarz/dp/B07TPWWH77/ref=pd_dp_d_dp_dealz_etdr_d_sccl_2_3/262-4917189-2519604?pd_rd_w=Elb4P&content-id=amzn1.sym.9e180c8f-9e03-45ed-9e8d-a81bde1e57a7&pf_rd_p=9e180c8f-9e03-45ed-9e8d-a81bde1e57a7&pf_rd_r=V8AWKNCDGFFCGC608EEV&pd_rd_wg=fgKo9&pd_rd_r=4f60d549-4049-4d88-b522-c8a9f68cdddd&pd_rd_i=B07TPWWH77&psc=1"
url = "http://127.0.0.1:2121/predict/" # port için app çalıştırırken uvicornla yapılandırdığın port'u gir!!
data = {"link": link}

response = requests.post(url, json=data)
result = response.json()
print(response.json())


