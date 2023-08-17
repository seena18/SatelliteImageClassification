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
    def __init__(self,TopRight,BottomLeft,center,arrCoord,type):
        self.TopRight = TopRight
        self.BottomLeft = BottomLeft
        self.center= center
        self.arrCoord=arrCoord
        self.type=type
        self.terrain=None
        self.elevation=None
    def __str__(self):
        return str(self.arrCoord)
    
googleapikey="ENTER_YOUR_API_KEY_FOR_GOOGLE_MAPS"
mapbox="ENTER_YOUR_API_KEY_FOR_MAPBOX"

PADDING = 2
#LONGINC and LATINC are the the units of latitude and longitude which represent the dimensions of a tile.
#When procedurally generating a grid of tiles, adjacent tile coordinates are defined by incrementing or decrement by LONGINC,LATINC
#The distance of one degree of latitude remains fairly constant no matter where you are on Earth. 
#However, degrees of longitude vary greatly in distance depending on where you are on earth.

#TODO: figure out how to convert users tile size preference into bounding box units of latitude and longitude.
#For example if a user wants a tile to be 1 square mile.
#We would want to calculate the appropriate lat and long degrees to represent 1 square mile depending on where the coordinate is located on earth
LONGINC=.0026
LATINC=.0024



#This function basically determines where the start and end point are located relative to one another, and places them in their appropriate corner of the grid
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
    grid[startingTile.arrCoord[0]+ydist][startingTile.arrCoord[1]+xdist]=Tile(-1,-1,endPoint,(-1,-1),"End")
    arr = np.array(grid)
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in arr[::-1,:]]))
    print('\n') 

#This function goes through every other tile on the grid and calculates the center coordinate and bounding box of each tile.
#This is so that the bounding box information of each tile, can later be used with MapBox API to retrive the respective satellite image associated with each tile

#TODO: There is probably a cleaner way to do this
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

#This function retrieves the associated satellite image of each tile in the grid, and uses an image detection model trained on hugging-face to classify what sort of terrain/area the tile is.
#TODO: the hugging-face model returns 5 possible classiffication in order of confidence values. Right now the API, chooses the label of the classification which the model is most confident about.
#However, it may be useful to incorporate all 5 classifications and their confidence values

def identifyGridTiles(grid):
    index=0
    for i in tqdm(grid):
        for j in i:

            response = requests.get(f'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/[{j.BottomLeft["longitude"]},{j.BottomLeft["latitude"]},{j.TopRight["longitude"]},{j.TopRight["latitude"]}]/224x224?padding=0&access_token={mapbox}')
            img = Image.open(BytesIO(response.content))
            img  = img.resize((224, 224))
            # output = open(f'{index}.jpg',"wb")
            # index+=1
            # output.write(response.content)
            # output.close()
            classifier = pipeline("image-classification", model="seena18/tier3_satellite_image_classification")
            j.terrain=classifier(img)[0]["label"]
            response = requests.get(f'https://maps.googleapis.com/maps/api/elevation/json?locations={j.center["latitude"]}%2C{j.center["longitude"]}&key={apikey}')
            print(response.json())

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
    print(response)
    j.elevation=response.json()["results"][0]['elevation']
    res={"coordinates": j.center,"terrain": j.terrain, "elevation": j.elevation}
    return res

app = FastAPI()
#api call for when the user wants to provide a starting point and an endpoint
@app.get("/{startLong}/{startLat}/{endLong}/{endLat}")
async def root(startLong:float,startLat:float,endLong:float,endLat:float):

    #initialize starting point and end point objects
    endPoint={"longitude": endLong, "latitude": endLat}
    startPoint={"longitude": startLong, "latitude": startLat}

    #initialize starting point bounding box objects
    #TR is Top Right corner
    #BL is Bottom Left corner
    startTR={"longitude": startPoint["longitude"] +(LONGINC/2), "latitude":  startPoint['latitude']+(LATINC/2)}
    startBL={"longitude": startPoint["longitude"] -(LONGINC/2), "latitude":  startPoint['latitude']-(LATINC/2)}
    
    #initialize the starting tile object of the grid, with the information from the starting point
    startingTile=Tile(startTR,startBL, startPoint,(0,0),"Start")

    #calculate the x and y components of distance in terms of the number of tiles between the start point and the end point
    xdist=round((endPoint["longitude"]-startPoint["longitude"])/(LONGINC))
    ydist=round((endPoint['latitude']-startPoint['latitude'])/(LATINC) )

    #initialize grid object, the number of tiles in the grid matrix should be atleast as large as the tile-wise distance between the start and end points plus any additional padding.
    #The padding value is currently hardcoded as a global variable into the API to add 1 extra tile of padding around the edges of the grid, but this could easily be change so that user can choose their own padding value.
    grid = [[Tile(-1,-1,-1,(0,0),None) for j in range((abs(xdist)+1+PADDING))] for i in range(abs(ydist)+1+PADDING)]
    
    #initialize start and end point tiles on the grid
    initGrid(grid,xdist,ydist,startingTile,endPoint)
    
    #calculate the coordinates and bounding boxes for the rest of the tiles in the grid that are not starting and ending tiles
    genGridCoords(grid,startingTile)
    
    #go through each tile and evaluate it with the image detection model
    identifyGridTiles(grid)
    return grid

#api call for when the user wants to identify a single coordinate
@app.get("/{startLong}/{startLat}")
async def root(startLong: float,startLat: float):
    startPoint={"longitude": startLong, "latitude": startLat}
    startTR={"longitude": startPoint["longitude"] +(LONGINC/2), "latitude":  startPoint['latitude']+(LATINC/2)}
    startBL={"longitude": startPoint["longitude"] -(LONGINC/2), "latitude":  startPoint['latitude']-(LATINC/2)}
    startingTile=Tile(startTR,startBL, startPoint,(0,0),"Start")
    return identifyCoord(startingTile)

#main function is for testing
def main():
    endPoint={"longitude": .0026, "latitude": .0024}
    startPoint={"longitude": 0, "latitude": 0}
    startTR={"longitude": startPoint["longitude"] +(LONGINC/2), "latitude":  startPoint['latitude']+(LATINC/2)}
    startBL={"longitude": startPoint["longitude"] -(LONGINC/2), "latitude":  startPoint['latitude']-(LATINC/2)}
    startingTile=Tile(startTR,startBL, startPoint,(0,0),"Start")
    xdist=round((endPoint["longitude"]-startPoint["longitude"])/(LONGINC))
    ydist=round((endPoint['latitude']-startPoint['latitude'])/(LATINC) )
    print(xdist,ydist)
    grid = [[Tile(-1,-1,-1,(0,0),None) for j in range((abs(xdist)+1+PADDING))] for i in range(abs(ydist)+1+PADDING)]
    #initialize start and end points on grid
    initGrid(grid,xdist,ydist,startingTile,endPoint)
    genGridCoords(grid,startingTile)
    identifyGridTiles(grid)


main()
#To test the code with the main function without running the API server, use the following linux command