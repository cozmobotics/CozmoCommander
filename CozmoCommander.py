#!/usr/bin/env python3

#basierend auf /home/martinpi/cozmo/cozmo_sdk_examples_1.4.1/tutorials/04_cubes_and_objects/03_go_to_object_test.py


# Copyright (c) 2018 Martin Piehslinger
# Copyright (c) 2016 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Graphical User Interface to some of Cozmo's features.
You need a Cozmo, the Cozmo SDK and a device (Android or IOS) connected to your computer. 
See Anki's SDK documentation for details. 

Have fun!
'''

# todo:
# viewer=4 ... map
# map button: map ein- und ausschalten (RAISED/SUNKEN) 
# head und lift slider ... command, Buttons weg
# Würfel durch Anklicken in der Karte selektieren (BCubex invoke) ... programmiert, aber geht nicht 
# Bug: Offensichtlich habe ich vier cubes in der Karte erzeugt   
# backup_onto_charger(max_drive_time=3)
# anim_names ... bisher verwende ich nur anim_triggers
# cliff ...? 
# drive_wheel_motors für Steuerung auf Kurvenbahnen, nicht so abgehackt. Grafische Eingabemöglichkeit? 
# Maus-button drücken und halten, und dann joystick-artig bewegen? 
# headlight ... Infrarot-Beleuchtung (Nacht-Modus) 
# turn_towards_face ... robot.turn_towards_face(face_to_follow) 
# enable_facial_expression_estimation ???
# entries for speed 
# delete walls (all of them) 
# walls in different color 
# Linux: "say" entry and button not visible
# move robot with cursor keys ... root.bind("<Key>", callbackKey), MapCanvas.bind("<Key>", callbackKey) 
# play sounds ... see 10_play_sound.py  ... cozmo.audio.AudioEvents
# map: redraw the axes when the user changes the sizo of the map .... event <Configure> 
# motion frame: Show robot's coordinates as status bar
# import: try/except ... 
# move forward/backward: let user choose which method to use (drive_straight or go to pose)
# wheelie
# draw an oval around the motion buttons 
# set up the top window in main(), start robotMainProgram with "try:" and issue an error message when device is not connected (for people who start CozmoCommander not from command line but from a graphical file manager) 
# viewer=4 --> create map

# done:
# draw cubes in map 2018-09-24
# map: dot to indicate position of robot 2018-09-24
# mark selectierted cube in map (change line width)
# map: crate wall 2018-09-28
# map doubleclick: draw little crosshair to indecate target 2018-09-28
# move forward: go to pose relative_to_ronot=True --> avoids walls (done, but it avoids walls only at a greater distance)
# abort_all_actions(log_abort_messages=False) .... wenn ich den Roboter nicht bewegen kann. oder in_parallel verwenden? 
# start_freeplay_behaviors() / stop_freeplay_behaviors()
# map axes: draw ticks every 100mm 


import sys

if (sys.version_info.major != 3):
	sys.exit('Please run CozmoCommander in Python 3.x')

try:
	import asyncio
except ImportError:
    sys.exit('Please run `pip3 install --user asyncio` to run CozmoCommander') 
	
try:
	import cozmo
	from cozmo.util import degrees, distance_mm, speed_mmps, Pose
except ImportError:
    sys.exit('Please run `pip3 install --user cozmo` to run CozmoCommander') 
 
try:
	import tkinter
	from tkinter import *
	from tkinter import messagebox
	# from tkinter.tix import *			# tooltips	# doesn't work 
except ImportError:
    sys.exit('Please run `pip3 install --user tkinter` to run CozmoCommander') 

try:
	import argparse
except ImportError:
    sys.exit('Please run `pip3 install --user argparse` to run CozmoCommander') 

try:
	import math
except ImportError:
    sys.exit('Please run `pip3 install --user math` to run CozmoCommander') 


#----------------------------------------------------------------	
def moveStraight (robot: cozmo.robot.Robot, Distance):
	# robot.drive_straight(distance_mm(Distance), speed_mmps(100)).wait_for_completed()
	# robot.drive_straight(distance_mm(Distance), speed_mmps(100))
	robot.go_to_pose(Pose(Distance, 0, 0, angle_z=degrees(0)), relative_to_robot=True)

#----------------------------------------------------------------	
def moveTurn 	(robot: cozmo.robot.Robot, Angle):
	# robot.turn_in_place(degrees(Angle)).wait_for_completed() 
	robot.turn_in_place(degrees(Angle)) 
	
#-----------------------------------------------------------------
def stop 	(robot: cozmo.robot.Robot):
	robot.abort_all_actions(log_abort_messages=False)
	
#-----------------------------------------------------------------
def playFree (robot: cozmo.robot.Robot):
	global PlayFree
	global BPlayFree
	
	if (not PlayFree):
		robot.start_freeplay_behaviors()
		PlayFree = True
		BPlayFree.config (relief = SUNKEN)
	else:	
		robot.stop_freeplay_behaviors()
		PlayFree = False
		BPlayFree.config (relief = RAISED)
		
		
#----------------------------------------------------------------	
def buttonCubeWindowGoto (robot: cozmo.robot.Robot, Distance):
	global CubeIndexGlobal
	robot.go_to_object(robot.world.light_cubes[CubeIndexGlobal], distance_mm(Distance)) 

	print ("Button Cube GoTo clicked")

	#----------------------------------------------------------------	
def buttonCubeWindowDock (robot: cozmo.robot.Robot, Angle):
	global CubeIndexGlobal
	robot.dock_with_cube(robot.world.light_cubes[CubeIndexGlobal], approach_angle=cozmo.util.degrees(Angle), num_retries=2)

	print ("Button Cube Dock clicked")

#----------------------------------------------------------------	
def buttonCubeWindowLift (robot: cozmo.robot.Robot):
	global CubeIndexGlobal
	robot.pickup_object(robot.world.light_cubes[CubeIndexGlobal], num_retries=3)

	print ("Button Cube Lift clicked")

#----------------------------------------------------------------	
def buttonCubeWindowPlaceOnTop (robot: cozmo.robot.Robot):
	global CubeIndexGlobal
	robot.place_on_object(robot.world.light_cubes[CubeIndexGlobal], num_retries=2)

	print ("Button Cube PlaceOnTop clicked")
	
#----------------------------------------------------------------	
def buttonCubeWindowRoll (robot: cozmo.robot.Robot):
	global CubeIndexGlobal
	# action = robot.roll_cube(robot.world.light_cubes[CubeIndexGlobal], check_for_object_on_top=True, num_retries=2)
	# action.wait_for_completed()
	#print("result:", action.result) 	
	
	try:
		robot.roll_cube(robot.world.light_cubes[CubeIndexGlobal], check_for_object_on_top=True, num_retries=2)
	except:
		messagebox.showinfo("Something wen wrong...")
		
	print ("Button Cube Roll clicked")

#----------------------------------------------------------------
def sayText (robot: cozmo.robot.Robot, Text):
	robot.say_text (Text)
#----------------------------------------------------------------	
def buttonCubeX(parent, robot: cozmo.robot.Robot, IndexCube):
	global CubeIndexGlobal
	global BCubeWindowWhichCube
	global BCube1
	global BCube2
	global BCube3
	
	print ("IndexCube " + str(IndexCube) + " Cube Id=" + str(robot.world.light_cubes[IndexCube].object_id) + " visible=" + str(robot.world.light_cubes[IndexCube].is_visible))
	# try:
		# # cubeWindow.deiconify()
		# # BCubeWindowWhichCube.config (text = "Cube" + str(robot.world.light_cubes[IndexCube].object_id))
		# cubeWindow.config (text = "Cube" + str(robot.world.light_cubes[IndexCube].object_id))
	# except:
		# messagebox.showinfo("Error", "Sorry, someone closed the cube window")
	# #cubeWindow.config (title = "Cube " + str(robot.world.light_cubes[IndexCube].object_id))
	
	BCube1.config (relief=RAISED)
	BCube2.config (relief=RAISED)
	BCube3.config (relief=RAISED)
	
	if (IndexCube==1):
		BCube1.config (relief=SUNKEN)
	elif (IndexCube==2):
		BCube2.config (relief=SUNKEN)
	elif (IndexCube==3):
		BCube3.config (relief=SUNKEN)
	
	CubeIndexGlobal = IndexCube
	
	print ("Button Cube" + str(IndexCube) + " clicked")
	
	
#----------------------------------------------------------------
def scaleLift (robot: cozmo.robot.Robot):
	robot.set_lift_height(ScLift.get(), in_parallel=True) 
 	
#----------------------------------------------------------------
def scaleHead (robot: cozmo.robot.Robot):
	robot.set_head_angle(degrees(ScHead.get()), in_parallel=True)  
 	
#----------------------------------------------------------------	
def cubeChangeColor (robot: cozmo.robot.Robot, IndexCube, Color):
	cols = [cozmo.lights.off_light] * 4
	for i in range(robot.world.light_cubes[IndexCube].object_id): # cube 1 gets 1 light, cube 2 gets 2 lights,  cube 3 gets 3 lights
		if (Color == "green"):
			cols[i] = cozmo.lights.green_light
		if (Color == "red"):
			cols[i] = cozmo.lights.red_light
			
	# if (IndexCube == CubeIndexGlobal):	# +++ geht nicht
		# cols[3] = "blue"
			
	robot.world.light_cubes[IndexCube].set_light_corners(*cols) 
	
#-------------------------------------------------------------------------
def animPlay (WhatToPlay):
	global AnimNames
	global CAnims
	global AnimLast
	global RobotGlobal
	
	print ("searching for ", WhatToPlay)
	AnimLast = WhatToPlay

	
	# find animation which matches the chosen name 
	Index = 0
	IndexToPlay = 0
	for Anim in (RobotGlobal.anim_triggers):
		# print (Anim.name)
		if (Anim.name == WhatToPlay):
			IndexToPlay = Index
		Index = Index + 1
	
	print ("playing ", RobotGlobal.anim_triggers[IndexToPlay].name)
	RobotGlobal.play_anim_trigger(RobotGlobal.anim_triggers[IndexToPlay])
	
	
#-------------------------------------------------------------------------
def printFaceData (Face):
	global LFaceData
	
	print ("ID:" + str(Face.face_id) + " name = " + Face.name)
	# LFaceData.config (text = "ID:" + str(Face.face_id) + " name = " + Face.name) +++++ bei LCubeWindowStatusBar geht's doch auch?????

# -------------------------------------------------------------------
def world2canvasX (WorldX):
	global MapWidth
	global MapHeight
	global MapScale
	
	return (WorldX / MapScale * MapWidth + MapWidth/2)
	
#--------------------------------------------------------------------
def world2canvasY (WorldY):
	global MapWidth
	global MapHeight
	global MapScale
	
	return (-WorldY / MapScale * MapWidth  + MapHeight/2)
	
#--------------------------------------------------------------------
def canvas2worldX (CanvasX):
	global MapWidth
	global MapHeight
	global MapScale

	X = CanvasX - MapWidth/2
	X = X / MapWidth * MapScale
	
	return (X)
	
#--------------------------------------------------------------------
def canvas2worldY (CanvasY):
	global MapWidth
	global MapHeight
	global MapScale

	Y = CanvasY - MapHeight/2
	Y = - Y / MapWidth * MapScale
	
	return (Y)

# -------------------------------------------------------------------
def angle360 (DeltaX, DeltaY):
	if (math.fabs(DeltaX) > 0.01):			# avoid division by 0
		Angle = math.fabs(DeltaY)/math.fabs(DeltaX)
		Angle = math.atan(Angle)
		Angle = math.degrees (Angle)
		# print (Angle)
	else:
		Angle = 90.0
	
	if   ((DeltaX > 0) and (DeltaY > 0)):
		pass
	elif ((DeltaX > 0) and (DeltaY < 0)):
		Angle = 360.0 - Angle
	elif ((DeltaX < 0) and (DeltaY > 0)):
		Angle = 180.0 - Angle
	elif ((DeltaX < 0) and (DeltaY < 0)):
		Angle = 180.0 + Angle
	return (Angle)
	
# -------------------------------------------------------------------
	
def onMapDoubleClick (coords):
	global MapActive
	global MapWindow
	global MapCanvas
	global MapWidth
	global MapHeight
	global MapRobotX
	global MapRobotY
	global RobotGlobal
	
	# print ("Got canvas click", coords.x, coords.y)
	
	# print (RobotGlobal.pose.position.x, RobotGlobal.pose.position.x)
	
	# X = coords.x - MapWidth/2
	# X = X / MapWidth * MapScale
	# Y = coords.y - MapHeight/2
	# Y = - Y / MapWidth * MapScale
	
	MapCanvas.create_line (coords.x - 4, coords.y, coords.x + 4, coords.y)
	MapCanvas.create_line (coords.x, coords.y - 4, coords.x, coords.y + 4)
	
	X = canvas2worldX (coords.x)
	Y = canvas2worldY (coords.y)
	
	DeltaX = X - RobotGlobal.pose.position.x
	DeltaY = Y - RobotGlobal.pose.position.y
	
		
	Angle = angle360 (DeltaX, DeltaY)
	
	# print (DeltaX, DeltaY, Angle)
	
	RobotGlobal.go_to_pose(Pose(X, Y, 0, angle_z=degrees(Angle)), relative_to_robot=False)
	
# -------------------------------------------------------------------
def createMap (robot: cozmo.robot.Robot):
	global MapActive
	global MapWindow
	global MapCanvas
	global MapWidth
	global MapHeight
	global MapRobotX
	global MapRobotY
	global RobotCircle
	global RobotCircleRadius
	global CubeSquares
	global BCube1
	global BCube2
	global BCube3
	
	if not MapActive:
		MapActive = True
		MapWindow = Toplevel(top, width=MapWidth, height=MapHeight)
		MapWindow.title ("Cozmo Commander 2D map")
		MapCanvas = Canvas (MapWindow, width=900, height=600)
		MapCanvas.pack()
		
		MapCanvas.create_line(0, MapHeight/2, MapWidth, MapHeight/2, fill="#C0C0C0")
		MapCanvas.create_line(MapWidth/2, 0, MapWidth/2, MapHeight, fill="#C0C0C0")
		
		X = 0
		NumTicks = int(MapWidth / 100 / 2)
		for i in range (NumTicks):
			X += 100
			MapCanvas.create_line (world2canvasX(X),  600/2 - 4, world2canvasX(X),  600/2 + 4, fill="#C0C0C0")
			MapCanvas.create_line (world2canvasX(-X), 600/2 - 4, world2canvasX(-X), 600/2 + 4, fill="#C0C0C0")
		
		Y = 0
		NumTicks = int(MapHeight / 100 / 2)
		for i in range (NumTicks):
			Y += 100
			MapCanvas.create_line (900/2 - 4, world2canvasY(Y),   900/2 + 4,  world2canvasY(Y),  fill="#C0C0C0")
			MapCanvas.create_line (900/2 - 4, world2canvasY(-Y),  900/2 + 4,  world2canvasY(-Y), fill="#C0C0C0")
		
		MapRobotX = robot.pose.position.x
		MapRobotY = robot.pose.position.y
		
		MapCanvas.bind ('<Double-1>', onMapDoubleClick)
		
		# RobotCircleRadius = 5
		RobotCircle = MapCanvas.create_oval ( 
			world2canvasX(0) - RobotCircleRadius, 
			world2canvasY(0) - RobotCircleRadius, 
			world2canvasX(0) + RobotCircleRadius, 
			world2canvasY(0) + RobotCircleRadius
			)
		MapCanvas.itemconfig(RobotCircle, fill="black")

		# for Index in range(4):
		for Index in range(3):
			CubeSquare = MapCanvas.create_rectangle ( 
				world2canvasX(0) - RobotCircleRadius, 
				world2canvasY(0) - RobotCircleRadius, 
				world2canvasX(0) + RobotCircleRadius, 
				world2canvasY(0) + RobotCircleRadius
				)
			CubeSquares.append(CubeSquare)
		
		# MapCanvas.tag_bind (CubeSquares[0], '<Double-1>', BCube1.invoke()) # funktioniert nicht 
		# MapCanvas.tag_bind (CubeSquares[1], '<Double-1>', BCube2.invoke())
		# MapCanvas.tag_bind (CubeSquares[2], '<Double-1>', BCube3.invoke())
		MapCanvas.tag_bind (CubeSquares[0], '<Double-1>', lambda: buttonCubeX(root, robot, 1))   #buttonCubeX(parent, robot: cozmo.robot.Robot, IndexCube)
		MapCanvas.tag_bind (CubeSquares[1], '<Double-1>', lambda: buttonCubeX(root, robot, 2))
		MapCanvas.tag_bind (CubeSquares[2], '<Double-1>', lambda: buttonCubeX(root, robot, 3))
		
		MapCanvas.bind ('<B1-Motion>', drawLineMouseDown)
		# MapCanvas.bind ('<Motion>', drawLineMouseUp)
		MapCanvas.bind ('<ButtonRelease-1>', drawLineMouseUp)

		
		drawMap (robot)	# first call to drawMap, from then on it will activate itself periodically

#------------------------------------------------------------------------------
def drawMap (robot: cozmo.robot.Robot):
	global MapWindow
	global MapActive
	global MapRobotX
	global MapRobotY
	global MapScale
	global RobotCircle
	global RobotCircleRadius
	global CubeSquares

	if (MapActive):
		X = robot.pose.position.x
		Y = robot.pose.position.y
		
		try:
			# MapCanvas.create_line   (MapRobotX / MapScale * MapWidth + MapWidth/2, - MapRobotY / MapScale * MapWidth  + MapHeight/2, X / 1000 * MapWidth + MapWidth/2, - Y / 1000 * MapWidth  + MapHeight/2)
			MapCanvas.coords (RobotCircle, 
				world2canvasX(MapRobotX) - RobotCircleRadius, 
				world2canvasY(MapRobotY) - RobotCircleRadius, 
				world2canvasX(MapRobotX) + RobotCircleRadius, 
				world2canvasY(MapRobotY) + RobotCircleRadius
				)
			MapCanvas.create_line   (world2canvasX(MapRobotX) , world2canvasY(MapRobotY), world2canvasX(X), world2canvasY(Y))
		except:
			MapActive = False
			# messagebox.showinfo("Error", "My map is gone!")
			# top.after (350, lambda: createMap(robot))
			
		MapRobotX = X
		MapRobotY = Y
		
	for IndexCube in range(1,4):
		MapCanvas.coords (CubeSquares[IndexCube-1],
			world2canvasX(robot.world.light_cubes[IndexCube].pose.position.x) - RobotCircleRadius,
			world2canvasY(robot.world.light_cubes[IndexCube].pose.position.y) - RobotCircleRadius,
			world2canvasX(robot.world.light_cubes[IndexCube].pose.position.x) + RobotCircleRadius,
			world2canvasY(robot.world.light_cubes[IndexCube].pose.position.y) + RobotCircleRadius
			)
			
		if (robot.world.light_cubes[IndexCube].is_visible):
			 MapCanvas.itemconfig (CubeSquares[IndexCube-1], fill="lightgreen")
		else:
			 MapCanvas.itemconfig (CubeSquares[IndexCube-1], fill="red")
		
		if (IndexCube == CubeIndexGlobal):
			MapCanvas.itemconfig (CubeSquares[IndexCube-1], width=3)
		else:
			MapCanvas.itemconfig (CubeSquares[IndexCube-1], width=1)
		
		
		
	# --- repeatedly restart this function ---
	top.after (205, lambda: drawMap(robot))

#----------------------------------------------------------------------------
def drawLineMouseUp (event):
	global FlagMouseDown
	global LineCoords
	global Line
	global MapCanvas
	
	if (FlagMouseDown == True):		# +++ no longer needed as we use <Release> instead of <Move>
		FlagMouseDown = False
		
		MapCanvas.itemconfig (Line, fill="darkred")
		MapCanvas.itemconfig (Line, width=3)
		
		DeltaX = canvas2worldX(LineCoords[2]) - canvas2worldX(LineCoords[0])
		DeltaY = canvas2worldY(LineCoords[3]) - canvas2worldY(LineCoords[1])
		
		Angle = angle360 (DeltaX, DeltaY)
		print ("Angle: ", Angle)
		# Angle += 90
		# if (Angle > 360):
			# Angle -= 360

		Wall = RobotGlobal.world.create_custom_fixed_object(
					Pose(canvas2worldX(LineCoords[0]) + DeltaX/2, canvas2worldY(LineCoords[1]) + DeltaY/2, 0, angle_z=degrees(Angle)),
					math.sqrt(DeltaX ** 2 + DeltaY ** 2), 10, 100, 
					relative_to_robot=False)			

		if Wall:
			print("Wall created successfully")
		else:
			print ("Could not create wall")

#----------------------------------------------------------------------------
def drawLineMouseDown (event):
	global FlagMouseDown
	global LineCoords
	global Line
	
	if (FlagMouseDown == False):
		# begin to draw line
		FlagMouseDown = True
		LineCoords[0] = event.x
		LineCoords[1] = event.y
		
		Line = MapCanvas.create_line (LineCoords[0], LineCoords[1], event.x, event.y) # actually the line length is 0
		
	else:
		LineCoords[2] = event.x
		LineCoords[3] = event.y
		MapCanvas.coords (Line, LineCoords[0], LineCoords[1], event.x, event.y)
		
#------------------tick--------------------------------------------------------
def tick (parent, robot: cozmo.robot.Robot):
	
	global CubeIndexGlobal
	global LCubeWindowStatusBar

	
	try:
		VisibleCube = robot.world.wait_for_observed_light_cube(timeout=0.1)
		# actually we don't need VisibleCube, and for now it doesn't matter if cubes are found. 
		# We call this function for its side effect, i.e. filling in the data into robot.world.light_cubes[]
		# print("Found cube: %s" % cube.object_id )
		pass
	except asyncio.TimeoutError:
		# print("Didn't find a cube") 
		pass
	
	if robot.world.light_cubes[1].is_visible:
		BCube1.config(bg = "lightgreen")
	else:
		BCube1.config(bg = "red")
	
	if robot.world.light_cubes[2].is_visible:
		BCube2.config(bg = "lightgreen")
	else:
		BCube2.config(bg = "red")
	
	if robot.world.light_cubes[3].is_visible:
		BCube3.config(bg = "lightgreen")
	else:
		BCube3.config(bg = "red")
	
	for IndexCube in range(1,4):
		if (robot.world.light_cubes[IndexCube].is_visible):
			cubeChangeColor (robot, IndexCube, "green")
		else:
			cubeChangeColor (robot, IndexCube, "red")
			
	ID     = robot.world.light_cubes[CubeIndexGlobal].object_id
	XPos   = round(robot.world.light_cubes[CubeIndexGlobal].pose.position.x)
	YPos   = round(robot.world.light_cubes[CubeIndexGlobal].pose.position.y)
	ZPos   = round(robot.world.light_cubes[CubeIndexGlobal].pose.position.z)
	AngleZ = round(robot.world.light_cubes[CubeIndexGlobal].pose.rotation.angle_z.degrees)
            
	LCubeWindowStatusBar.config (text = "Cube" + str(ID) + ": X=" + str(XPos) + ", Y=" + str(YPos) + ", Z=" + str(ZPos) + ", " + str(AngleZ) + "°")
	
	# --------faces------------
	
	global OldFace	# doesnt really need to be global, but it mimics a static variable here
	SeeFace = True
	
	try:
		Face = robot.world.wait_for_observed_face(timeout=0.1) 
	except asyncio.TimeoutError:
		SeeFace = False
	
	if SeeFace:
		if OldFace == 0:
			NewFace = True			# first time we see a face
		elif OldFace.is_visible:
			NewFace = False			# we have seen a face before
		else:
			NewFace = True			# face came in sight again
		
		if NewFace:
			printFaceData (Face)
			
		OldFace = Face					# get ready for next time 
		
	else:
		OldFace = False

		
	# --- repeatedly restart this function ---
	parent.after (1000, lambda: tick(parent, robot))

#----------------robotMainProgram----------------------------------------------------
def robotMainProgram(robot: cozmo.robot.Robot):

	global top 		
	global LDist 		
	global EDist 		
	global LAng 		
	global EAng 		
	global BForward 	
	global BBack 		
	global BRight 		
	global BLeft 		
	global BCube1 		
	global BCube2 		
	global BCube3 		
	global ScHead 		
	global BHead 		
	global ScLift 		
	global BLift 		
	global cubeWindow 	
	# global BCubeWindowWhichCube 
	# global BCubeWindowClose 		
	global BCubeWindowDock 		
	global SCubeWindowDockAngle
	global BCubeWindowLift 		
	global BCubeWindowPlaceOnTop 
	global BCubeWindowRoll
	global LFaceData
	global LStatusBar
	global LCubeWindowStatusBar
	global AnimNames
	global CAnims
	global AnimLast
	global BPlayFree

	global RobotGlobal
	
	RobotGlobal = robot

	
	# set up the GUI
	top = tkinter.Tk()
	top.geometry("900x600")
	top.title("Cozmo Commander")
	# ToolTp = Balloon()	# doesn't work 
	
	# frames
	motionWindow = Frame(top, bd=2, width=300, height=450, relief=GROOVE)
	motionWindow.grid_propagate(0)			# frame at fixed size instead of shrink to content
	motionWindow.place (x=0, y=50)

	cubeWindow = Frame(top, bd=2, width=300, height=450, relief=GROOVE)
	cubeWindow.grid_propagate(0)			# frame at fixed size instead of shrink to content
	cubeWindow.place (x=300, y=50)

	FaceWindow = Frame(top, bd=2, width=300, height=450, relief=GROOVE)
	FaceWindow.grid_propagate(0)			# frame at fixed size instead of shrink to content
	FaceWindow.place (x=600, y=50)

	# --- motion controls ---
	Row=0
	LMotion = Label (motionWindow, text="motion", bd=2, relief=GROOVE).grid (row=Row, columnspan=3)
	Row+=1
	LEmpty01 = Label (motionWindow, text="").grid (row=Row, columnspan=3)
	# LMotion.place(x=0, y=0)
	
	Row+=1
	LDist = Label (motionWindow, text="Distance")
	LDist.grid(row=Row, sticky=W)
	# ToolTp.bind_widget(LDist, balloonmsg="Distance in mm to move when \"Forward\" or \"Backward\" is pressed")	# doesn't work 
	EDist = Entry (motionWindow, bd=2)
	EDist.grid(row=Row, column=2, columnspan=2)
	EDist.insert (0, "100")	# start value

	Row+=1
	LAng = Label (motionWindow, text="Angle")
	LAng.grid(row=Row, sticky=W)
	# ToolTp.bind_widget(LAng, balloonmsg="Angle in ° to turn when \"Left\" or \"Right\" is pressed")	# doesn't work 
	EAng = Entry (motionWindow, bd=2)
	EAng.grid(row=Row, column=2, columnspan=2)
	EAng.insert (0, "45")	# start value

	Row+=1
	LEmpty02 = Label (motionWindow, text="").grid (row=Row, columnspan=3)

	Row+=1
	BForward = Button(motionWindow, text = "Forward", command = lambda: moveStraight(robot, float(EDist.get())))	
	BForward.grid(row=Row, column=2)
	# ToolTp.bind_widget(BForward, balloonmsg="Move Forward by the distance in mm given above")	# doesn't work 

	Row+=1
	BRight = Button(motionWindow, text = "Right", command = lambda: moveTurn(robot, float(EAng.get())*(-1.0)))
	BRight.grid(row=Row, column=3)

	BLeft = Button(motionWindow, text = "Left", command = lambda: moveTurn(robot, float(EAng.get())))
	BLeft.grid(row=Row, column=1)

	Row+=1
	BBack = Button(motionWindow, text = "Backward", command = lambda: moveStraight(robot, float(EDist.get())*(-1.0)))
	BBack.grid(row=Row, column=2)

	Row+=1
	LEmpty03 = Label (motionWindow, text="").grid (row=Row, columnspan=3)

	Row+=1
	ScHead = Scale (motionWindow, orient = VERTICAL, from_ = 45, to = -25, resolution=5)
	ScHead.grid(row=Row+1, column=1)
	ScHead.set(0)
	BHead = Button(motionWindow, text = "Head", command = lambda: scaleHead(robot))
	BHead.grid(row=Row, column=1)
	BHead.invoke() 	# set head to horizontal at startup
	ScLift = Scale (motionWindow, orient = VERTICAL, from_ = 1.0, to = 0.0, resolution=0.1)
	ScLift.grid(row=Row+1, column=2)
	ScLift.set(0)
	BLift = Button(motionWindow, text = "Lift", command = lambda: scaleLift(robot))
	BLift.grid(row=Row, column=2)
	BLift.invoke() 	# set lift down at startup
	
	Row+=2
	LEmpty04 = Label (motionWindow, text="").grid (row=Row, columnspan=3)

	Row+=1
	BCanvas = Button (motionWindow, text = "map", command = lambda: createMap(robot)) 
	BCanvas.grid(row=Row, column=1)
	BStop = Button (motionWindow, text = "stop", command = lambda: stop(robot)) 
	BStop.grid(row=Row, column=2)
	BPlayFree = Button (motionWindow, text = "play", relief = RAISED, bd=2, command = lambda: playFree(robot))
	BPlayFree.grid(row=Row, column=3)

	# --- cube window ---
	Row=0
	LCube = Label (cubeWindow, text="cubes", bd=2, relief=GROOVE).grid (row=Row, columnspan=3)
	Row+=1
	LEmpty10 = Label (cubeWindow, text="").grid (row=Row, columnspan=3)
	
	Row+=1
	BCube1 = Button(cubeWindow, text = "Cube" + str(robot.world.light_cubes[1].object_id), relief=RAISED, bd=5, command = lambda: buttonCubeX(motionWindow, robot, 1))
	BCube1.grid(row=Row, column=1)
	BCube2 = Button(cubeWindow, text = "Cube" + str(robot.world.light_cubes[2].object_id), relief=RAISED, bd=5, command = lambda: buttonCubeX(motionWindow, robot, 2))
	BCube2.grid(row=Row, column=2)
	BCube3 = Button(cubeWindow, text = "Cube" + str(robot.world.light_cubes[3].object_id), relief=RAISED, bd=5, command = lambda: buttonCubeX(motionWindow, robot, 3))
	BCube3.grid(row=Row, column=3)

	Row+=1
	LEmpty11 = Label (cubeWindow, text="").grid (row=Row, columnspan=3)
	
	Row+=1
	BCubeWindowGoto = Button (cubeWindow, text="go to", command = lambda: buttonCubeWindowGoto(robot, float(ECubeWindowGotoDistance.get())))
	BCubeWindowGoto.grid(row=Row, column=1, sticky=W)
	ECubeWindowGotoDistance = Entry (cubeWindow)
	ECubeWindowGotoDistance.grid (row=Row, column=2, columnspan=2, sticky=W)
	ECubeWindowGotoDistance.insert(0,70)
	Row+=1
	BCubeWindowDock = Button (cubeWindow, text="dock", command = lambda: buttonCubeWindowDock(robot, SCubeWindowDockAngle.get()))
	BCubeWindowDock.grid(row=Row, column=1, sticky=W)
	SCubeWindowDockAngle = Scale (cubeWindow, orient = HORIZONTAL, from_=0, to=270, resolution=90)
	SCubeWindowDockAngle.grid (row=Row, column=2, columnspan=2)
	Row+=1
	BCubeWindowLift = Button (cubeWindow, text="lift", command = lambda: buttonCubeWindowLift(robot))
	BCubeWindowLift.grid(row=Row, column=1, sticky=W)
	Row+=1
	BCubeWindowPlaceOnTop = Button (cubeWindow, text="put on top", command = lambda: buttonCubeWindowPlaceOnTop(robot))
	BCubeWindowPlaceOnTop.grid(row=Row, column=1, sticky=W)
	Row+=1
	BCubeWindowRoll = Button (cubeWindow, text="roll", command = lambda: buttonCubeWindowRoll(robot))
	BCubeWindowRoll.grid(row=Row, column=1, sticky=W)
	
	LCubeWindowStatusBar = Label (cubeWindow, text="Status...", bd=2, relief=FLAT, anchor=W)
	LCubeWindowStatusBar.place (x=0, y=425)
	
	# --- face window ---
	Row = 0
	LFaceWindow = Label (FaceWindow, text="faces", bd=2, relief=GROOVE).grid (row=Row, columnspan=3)
	Row+=1
	LEmpty20 = Label (FaceWindow, text="").grid (row=Row, columnspan=3)
	
	Row+=1
	LFaceData = Label (FaceWindow, text="").grid (row=Row, columnspan=3, sticky=W)

	# --- lower region ----
	LStatusBar = Label (top, text="Status...", bd=2, relief=GROOVE, anchor=W)
	LStatusBar.pack (side=BOTTOM, fill=X)
	
	FSayText = Frame(width=900)
	# FSayText.pack_propagate(0)			# frame at fixed size instead of shrink to content +++ 
	BSayText = Button (FSayText, text = "say", command = lambda: sayText (robot, ESayText.get()))
	BSayText.pack (side=RIGHT)
	ESayText = Entry (FSayText, width=700)
	ESayText.pack (side=LEFT, expand= YES, fill = BOTH)
	ESayText.insert (0, "Hallo")
	FSayText.pack (side=BOTTOM)
	
	FAnims = Frame(top)
	AnimChosen = StringVar()
	AllAnimationTriggers = robot.anim_triggers 
	AnimNames = []
	for Anim in (AllAnimationTriggers):
		AnimNames.append(Anim.name)

	AnimChosen.set (AnimNames[0])
	AnimLast = AnimNames[0]
	CAnims = OptionMenu(FAnims, AnimChosen, *AnimNames, command=animPlay)	
	CAnims.pack(side=LEFT)
	BAnims = Button (FAnims, text="repeat", command=lambda: animPlay(AnimLast))
	BAnims.pack (side=RIGHT)
	FAnims.pack (side=BOTTOM)
		
		
		
		
		
	# start background process(es) 
	top.after (1000, lambda: tick(top, robot))

	# start GUI
	top.mainloop()
	
#---------------------------------start-working-------------------------
# parse arguments 
parser = argparse.ArgumentParser(description="Simple graphic interface for Cozmo")
parser.add_argument("--viewer", type=str, default=0, help="0 = no viewer (default), 1 = Camera, 2 = 3D, 3 = Camera+3D")
args = parser.parse_args()

Use3D  = False
UseCam = False
OffCharger = True

Viewer = int(args.viewer)
if ((Viewer & 1) != 0):
		UseCam = True
if ((Viewer & 2) != 0):
		Use3D = True
if ((Viewer & 4) != 0):
		cozmo.robot.Robot.drive_off_charger_on_connect = False  # Cozmo can stay on his charger for this example 
		
# global variables
CubeIndexGlobal = 1
OldFace = 0
MapActive = False
MapWindow = 0
MapCanvas = 0
MapWidth  = 900
MapHeight = 600
MapRobotX = 0
MapRobotY = 0
MapScale  = 1000
RobotGlobal = 0
AnimNames = []
AnimLast = ""
RobotCircle = 0
RobotCircleRadius = 5
CubeSquares = []
FlagMouseDown = False
Line = 0
LineCoords = [0,0,0,0]
PlayFree = False



		
# global variables for the GUI
# when we refer to a control from outside robotMainProgram, like changing the color of a button, 
# we need to have it global. 
# We cannot yet set them up because we need "robot" to be passed as a parameter, and this will be known in robotMainProgram. 
# Furthermore, they must reside in robotMainProgram. Otherwise the viewers cannot be used. 
# For now, they are integers an will be assigned the appropriate type later. 
top 					= 0
LDist 					= 0
EDist 					= 0
LAng 					= 0
EAng 					= 0
BForward 				= 0
BBack 					= 0
BRight 					= 0
BLeft 					= 0
BCube1 					= 0
BCube2 					= 0
BCube3 					= 0
ScHead 					= 0
BHead 					= 0
ScLift 					= 0
BLift 					= 0
cubeWindow 				= 0
BCubeWindowWhichCube 	= 0
BCubeWindowClose 		= 0
BCubeWindowDock 		= 0
SCubeWindowDockAngle	= 0
BCubeWindowLift 		= 0
BCubeWindowPlaceOnTop 	= 0
BCubeWindowRoll			= 0
LFaceData				= 0
LCubeWindowStatusBar	= 0
LStatusBar				= 0
CAnims					= 0
BPlayFree				= 0

# start main program
#cozmo.robot.Robot.drive_off_charger_on_connect = False  # Cozmo can stay on charger for now 
cozmo.run_program(robotMainProgram, use_3d_viewer=Use3D, use_viewer=UseCam)
