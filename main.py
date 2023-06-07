from transformers import AutoFeatureExtractor, AutoModelForImageClassification
from transformers import pipeline
from PIL import Image
import requests
from pprint import pprint
from io import BytesIO
import numpy as np
from collections import deque as queue
import copy
from tqdm import tqdm
from fastapi import FastAPI
from fastapi import FastAPI, Request


def isEndpoint(nextTile,endpoint):
  if nextTile==-1:
    return False
  elif FindPoint(nextTile.BottomLeft.longitude,nextTile.BottomLeft.latitude,
                 nextTile.TopRight.longitude,nextTile.TopRight.latitude,
                 endpoint.longitude,endpoint.latitude):
     return True
  else:
     return False
def isValid(cell, row, col,bound1,bound2):
   
    # If cell lies out of bounds
    if (row < 0 or col < 0 or row >= bound1 or col >= bound2):
        return False
 
    # If cell is already visited
    if (cell.visited==True):
        return False
 
    # Otherwise
    return True


def FindPoint(x1, y1, x2,
              y2, x, y):
    if withinLong(x1, x2, x) and withinLat(y1, y2, y):
        return True
    else:
        return False
def withinLong(x1, x2, x):
    if x >= x1 and x <= x2 :
        return True
    else:
        return False
    
def withinLat(y1, y2, y):
    if y >= y1 and y <= y2:
        return True
    else:
        return False
class Tile:
    center: dict
    def __init__(self, north, south,east,west,TopRight,BottomLeft,center,arrCoord,type):
        self.TopRight = TopRight
        self.BottomLeft = BottomLeft
        self.center= center
        self.arrCoord=arrCoord
        self.type=None
        self.terrain=None
        self.elevation=None
    def __str__(self):
        return str(self.arrCoord)
    

apikey="AIzaSyB7iQIx-AjD_yFaoXt-yK8PiXsD7eKw6EA"
mapqkey="Ps637jCnjAil3mRyCsuQT98Qss6iIsIK"
mapbox="pk.eyJ1Ijoic2VlbmExOCIsImEiOiJjbGk2Z2ozc3IyM2kyM2Rtdm5uaTBsd2Q4In0.9UZWXUge8N72-5ZRDgFBFA"
PADDING = 2
LONGINC=.0026
LATINC=.0024




def initGrid(grid,xdist,ydist,startingTile,endPoint):
    if(xdist>=0):
        if(ydist>=0):
            grid[int(PADDING/2)][int(PADDING/2)]=startingTile
            startingTile.arrCoord=(int(PADDING/2),int(PADDING/2))
        else:
            grid[abs(ydist)+int(PADDING/2)][int(PADDING/2)]=startingTile
            startingTile.arrCoord=(abs(ydist)+int(PADDING/2),int(PADDING/2))
    else:
        if(ydist>=0):
            grid[int(PADDING/2)][abs(xdist)+int(PADDING/2)]=startingTile
            startingTile.arrCoord=(int(PADDING/2),abs(xdist)+int(PADDING/2))
        else:
            grid[abs(ydist)+int(PADDING/2)][abs(xdist)+int(PADDING/2)]=startingTile
            startingTile.arrCoord=(abs(ydist)+int(PADDING/2),abs(xdist)+int(PADDING/2),)
    print(startingTile.arrCoord)   
    grid[startingTile.arrCoord[0]+ydist][startingTile.arrCoord[1]+xdist]=Tile(-1,-1,-1,-1,-1,-1,endPoint,(-1,-1),"End")
    arr = np.array(grid)
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in arr[::-1,:]]))
    print('\n') 

def genGridCoords(grid,startingTile):
    accumTR=copy.copy(startingTile.TopRight)
    accumBL=copy.copy(startingTile.BottomLeft)
    accumCenter=copy.copy(startingTile.center)
    for i in range(startingTile.arrCoord[0],len(grid)):
        accumTR["latitude"]+=LATINC
        accumBL["latitude"]+=LATINC
        accumCenter["latitude"]+=LATINC
        accumTR["longitude"]=startingTile.TopRight["longitude"]
        accumBL["longitude"]=startingTile.BottomLeft["longitude"]
        accumCenter["longitude"]=startingTile.center["longitude"]
        for j in range(startingTile.arrCoord[1],len(grid[0])):
            if( (i==startingTile.arrCoord[0] and j==startingTile.arrCoord[1])):
                accumTR["latitude"]-=LATINC
                accumBL["latitude"]-=LATINC
                accumCenter["latitude"]-=LATINC
            else:
                if(j!=startingTile.arrCoord[1]):
                    accumTR["longitude"]+=LONGINC
                    accumBL["longitude"]+=LONGINC
                    accumCenter["longitude"]+=LONGINC
                grid[i][j].arrCoord=(i,j)
                grid[i][j].TopRight=copy.copy(accumTR)
                grid[i][j].BottomLeft=copy.copy(accumBL)
                grid[i][j].center=copy.copy(accumCenter)
                
        print("")

    accumTR=copy.copy(startingTile.TopRight)
    accumBL=copy.copy(startingTile.BottomLeft)
    accumCenter=copy.copy(startingTile.center)
    for i in range(startingTile.arrCoord[0]-1,-1,-1):
        accumTR["latitude"]-=LATINC
        accumBL["latitude"]-=LATINC
        accumCenter["latitude"]-=LATINC
        accumTR["longitude"]=startingTile.TopRight["longitude"]
        accumBL["longitude"]=startingTile.BottomLeft["longitude"]
        accumCenter["longitude"]=startingTile.center["longitude"]
        for j in range(startingTile.arrCoord[1]-1,-1,-1):
            if( (i==startingTile.arrCoord[0] and j==startingTile.arrCoord[1])):
                accumTR["latitude"]+=LATINC
                accumBL["latitude"]+=LATINC
                accumCenter["latitude"]+=LATINC
            else:
                if(j!=startingTile.arrCoord[1]):
                    accumTR["longitude"]-=LONGINC
                    accumBL["longitude"]-=LONGINC
                    accumCenter["longitude"]-=LONGINC
                grid[i][j].arrCoord=(i,j)
                grid[i][j].TopRight=copy.copy(accumTR)
                grid[i][j].BottomLeft=copy.copy(accumBL)
                grid[i][j].center=copy.copy(accumCenter)
        print("")

    accumTR=copy.copy(startingTile.TopRight)
    accumBL=copy.copy(startingTile.BottomLeft)
    accumCenter=copy.copy(startingTile.center)
    for i in range(startingTile.arrCoord[0],len(grid)):
        accumTR["latitude"]+=LATINC
        accumBL["latitude"]+=LATINC
        accumCenter["latitude"]+=LATINC
        accumTR["longitude"]=startingTile.TopRight["longitude"]
        accumBL["longitude"]=startingTile.BottomLeft["longitude"]
        accumCenter["longitude"]=startingTile.center["longitude"]
        for j in range(startingTile.arrCoord[1],-1,-1):
            if( (i==startingTile.arrCoord[0] and j==startingTile.arrCoord[1])):
                accumTR["latitude"]-=LATINC
                accumBL["latitude"]-=LATINC
                accumCenter["latitude"]-=LATINC
            else:
                if(j!=startingTile.arrCoord[1]):
                    accumTR["longitude"]-=LONGINC
                    accumBL["longitude"]-=LONGINC
                    accumCenter["longitude"]-=LONGINC
                grid[i][j].arrCoord=(i,j)
                grid[i][j].TopRight=copy.copy(accumTR)
                grid[i][j].BottomLeft=copy.copy(accumBL)
                grid[i][j].center=copy.copy(accumCenter)

        print("")
    accumTR=copy.copy(startingTile.TopRight)
    accumBL=copy.copy(startingTile.BottomLeft)
    accumCenter=copy.copy(startingTile.center)
    for i in range(startingTile.arrCoord[0]-1,-1,-1):
        accumTR["latitude"]-=LATINC
        accumBL["latitude"]-=LATINC
        accumCenter["latitude"]-=LATINC
        accumTR["longitude"]=startingTile.TopRight["longitude"]
        accumBL["longitude"]=startingTile.BottomLeft["longitude"]
        accumCenter["longitude"]=startingTile.center["longitude"]
        for j in range(startingTile.arrCoord[1],len(grid[0])):
            if( (i==startingTile.arrCoord[0] and j==startingTile.arrCoord[1])):
                accumTR["latitude"]-=LATINC
                accumBL["latitude"]-=LATINC
                accumCenter["latitude"]-=LATINC
            else:
                if(j!=startingTile.arrCoord[1]):
                    accumTR["longitude"]+=LONGINC
                    accumBL["longitude"]+=LONGINC
                    accumCenter["longitude"]+=LONGINC
                grid[i][j].arrCoord=(i,j)
                grid[i][j].TopRight=copy.copy(accumTR)
                grid[i][j].BottomLeft=copy.copy(accumBL)
                grid[i][j].center=copy.copy(accumCenter)
        print("")
    arr = np.array(grid)
    print('\n')           
    print('\n'.join(['\t'.join([(str(cell)) for cell in row]) for row in arr[::-1,:]]))
    print('\n')  
    print('\n')  
    print('\n')

def identifyGridTiles(grid):
    for i in tqdm(grid):
        for j in i:

            response = requests.get(f'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/[{j.BottomLeft["longitude"]},{j.BottomLeft["latitude"]},{j.TopRight["longitude"]},{j.TopRight["latitude"]}]/224x224?padding=0&access_token={mapbox}')
            img = Image.open(BytesIO(response.content))
            img  = img.resize((224, 224))
            classifier = pipeline("image-classification", model="seena18/tier3_satellite_image_classification")
            j.terrain=classifier(img)[0]["label"]
            response = requests.get(f'https://maps.googleapis.com/maps/api/elevation/json?locations={j.center["latitude"]}%2C{j.center["longitude"]}&key={apikey}')
            j.elevation=response.json()["results"][0]['elevation']
    print("")
    print("")
    for i in tqdm(reversed(grid)):
        for j in i:
            if j.type!=-1:
                print(j.terrain,j.elevation,j.type, end="\t\t")
            else:
                print(j.terrain,j.elevation, end="\t\t")
        print("")

def identifyCoord(tile):
    index=0
    j=tile
    response = requests.get(f'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/[{j.BottomLeft["longitude"]},{j.BottomLeft["latitude"]},{j.TopRight["longitude"]},{j.TopRight["latitude"]}]/224x224?padding=0&access_token={mapbox}')
    img = Image.open(BytesIO(response.content))
    img  = img.resize((224, 224))
    classifier = pipeline("image-classification", model="seena18/tier3_satellite_image_classification")
    j.terrain=classifier(img)[0]["label"]
    response = requests.get(f'https://maps.googleapis.com/maps/api/elevation/json?locations={j.center["latitude"]}%2C{j.center["longitude"]}&key={apikey}')
    j.elevation=response.json()["results"][0]['elevation']
    res={"coordinates": j.center,"terrain": j.terrain, "elevation": j.elevation}
    return res

app = FastAPI()

@app.get("/{startLong}/{startLat}/{endLong}/{endLat}")
async def root(startLong:float,startLat:float,endLong:float,endLat:float):

    endPoint={"longitude": endLong, "latitude": endLat}
    startPoint={"longitude": startLong, "latitude": startLat}
    startTR={"longitude": startPoint["longitude"] +(LONGINC/2), "latitude":  startPoint['latitude']+(LATINC/2)}
    startBL={"longitude": startPoint["longitude"] -(LONGINC/2), "latitude":  startPoint['latitude']-(LATINC/2)}
    startingTile=Tile(-1,-1,-1,-1,
    startTR,startBL, startPoint,(0,0),"Start")
    xdist=round((endPoint["longitude"]-startPoint["longitude"])/(LONGINC))
    ydist=round((endPoint['latitude']-startPoint['latitude'])/(LATINC) )
    print(xdist,ydist)
    grid = [[Tile(-1,-1,-1,-1,-1,-1,-1,(0,0),None) for j in range((abs(xdist)+1+PADDING))] for i in range(abs(ydist)+1+PADDING)]
    #initialize start and end points on grid
    initGrid(grid,xdist,ydist,startingTile,endPoint)
    genGridCoords(grid,startingTile)
    identifyGridTiles(grid)
    return grid

@app.get("/{startLong}/{startLat}")
async def root(startLong: float,startLat: float):
    startPoint={"longitude": startLong, "latitude": startLat}
    startTR={"longitude": startPoint["longitude"] +(LONGINC/2), "latitude":  startPoint['latitude']+(LATINC/2)}
    startBL={"longitude": startPoint["longitude"] -(LONGINC/2), "latitude":  startPoint['latitude']-(LATINC/2)}
    startingTile=Tile(-1,-1,-1,-1,
    startTR,startBL, startPoint,(0,0),"Start")
    return identifyCoord(startingTile)



def main():
    endPoint={"longitude": .0026, "latitude": .0024}
    startPoint={"longitude": 0, "latitude": 0}
    startTR={"longitude": startPoint["longitude"] +(LONGINC/2), "latitude":  startPoint['latitude']+(LATINC/2)}
    startBL={"longitude": startPoint["longitude"] -(LONGINC/2), "latitude":  startPoint['latitude']-(LATINC/2)}
    startingTile=Tile(-1,-1,-1,-1,
    startTR,startBL, startPoint,(0,0),"Start")
    xdist=round((endPoint["longitude"]-startPoint["longitude"])/(LONGINC))
    ydist=round((endPoint['latitude']-startPoint['latitude'])/(LATINC) )
    print(xdist,ydist)
    grid = [[Tile(-1,-1,-1,-1,-1,-1,-1,(0,0),-1) for j in range((abs(xdist)+1+PADDING))] for i in range(abs(ydist)+1+PADDING)]
    #initialize start and end points on grid
    initGrid(grid,xdist,ydist,startingTile,endPoint)
    genGridCoords(grid,startingTile)
    identifyGridTiles(grid)

