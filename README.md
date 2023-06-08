<a name="br1"></a> 

**Map Classiﬁcaꢀon API Manual and Documentaꢀon**

**Seena Abed**

**June 08, 2023**

[**hꢁps://satelliteimageclassiﬁcaꢀon-producꢀon.up.railway.app/docs**](https://satelliteimageclassification-production.up.railway.app/docs)



<a name="br2"></a> 

**Background**

The map classiﬁcaꢀon API provides two endpoints which return terrain and elevaꢀon data given laꢀtude

and longitude informaꢀon of a map.

Currently the API converts given coordinates into ꢀles of approximately .017 square miles, this is about

.0026 degrees longitude and .00024 degrees laꢀtude in North America. This value has been arbitrarily

chosen and may be allowed to be variably adjusted in future rendiꢀons.

**A ꢀle at the bare minimum has the following aꢁributes:**

**Field**

**Descripꢀon**

TopRight

coordinates of the top right corner of the ꢀle’s

bounding box

BoꢁomLeꢂ

Center

coordinates of the boꢁom leꢂ corner of the ꢀle’s

bounding box

coordinates of the center of ꢀle

**For Example**:

When given a center coordinate of (Longitude: -120.6633, Laꢀtude: 35.3006).

The API will produce a ꢀle with To p Right bounding box coordinates of (Longitude: -120.6618,

Laꢀtude: 35.3018) and Boꢁom Leꢂ bounding box coordinates of (Longitude: -120.6644,

Laꢀtude: 35.3994)

(Longitude: -120.6618,

Laꢀtude: 35.3018)

(Longitude: -120.6633,

Laꢀtude: 35.3006)

Approx.

.0024

degrees

laꢀtude

(Longitude: -120.6644,

Approx. .0026 degrees longitude

Laꢀtude: 35.3994)

Tiles are then used diﬀerently depending which API endpoint is being uꢀlized.



<a name="br3"></a> 

**Endpoints**

**Grid Generaꢀon and Classiﬁcaꢀon Endpoint:**

**hꢁps://satelliteimageclassiﬁcaꢀon-producꢀon.up.railway.app/{startLong}/{startLat}/{endLong}/{endLat}**

This API endpoint will return a JSON structure represenꢀng a 2-dimensional grid of ꢀles of the area

encompassing the two given coordinates. Each ꢀle in the grid will include elevaꢀon data and will have

been classiﬁed using a satellite image classiﬁcaꢀon model. The grid includes padding as well as to avoid

having start and end coordinates tucked into corners.

**Procedure:**

\-

Given start and end coordinates. The API generates a 2-dimensional list of ꢀles with the start and

end ꢀles placed relaꢀve to one another as well as a layer of ꢀles which serve as padding around

the edges.

\-

\-

The API then procedurally ﬁlls in the bounding box and coordinate informaꢀon of every empty

ꢀle in the grid. (Any element that isn’t the start or end ꢀle)

For each ꢀle in the grid, the API obtains a staꢀc satellite image using MapBox API and classiﬁes

the image using a classiﬁcaꢀon model, at the same ꢀme, it also obtains the elevaꢀon data of the

ꢀle using google maps API

\-

The resulꢀng grid with the classiﬁcaꢀon and elevaꢀon data is returned as a server response.

**Basic visual Representaꢀon of the process:**

Detached

House

Elevaꢀon: 100 Elevaꢀon: 100

Detached

House

Detached

House

Elevaꢀon: 100

Detached

House

Elevaꢀon: 100

Road

Elevaꢀon: 100

Padding

Detached

House

Elevaꢀon: 100 Elevaꢀon: 100

Detached

House

Baseball ﬁeld

Elevaꢀon: 100

Baseball ﬁeld Commercial

Elevaꢀon: 100 Area

Elevaꢀon: 100

End

End

Detached

House

Detached

House

Elevaꢀon: 100 Elevaꢀon: 100

Detached

House

Elevaꢀon: 100

Commercial

Area

Elevaꢀon: 100 Elevaꢀon: 100

Commercial

Area

Detached

House

Elevaꢀon: 100

Start

Detached

House

Elevaꢀon: 100

Commercial

Area

Elevaꢀon: 100 Elevaꢀon: 100

Commercial

Area

Detached

House

Elevaꢀon: 100

Start

Detached

House

Elevaꢀon: 100

Detached

House

Detached

House

Elevaꢀon: 100 Elevaꢀon: 100

Detached

House

Elevaꢀon: 100 Elevaꢀon: 100

Detached

House



<a name="br4"></a> 

**Each ꢀle returned in the 2-dimensional JSON structure will contain the following ﬁelds:**

**Field**

**Type**

**Descripꢀon**

TopRight

Object:

{longitude: ﬂoat, laꢀtude:

coordinates of the top right corner of the ꢀle’s bounding box

ﬂoat }

BoꢁomLeꢂ

Center

Object:

{ longitude: ﬂoat, laꢀtude:

ﬂoat }

Object:

coordinates of the boꢁom leꢂ corner of the ꢀle’s bounding box

coordinates of the center of ꢀle

{ longitude: ﬂoat, laꢀtude:

ﬂoat }

arrCoord

type

List:

[int,int]

String

The ꢀle’s x and y coordinates in the 2-dimensional structure.

Indexed starꢀng at 0.

Indicator of the ꢀle’s type. “Start”, “End” or NULL if the ꢀle does

not contain the start or end coordinate

terrain

String

Float

Indicator of the ꢀle’s terrain. (Ex. “Detached Home”, “Commercial

Area”,

“Paddy ﬁeld” etc…) A list of the 51 possible classiﬁcaꢀons can be

found [here](https://captain-whu.github.io/DiRS/files/MAID_ClsNet.jpg)

Float value represenꢀng elevaꢀon in feet of the ꢀle’s center

coordinate.

Elevaꢀon

**Usage Example:**

An API request to /0/0/0.0026/0.0024

**Given:**

Starꢀng Coordinate: {Longitude: 0 , laꢀtude: 0}

Ending Coordinate: {Longitude: 0.0026, laꢀtude: 0.0024}

**Resulꢀng JSON structure format:**

{

"TopRight": {

[

"longitude": 0.0013,

"latitude": -0.0012

[

},

{

"BottomLeft": {

"TopRight": {

"longitude": -0.0013,

"latitude": -0.0012

},

"BottomLeft": {

"longitude": -0.0039,

"latitude": -0.0036

},

"center": {

"longitude": -0.0026,

"latitude": -0.0024

},

"longitude": -0.0013,

"latitude": -0.0036

},

"center": {

"longitude": 0,

"latitude": -0.0024

},

"arrCoord": [

0,

1

],

Tile at (0,1)

Tile at (0,0)

"type": null,

"arrCoord": [

0,

0

],

"terrain": "paddy field",

"elevation": -3524.3310546875

},

…

],

"type": null,

"terrain": "paddy field",

"elevation": -3408.3642578125

…

},

]



<a name="br5"></a> 

**Visual Representaꢀon of Resulꢀng Grid:**

TopRight: {longitude": -0.0013,

"latitude": 0.006},

TopRight: {longitude": 0.0013, "latitude":

0\.006},

TopRight: {longitude": 0.0039, "latitude":

0\.006},

TopRight: {longitude": 0.0065, "latitude":

0\.006},

BottomLeft: {"longitude": -0.0039,

"latitude": 0.0036},

Center: {"longitude": -0.0026,

"latitude": 0.0048

BottomLeft: {"longitude": -0.0013,

"latitude": 0.0036},

Center: {"longitude": 0,

"latitude": 0.0048

},

BottomLeft: {"longitude": 0.0013,

"latitude": 0.0036},

Center: {"longitude": .0026,

"latitude": 0.0048

},

BottomLeft: {"longitude": 0.0039,

"latitude": 0.0036},

Center: {"longitude": .0052,

"latitude": 0.0048

},

},

**arrCoord: [3,0],**

type: null,

**arrCoord: [3,1],**

type: null,

**arrCoord: [3,2],**

type: null,

**arrCoord: [3,3],**

type: null,

terrain: "paddy field",

elevation: -3299.668701171875

terrain: "paddy field",

elevation: -3438.31884765625

terrain: "paddy field",

terrain: "paddy field",

elevation: -3703.91162109375

elevation:

-<sub>3574.12890625</sub>

TopRight: {longitude": -0.0013,

"latitude": 0.0036},

TopRight: {longitude": 0.0013, "latitude":

0\.0036},

TopRight: {longitude": 0.0039, "latitude":

0\.0036},

TopRight: {longitude": 0.0065, "latitude":

0\.0036},

BottomLeft: {"longitude": -0.0039,

"latitude": 0.0012},

Center: {"longitude": -0.0026,

"latitude": 0.0024

BottomLeft: {"longitude": -0.0013,

"latitude": 0.0012},

Center: {"longitude": 0,

"latitude": 0.0024

BottomLeft: {"longitude": 0.0013,

"latitude": 0.0012},

Center: {"longitude": 0.0026,

"latitude": 0.0024

BottomLeft: {"longitude": 0.0039,

"latitude": 0.0012},

Center: {"longitude": 0.0052,

"latitude": 0.0024

},

},

},

},

**arrCoord: [2,0],**

**arrCoord: [2,1],**

**arrCoord: [2,2],**

**arrCoord: [2,3],**

type: null,

type: null,

type: “End”,

type: NULL,

terrain: "paddy field",

elevation: - 3336.49072265625

terrain: "paddy field",

elevation: -3464.0380859375

terrain: "paddy field",

elevation: -3588.745361328125

terrain: "paddy field",

elevation: -3707.98046875

TopRight: {longitude": -0.0013,

"latitude": 0.0012},

BottomLeft: {"longitude": -0.0039,

"latitude": -0.0012},

Center: {"longitude": -0.0026,

"latitude": 0

TopRight: {longitude": 0.0013, "latitude":

0\.0012},

BottomLeft: {"longitude": -0.0013,

"latitude": -0.0012},

Center: {"longitude": 0.

"latitude": 0

TopRight: {longitude": 0.0039, "latitude":

0\.0012},

BottomLeft: {"longitude": 0.0013,

"latitude": -0.0012},

Center: {"longitude": .0026.

"latitude": 0

TopRight: {longitude": 0.0065, "latitude":

0\.0012},

BottomLeft: {"longitude": 0.0039

"latitude": -0.0012},

Center: {"longitude": 52.

"latitude": 0

},

},

},

},

**arrCoord: [1,0],**

**arrCoord: [1,1],**

**arrCoord: [1,2],**

**arrCoord: [1,3],**

type: null,

type: “Start”,

type: null,

type: “Start”,

terrain: "paddy field",

elevation: - 3372.724365234375

terrain: "paddy field",

elevation: - 3492

terrain: "paddy field",

elevation: -3608.435546875

terrain: "paddy field",

elevation: - -3718.618408203125

TopRight: {longitude": -0.0013,

"latitude": -0.0012},

BottomLeft: {"longitude": -0.0039,

"latitude": -0.0036},

Center: {"longitude": -0.0026,

"latitude": -0.0024

TopRight: {longitude": 0.0013, "latitude":

-0.0012},

BottomLeft: {"longitude": -0.0013,

"latitude": -0.0036},

Center: {"longitude": 0,

"latitude": -0.0024

TopRight: {longitude": 0.0039, "latitude":

-0.0012},

BottomLeft: {"longitude": 0.0013,

"latitude": -0.0036},

Center: {"longitude": 0.0026,

"latitude": -0.0024

TopRight: {longitude": 0.0065, "latitude":

-0.0012},

BottomLeft: {"longitude": 0.0039,

"latitude": -0.0036},

Center: {"longitude": 0.0052

"latitude": -0.0024

},

},

},

},

**arrCoord: [0,0],**

**arrCoord: [0,1],**

**arrCoord: [0,2],**

**arrCoord: [0,3],**

type: null,

type: null,

type: null,

type: null,

terrain: "paddy field",

elevation: -3408.3642578125},

terrain: "paddy field",

elevation: -3524.3310546875

terrain: "paddy field",

elevation: -3636.630859375

terrain: "paddy field",

elevation: -3743.458251953125



<a name="br6"></a> 

**Single Coordinate Classiﬁcaꢀon Endpoint**

**hꢁps://satelliteimageclassiﬁcaꢀon-producꢀon.up.railway.app/{longitude}/{laꢀtude}**

Given a single coordinate consisꢀng of longitude and laꢀtude, the API will return the terrain classiﬁcaꢀon

and elevaꢀon data of that coordinate.

**Procedure:**

\-

\-

The given coordinate is turned into a ꢀle.

The ꢀle classiﬁed by obtaining its corresponding image from Mapbox API and running the image

image through a classiﬁcaꢀon model.

\-

\-

The elevaꢀon data is obtained at the same ꢀme from Google Maps API

The classiﬁcaꢀon and elevaꢀon data are then returned as server response.

**Usage example:**

API request to /-120.677/35.2944

**Given:**

Coordinate: {longitude: -120.677, laꢀtude: 35.2944}

**Resulꢀng JSON structure:**

{

"coordinates": {

"longitude": -120.677,

"laꢀtude": 35.2944

},

"terrain": "detached house",

"elevaꢀon": 76.75740814208984

**}**

