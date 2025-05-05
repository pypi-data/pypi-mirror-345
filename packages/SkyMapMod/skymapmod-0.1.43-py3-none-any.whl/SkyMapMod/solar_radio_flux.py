import requests
import numpy as np

url = "https://www.spaceweather.gc.ca/solar_flux_data/daily_flux_values/fluxtable.txt"
response = requests.get(url)

a = response.text
a = a.split('\n')

fluxdate = []
fluxtime = []
fluxjulian = []
fluxcarrington = []
fluxobsflux = []
fluxadjflux = []
fluxursi = []
for i in range(2, len(a)-1):
    fluxdate.append(a[i].split()[0])
    fluxtime.append(a[i].split()[1])
    fluxjulian.append(a[i].split()[2])
    fluxcarrington.append(a[i].split()[3])
    fluxobsflux.append(a[i].split()[4])
    fluxadjflux.append(a[i].split()[5])
    fluxursi.append(a[i].split()[6])

fluxdate = np.array(fluxdate)
fluxtime = np.array(fluxtime)
fluxjulian = np.array(fluxjulian)
fluxcarrington = np.array(fluxcarrington)
fluxobsflux = np.array(fluxobsflux)
fluxadjflux = np.array(fluxadjflux)
fluxursi = np.array(fluxursi)