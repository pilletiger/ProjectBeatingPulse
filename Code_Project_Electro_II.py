#Import of libraries
import folium #For the map
import webbrowser #For opening the map in html
import requests #For scraping the data send over WiFi
from bs4 import BeautifulSoup #Webscraping
from tkinter import* #GUI
import subprocess
import time
from folium.plugins import MousePosition
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import pandas as pd
#Path setup
path = "C:/Users/olive/kort.html"
path_web = "http://192.168.1.1/"
values = []
zs = 8
zmi = 8
zma = 20

#Initial Map
m = folium.Map(location=[56.288760, 10.904211],zoom_start=zs,
               min_zoom = zmi, max_zoom = zma,) #Setup map at coordinates

#https://github.com/python-visualization/folium/blob/main/examples/plugin-MousePosition.ipynb
MousePosition().add_to(m)

formatter = "function(num) {return L.Util.formatNum(num, 6) + ' º ';};"

MousePosition(
    position="topright",
    separator=" | ",
    empty_string="NaN",
    lng_first=True,
    num_digits=20,
    prefix="Coordinates:",
    lat_formatter=formatter,
    lng_formatter=formatter,
).add_to(m)
m.save(path)                         #save as HTML file
webbrowser.open(path, new=0)                 #Open in webbrowser

def printInput(i,n):
    global markerpos
    global marker
    global design_time
    global area_coords_lat
    global area_coords_lon
    if n == 0:
        icn = "burst"
        colr = "lightgray"
        pop = "Dis. M. "
    else:
        icn = "truck-medical"
        colr = "green"
        pop = "Evac. M. "
    inpLa = float(e.get(1.0, "end-1c"))
    inpLo = float(en.get(1.0, "end-1c"))
    area_coords_lat.append(inpLa)
    area_coords_lon.append(inpLo)
    markerpos.append([inpLo,inpLa])
    marker = folium.Marker(location = [inpLo, inpLa], popup= pop+ str(i),
                  icon=folium.Icon(color = colr,
                  icon=icn, prefix="fa"))
    first.destroy()

def Create(i,n):
    global running
    global markerpos
    global design_time
    global evac_lat
    global evac_lon
    global area_coords_lat
    global area_coords_lon
    global dis_lat
    global dis_lon
    if i < 3:
        pass
    else:
        if n == 0:
            colr = "lightgray"
            dis_lat = area_coords_lat
            dis_lon = area_coords_lon
        else:
            colr = "green"
            evac_lat = area_coords_lat
            evac_lon = area_coords_lon
        running = False
        markerpos.append(markerpos[0])
        first.destroy()
        folium.PolyLine(markerpos, color=colr, fill = True, tooltip =design_time[n] ).add_to(m)

def Skip():
    global skip
    global running
    global m
    skip = True
    running = False
    
    global dis_lat
    global dis_lon
    global evac_lat
    global evac_lon
    
    dis_lon = [10.191334,10.191295,10.19112,
               10.191088,10.191946,10.19204,
               10.191334]
    dis_lat = [56.172085,56.17199,56.172013,
               56.17193,56.171828,56.171993,
               56.172085]
    evac_lon = [10.190954,10.190884,10.191083,10.191142,
                 10.190954]
    evac_lat = [56.172133,56.171952,56.171928,
                 56.172108,56.172131]
    
    m = folium.Map(location=[56.17193,10.191088],zoom_start=17,
                   min_zoom = 17, max_zoom = zma,) #Setup map at coordinates
    pre_markers_dis = []
    pre_markers_evac = []
    for x in range(0, len(dis_lon)):
        pre_markers_dis.append([dis_lat[x],dis_lon[x]])
    for x in range(0, len(evac_lon)):
        pre_markers_evac.append([evac_lat[x],evac_lon[x]])
    for x in range(0,len(pre_markers_evac)):
        print(x)
        print(pre_markers_evac[x])
        m.add_child(folium.Marker(location = pre_markers_evac[x], popup= "Evac. M."+ str(x),
                      icon=folium.Icon(color = "green",
                      icon="truck-medical", prefix="fa")))
    folium.PolyLine(pre_markers_evac, color="green", fill = True, tooltip ="Evacuation area" ).add_to(m)
    for x in range(len(pre_markers_dis)):
        print(x)
        print(pre_markers_dis[x])
        m.add_child(folium.Marker(location = pre_markers_dis[x], popup= "Dis. M."+ str(x),
                      icon=folium.Icon(color = "lightgray",
                      icon="burst", prefix="fa")))
    folium.PolyLine(pre_markers_dis, color="lightgray", fill = True, tooltip ="Disaster Area" ).add_to(m)
    m.save(path)                         #save as HTML file
    webbrowser.open(path, new=0)
    first.destroy()
    print("endskip")
    
evac_lat = []
evac_lon = []
dis_lat = []
dis_lon = []

skip = False

for n in range(2):
    if skip == True:
        print("for_skip")
        break
    area_coords_lat = []
    area_coords_lon = []
    markerpos = []
    marker = folium.Marker()
    running = True
    i = 0
    design_time = ["Disaster Area", "Evacuation Area"]
    while running:
        i +=1
        first = Tk()
        Label(first, text= "Create " + design_time[n]).grid(row=0)
        Label(first, text="Longitude:").grid(row=1)
        Label(first, text="Lattitude:").grid(row=2)
        e = Text(first, height = 1, width = 20)
        en = Text(first, height = 1, width = 20)
        e.grid(row=1, column=1)
        en.grid(row=2, column=1)
        
        saveButton = Button(first,
                                text = "Save Marker", 
                                command = lambda: printInput(i,n))
        saveButton.grid(row=3, column =0)
        createButton = Button(first,
                                text = "Create Area from Markers", 
                                command = lambda : Create(i,n))
        createButton.grid(row=3, column =1)
        skipButton = Button(first,
                                text = "Skip", 
                                command = lambda : Skip())
        skipButton.grid(row=3, column =2)
        first.mainloop()
        if skip:
            print("Skip")
            break
        else:
            m.add_child(marker)
            m.save(path)                         #save as HTML file
            webbrowser.open(path, new=0)
                        #Open in webbrowser

cols = ['Lat', 'Lon']
df_poly_disaster = pd.DataFrame({
                    "Lat" : dis_lon,
                    "Lon" : dis_lat,
                    })
df_poly_evac = pd.DataFrame({
                    "Lat" : evac_lon,
                    "Lon" : evac_lat,
                    })

polygon_disaster = Polygon([tuple(x) for x in df_poly_disaster[['Lat', 'Lon']].to_numpy()])
polygon_evac = Polygon([tuple(x) for x in df_poly_evac[['Lat', 'Lon']].to_numpy()])

print("We are here now")

#Check name of Wifi im connected to
def get_wifi_name():
    output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"]).decode("utf-8")
    wifi_name = next((line.split(":")[1].strip() for line in output.split("\n") if "SSID" in line), None)
    return wifi_name


def CheckWifi():
    global current_wifi_name
    while True:
        if current_wifi_name == "TriageArmband":
            Label(second, text= "Wifi found, wait 5 sec" ).grid(row=0)
            time.sleep(5)
            second.destroy()
            break
        else:
            current_wifi_name = get_wifi_name()
            print(current_wifi_name)
            
current_wifi_name = get_wifi_name()
second = Tk()
Label(second, text= "Connect to patient" ).grid(row=0)
CheckWifi()
second.after(0, CheckWifi)
second.mainloop()

evacuated = False
blink_bool = False
prev_color = "white"
isMoving = ""
root = Tk()  # create root window

def value_updater(inputarray):
    global prev_color
    global values
    global isMoving
    if values:
        prev_color = values[6]
    print("We are in the updater")
    #Tjek timeout værdien.
    try:
        htmldata = requests.get(path_web, timeout=2.5)   #Open the webside
    except:
        print("timed out")
        values = value_updater(values)
    item_array = []
    soup = BeautifulSoup(htmldata.text, 'html.parser') #scraper
    for item in soup.find_all('p'):
        item_array.append(item.text)
    
    #Variable setup
    H = item_array[0]                #Horizontal coordinate
    L = item_array[1]                 #Latitude coordinate
    temp = item_array[2]              #Temperature
    oxygen = item_array[3]            #Oxygen
    pulse = item_array[4]            #Heartrate
    evac = item_array[5]             #Evacuation status
    confidence = item_array[9]        #Confidense of pulseoximeter
    HRMONSTAT = item_array[10]   #Status of pulseoximteter
    if int(confidence) < 95 or int(HRMONSTAT) != 3:
        clr = prev_color
        readGood = "Manually check condition: Previous stat.: "
    else:
        readGood = ""
        clr = item_array[6]           #Triage color code
    patient_position = pd.DataFrame({
                                    "Lat" : [L],
                                    "Lon" : [H],})
    if polygon_disaster.contains(Point(patient_position['Lat'],patient_position['Lon'])):
        status = "Patient is in disaster area"
    elif polygon_evac.contains(Point(patient_position['Lat'],patient_position['Lon'])):
        status = "Patient is in evacutian area"
    else:
        status = "Patient is unaccounted for"
    if evacuated == False:
        isMoving = item_array[8]
    #vitals = "Patient\n" + temp +"C* "+ pulse +"BPM\n"+ "Ox.: " + oxygen +"\n"
    vals = [H,L,temp,oxygen,pulse,evac,clr,status,isMoving,confidence,HRMONSTAT,readGood,prev_color] #Array with all values in
    try:
        return vals
    finally:
        gui_updater(vals)
        root.after(1000, value_updater,values)

def isEvac():
    global evacuated
    global isMoving
    evacuated = True
    isMoving = "Patient Evacuation Confirmed"

def gui_updater(v):
    global blink_bool
    # Example labels that could be displayed under the "Tool" menu
    print("Status is " + v[10])
    if int(v[9]) < 95 or int(v[10]) != 3:
        if blink_bool == False:
            root.config(bg= v[6])  # specify background color
            blink_bool = True
        else:
            blink_bool = False
            root.config(bg="gray")
    else:
        root.config(bg= v[6])  # specify background color
        blink_bool = False
    if v[7] == "Patient is in evacutian area" and evacuated == False or v[7] == "Patient is unaccounted for" and evacuated == False:
        Button(tool_bar, text="Confirm Evacuation", command = isEvac).grid(row=0, column=2)
    Label(tool_bar, text="TRIAGE EVAL: ").grid(row=1, column=0, padx=5, pady=5)
    Label(tool_bar, text="Evacuation status:").grid(row=2, column=0, padx=5, pady=5)
    Label(tool_bar, text="Pulse:").grid(row=3, column=0, padx=5, pady=5)
    Label(tool_bar, text="Blood Oxygen").grid(row=4, column=0, padx=5, pady=5)
    Label(tool_bar, text="Temperature").grid(row=5, column=0, padx=5, pady=5)
    Label(tool_bar, text="Pulse Oximeter Confidence").grid(row=6, column=0, padx=5, pady=5)
    Label(tool_bar, text="Pulse Oximeter Status: ").grid(row=7, column=0, padx=5, pady=5)
    Label(tool_bar, text="Current Coordinate Position").grid(row=8, column=0, padx=5, pady=5)    
    
    Label(tool_bar, text="ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",foreground = "white").grid(row=1, column=1, padx=5, pady=5)
    Label(tool_bar, text="ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",foreground = "white").grid(row=2, column=1, padx=5, pady=5)
    Label(tool_bar, text="ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",foreground = "white").grid(row=3, column=1, padx=5, pady=5)
    Label(tool_bar, text="ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",foreground = "white").grid(row=4, column=1, padx=5, pady=5)
    Label(tool_bar, text="ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",foreground = "white").grid(row=5, column=1, padx=5, pady=5)
    Label(tool_bar, text="ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",foreground = "white").grid(row=6, column=1, padx=5, pady=5)
    Label(tool_bar, text="ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",foreground = "white").grid(row=7, column=1, padx=5, pady=5)
    Label(tool_bar, text="ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss",foreground = "white").grid(row=8, column=1, padx=5, pady=5)
    
    Label(tool_bar, text=v[11]+v[6],bg = "white").grid(row=1, column=1, padx=5, pady=5)
    Label(tool_bar, text=v[5]+ " " + v[7],bg = "white").grid(row=2, column=1, padx=5, pady=5)
    Label(tool_bar, text=v[4],bg = "white").grid(row=3, column=1, padx=5, pady=5)
    Label(tool_bar, text=v[3],bg = "white").grid(row=4, column=1, padx=5, pady=5)
    Label(tool_bar, text=v[2],bg = "white").grid(row=5, column=1, padx=5, pady=5)
    Label(tool_bar, text=v[9],bg = "white").grid(row=6, column=1, padx=5, pady=5)
    Label(tool_bar, text=v[10],bg = "white").grid(row=7, column=1, padx=5, pady=5)
    Label(tool_bar, text="Hor. " + v[0] + " , Lat. " + v[1] + " " + v[8]).grid(row=8, column=1, padx=5, pady=5)

#GUI
#https://www.pythonguis.com/tutorials/use-tkinter-to-design-gui-layout/

root.title("Vital Monitor")  # title of the GUI window
root.maxsize(750, 1000)  # specify the max size the window can expand to



# Create left and right frames
left_frame = Frame(root, width=400, height=900, bg='grey')
left_frame.grid(row=0, column=0, padx=10, pady=5)

# Create frames and labels in left_frame
Label(left_frame, text="Patient Monitor").grid(row=0, column=0, padx=5, pady=5)

# Create tool bar frame
tool_bar = Frame(left_frame, width=300, height=900)
tool_bar.grid(row=2, column=0, padx=5, pady=5)

# Example labels that serve as placeholders for other widgets
Label(tool_bar, text="Patient 1", relief=RAISED).grid(row=0, column=0, padx=5, pady=3, ipadx=10)  # ipadx is padding inside the Label widget
Label(tool_bar, text="Vitals & Condition", relief=RAISED).grid(row=0, column=1, padx=5, pady=3, ipadx=10)

values = value_updater(values)

#Map
"""
m = folium.Map(location=[float(values[0]), float(values[1])],zoom_start=14,
               min_zoom = 14, max_zoom = 50, tiles="C:/Users/olive/Downloads/folium_offline-master/data/denmark.mbtiles", attr= "Open") #Setup map at coordinates
print([float(values[0]), float(values[1])]) """
m.add_child(folium.Marker(location = [float(values[0]), float(values[1])], popup="Patient 1",
              icon=folium.Icon(color = "red",
              icon="heart-circle-exclamation", prefix="fa"))) #add marker

m.save(path)                                 #save as HTML file
webbrowser.open(path, new=0)                 #Open in webbrowser
root.mainloop()




