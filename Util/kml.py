from zipfile import ZipFile
from GPXdata import GPSPoint, haversine

"""
def KmzParser2(filename):
"""
    #Parse KMZ file produced by Google MAP, extract GPS data to a list

    #Args:
    #  (string) filename: the KMZ file
    #Return:
    #  (list) gpsList: a list of GPS points [(lat, lng), (lat,lng),...],
    #  (linked list) head: a linked list of GPS points
"""
    kmz = ZipFile(filename, 'r')
    kml = kmz.open('doc.kml','r')
    #gpsStr = None
    for i, x in enumerate(kml):
        if "<coordinates>" in x:
            direction = x.replace("<coordinates>","").replace("</coordinates>","").replace("\t","").replace("\n","")
            break #the desired data will be the first data with "<coordinates>" keyword
    #transform string to GPS list
    gpsData = direction.strip().split()
    
    #GPS list
    gpsList = []
    for gps in gpsData:
        data = gps.split(",")
        gpsList.append((float(data[1]), float(data[0])))

    #GPS linked list
    #a path must have at least two GPS points (start and end)
    length = len(gpsList)
    head = GPSPoint(gpsList[0][0],gpsList[0][1])
    pointer = head
    for i in xrange(1,length):
        pointer.next = GPSPoint(gpsList[i][0], gpsList[i][1])
        pointer.distance = haversine(pointer.lat, pointer.lng,
                                     gpsList[i][0], gpsList[i][1])*1000
        pointer = pointer.next
        
    return gpsList, head
"""

def KmzParser(filename):
    """
    Parse KMZ file produced by Google MAP, extract GPS data to a list

    Args:
      (string) filename: the KMZ file
    Return:
      (linked list) head: a linked list of GPS points
    """
    kmz = ZipFile(filename, 'r')
    kml = kmz.open('doc.kml','r')
    coordinates = []
    for i, x in enumerate(kml):
        if "<coordinates>" in x:
            coordinates.append(x.replace("<coordinates>","").replace("</coordinates>","").replace("\t","").replace("\n",""))
            #the desired data will be the first data with "<coordinates>" keyword
        if "</LineString>" in x:
            #in a route KMZ file, we only need the first coordinates data
            #the other two are source and destination points
            break

    first = True
    head = None #the head of GPSPoint linked list
    pointer = None
    GPSList = []
    for coordinate in coordinates:
        GPSs = coordinate.split()
        for GPS in GPSs:
            lng, lat, _ = GPS.split(",")
            lat = float(lat)
            lng = float(lng)
            if first:
                head = GPSPoint(lat, lng)
                pointer = head
                first = False
            else:
                pointer.next = GPSPoint(lat, lng)
                pointer.distance = haversine(pointer.lat, pointer.lng,
                                             lat, lng)*1000
                pointer = pointer.next

    return head
