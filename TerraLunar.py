#!/usr/bin/python3
# 2-D orbital mechanics simulation in Earth-Moon space.
# by Thomas during Spring 2020 for learning Python & SWEng
# presently works well in Raspbian Mu Python environment
# use simplified Newtonian physics and numerical integrations
# F = ma = GMm/r^2
# a = F/m = GM/r^2
# v = v + dv = v + adt
# x = x + dx = x + vdt
# t = t + dt

import graphics as gr
from random import randint
import math
import time

# global objects for graphics, Earth, Moon, and one spacecraft

displaychoice = 5
displayoptions = [[0, "small netbook screen", 1024, 580],
                  [1, "medium 720p screen", 1280, 700],
                  [2, "large 1080p screen", 1920, 1080],
                  [3, "huge 4k big screen", 3840, 2100],
                  [4, "for Raspbian at 1080p", 1917, 1030],
                  [5, "Win10 1920x1080 with 125% scaleup", 1540, 840]]

winwidth = int(displayoptions[displaychoice][2])
winheight = int(displayoptions[displaychoice][3])
print('Display = ' + displayoptions[displaychoice][1])

# define a class to store each set of initial conditions
class Iset:
    def __init__(self, moonstartangle=60.0,
                 shipxmd=1.0,
                 shipymd=0.0,
                 shipvx=0.0,
                 shipvy=851.0,
                 dtime=10,
                 winscale=1.2,
                 radscale=5.0,
                 plottrigger=70,
                 checktrigger=1000,
                 description='Default setup'):

        self.moonstartangle = moonstartangle
        self.shipxmd = shipxmd
        self.shipymd = shipymd
        self.shipvx = shipvx
        self.shipvy = shipvy
        self.dtime = dtime
        self.winscale = winscale
        self.radscale = radscale
        self.plottrigger = plottrigger
        self.checktrigger = checktrigger
        self.description = description

setuplib = (['moonang','xmd','ymd','vx','vy','dt','wscale','rscale','pltrig','chktrig','Description'],
            [60.0, 1.1, 0.0, 0.0, 1000.0, 30, 2.0, 5.0, 60, 1000, 'eventual escape'],
            [60.0, 1.1, 0.0, 0.0, 1000.0, 1, 2.0, 5.0, 600, 4000, 'lunar impact 1M steps; small dt'],
            [60.0, 1.1, 0.0, 0.0, 1000.0, 10, 2.0, 5.0, 60, 1000, 'eventual lunar impact; medium dt'],
            [60.0, 1.1, 0.0, 0.0, 1000.0, 60, 2.0, 5.0, 60, 1000, 'eventual lunar impact; big dt'],
            [60.0, 1.1, 0.0, 0.0, 1000.0, 30, 2.0, 5.0, 60, 1000, 'eventual escape'],
            [0.0, 0.017, 0.0, 0.0, 9200.0, 1, 0.03, 1.0, 20, 1000, 'elliptical orbit'],
            [0.0, 0.017, 0.0, 0.0, 7900.0, 1, 0.02, 1.0, 10, 1000, 'LEO = low Earth orbit'],
            [0.0, 0.10968811, 0.0, 0.0, 3074.7937, 1, 0.15, 1.0, 50, 1000, 'geosynchronous orbit'],
            [0.0, 0.8491, 0.0, 0.0, 861.2724303351446, 10, 1.2, 1.0, 70, 1000, 'just inside L1 lunar orbit'],
            [0.0, 0.8491, 0.0, 0.0, 861.2724303351447, 10, 1.2, 1.0, 70, 1000, 'just outside L1 lunar orbit'],
            [0.0, 0.8491, 0.0, 0.0, 861.27243, 10, 1.2, 1.0, 70, 1000, 'just below L1 orbit'],
            [0.0, 0.85, 0.0, 0.0, 870.0, 10, 1.2, 1.0, 70, 1000, 'near L1'],
            [0.0, 0.90, 0.0, 0.0, 770.0, 10, 1.2, 1.0, 70, 1000, 'distant lunar orbit'],
            [135.4, 0.0168, 0.0, 0.0, 11050.0, 1, 2.7, 1.0, 70, 1000, 'escape with lunar assist'],
            [135.0, 0.0168, 0.0, 0.0, 11050.0, 3, 0.7, 1.0, 70, 1000, 'Ranger direct lunar impact'],
            [0.0, 0.995, 0.0, 0.0, 2590.0, 10, 1.1, 1.0, 70, 1000, 'Apollo 8 orbiting moon'],
            [135.0, 0.017, 0.0, 0.0, 10998.0, 1, 0.7, 1.0, 40, 1000, 'Apollo 13 safe return'],
            [135.0, 0.017, 0.0, 0.0, 10990.0, 1, 0.7, 1.0, 40, 1000, 'direct lunar impact'],
            [135.0, 0.017, 0.0, 0.0, 11000.0, 1, 1.2, 1.0, 40, 1000, 'lost Apollo 13'],
            [130.0, 0.02, 0.0, 0.0, 10080.0, 10, 1.1, 1.0, 70, 1000, '2-orbit lunar impact'],
            [60.0, 0.8, 0.0, 400.0, 1100., 50, 3.0, 5.0, 60, 1000, 'failed L4; eventual lunar impact'],
            [60.0, 0.8, 0.0, 100.0, 1073., 10, 10.0, 10.0, 1000, 10000, 'gravity assist escape'],
            [60.0, 1.0, 0.0, 0.0, 900.0, 101, 1.3, 1.0, 100, 1000, 'lunar impact 1.5M loops'],
            [60.0, 1.0, 0.0, 0.0, 900.0, 60, 1.5, 5.0, 80, 1000, 'many lunar interactions'],
            [60.0, 1.0, 0.0, 0.0, 900.0, 30, 1.3, 1.0, 100, 1000, 'lunar impact, 839k steps'],
            [60.0, 1.0, 0.0, 0.0, 900.0, 10, 2.0, 5.0, 500, 4000, 'temporary lunar orbits then impact'],
            [55.0, 3.0, 0.0, 0.0, 0.0, 10, 2.0, 1.0, 100, 1000, 'non-fall to Earth from 3 moondistances.'],
            [40.0, 5.0, 0.0, 0.0, 0.0, 1, 3.0, 1.0, 500, 10000, 'fall to Earth from 5 moondistances.'],
            [60.0, 0.9, 0.0, 0.0, 950.0, 60, 1.7, 5.0, 30, 1000, '1.1M steps to Lunar Impact'],
            [60.0, 0.8, 0.0, 0.0, 1073., 10, 1.3, 1.0, 100, 1000, 'lunar impact'],
            [60.0, 1.0, 0.0, 0.0, 923.0, 10, 1.1, 1.0, 70, 1000, 'lunar impact, vy=921-926'])

def grabsetup(i):   # return indexed setup from sample library
    return Iset(moonstartangle=setuplib[i][0],
                shipxmd=setuplib[i][1],
                shipymd=setuplib[i][2],
                shipvx=setuplib[i][3],
                shipvy=setuplib[i][4],
                dtime=setuplib[i][5],
                winscale=setuplib[i][6],
                radscale=setuplib[i][7],
                plottrigger=setuplib[i][8],
                checktrigger=setuplib[i][9],
                description=setuplib[i][10])

# for i in range(1, len(setuplib)):
#     print(str(i), setuplib[int(i)][10])

i = 1
columns = 3
while i < len(setuplib):
    for j in range(i, min(i+columns, len(setuplib))):
        print(f'{j:2d} {setuplib[j][10]:40}', end='')
    print()
    i += columns

query = None
while query is None:
    query = input("Choose an initial setup: ")
    if query == '':     # <Enter> is convenient
        query = 1
    else:
        try:
            query = int(query)
        except:
            print("Enter a number to choose initial setup.")
            query = None

if query < 1:
    query = 1
if query > len(setuplib)-1:
    query = len(setuplib)-1
setupnum = query

inz = grabsetup(setupnum)

win = gr.GraphWin("Noobie TerraLunar Python program", winwidth, winheight)
win.setBackground('black')

# plot some random stars
for i in range(50):
    x = randint(0, winwidth-1)
    y = randint(0, winheight-1)
    win.plotPixel(x, y, color='white')

# use MKS units:  meter, kg, sec
# use average Earth-Moon distance for view scaling
moondistance = 3.84399e8

# set up initial conditions in our simulated universe
# Earth at center origin
earthrad = 6.3781e6
earthx = 0.0
earthy = 0.0

# set up window with worldly plot coordinates lower left and upper right
yll = -moondistance * inz.winscale
yur = moondistance * inz.winscale
xll = yll * winwidth/winheight
xur = yur * winwidth/winheight
win.setCoords(xll, yll, xur, yur)

earth = gr.Circle(gr.Point(earthx, earthy), inz.radscale*earthrad)
earth.setWidth(2)
earth.setFill('blue')
earth.setOutline('blue')
earth.draw(win)

moonrad = 1.7374e6
moonangle = math.radians(inz.moonstartangle)    # was degrees for convenience
moonx = earthx + moondistance*math.cos(math.radians(moonangle))
moony = earthy + moondistance*math.sin(math.radians(moonangle))
oldmx = moonx
oldmy = moony
moon = gr.Circle(gr.Point(moonx, moony), inz.radscale*moonrad)
moon.setWidth(1)
moon.setFill('grey')
moon.setOutline('white')
moon.draw(win)
win.plot(moonx, moony, color='dark grey')

textul = gr.Text(gr.Point(xll*6/8, yur*7/8), inz.description)
textul.setTextColor('green')
textul.draw(win)

textur = gr.Text(gr.Point(xur*6/8, yur*7/8), text='Click to exit')
textur.setTextColor('pink')
textur.draw(win)

textlr = gr.Text(gr.Point(xur*6/8, yll*7/8), text='Iterations/second')
textlr.setTextColor('yellow')
textlr.draw(win)

shipx = earthx + moondistance*inz.shipxmd
shipy = earthy + moondistance*inz.shipymd
d2e = math.hypot(shipx - earthx, shipy - earthy)
shipvx = inz.shipvx
shipvy = inz.shipvy
shipcolors = ['red', 'tan', 'green', 'cyan', 'magenta', 'yellow']
shipcolor = 0
colorsteps = 0
win.plot(shipx, shipy, color=shipcolors[shipcolor])
trendcolor = 'blue'

simtime = 0             # elapsed simulation time
dtime = inz.dtime       # time step for simulation
gravcon = -6.67430e-11
earthgrav = gravcon * 5.972e24
moongrav = gravcon * 7.342e22
# moon orbits counterclockwise 360 degrees/(27 days + 7 hr + 43 min + 12 sec)
moonstep = math.radians(dtime*360./(27.*24*60*60 + 7.*3600 + 43.*60 + 12.))

iters = 0
olditers = iters
starttime = time.time()
oldtime = starttime
plots = 0
ips = 0

while win.checkMouse() is None:
    oldd2e = d2e
    d2e = math.hypot(shipx - earthx, shipy - earthy)
    if d2e < earthrad:
        earth.setFill('red')
        earth.move(0, 0)
        print(">>>>>>> Crashed on Earth ! <<<<<<<")
        break
    d2m = math.hypot(shipx - moonx, shipy - moony)
    if d2m < moonrad:
        moon.setFill('red')
        moon.move(0, 0)
        print("* * * * * * *  Lunar impact !  * * * * * * *")
        break
    s2eaccel = dtime * earthgrav / (d2e * d2e * d2e)
    s2maccel = dtime * moongrav / (d2m * d2m * d2m)
    shipvx += s2eaccel * (shipx - earthx) + s2maccel * (shipx - moonx)
    shipvy += s2eaccel * (shipy - earthy) + s2maccel * (shipy - moony)
    oldshipy = shipy
    shipx += dtime * shipvx
    shipy += dtime * shipvy
    if oldshipy < earthy and shipy >= earthy:
        colorsteps += 1
        shipcolor = colorsteps % len(shipcolors)
    moonangle += moonstep
    moonx = earthx + moondistance*math.cos(moonangle)
    moony = earthy + moondistance*math.sin(moonangle)
    ''' Graphic update is done less often than numerical integration. '''
    if iters % inz.plottrigger == 0:
        moon.move(moonx - oldmx, moony - oldmy)
        win.plot(shipx, shipy, color=shipcolors[shipcolor])
        oldmx = moonx
        oldmy = moony
        plots += 1
    if iters % inz.checktrigger == 0:
        trendcolor = 'green'
        if d2e > oldd2e:
            trendcolor = 'red'     # increasing distance to Earth
        earth.setOutline(trendcolor)
        # earth.move(0, 0)
        newtime = time.time()   # calculate current iterations per second
        delta = newtime - oldtime
        if delta != 0:
            ips = int((iters - olditers)/delta)
        # print(0, ips)
        oldtime = newtime
        olditers = iters
        # textlr.undraw()
        textlr.setText('ips = ' + str(ips))
        # textlr.draw(win)
    simtime += dtime
    iters += 1

stoptime = time.time()
elapsedtime = stoptime - starttime
if elapsedtime == 0:
    elapsedtime = 1
itrate = int(iters / elapsedtime)
plotrate = int(plots / elapsedtime)

print()
print(str(setupnum), " ", inz.description,
      "  elapsed=", str(int(elapsedtime)),
      "  iters=", str(iters),
      "  last.ips=", str(ips), "  avg.ips=", str(itrate),
      "  plot.rate=", str(plotrate),
      "  d2e-oldd2e=", str(int(d2e-oldd2e)))

win.getMouse()    # wait for final mouse click
win.close()

print()

import code		# drop into a Python shell
code.interact( local=dict( globals(), **locals() ) )
# end
