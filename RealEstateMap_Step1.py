"""
The purpose of this application is to retrieve data on houses for sale in a previously identified location,
using a previously identified realtor's website. The code is designed to scrape from that specific website;
this is because the way the data is presented is unique to each real estate company's website. I have only
used one realtor therefore cannot speak to how well (if at all) this would work for a different realtor.

In three parts:
Scrape base data
Add bands
Get geocords

"""
import requests
from bs4 import BeautifulSoup
import pandas
import math

base_url1="https://www.weichert.com/NJ/Union/Scotch_Plains/Listings/Homes/?pg="
#picking the last item (i.e. index -1) tells us last page number, hence how many pages to loop through
req1=requests.get(base_url1+str(1))
cont1=req1.content
soup1=BeautifulSoup(cont1,"html.parser")
lpTarget=soup1.find("span",{"class":"ListingCount"}).text
lastPage=int(lpTarget)/20
lastPage=math.ceil(lastPage)

dicList=[]
cleanAddresses=[]
priceList=[]
bedCount=[]
fullBathCount=[]
halfBathCount=[]
bedBathCount=[]

# function for managing how address data is presented on website
def addressCleanerV7(singleRawAddress):
    decapItemAsList=singleRawAddress.split()
    decapSub=[]
    decapSub.append(decapItemAsList[0]) # add house number without modification
    for item in range(1,len(decapItemAsList)-3): # excludes town and state
        decapSub.append(decapItemAsList[item].capitalize())
        decapAdd=' '.join(decapSub)
        decapAdd=decapAdd+', Scotch Plains, NJ'
    return decapAdd

for page in range(1,int(lastPage+1),1):
    #print(base_url+str(page)+".html")
    req1=requests.get(base_url1+str(page)) #gets content from page
    cont1=req1.content # assigns page content to a variable
    soup1=BeautifulSoup(cont1,"html.parser") # converts page content variable into a BS object

    all1=soup1.find_all("div",{"class":"listingsummary"})

    # iterate through all1 (a list of lists with lots of extraneous text) and pick out key info
    # starting with the address
    for item in all1:
        dic={}
        rawAddress=item.find_all("div",{"class":"address"})[0].text
        cleanAddVar=addressCleanerV7(rawAddress)
        dic["Address"]=cleanAddVar

        housePrice=item.find("div",{"class":"price"}).text.replace("\r","").replace("\n","").replace(" ","")
        dic["Price"]=housePrice

        bedBathVar=item.find("div",{"class":"bedsBath"}).text.replace("|","").split()

        if len(bedBathVar) < 8: # make lists equal lengths for ease of integration into DF
            bedBathVar.append('0')
            bedBathVar.append('half')
            bedBathVar.append('baths')

        bedSub=' '.join(bedBathVar[:2])
        dic["Beds"]=bedSub
        fullBathSub=' '.join(bedBathVar[2:5])
        dic["Full Baths"]=fullBathSub
        halfBathSub=' '.join(bedBathVar[5:])
        dic["Half Baths"]=halfBathSub

        # area and lot size
        areaLotSizeVar=item.find("div",{"class":"size"})
        try:
            areaLotSizeSub=areaLotSizeVar.text.replace("|","").split()
            if len(areaLotSizeSub)==5:
                lotSize=areaLotSizeSub[3]+" acres"
                areaSub=areaLotSize[1]+" sqft"
            if len(areaLotSizeSub)==4:
                areaSub="Not avail."
                lotSize=areaLotSizeSub[1:]
                lotSize=' '.join(lotSize)
            if len(areaLotSizeSub)==3:
                areaSub="Not avail."
                lotSize=areaLotSizeSub[1]+" acres"
        except:
            areaLotSizeSub="Data error"

#        dic["Area"]=areaSub
        dic["Lot Size"]=lotSize

        dicList.append(dic)
df=pandas.DataFrame(dicList)
df=df[["Address","Price","Beds","Full Baths", "Half Baths", "Lot Size"]]
df = df[df.Address != "Address Not Provided, Scotch Plains, NJ"]
df.to_csv("SPRealEstate06252018.csv")
df
