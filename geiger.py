#Radiation Logger v1.0
#A simple program to log the output of one's gieger counter and output easy to read data
#Written by Noah Torname


#set up important program stuff
import time
import RPi.GPIO as GPIO
import os
import _thread
import http.server
import socketserver
global counts
counts = 0

#set up your Pi or accepting the geiger output
pin = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.IN)

#counts radioactive particles that enter the geiger-muller tube
def rawGather():
    print("stared raw gather")
    while True:
        global counts
        GPIO.wait_for_edge(pin, GPIO.RISING) #interrupts thread until count
        counts += 1
        time.sleep(0.01) #hysteresis to prevent double counting

#each minute logs counts to a minute-by-minute text file
def lastMinute():
    while True:
        global counts
        time.sleep(60)
        minutelog = open("./lasthour.txt", "a")
        minutelog.write("{0} {1}\n" .format((time.strftime("%m/%d/%Y %H:%M ")),counts))
        minutelog.close()
        short(60, "lasthour.txt")
        toWeb("lasthour.txt")
        print("logged", counts, "counts last minute")
        counts = 0

#each hour logs counts to a hour-by-hour text file
def lastHour():
    while True:
        time.sleep(3600.1) #1/10th second prevents race condition
        hourTotal = 0
        temp = []
        toAvgMins = open("./lasthour.txt", "r")
        info = toAvgMins.readlines()
        for line in info: #searches for useful data in each line
            val =(line[((line.find("  ")) + 2):])
            temp.append(int(val))
        for i in temp: #averages useful data
            hourTotal = hourTotal + i
        hourTotal = round((hourTotal / len(info)), 1)
        hourlog = open("./lastday.txt", "a")
        hourlog.write("{0} {1}\n" .format((time.strftime("%m/%d/%Y %H:%M ")), hourTotal))
        hourlog.close()
        short(24, "lastday.txt")
        toWeb("lastday.txt")
        print ("last hour average ", hourTotal)

#each day logs counts to a day-by-day text file
def allTime():
    while True:
        time.sleep(86400.1) #1/10th second prevents race condition
        dayTotal = 0
        temp = []
        toAvgHrs = open("./lastday.txt", "r")
        info = toAvgHrs.readlines()
        for line in info:: #searches for useful data in each line
            val =(line[((line.find("  ")) + 2):])
            temp.append(float(val))
        for i in temp: #averages useful data
            dayTotal = dayTotal + i
        dayTotal = round((dayTotal / len(info)), 1)
        daylog = open("./daily.txt", "a")
        daylog.write("{0} {1}\n" .format((time.strftime("%m/%d/%Y %H:%M ")), dayTotal))
        daylog.close()
        toWeb("daily.txt")
        print ("last day average", dayTotal)

#shortens files to correct time spaces
def short(entries, files):
    file = open(files, "r")
    data = file.readlines()
    file.close()
    if len(data) > entries:
        data.sort()
        data = data[(len(data)-entries):]
    file = open(files, "w")
    for entry in data:
      file.write("%s" % entry)
    file.close()

#moves data from text file to website
#   This seemed easier to me than attempting to understand JSON
def toWeb(file):
    x = []
    y = []
    comp = []
    data = open(file, "r")
    info = data.readlines()
    
    for line in info: #writes date and counts to separate array
        x.append(line[:(line.find("  "))])
        y.append(float(line[(line.find("  ")):]))

    web = open("index.html", "r+")
    html = web.read()
    
    for i in range (0,len(x)): #begins to assemble string for replacing table in the google chart 
        temp = (str(x[i]), float(y[i]))
        comp.append(temp)

    #these are the comments in the HTML file the data is inserted between
    a = (html.index(("".join(("<!-- ",file, " -->"))))) + (len(("".join(("<!-- ",file, " -->")))))
    b = (html.index(("".join(("]);<!-- end ", file, " -->")))))

    web.close()
    
    #gives string proper formant and correct placement in the file
    temp = str(comp)
    temp = temp.replace("[(", "\n[")
    temp = temp.replace(")]", "]")
    temp = temp.replace("(", "[")
    temp = temp.replace(")", "]")
    output = html.replace((html[a:b]), temp)

    web = open("index.html", "w")
    web.write("")
    web.write(output)
    data.close()
    web.close()
    
#starts website to see data in easy way
def webServer():
    print ("starting web server\n")
    while True: #deals with the weird issue of the server dying decently well
        try:
            Handler = http.server.SimpleHTTPRequestHandler
            http.server = socketserver.TCPServer(("", 80), Handler)
            http.server.serve_forever()
        except:
            print("Server error. restarting...")


#main bit of code to run all the stuff above
print("Radiation Logger v1.0\nMade by Noah Torname - June 2016\n\n")
time.sleep(1)
_thread.start_new_thread(webServer, ())
_thread.start_new_thread(lastMinute, ())
_thread.start_new_thread(lastHour, ())
_thread.start_new_thread(allTime, ())
rawGather()
