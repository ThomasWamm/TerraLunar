#!/usr/bin/python3
#
# 2-D orbital mechanics simulation in Earth-Moon space.
# by Thomas during 2020 for learning Python & SWEng
#     2020-Dec-16 -- Added more setups to library.
#
# Presently works well in RaspberryOS Mu Python environment.
# Mystery:  different CPUs give different results!
#
# Use simplified Newtonian physics and numerical integrations.
# F = ma = -GMm/r^2
# a = F/m = -GM/r^2
# v = v + dv = v + adt
# x = x + dx = x + vdt
# t = t + dt

# This version runs on Linux, Windows, and MacOS with Python3.7 or higher.
# Comment-hidden code might still be usable with Pythonista app on iOS.

TerraLunar_version = "0.1.2.2"

import graphics as gr        # graphics.py is a wrapper for the tkinter module
from random import randint
import math
import time
import code
import json
''' for iOS:
import canvas
import motion
import dialogs
'''

print('\n')
print(f'TerraLunar ver {TerraLunar_version}: simplified orbital mechanics simulation')

# Need adaptability for different display devices...

cfg_Air2 = {'for custom configuration: ': 'edit then resave as tl.cfg',
            'windowwidth': 760,
            'windowheight': 900,
            'localconfig': 'optimized for iPad Air2'}

cfg_iPhX = {'for custom configuration: ': 'edit then resave as tl.cfg',
            'windowwidth': 500,
            'windowheight': 900,
            'localconfig': 'optimized for iPhoneX'}

cfg_iPod6 = {'for custom configuration: ': 'edit then resave as tl.cfg',
             'windowwidth': 300,
             'windowheight': 426,
             'localconfig': 'optimized for iPod6'}

cfg_Rpi = {'for custom configuration: ': 'edit then resave as tl.cfg',
           'windowwidth': 1930,
           'windowheight': 1040,
           'localconfig': 'RaspberryOS with 1920x1080 display'}

cfg = cfg_Rpi

# First write out a sample configuration file...

with open('tl-sample.cfg', 'w') as f:
    json.dump(cfg, f)

# Then look for a customized configuration file...

try:
    with open('tl.cfg', 'r') as f:
        cfg = json.load(f)
except:
    print('Custom config file tl.cfg not found, so will use defaults.')

# For security, probably some input checking should be done here, someday.

winwidth = int(cfg['windowwidth'])
winheight = int(cfg['windowheight'])
localconfig = cfg['localconfig']

print(f'Screen width x height = {winwidth} x {winheight} {localconfig}')
print()

# Global objects for graphics, Earth, Moon, and one spacecraft...

# define a class to store a set of initial conditions...

class Initset:
    def __init__(self, moondegrees=60.0,
                 shipxmd=1.0,
                 shipymd=0.0,
                 shipvx=0.0,
                 shipvy=851.0,
                 dtime=10,
                 winscale=1.2,
                 radscale=5.0,
                 checktrigger=1000,
                 description='Default setup'):

        self.moondegrees = moondegrees
        self.shipxmd = shipxmd
        self.shipymd = shipymd
        self.shipvx = shipvx
        self.shipvy = shipvy
        self.dtime = dtime
        self.winscale = winscale
        self.radscale = radscale
        self.checktrigger = checktrigger
        self.description = description

# A variety of interesting setups have been accumulated during development...

setuplib = (['moondeg','xmd','ymd','vx','vy','dt','wscale','rscale','chktrig','Description'],
            [60.0, 1.1, 0.0, 0.0, 1000.0, 30, 19.0, 5.0, 10000, '9.4M steps to escape'],
            [60.0, 1.1, 0.0, 0.0, 1000.0, 60, 1.6, 5.0, 10000, '323k steps to lunar impact'],
            [60.0, 1.1, 0.0, 0.0, 1000.0, 1, 5.0, 5.0, 40000, 'escape within 1B steps; small dt'],
            [60.0, 1.1, 0.0, 0.0, 1000.0, 10, 2.0, 5.0, 10000, 'eventual lunar impact; medium dt'],
            [60.0, 1.1, 0.0, 0.0, 1000.0, 60, 2.0, 5.0, 10000, 'eventual lunar impact; big dt'],
            [60.0, 1.1, 0.0, 0.0, 1000.0, 30, 2.0, 5.0, 10000, '8M steps to escape'],
            [0.0, 0.017, 0.0, 0.0, 9200.0, 1, 0.03, 1.0, 1000, 'elliptical orbit'],
            [0.0, 0.017, 0.0, 0.0, 7900.0, 1, 0.02, 1.0, 1000, 'LEO = low Earth orbit'],
            [0.0, 0.10968811, 0.0, 0.0, 3074.7937, 1, 0.15, 1.0, 1000, 'geosynchronous orbit'],
            [0.0, 0.8491, 0.0, 0.0, 861.2724303351446, 10, 1.2, 1.0, 10000, 'just outside L1'],
            [0.0, 0.8491, 0.0, 0.0, 861.2724303351447, 10, 1.2, 1.0, 10000, 'outside 22M inside outside L1'],
            [0.0, 0.8491, 0.0, 0.0, 861.27243, 10, 1.2, 1.0, 10000, 'just below L1'],
            [0.0, 0.85, 0.0, 0.0, 870.0, 10, 1.2, 1.0, 10000, 'near L1'],
            [0.0, 0.90, 0.0, 0.0, 770.0, 10, 1.2, 1.0, 10000, 'distant lunar orbit'],
            [135.4, 0.0168, 0.0, 0.0, 11050.0, 1, 2.7, 1.0, 10000, 'escape with lunar assist'],
            [135.0, 0.0168, 0.0, 0.0, 11050.0, 1, 0.7, 1.0, 10000, 'Ranger direct lunar impact'],
            [0.0, 0.995, 0.0, 0.0, 2590.0, 10, 1.1, 1.0, 10000, 'Apollo 8 orbiting moon'],
            [135.0, 0.017, 0.0, 0.0, 10998.0, 1, 0.7, 1.0, 10000, 'Apollo 13 safe return'],
            [135.0, 0.017, 0.0, 0.0, 10990.0, 1, 0.7, 1.0, 10000, 'direct lunar impact'],
            [135.0, 0.017, 0.0, 0.0, 11000.0, 1, 0.8, 1.0, 10000, 'lost Apollo 13'],
            [130.0, 0.02, 0.0, 0.0, 10080.0, 10, 1.1, 1.0, 10000, '2-orbit lunar impact'],
            [60.0, 0.8, 0.0, 400.0, 1100., 50, 1.8, 5.0, 10000, 'failed L4; 11M steps to moon'],
            [60.0, 0.8, 0.0, 100.0, 1073., 10, 5.0, 10.0, 10000, 'eventual lunar impact #2'],
            [60.0, 1.0, 0.0, 0.0, 900.0, 101, 1.3, 1.0, 10000, 'lunar impact 1.5M loops'],
            [60.0, 1.0, 0.0, 0.0, 900.0, 60, 39.5, 5.0, 10000, 'many lunar interactions'],
            [60.0, 1.0, 0.0, 0.0, 900.0, 30, 1.3, 1.0, 10000, 'lunar impact, 2.2M steps'],
            [60.0, 1.0, 0.0, 0.0, 900.0, 10, 2.0, 5.0, 40000, 'temporary lunar orbits then impact'],
            [55.0, 3.0, 0.0, 0.0, 0.0, 10, 2.0, 1.0, 10000, 'non-fall to Earth from 3 moondistances.'],
            [40.0, 5.0, 0.0, 0.0, 0.0, 1, 3.0, 1.0, 10000, 'fall to Earth from 5 moondistances.'],
            [60.0, 0.9, 0.0, 0.0, 950.0, 60, 1.7, 5.0, 10000, '11.85M steps to Lunar Impact'],
            [60.0, 0.8, 0.0, 0.0, 1073., 10, 1.3, 1.0, 10000, 'lunar impact'],
            [60.0, 1.0, 0.0, 0.0, 923.0, 10, 1.1, 1.0, 10000, 'lunar impact, vy=921-926'],
            [0.0, 0.98, 0.0, 0.0, 2000.0, 10, 1.1, 1.0, 10000, 'medium distance lunar orbit 1'],
            [0.0, 0.95, 0.0, 0.0, 1500.0, 10, 1.1, 1.0, 10000, 'medium distance lunar orbit 2'],
)

def grabsetup(i):   # return one setup from library
    return Initset(moondegrees=setuplib[i][0],
                   shipxmd=setuplib[i][1],
                   shipymd=setuplib[i][2],
                   shipvx=setuplib[i][3],
                   shipvy=setuplib[i][4],
                   dtime=setuplib[i][5],
                   winscale=setuplib[i][6],
                   radscale=setuplib[i][7],
                   checktrigger=setuplib[i][8],
                   description=setuplib[i][9])

def parseparams(d):   # extract setup from json dictionary object
    return Initset(moondegrees=d['moondeg'],
                   shipxmd=d['xmd'],
                   shipymd=d['ymd'],
                   shipvx=d['vx'],
                   shipvy=d['vy'],
                   dtime=d['dt'],
                   winscale=d['wscale'],
                   radscale=d['rscale'],
                   checktrigger=d['chktrig'],
                   description=d['Description'])

def grabsnap():   # grab parameter snapshot to enable logging and replays
    snapdict = {'moondeg': math.degrees(moonangle),
                'xmd': shipx/moondistance,
                'ymd': shipy/moondistance,
                'vx': shipvx,
                'vy': shipvy,
                'dt': dtime,
                'wscale': inz.winscale,
                'rscale': inz.radscale,
                'chktrig': inz.checktrigger,
                'Description': 'Snapshot from: ' + inz.description}
    return snapdict


# Display the available initial condition setups...

i = 1
columns = 2    # for smaller displays, e.g. mobiles
columns = 3    # for larger displays
while i < len(setuplib):
    for j in range(i, min(i+columns, len(setuplib))):
        print(f'{j:2d} {setuplib[j][9]:40}', end='')
    print()
    i += columns

# Now ask the user (thru console I/O) to choose one of the setups...

query = None
while query is None:
    query = input("Choose an initial setup (or 0 for json file): ")
    if query == '':     # <Enter> is convenient
        query = 1
    else:
        try:
            query = int(query)
        except:
            print("Enter a number to choose initial setup.")
            query = None

setupnum = query
if setupnum < 1:
    setupnum = 1
if setupnum > len(setuplib)-1:
    setupnum = len(setuplib)-1

inz = grabsetup(setupnum)

params = None
if query == 0:
    try:
        # paramfile = dialogs.pick_document()
        # Don't know about non-iOS file-picking yet,
        paramfile = 'tl-setup.json'   # so hardcode a filename.
        with open(paramfile, 'r') as f:
            params = json.load(f)
        inz = parseparams(params)
        print()
        print('Found parameter file ' + paramfile +
              ' with description: ' + inz.description)
        print()
        setupnum = query
    except:
        print('\nValid parameter file not found, so will use setup 1.')
        inz = grabsetup(setupnum)


# Create the graphics display window...

win = gr.GraphWin("Noobie TerraLunar Python program", winwidth, winheight)
win.setBackground('black')

''' for iOS version...
canvas.set_size(winwidth, winheight)
canvas.set_aa_enabled(False)  # disable anti-aliasing so thin lines visible
canvas.set_fill_color(0, 0, .15)   # make space almost black
canvas.fill_rect(0, 0, winwidth, winheight)
'''

# plot some random stars...

# canvas.set_fill_color(1, 1, 1)   # for iOS
for i in range(50):
    x = randint(0, winwidth-1)
    y = randint(0, winheight-1)
    win.plotPixel(x, y, color='white')  # non-iOS
    # canvas.fill_pixel(x, y)   # for iOS

# For the numerical physics model, use MKS units:  meter, kilogram, second.
# Use the average Earth-Moon distance as a unit for view scaling.

moondistance = 3.84399e8

# Set up initial conditions in our simulated universe...
# Earth is at display center origin.

earthrad = 6.3781e6
earthx = 0.0
earthy = 0.0

# Set up window with worldly plot coordinates lower left and upper right...

yll = -moondistance * inz.winscale
yur = moondistance * inz.winscale
xll = yll * winwidth/winheight
xur = yur * winwidth/winheight
win.setCoords(xll, yll, xur, yur)

earth = gr.Circle(gr.Point(earthx, earthy), inz.radscale*earthrad)
earth.setWidth(2)
earth.setFill('blue')
trendcolor = 'blue'  # Earth outline color will provide hints
earth.setOutline(trendcolor)
earth.draw(win)

winmin = min(winwidth, winheight)
winmax = max(winwidth, winheight)
viewscale = winmin / (3.0 * moondistance * inz.winscale)  # pixels/meter
apixel = 2.5 / viewscale   # movement size to provoke a screen update
offscreen = 0.4 * winmax / viewscale     # meters to be out of view
crumbinterval = 5
crumbsteps = crumbinterval

''' for iOS...
canvas.translate(winwidth/2.0, winheight/2.0)   # earth at center of view
canvas.scale(viewscale, viewscale)

# RGB colorsets for Earth and Moon

er, eg, eb = 0.2, 0.2, 1.0      # the blue-ish Earth
mr, mg, mb = 0.6, 0.6, 0.4      # the grey-ish Moon

def show_earth(er, eg, eb):
    canvas.save_gstate()
    canvas.set_fill_color(er, eg, eb)
    rad = earthrad * inz.radscale
    diam = 2.0 * rad
    canvas.fill_ellipse(earthx - rad, earthy - rad, diam, diam)
    canvas.restore_gstate()

def show_moon(mr, mg, mb):
    canvas.save_gstate()
    canvas.set_fill_color(mr, mg, mb)
    rad = moonrad * inz.radscale
    diam = 2.0 * rad
    canvas.fill_ellipse(moonx - rad, moony - rad, diam, diam)
    canvas.restore_gstate()

def hide_old_moon():
    canvas.save_gstate()
    canvas.set_fill_color(0,0,0)  # paint it as black as outer space
    rad = moonrad * inz.radscale
    diam = 2.0 * rad
    canvas.fill_ellipse(oldmx - rad, oldmy - rad, diam, diam)
    canvas.restore_gstate()

show_earth(er, eg, eb)
'''

moonrad = 1.7374e6   # radius of moon in meters

moonangle = math.radians(inz.moondegrees)  # calculate with radians
moonx = earthx + moondistance*math.cos(moonangle)
moony = earthy + moondistance*math.sin(moonangle)
oldmx = moonx  # to keep track of previous displayed moon location
oldmy = moony

''' for iOS...
hide_old_moon()
show_moon(mr, mg, mb)
'''

moon = gr.Circle(gr.Point(moonx, moony), inz.radscale*moonrad)
moon.setWidth(1)
moon.setFill('grey')
moon.setOutline('white')
moon.draw(win)
win.plot(moonx, moony, color='red')  # leave red dot where moon started

# Display some textual information (non-iOS version)...

textversion = gr.Text(gr.Point(xll*0.90, yur*0.95), "TerraLunar ver " + TerraLunar_version)
textversion.setTextColor('cyan')
textversion.draw(win)

textul = gr.Text(gr.Point(xll*0.85, yur*0.90), inz.description)
textul.setTextColor('cyan')
textul.draw(win)

textur = gr.Text(gr.Point(xur*0.90, yur*0.95), text='Click to exit')
textur.setTextColor('pink')
textur.draw(win)

textlr = gr.Text(gr.Point(xur*0.75, yll*0.95), text='########## steps @ ######/sec')
textlr.setTextColor('yellow')
textlr.draw(win)

shipstatus = 'in orbit'
textll = gr.Text(gr.Point(xll*0.75, yll*0.95), text='Status:  ' + shipstatus)
textll.setTextColor('white')
textll.draw(win)

shipx = earthx + moondistance*inz.shipxmd
shipy = earthy + moondistance*inz.shipymd
oldx = shipx  # to keep track of previous displayed ship location
oldy = shipy
d2e = math.hypot(shipx - earthx, shipy - earthy)
moonunits = d2e / moondistance
shipvx = inz.shipvx
shipvy = inz.shipvy

pathcolors = ['red', 'tan', 'green', 'cyan', 'magenta', 'yellow']
pathcolor = 0
colorsteps = 0

win.plot(shipx, shipy, color=pathcolors[pathcolor])

''' for iOS...
pathcolors = [(1,0,0), (0,1,0), (0.6,0.6,1), (1,1,0), (1,0,1), (0,1,1)]

def setpathcolor(i):
    if i in range(0, len(pathcolors)):
        colorset = pathcolors[i]
    else:
        colorset = (1,1,1)
    canvas.set_fill_color(colorset[0], colorset[1], colorset[2])

setpathcolor(pathcolor)
canvas.fill_pixel(shipx, shipy)
'''

# draw ship as a small red square
halfship = 1.5 / viewscale
ship = gr.Rectangle(gr.Point(shipx-halfship, shipy-halfship),
                    gr.Point(shipx+halfship, shipy+halfship))
ship.setWidth(1)
ship.setFill('red')
ship.setOutline('red')
ship.draw(win)

simtime = 0             # elapsed simulation time
dtime = inz.dtime       # time step for simulation
gravcon = -6.67430e-11
earthgrav = gravcon * 5.972e24
moongrav = gravcon * 7.342e22
# moon orbits counterclockwise 360 degrees/(27 days + 7 hr + 43 min + 12 sec)
moonstep = math.radians(360.*dtime/(27.*24*60*60 + 7.*3600 + 43.*60 + 12.))

orbits = 0     # to count orbits around Earth
steps = 0
oldsteps = steps
starttime = time.time()   # non-iOS version
# starttime = time.process_time()   # iOS version
oldtime = starttime
plots = 0
sps = 0
maxsps = 0
timestamp = time.asctime(time.localtime())
running = True

# motion.start_updates()  # enable iOS device accelerometers

logfile = open('tl-log.txt', 'a')  # open log file for append
logfile.write(f"\n{setupnum}: {inz.description}\n")
logfile.write('Start @ ' + timestamp + '\n')

print('Started @ ' + timestamp)

# top of big numerical integration simulation loop...

# while running:       # iOS version

while win.checkMouse() is None:     # break out on mouse click
    oldd2e = d2e
    d2e = math.hypot(shipx - earthx, shipy - earthy)
    if d2e < earthrad:
        earth.setFill('red')
        earth.move(0, 0)
        # show_earth(1,0,0)  # red crash site (iOS version)
        shipstatus = "Crashed on Earth !"
        break

    d2m = math.hypot(shipx - moonx, shipy - moony)
    if d2m < moonrad:
        moon.setFill('red')
        moon.move(0, 0)
        # show_moon(1,0,0)   # red crash site (iOS version)
        shipstatus = "Crashed on Moon !"
        break

    s2eaccel = dtime * earthgrav / (d2e * d2e * d2e)
    s2maccel = dtime * moongrav / (d2m * d2m * d2m)
    shipvx += s2eaccel * (shipx - earthx) + s2maccel * (shipx - moonx)
    shipvy += s2eaccel * (shipy - earthy) + s2maccel * (shipy - moony)
    oldshipy = shipy  # to detect crossing of x-axis each orbit of Earth
    shipx += dtime * shipvx
    shipy += dtime * shipvy

    if oldshipy < earthy and shipy >= earthy:  # detect x-axis crossings
        orbits += 1
        colorsteps += 1   # change ship color every orbit around Earth
        snapshot = grabsnap()    # snapshot and log current parameters
        json.dump(snapshot, logfile)
        logfile.write('\n')

    moonangle += moonstep
    moonx = earthx + moondistance*math.cos(moonangle)
    moony = earthy + moondistance*math.sin(moonangle)

    ''' Graphic update is done less often than numerical integration. '''

    if abs(shipx - oldx) + abs(shipy - oldy) + abs(moonx - oldmx) + abs(moony - oldmy) > apixel:
        # only update display when ship or moon moves at least a pixel
        moon.move(moonx - oldmx, moony - oldmy)
        ship.move(shipx - oldx, shipy - oldy)
        crumbsteps -= 1   # occasionally drop a crumb on the path
        if crumbsteps <= 0:
            crumbsteps = crumbinterval
            pathcolor = colorsteps % len(pathcolors)
            win.plot(shipx, shipy, color=pathcolors[pathcolor])
            # setpathcolor(pathcolor)  # for iOS version
            # canvas.fill_pixel(shipx, shipy)
        oldx = shipx
        oldy = shipy
        # hide_old_moon()  # for iOS version
        # show_moon(mr, mg, mb)
        oldmx = moonx
        oldmy = moony
        plots += 1

    if steps % inz.checktrigger == 0:
        # display periodic status updates
        trendcolor = 'green'
        if d2e > oldd2e:
            trendcolor = 'red'     # increasing distance to Earth
        earth.setOutline(trendcolor)
        # calculate current sps (steps per second)...
        newtime = time.time()
        # newtime = time.process_time()  # for iOS ?
        delta = newtime - oldtime
        if delta != 0:
            sps = int((steps - oldsteps)/delta)
            maxsps = max(maxsps, sps)
        # print(0, sps)   # for studying loop slowdown vs. time
        oldtime = newtime
        oldsteps = steps
        steps_string = f"{steps:,.0f} steps  @  {sps} /sec"
        textlr.setText(steps_string)

        moonunits = d2e / moondistance
        status_string = f"Ship status:  {shipstatus}  @  {moonunits:.1f} moonunits"
        textll.setText(status_string)

        velocity = math.hypot(shipvx, shipvy)
        escapevelocity = math.sqrt(-2.0 * (earthgrav + moongrav) / d2e)

        if (velocity > escapevelocity) and (d2e > offscreen):
            earth.setFill('green')  # show green Earth then quit
            earth.setOutline('green')
            # show_earth(0,1,0)   # iOS
            shipstatus = "Escape velocity !  Lost in space!"
            break

        ''' for iOS gadgets, use device orientation as user input...
        gravx, gravy, gravz = motion.get_gravity()  # device orientation

        if gravz > 0.3:    # quit if user turns device screen downwards
            show_earth(1,1,0)   # show yellow Earth
            break

        if gravx > 0.8:    # output info if tipped to landscape
            print(f"{moonunits:6.2f} moonu @ {velocity:7.0f} mps")
        '''

    simtime += dtime
    steps += 1
    # Bottom of big numerical integration loop; repeat until terminated.

running = False
# Simulation loop has exited. Output stats and clean up...

# motion.stop_updates()   # release iOS device accelerometers

timestamp = time.asctime(time.localtime())
logfile.write('End   @ ' + timestamp + '\n-----------------------------\n')
print('Stopped @ ' + timestamp)   # sometimes I run it for days

stoptime = time.time()
# stoptime = time.process_time()   # iOS
elapsedtime = stoptime - starttime
if elapsedtime == 0:
    elapsedtime = 1.0
itrate = int(steps / elapsedtime)
plotrate = int(plots / elapsedtime)
moonunits = d2e / moondistance
velocity = math.hypot(shipvx, shipvy)

status_string = f"Ship status:  {shipstatus}  @  {moonunits:.1f} moonunits"
textll.setText(status_string)

steps_string = f"{steps:,.0f} steps  @  {sps} /sec"
textlr.setText(steps_string)

print('\nShip status:  ' +  shipstatus)
print(f"{setupnum}: {inz.description}\n",
      f"{steps} steps in {int(elapsedtime)} seconds\n",
      f"avg.sps={itrate}   last.sps={sps}   max.sps={maxsps}\n",
      f"plot.rate={plotrate}    orbits={orbits}\n")
print(f"{moonunits:6.2f} moonu @ {velocity:7.0f} mps")

snapshot = grabsnap()    # snapshot and log final parameters
snapshot["Description"] = f"Final snapshot; {shipstatus}"
json.dump(snapshot, logfile)
logfile.write('\n==============================\n')
logfile.close()
print(snapshot)

win.getMouse()    # wait for final mouse click
win.close()

timestamp = time.asctime(time.localtime())
print('Exited  @ ' + timestamp)   # sometimes I ignore it for days

# optionally drop into a Python shell
#code.interact(local=dict(globals(), **locals()))
# end.