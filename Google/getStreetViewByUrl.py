import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from time import sleep
from PIL import Image
from GPS.GPSPoint import GPSPoint
from GPS.getBearing import getBearing
from Google.combineUrl import combineUrl
from Google.Drive import GDriveUpload
from config import GPS_DISTANCE, FOLDER_NAME, OUTPUT_DIRECTORY
from File.outputCSV import outputCSV
import webbrowser

def getStreetViewByUrl(path, outputDirectory):
    """
    Snapshot Google street view directly via url and store the images

    Args:
      (GPSPoint) path: the location of previous GPS node, used to calculate the bearing
    Return:
      (list) SVPoint: a list of street view points
    """
    # Google street view url
    url = "http://maps.google.com/maps?q=&layer=c&"
    # Extracted image number
    imgNum = 1
    # The distance between every two consecutive street view images
    distanceBound = GPS_DISTANCE * 1000 # Convert to meter
    # Set distance = distanceBound so that the street view image of 
    # the starting point will be captured.
    distance = distanceBound 
    # The flag for the last point
    last = False 
    # Record the previous GPS data for calculating the bearing with 
    # current point
    preGPS = None
    # street view points 
    SVPoint = []
    # Data set for csv file
    csvDataset = []
    GPSList = {}

    while path.next != None or last:
        if distance >= distanceBound or last:
            # If the accumulated distance between two GPS points is 
            # larger than the desired distanceBound 
            # or it reaches the end of this route.

            # Google street view parameters
            if not last:
                bearing = getBearing(path, path.next)
            else:
                bearing = getBearing(preGPS, path)
            param = {
                #GPS location
                "cbll" : str(path.lat) + ',' + str(path.lng),
                #1. Street View/map arrangement, 11=upper half Street View and lower half map, 
                #   12=mostly Street View with corner map
                #2. Rotation angle/bearing (in degrees)
                #3. Tilt angle: -90 (straight up) to 90 (straight down)
                #4. Zoom level: 0-2
                #5. Pitch (in degrees): -90 (straight up) to 90 (straight down), default 5
                "cbp"  : "12,"+str(bearing)+",0,0,0"
            }

            # Record the street view images' location
            SVPoint.append((path.lat, path.lng))
            # The name of the originally extracted image
            imgName = outputDirectory + "original/" + "StreetView-" + str(imgNum).zfill(4) + ".jpg";
            # The name of the cropped image
            cropImgName = outputDirectory + "StreetView-" + str(imgNum).zfill(4) + ".jpg";
            csvDataset.append(cropImgName)
            GPSList[cropImgName] = (path.lat, path.lng)
            
            # Open url on browser
            requestUrl = combineUrl(url, param)
            webbrowser.open(requestUrl)
            # Wait for browser opens the page
            sleep(6) 
            
            # Screen shot
            command = "screencapture " + imgName
            os.system(command)
            im = Image.open(imgName)
            
            # Get captured image size
            width, height = im.size
            
            # Crop the captured area, need to be customized depending on different computer
            im.crop((60, 350, width-130, height-320)).save(cropImgName)
            print cropImgName + " captured!   distance:" + str(distance)
            
            # Reset the accumulated distance
            distance = 0
            # Accrete the image number
            imgNum += 1

        distance += path.distance
        if not last:
            if path.next.next == None:
                #capture the street view of the last location
                last = True
                preGPS = path
            path = path.next
        else:
            print "last"
            last = False

    # Upload images to Google Drive
    links = GDriveUpload(csvDataset, FOLDER_NAME)

    # Generate data for csv file
    csvDataset = []
    for link in links:
        csvDataset.append([link.strip().split("/")[-1], links[link], GPSList[link]])
    csvDataset = sorted(csvDataset)
    csvDataset.insert(0,['Image name', 'Image', 'GPS'])
    # Output data to a csv file
    outputCSV(csvDataset, OUTPUT_DIRECTORY + "GoogleStreetView_m4.csv")        

    return SVPoint