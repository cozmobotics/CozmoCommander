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
# map button: map ein- und ausschalten (RAISED/SUNKEN) 
# Würfel durch Anklicken in der Karte selektieren (BCubex invoke) ... programmiert, aber geht nicht 
# backup_onto_charger(max_drive_time=3)
# anim_names ... bisher verwende ich nur anim_triggers
# drive_wheel_motors für Steuerung auf Kurvenbahnen, nicht so abgehackt. Grafische Eingabemöglichkeit? --> extra project
# Maus-button drücken und halten, und dann joystick-artig bewegen?  --> extra project
# turn_towards_face ... robot.turn_towards_face(face_to_follow) 
# enable_facial_expression_estimation ???
# delete walls (all of them) 
# play sounds ... see 10_play_sound.py  ... cozmo.audio.AudioEvents
# map: redraw the axes when the user changes the sizo of the map .... event <Configure> 
# motion frame: Show robot's coordinates as status bar
# draw an oval around the motion buttons 
# set up the top window in main(), start robotMainProgram with "try:" and issue an error message when device is not connected (for people who start CozmoCommander not from command line but from a graphical file manager) 
# When user clicks on map button again, put focus on map 
# get_on_charger() ... map is not updated. Parallel tasks with threading? 
# German description (html)
# get_on_charger() ... optionally exit the program when PROCEDURE SUCCEEDED
# show a little animation on the map when cube is tapped. Programmed, bot does not work (see drawRingAnimation())
# ISSUE: "say" entry and button not visible when using viewer=1 ("say" entry and button appear on viewer window) 
# ISSUE: animation menu doesn't show test when using viewer=1 
# ISSUE: program hangs when closing the viewer window 
# take picture/video and save it 
# multi robot 
# display robot serial number ... function robot.serial(). Where to put it? Menu --> about 
# Add a menu. Menu items: help, about, debug level 
# volume control 

# done:
# draw cubes in map 2018-09-24
# map: dot to indicate position of robot 2018-09-24
# mark selectierted cube in map (change line width)
# map: crate wall 2018-09-28
# map doubleclick: draw little crosshair to indecate target 2018-09-28
# move forward: go to pose relative_to_ronot=True --> avoids walls (done, but it avoids walls only at a greater distance)
# abort_all_actions(log_abort_messages=False) .... wenn ich den Roboter nicht bewegen kann. oder in_parallel verwenden? 
# start_freeplay_behaviors() / stop_freeplay_behaviors()
# walls in different color 
# map axes: draw ticks every 100mm 
# Bug: Offensichtlich habe ich vier cubes in der Karte erzeugt   
# import: try/except ... 
# entry for speed 2018-10-18
# --- git commit --- 2018-10-19 ---
# move forward/backward: let user choose which method to use (drive_straight or go to pose) 2018-10-18
# head und lift slider ... command, get rid of Buttons (doesn't work very well, I keep the buttons)
# wheelie (programmed, but Cozmo stops with message "cozmo.general INFO     Robot delocalized - invalidating poses for all objects")
# The selected cube gets a blue light 2018-10-20
# "Go to/from Charger"
# Get battery status, print in status line  2018-10-20
# Cube Status line: print bttery status   2018-10-20
# Integrate get_on_charger() by Lucas Waelti  2018-10-23
# --- git commit --- 2018-10-23 ---
# map: represent robot as arc, showing its rotation angle 2018-10-23
# move robot with cursor keys ... root.bind("<Key>", callbackKey), MapCanvas.bind("<Key>", callbackKey)  2018-10-24
# bugfix: handle situation when a cube is not connected (e.g. battery low). Not yet perfect, but at least I don`t crash. 
# select a cube by tapping it. Programmed, bot does not work. Program hangs after a few times a cube got tapped.  
# option --tap ... disable handler for cube tapped event (workaround)
# option --viewer=4 ... 2D map 
# option --docc (drive off charger contacts) 
# option: --dfac (disconnect from all cubes)
# button to disconnect/connect from/to cubes 
# debug feature, lets you define a debug level 
# button to enable color image ... color_image_enabled()
# button to enable Infraread (night-Mode) ... set_head_light(enable)
# ISSUE: program hangs when tapping cubes. Workaround: disable tapping via command line option. Solution: enable_block_tap_filter
# result of cliff detection in status line
# picked up --> status line 

import sys
import time

if (sys.version_info.major != 3):
	sys.exit('Please run CozmoCommander in Python 3.x')

try:
	import asyncio
except ImportError:
    sys.exit('Please run `pip3 install --user asyncio` to run CozmoCommander') 
	
try:
	import cozmo
	from cozmo.util import degrees, radians, distance_mm, speed_mmps, Pose
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

#-----------------------------------------------------------------
def debug (Level, Message): 
	global args
	if (Level <= args.debug):
		print (Message)
	
#-----------------------------------------------------------------
def methodDriveStraight ():
	global BMethodDriveStraight
	global BMethodGoToPose
	global DriveMethod
	global ESpeed
	
	debug (3,"Drive straight")
	BMethodDriveStraight.config (relief = SUNKEN)
	BMethodGoToPose.config (relief = RAISED)
	DriveMethod	= "DriveStraight"
	ESpeed.config (state = NORMAL)
	
#-----------------------------------------------------------------
def methodGoToPose ():
	global BMethodDriveStraight
	global BMethodGoToPose
	global DriveMethod
	global ESpeed
	
	debug (3,"Go to pose")
	BMethodDriveStraight.config (relief = RAISED)
	BMethodGoToPose.config (relief = SUNKEN)
	DriveMethod	= "GoToPose"
	ESpeed.config (state = DISABLED)
	

#----------------------------------------------------------------	
def moveStraight (robot: cozmo.robot.Robot, Distance, Speed):
	global DriveMethod
	# robot.drive_straight(distance_mm(Distance), speed_mmps(Speed)).wait_for_completed()
	if (DriveMethod == "DriveStraight"):
		robot.drive_straight(distance_mm(Distance), speed_mmps(Speed))
	else:
		robot.go_to_pose(Pose(Distance, 0, 0, angle_z=degrees(0)), relative_to_robot=True)


#----------------------------------------------------------------	
def moveTurn 	(robot: cozmo.robot.Robot, Angle):
	# robot.turn_in_place(degrees(Angle)).wait_for_completed() 
	robot.turn_in_place(degrees(Angle)) 
	
#-----------------------------------------------------------------
def stop 	(robot: cozmo.robot.Robot):
	robot.stop_all_motors()
	robot.abort_all_actions(log_abort_messages=False)
	
#-----------------------------------------------------------------
def playFree (robot: cozmo.robot.Robot):
	global PlayFree
	global BPlayFree
	
	if (not PlayFree):
		robot.start_freeplay_behaviors()
		PlayFree = True
		BPlayFree.config (relief = SUNKEN)
		debug (3,"start_freeplay_behaviors")
	else:	
		robot.stop_freeplay_behaviors()
		PlayFree = False
		BPlayFree.config (relief = RAISED)
		debug (3,"stop_freeplay_behaviors")
		
		
#----------------------------------------------------------------	
def buttonCubeWindowGoto (robot: cozmo.robot.Robot, Distance):
	global CubeIndexGlobal
	robot.go_to_object(robot.world.light_cubes[CubeIndexGlobal], distance_mm(Distance)) 

	debug (3,"Button Cube GoTo clicked")

	#----------------------------------------------------------------	
def buttonCubeWindowDock (robot: cozmo.robot.Robot, Angle):
	global CubeIndexGlobal
	robot.dock_with_cube(robot.world.light_cubes[CubeIndexGlobal], approach_angle=cozmo.util.degrees(Angle), num_retries=2)

	debug (3,"Button Cube Dock clicked")

#----------------------------------------------------------------	
def buttonCubeWindowLift (robot: cozmo.robot.Robot):
	global CubeIndexGlobal
	robot.pickup_object(robot.world.light_cubes[CubeIndexGlobal], num_retries=3)

	debug (3,"Button Cube Lift clicked")

#----------------------------------------------------------------	
def buttonCubeWindowPlaceOnTop (robot: cozmo.robot.Robot):
	global CubeIndexGlobal
	robot.place_on_object(robot.world.light_cubes[CubeIndexGlobal], num_retries=2)

	debug (3,"Button Cube PlaceOnTop clicked")
	
#----------------------------------------------------------------	
def buttonCubeWindowRoll (robot: cozmo.robot.Robot):
	global CubeIndexGlobal
	# action = robot.roll_cube(robot.world.light_cubes[CubeIndexGlobal], check_for_object_on_top=True, num_retries=2)
	# action.wait_for_completed()
	#print("result:", action.result) 	
	
	try:
		robot.roll_cube(robot.world.light_cubes[CubeIndexGlobal], check_for_object_on_top=True, num_retries=2)
	except:
		messagebox.showinfo("Something went wrong...")
		

#----------------------------------------------------------------	
def buttonCubeWindowWheelie (robot: cozmo.robot.Robot):
	global CubeIndexGlobal
	
	try:
		robot.pop_a_wheelie(robot.world.light_cubes[CubeIndexGlobal], num_retries=2)
	except:
		messagebox.showinfo("Something went wrong...")
		
#---------------------------------------------------------------------------------
def buttonCubeWindowDisConnect (robot: cozmo.robot.Robot):
	global CubesConnected
	global BCubeDisConnect
	
	if CubesConnected:
		robot.world.disconnect_from_cubes() 
		CubesConnected = False
		BCubeDisConnect.config (text = "connect to all cubes")
	else:
		robot.world.connect_to_cubes()
		CubesConnected = True
		BCubeDisConnect.config (text = "disconnect from all cubes")
		
#----------------------------------------------------------------
def sayText (robot: cozmo.robot.Robot, Text):
	robot.say_text (Text)
#----------------------------------------------------------------	
def buttonCubeX(robot: cozmo.robot.Robot, IndexCube):
	global CubeIndexGlobal
	global BCubeWindowWhichCube
	global BCube1
	global BCube2
	global BCube3
	
	debug (2,"IndexCube " + str(IndexCube) + " Cube Id=" + str(robot.world.light_cubes[IndexCube].object_id) + " visible=" + str(robot.world.light_cubes[IndexCube].is_visible))
	
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
	
	debug (3,"Button Cube" + str(IndexCube) + " clicked")
	
	
#----------------------------------------------------------------
def scaleLift (Height):
	global RobotGlobal
	
	RobotGlobal.set_lift_height(float(Height), in_parallel=True) 




	# robot.set_lift_height(ScLift.get(), in_parallel=True) 
 	
#----------------------------------------------------------------
def scaleHead (Angle):
	global RobotGlobal
	
	RobotGlobal.set_head_angle(degrees(int(Angle)), in_parallel=True) 
	# RobotGlobal.set_head_angle(degrees(ScHead.get()), in_parallel=True)  
	
	# robot.set_head_angle(degrees(ScHead.get()), in_parallel=True)  
 	
########################## Charger related code ##########################
def frustrated(robot: cozmo.robot.Robot):
    trigger = cozmo.anim.Triggers.FrustratedByFailureMajor  
    robot.play_anim_trigger(trigger)

def celebrate(robot: cozmo.robot.Robot):
    trigger = cozmo.anim.Triggers.CodeLabCelebrate  
    # robot.play_anim_trigger(trigger,body=True,lift=True,parallel=True)
    robot.play_anim_trigger(trigger)

def turn_around():
    global RobotGlobal
    robot = RobotGlobal
    robot.turn_in_place(degrees(-180)).wait_for_completed()
    return


def find_charger():
    global RobotGlobal
    robot = RobotGlobal

    while(True):
        
        behavior = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
        try: 
            seen_charger = robot.world.wait_for_observed_charger(timeout=10,include_existing=True)
        except:
            seen_charger = None
        behavior.stop()
        if(seen_charger != None):
            debug (2,seen_charger)
            return seen_charger
        frustrated(robot)
        robot.say_text('Charge?',duration_scalar=0.5).wait_for_completed()
    return None

def go_to_charger():
    # Driving towards charger without much precision
    global RobotGlobal
    robot = RobotGlobal

    charger = None
    ''' cf. 08_drive_to_charger_test.py '''
    # see if Cozmo already knows where the charger is
    if robot.world.charger:
        # make sure Cozmo was not delocalised after observing the charger
        if robot.world.charger.pose.is_comparable(robot.pose):
            debug (1,"Cozmo already knows where the charger is!")
            charger = robot.world.charger
        else:
            # Cozmo knows about the charger, but the pose is not based on the
            # same origin as the robot (e.g. the robot was moved since seeing
            # the charger) so try to look for the charger first
            pass
    if not charger:
        charger = find_charger()
    
    action = robot.go_to_object(charger,distance_from_object=distance_mm(80), in_parallel=False, num_retries=5)
    #action = robot.go_to_pose(charger.pose)
    action.wait_for_completed()
    return charger

def disp_coord(charger: cozmo.objects.Charger):
    # Debugging function used to diplay coordinates of objects
    # (Not currently used)
    global RobotGlobal
    robot = RobotGlobal

    r_coord = robot.pose.position #.x .y .z, .rotation otherwise
    r_zRot = robot.pose_angle.degrees # or .radians
    c_coord = charger.pose.position
    c_zRot = charger.pose.rotation.angle_z.degrees

    debug (3,'Recorded coordinates of the robot and charger:')
    debug (3,'Robot:' + str(end=' '))
    debug (3,r_coord)
    debug (3,r_zRot)
    debug (3,'Charger:' + str(end=' '))
    debug (3,c_coord)
    debug (3,c_zRot)
    debug (3,'\n')

PI = 3.14159265359
def clip_angle(angle=3.1415):
	# Allow Cozmo to turn the least possible. Without it, Cozmo could
	# spin on itself several times or turn for instance -350 degrees
	# instead of 10 degrees. 
    global PI

    # Retreive supplementary turns (in radians)
    while(angle >= 2*PI):
        angle -= 2*PI
    while(angle <= -2*PI):
        angle += 2*PI
    # Select shortest rotation to reach the target
    if(angle > PI):
    	angle -= 2*PI
    elif(angle < -PI):
    	angle += 2*PI
    return angle

def check_tol(charger: cozmo.objects.Charger,dist_charger=40):
    # Check if the position tolerance in front of the charger is respected
    global RobotGlobal
    robot = RobotGlobal
    global PI

    distance_tol = 5 # mm, tolerance for placement error
    angle_tol = 5*PI/180 # rad, tolerance for orientation error

    try: 
        charger = robot.world.wait_for_observed_charger(timeout=2,include_existing=True)
    except:
        debug (1,'WARNING: Cannot see the charger to verify the position.')

    # Calculate positions
    r_coord = [0,0,0]
    c_coord = [0,0,0]
    # Coordonates of robot and charger
    r_coord[0] = robot.pose.position.x #.x .y .z, .rotation otherwise
    r_coord[1] = robot.pose.position.y
    r_coord[2] = robot.pose.position.z
    r_zRot = robot.pose_angle.radians # .degrees or .radians
    c_coord[0] = charger.pose.position.x
    c_coord[1] = charger.pose.position.y
    c_coord[2] = charger.pose.position.z
    c_zRot = charger.pose.rotation.angle_z.radians

    # Create target position 
    # dist_charger in mm, distance if front of charger
    c_coord[0] -=  dist_charger*math.cos(c_zRot)
    c_coord[1] -=  dist_charger*math.sin(c_zRot)

    # Direction and distance to target position (in front of charger)
    distance = math.sqrt((c_coord[0]-r_coord[0])**2 + (c_coord[1]-r_coord[1])**2 + (c_coord[2]-r_coord[2])**2)

    if(distance < distance_tol and math.fabs(r_zRot-c_zRot) < angle_tol):
    	return 1
    else: 
    	return 0

def final_adjust(charger: cozmo.objects.Charger,dist_charger=40,speed=40,critical=False):
    # Final adjustement to properly face the charger.
    # The position can be adjusted several times if 
    # the precision is critical, i.e. when climbing
    # back onto the charger.  
    global RobotGlobal
    robot = RobotGlobal
    global PI

    while(True):
        # Calculate positions
	    r_coord = [0,0,0]
	    c_coord = [0,0,0]
	    # Coordonates of robot and charger
	    r_coord[0] = robot.pose.position.x #.x .y .z, .rotation otherwise
	    r_coord[1] = robot.pose.position.y
	    r_coord[2] = robot.pose.position.z
	    r_zRot = robot.pose_angle.radians # .degrees or .radians
	    c_coord[0] = charger.pose.position.x
	    c_coord[1] = charger.pose.position.y
	    c_coord[2] = charger.pose.position.z
	    c_zRot = charger.pose.rotation.angle_z.radians

	    # Create target position 
	    # dist_charger in mm, distance if front of charger
	    c_coord[0] -=  dist_charger*math.cos(c_zRot)
	    c_coord[1] -=  dist_charger*math.sin(c_zRot)

	    # Direction and distance to target position (in front of charger)
	    distance = math.sqrt((c_coord[0]-r_coord[0])**2 + (c_coord[1]-r_coord[1])**2 + (c_coord[2]-r_coord[2])**2)
	    vect = [c_coord[0]-r_coord[0],c_coord[1]-r_coord[1],c_coord[2]-r_coord[2]]
	    # Angle of vector going from robot's origin to target's position
	    theta_t = math.atan2(vect[1],vect[0])

	    debug (2,'CHECK: Adjusting position')
	    # Face the target position
	    angle = clip_angle((theta_t-r_zRot))
	    robot.turn_in_place(radians(angle)).wait_for_completed()
	    # Drive toward the target position
	    robot.drive_straight(distance_mm(distance),speed_mmps(speed)).wait_for_completed()
	    # Face the charger
	    angle = clip_angle((c_zRot-theta_t))
	    robot.turn_in_place(radians(angle)).wait_for_completed()

        # In case the robot does not need to climb onto the charger
	    if not critical:
	        break
	    elif(check_tol(charger,dist_charger)):
	    	debug (2,'CHECK: Robot aligned relativ to the charger.')
	    	break
    return

def restart_procedure(charger: cozmo.objects.Charger):
    global RobotGlobal
    robot = RobotGlobal

    robot.stop_all_motors()
    robot.set_lift_height(height=0.5,max_speed=10,in_parallel=True).wait_for_completed()
    robot.pose.invalidate()
    charger.pose.invalidate()
    debug (1,'ABORT: Driving away')
    #robot.drive_straight(distance_mm(150),speed_mmps(80),in_parallel=False).wait_for_completed()
    robot.drive_wheels(80,80,duration=2)
    turn_around()
    robot.set_lift_height(height=0,max_speed=10,in_parallel=True).wait_for_completed()
    # Restart procedure
    get_on_charger()
    return

def get_on_charger():
    global RobotGlobal
    robot = RobotGlobal
    global pitch_threshold

    robot.set_head_angle(degrees(0),in_parallel=False).wait_for_completed()
    pitch_threshold = math.fabs(robot.pose_pitch.degrees)
    pitch_threshold += 1 # Add 1 degree to threshold
    debug (3,'Pitch threshold: ' + str(pitch_threshold))

    # Drive towards charger
    go_to_charger()

    # Let Cozmo first look for the charger once again. The coordinates
    # tend to be too unprecise if an old coordinate system is kept.
    if robot.world.charger is not None and robot.world.charger.pose.is_comparable(robot.pose):
        robot.world.charger.pose.invalidate()
    charger = find_charger()

    # Adjust position in front of the charger
    final_adjust(charger,critical=True)
    
    # Turn around and start going backward
    turn_around()
    robot.drive_wheel_motors(-120,-120)
    robot.set_lift_height(height=0.5,max_speed=10,in_parallel=True).wait_for_completed()
    robot.set_head_angle(degrees(0),in_parallel=True).wait_for_completed()

    # This section allow to wait for Cozmo to arrive on its charger
    # and detect eventual errors. The whole procedure will be restarted
    # in case something goes wrong.
    timeout = 2 # seconds before timeout  #+++ was: 1
    t = 0
    # Wait for back wheels to climb on charger
    while(True):
        time.sleep(.1)
        t += 0.1
        if(t >= timeout):
            debug (1,'ERROR: robot timed out before climbing on charger.')
            restart_procedure(charger)
            return
        elif(math.fabs(robot.pose_pitch.degrees) >= pitch_threshold):
            debug (3,'CHECK: backwheels on charger.')
            break
    # Wait for front wheels to climb on charger
    timeout = 2
    t = 0
    while(True):
        time.sleep(.1)
        t += 0.1
        if(math.fabs(robot.pose_pitch.degrees) > 20 or t >= timeout):
            # The robot is climbing on charger's wall -> restart
            debug (1,'ERROR: robot climbed on charger\'s wall or timed out.')
            restart_procedure(charger)
            return
        elif(math.fabs(robot.pose_pitch.degrees) < pitch_threshold):
            debug (3,'CHECK: robot on charger, backing up on pins.')
            robot.stop_all_motors()
            break

    # Final backup onto charger's contacts
    robot.set_lift_height(height=0,max_speed=10,in_parallel=True).wait_for_completed()
    robot.backup_onto_charger(max_drive_time=3)
    if(robot.is_on_charger):
    	debug (1,'PROCEDURE SUCCEEDED')
    else: 
    	restart_procedure(charger)
    	return

    # Celebrate success
    robot.drive_off_charger_contacts().wait_for_completed()
    celebrate(robot) # A small celebration where only the head moves
    robot.backup_onto_charger(max_drive_time=3)
    return

########################################################################################################




#----------------------------------------------------------------
def goToCharger(robot: cozmo.robot.Robot):
	
	# +++ todo: go_to_pose is not accurate enough. Therefore, stop in front of the charger looking to it, find the charger, adjust robot position, and then back up. 
	# +++ todo: When on charger, drive off chager contacts. 

	if (robot.is_on_charger):
		robot.drive_off_charger_contacts(robot).wait_for_completed()
		robot.drive_straight(distance_mm(100), speed_mmps(100))
	else:
		get_on_charger()
	
		# robot.go_to_pose(Pose(150, 0, 0, angle_z=degrees(180))).wait_for_completed()
		# Charger = robot.world.wait_for_observed_charger(timeout=2, include_existing=True)
		# if (Charger):
			
			# YPos = robot.world.charger.pose.position.y
			# AngleZ = robot.world.charger.pose.rotation.angle_z.degrees
			# print ("Charger Y:" + str(round(YPos)) + " Angle:" + str(round(AngleZ)) )
			
			# # if (math.fabs(YPos) > 15): 
				# # pass # adjust position
			
			# robot.go_to_pose(Pose(100, YPos, 0, angle_z=degrees(AngleZ-180))).wait_for_completed()
			
			# robot.backup_onto_charger(max_drive_time=5)
			# if (robot.is_on_charger):
				# print ("Success!")
			
		# else: 
			# print ("Sorry, cannot see the charger. Have you moved it away?")


#----------------------------------------------------------------	
def cubeChangeColor (robot: cozmo.robot.Robot, IndexCube, Color):
	cols = [cozmo.lights.off_light] * 4
	
	if (IndexCube == CubeIndexGlobal):							# the selected cube gets a blue light 
		cols[3] = cozmo.lights.blue_light
	
	if (robot.world.light_cubes[IndexCube].object_id != None):
		for i in range(robot.world.light_cubes[IndexCube].object_id): # cube 1 gets 1 light, cube 2 gets 2 lights,  cube 3 gets 3 lights
			if (Color == "green"):
				cols[i] = cozmo.lights.green_light
			if (Color == "red"):
				cols[i] = cozmo.lights.red_light
			
		robot.world.light_cubes[IndexCube].set_light_corners(*cols) 
	
#-------------------------------------------------------------------------
def animPlay (WhatToPlay):
	global AnimNames
	global CAnims
	global AnimLast
	global RobotGlobal
	
	debug (4,"searching for " + WhatToPlay)
	AnimLast = WhatToPlay

	
	# find animation which matches the chosen name 
	Index = 0
	IndexToPlay = 0
	for Anim in (RobotGlobal.anim_triggers):
		# print (Anim.name)
		if (Anim.name == WhatToPlay):
			IndexToPlay = Index
		Index = Index + 1
	
	debug (3,"playing " + RobotGlobal.anim_triggers[IndexToPlay].name)
	RobotGlobal.play_anim_trigger(RobotGlobal.anim_triggers[IndexToPlay])
	
	
#-------------------------------------------------------------------------
def printFaceData (Face):
	global LFaceData
	
	debug (3,"ID:" + str(Face.face_id) + " name = " + Face.name)
	LFaceData.config (text = "ID:" + str(Face.face_id) + " name = " + Face.name)
	
	# if (Face.is_visible):						# +++ is always true, so it doesn't make sense 
		# LFaceData.config (fg="green")
	# else:
		# LFaceData.config (fg="red")

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
	
	# debug (5,"Got canvas click" + str(coords.x) + str(coords.y))
	
	# debug (5, str(RobotGlobal.pose.position.x),  + str(RobotGlobal.pose.position.x))
	
	MapCanvas.create_line (coords.x - 4, coords.y, coords.x + 4, coords.y)
	MapCanvas.create_line (coords.x, coords.y - 4, coords.x, coords.y + 4)
	
	X = canvas2worldX (coords.x)
	Y = canvas2worldY (coords.y)
	
	DeltaX = X - RobotGlobal.pose.position.x
	DeltaY = Y - RobotGlobal.pose.position.y
	
		
	Angle = angle360 (DeltaX, DeltaY)
	
	debug (5, str(DeltaX) + str(DeltaY) + str(Angle))
	
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
		
		MapCanvas.bind ("<Key>", keyPressed)
		
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
		RobotCircle = MapCanvas.create_arc ( 
			world2canvasX(0) - 3*RobotCircleRadius, 
			world2canvasY(0) - 3*RobotCircleRadius, 
			world2canvasX(0) + 3*RobotCircleRadius, 
			world2canvasY(0) + 3*RobotCircleRadius,
			start = 330,
			extent = 60,
			fill = "black"
			)
		# MapCanvas.itemconfig(RobotCircle, fill="black")

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
		MapCanvas.tag_bind (CubeSquares[0], '<Double-1>', lambda: buttonCubeX(robot, 1))   #buttonCubeX(parent, robot: cozmo.robot.Robot, IndexCube)
		MapCanvas.tag_bind (CubeSquares[1], '<Double-1>', lambda: buttonCubeX(robot, 2))
		MapCanvas.tag_bind (CubeSquares[2], '<Double-1>', lambda: buttonCubeX(robot, 3))
		
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
				world2canvasX(MapRobotX) - 3*RobotCircleRadius, 
				world2canvasY(MapRobotY) - 3*RobotCircleRadius, 
				world2canvasX(MapRobotX) + 3*RobotCircleRadius, 
				world2canvasY(MapRobotY) + 3*RobotCircleRadius
				)
			MapCanvas.itemconfig (RobotCircle, start = robot.pose.rotation.angle_z.degrees - 30, extent = 60)
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
def drawRingAnimation (PosX, PosY, MaxRad, Rad=0, Count=0, Ring=None):
	global MapCanvas
	
	debug (5,"PosX:" + str(PosX) + " PosY:" + str(PosY) + " MaxRad:" + str(MaxRad) + " Rad:" + str(Rad) + " Count:" + str(Count) + " Ring:" + str(Ring))
	
	if (Ring==None):	# first call 
		Ring = MapCanvas.create_oval (PosX-1,PosY-1,PosX+1,PosY+1)
	else:				# subsequent calls
		MapCanvas.coords (Ring, PosX-Rad, PosY-Rad,PosX+Rad,PosY+Rad)
	
	Rad=MaxRad/10*Count
	
	if (Count < 10):
		MapCanvas.after (20, lambda: drawRingAnimation (PosX, PosY, MaxRad, Rad, Count+1, Ring)) 
	else:
		Ring.destroy() # here I get an error message "AttributeError: 'int' object has no attribute 'destroy'"

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
		debug (5,"Angle: " + str(Angle))
		# Angle += 90
		# if (Angle > 360):
			# Angle -= 360

		Wall = RobotGlobal.world.create_custom_fixed_object(
					Pose(canvas2worldX(LineCoords[0]) + DeltaX/2, canvas2worldY(LineCoords[1]) + DeltaY/2, 0, angle_z=degrees(Angle)),
					math.sqrt(DeltaX ** 2 + DeltaY ** 2), 10, 100, 
					relative_to_robot=False)			

		if Wall:
			debug (3,"Wall created successfully")
		else:
			debug (1,"Could not create wall")

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
	global LMotionWindowStatusBar
	global LStatusBar

	# ---Cubes---
	try:
		VisibleCube = robot.world.wait_for_observed_light_cube(timeout=0.1)
		# actually we don't need VisibleCube, and for now it doesn't matter if cubes are found. 
		# We call this function for its side effect, i.e. filling in the data into robot.world.light_cubes[]
		debug (7,"Found cube: " + str(VisibleCube.object_id) )
		pass
	except asyncio.TimeoutError:
		debug (6,"Didn't find a cube") 
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
	
	# Cube Window Status bar
	if (robot.world.light_cubes[CubeIndexGlobal].object_id != None):
		ID     = robot.world.light_cubes[CubeIndexGlobal].object_id
		XPos   = round(robot.world.light_cubes[CubeIndexGlobal].pose.position.x)
		YPos   = round(robot.world.light_cubes[CubeIndexGlobal].pose.position.y)
		ZPos   = round(robot.world.light_cubes[CubeIndexGlobal].pose.position.z)
		AngleZ = round(robot.world.light_cubes[CubeIndexGlobal].pose.rotation.angle_z.degrees)
		LCubeWindowStatusBar.config (text = "Cube" + str(ID) + ": X=" + str(XPos) + ", Y=" + str(YPos) + ", Z=" + str(ZPos) + ", " + str(AngleZ) + "° Batt:" + robot.world.light_cubes[CubeIndexGlobal].battery_str)
	
	# Motion Window Status bar
	XPos   = round(robot.pose.position.x)
	YPos   = round(robot.pose.position.y)
	ZPos   = round(robot.pose.position.z)
	AngleZ = round(robot.pose.rotation.angle_z.degrees)
	LMotionWindowStatusBar.config (text = "X=" + str(XPos) + ", Y=" + str(YPos) + ", Z=" + str(ZPos) + ", " + str(AngleZ) + "°")
	
	# main window status bar 
	# todo: do it less frequently, we do not need it every second 
	if (robot.is_charging):
		ChargerText = ", Charging"
	else:
		ChargerText = ""
		
	if (robot.is_cliff_detected):
		CliffText = ", Cliff!"
	else:
		 CliffText= ""
		
	
	if (robot.is_picked_up):
		PickText = ", picked up"
	else:
		 PickText= ""
		
		
	LStatusBar.config (text = "Battery " +  str(round(robot.battery_voltage, 1)) + " V = " + str (round ((robot.battery_voltage - 3.7) / (4.7 - 3.7) * 100)) + "%"  + ChargerText + CliffText + PickText)
	
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

#--------------------------------------------------------
def keyPressed (event):
	global BForward
	global BBack
	global BLeft
	global BRight
	global BCube1
	global BCube2
	global BCube3

	# if EDist != EDist.focus_get():
	
	if event.keysym == "Up":
		BForward.invoke()
	elif event.keysym == "Down":
		BBack.invoke()
	elif event.keysym == "Left":
		BLeft.invoke()
	elif event.keysym == "Right":
		BRight.invoke()
	elif event.keysym == "F1":
		BCube1.invoke()
	elif event.keysym == "F2":
		BCube2.invoke()
	elif event.keysym == "F3":
		BCube3.invoke()
	else:
		debug (5,"Key pressed " + event.keysym)

#--------------------------------------------------------------------------------------
def on_cube_tapped(evt, **kw): 
	global MapActive
	
	debug (5,"tapped! " + str(evt))
	debug (3,"object_id =     " + str(evt.obj.object_id))
	debug (3,"tap_count =     " + str(evt.tap_count))
	debug (3,"tap_duration =  " + str(evt.tap_duration))
	debug (3,"tap_intensity = " + str(evt.tap_intensity))
	
	# find button which matches the object_id
	ButtonIndex = -1
	for Count in range(1,4):
		if (RobotGlobal.world.light_cubes[Count].object_id == evt.obj.object_id):
			ButtonIndex = Count
	debug (5,"ButtonIndex: " + str (ButtonIndex))
	
	if (ButtonIndex != -1):
		buttonCubeX(RobotGlobal, ButtonIndex)
	
	# if (MapActive == True):
		# PosX = world2canvasX (evt.obj.pose.position.x)
		# PosY = world2canvasY (evt.obj.pose.position.y)
		
		# drawRingAnimation (PosX, PosY, evt.tap_intensity / 4) # does not yet work

#------------------------------------------------------------------------------------
def infrared (robot: cozmo.robot.Robot, Button):
	# print (Button.cget ('relief'))
	if (Button.cget ('relief') == RAISED):
		robot.set_head_light(True)
		Button.config (relief=SUNKEN)
	else:
		robot.set_head_light(False)
		Button.config (relief=RAISED)
		
##------------------------------------------------------------------------------------
def colorImage (robot: cozmo.robot.Robot, Button):
	# print (Button.cget ('relief'))
	if (Button.cget ('relief') == RAISED):
		robot.camera.color_image_enabled=True
		Button.config (relief=SUNKEN)
	else:
		robot.camera.color_image_enabled=False
		Button.config (relief=RAISED)
		
#----------------robotMainProgram----------------------------------------------------
def robotMainProgram(robot: cozmo.robot.Robot):

	global top 		
	global LDist 		
	global EDist 		
	global ESpeed
	global LAng 		
	global EAng 		
	global BMethodDriveStraight
	global BMethodGoToPose
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
	global LMotionWindowStatusBar
	global AnimNames
	global CAnims
	global AnimLast
	global BPlayFree
	global CubesConnected
	global BCubeDisConnect
	
	global args
	global RobotGlobal
	
	RobotGlobal = robot

	robot.enable_stop_on_cliff(True)
	
	# set up the GUI
	top = tkinter.Tk()
	top.geometry("900x700")
	top.title("Cozmo Commander")
	# ToolTp = Balloon()	# doesn't work 
	
	# frames
	motionWindow = Frame(top, bd=2, width=300, height=550, relief=GROOVE)
	motionWindow.grid_propagate(0)			# frame at fixed size instead of shrink to content
	motionWindow.place (x=0, y=50)

	cubeWindow = Frame(top, bd=2, width=300, height=550, relief=GROOVE)
	cubeWindow.grid_propagate(0)			# frame at fixed size instead of shrink to content
	cubeWindow.place (x=300, y=50)

	FaceWindow = Frame(top, bd=2, width=300, height=550, relief=GROOVE)
	FaceWindow.grid_propagate(0)			# frame at fixed size instead of shrink to content
	FaceWindow.place (x=600, y=50)

	# --- motion controls ---
	Row=0
	LMotion = Label (motionWindow, text="motion", bd=2, relief=GROOVE)
	LMotion.grid (row=Row, column=0)
	# LMotion.place(x=0, y=0)
	
	Row+=1
	BForward = Button(motionWindow, text = "Forward", command = lambda: moveStraight(robot, float(EDist.get()), float(ESpeed.get())))	
	BForward.grid(row=Row, column=2)
	# ToolTp.bind_widget(BForward, balloonmsg="Move Forward by the distance in mm given above")	# doesn't work 

	Row+=1
	BRight = Button(motionWindow, text = "Right", command = lambda: moveTurn(robot, float(EAng.get())*(-1.0)))
	BRight.grid(row=Row, column=3)

	BLeft = Button(motionWindow, text = "Left", command = lambda: moveTurn(robot, float(EAng.get())))
	BLeft.grid(row=Row, column=1)

	Row+=1
	BBack = Button(motionWindow, text = "Backward", command = lambda: moveStraight(robot, float(EDist.get())*(-1.0), float(ESpeed.get())))
	BBack.grid(row=Row, column=2)

	Row+=1
	LEmpty01 = Label (motionWindow, text="").grid (row=Row, columnspan=3)
	
	Row+=1
	LMethod = Label (motionWindow, text="Method")
	LMethod.grid(row=Row)
	BMethodDriveStraight = Button(motionWindow, text = "Drive Straight", relief=SUNKEN, command = methodDriveStraight)
	BMethodDriveStraight.grid(row=Row, column=2, columnspan=2)
	BMethodGoToPose = Button(motionWindow, text = "Go to Pose", command = methodGoToPose)
	BMethodGoToPose.grid(row=Row, column=4, columnspan=2)
	
	Row+=1
	LEmpty02 = Label (motionWindow, text="").grid (row=Row, columnspan=3)

	Row+=1
	LDist = Label (motionWindow, width=6, text="Distance")
	LDist.grid(row=Row, sticky=W)
	# ToolTp.bind_widget(LDist, balloonmsg="Distance in mm to move when \"Forward\" or \"Backward\" is pressed")	# doesn't work 
	EDist = Entry (motionWindow, bd=2, width=7)
	EDist.grid(row=Row, column=2)
	EDist.insert (0, "100")	# start value
	EDist.bind ("<Key>", None)
	LDist1 = Label (motionWindow, text="mm")
	LDist1.grid(row=Row, column=3, sticky=W)

	ESpeed = Entry (motionWindow, bd=2, width=7)
	ESpeed.grid(row=Row, column=4)
	ESpeed.insert (0, "50")	# start value
	LSpeed = Label (motionWindow, text="mm/s")
	LSpeed.grid(row=Row, column=5, sticky=W)
	
	Row+=1
	LAng = Label (motionWindow, width=6, text="Angle")
	LAng.grid(row=Row, sticky=W)
	# ToolTp.bind_widget(LAng, balloonmsg="Angle in ° to turn when \"Left\" or \"Right\" is pressed")	# doesn't work 
	EAng = Entry (motionWindow, bd=2, width=7)
	EAng.grid(row=Row, column=2)
	EAng.insert (0, "45")	# start value
	LAng1 = Label (motionWindow, text="deg")
	LAng1.grid(row=Row, column=3, sticky=W)

	Row+=1
	LEmpty03 = Label (motionWindow, text="").grid (row=Row, columnspan=3)

	Row+=1
	LEmpty04 = Label (motionWindow, text="").grid (row=Row, columnspan=3)

	Row+=1
	ScHead = Scale (motionWindow, orient = VERTICAL, from_ = 44, to = -25, resolution=1, command = scaleHead)
	ScHead.grid(row=Row+1, column=1)
	ScHead.set(0)
	BHead = Button(motionWindow, text = "Head", command = lambda: scaleHead(ScHead.get()))
	BHead.grid(row=Row, column=1)
	BHead.invoke() 	# set head to horizontal at startup
	ScLift = Scale (motionWindow, orient = VERTICAL, from_ = 1.0, to = 0.0, resolution=0.1, command = scaleLift)
	ScLift.grid(row=Row+1, column=2)
	ScLift.set(0)
	BLift = Button(motionWindow, text = "Lift", command = lambda: scaleLift(ScLift.get()))
	BLift.grid(row=Row, column=2)
	BLift.invoke() 	# set lift down at startup
	
	Row+=2
	LEmpty05 = Label (motionWindow, text="").grid (row=Row, columnspan=3)

	Row+=1
	BCanvas = Button (motionWindow, text = "map", command = lambda: createMap(robot)) 
	BCanvas.grid(row=Row, column=1)
	BStop = Button (motionWindow, text = "stop", command = lambda: stop(robot)) 
	BStop.grid(row=Row, column=2)
	BPlayFree = Button (motionWindow, text = "play", relief = RAISED, bd=2, command = lambda: playFree(robot))
	BPlayFree.grid(row=Row, column=3)

	Row+=1
	LEmpty06 = Label (motionWindow, text="").grid (row=Row, columnspan=3)

	Row+=1
	BCharger = Button (motionWindow, text = "Go to/from Charger", command = lambda: goToCharger(robot))
	BCharger.grid(row=Row, column=1, columnspan=2)
	
	
	LMotionWindowStatusBar = Label (motionWindow, text="Status...", bd=2, relief=FLAT, anchor=W)
	LMotionWindowStatusBar.place (x=0, y=525)


	# --- cube window ---
	Row=0
	LCube = Label (cubeWindow, text="cubes", bd=2, relief=GROOVE)
	LCube.grid (row=Row, column=0)
	
	Row+=1
	LEmpty10 = Label (cubeWindow, text="").grid (row=Row, columnspan=3)
	
	Row+=1
	BCube1 = Button(cubeWindow, text = "Cube" + str(robot.world.light_cubes[1].object_id), relief=SUNKEN, bd=5, command = lambda: buttonCubeX(robot, 1))
	BCube1.grid(row=Row, column=1)
	BCube2 = Button(cubeWindow, text = "Cube" + str(robot.world.light_cubes[2].object_id), relief=RAISED, bd=5, command = lambda: buttonCubeX(robot, 2))
	BCube2.grid(row=Row, column=2)
	BCube3 = Button(cubeWindow, text = "Cube" + str(robot.world.light_cubes[3].object_id), relief=RAISED, bd=5, command = lambda: buttonCubeX(robot, 3))
	BCube3.grid(row=Row, column=3)

	Row+=1
	LEmpty11 = Label (cubeWindow, text="").grid (row=Row, columnspan=3)
	
	Row+=1
	BCubeWindowGoto = Button (cubeWindow, text="go to", command = lambda: buttonCubeWindowGoto(robot, float(ECubeWindowGotoDistance.get())))
	BCubeWindowGoto.grid(row=Row, column=1, sticky=W)
	ECubeWindowGotoDistance = Entry (cubeWindow, width=7)
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
	Row+=1
	BCubeWindowRoll = Button (cubeWindow, text="wheelie", command = lambda: buttonCubeWindowWheelie(robot))
	BCubeWindowRoll.grid(row=Row, column=1, sticky=W)
	Row+=1
	BCubeDisConnect = Button (cubeWindow, text = "disconnect from all cubes", width=20, command = lambda: buttonCubeWindowDisConnect(robot)) 
	BCubeDisConnect.grid(row=Row, column=1, columnspan=3, sticky=W)
	
	LCubeWindowStatusBar = Label (cubeWindow, text="Status...", bd=2, relief=FLAT, anchor=W)
	LCubeWindowStatusBar.place (x=0, y=525)
	
	# --- face window ---
	Row = 0
	LFaceWindow = Label (FaceWindow, text="faces", bd=2, relief=GROOVE)
	LFaceWindow.grid (row=Row, column=0)
	
	Row+=1
	LEmpty20 = Label (FaceWindow, text="").grid (row=Row, columnspan=3)
	
	Row+=1
	LFaceData = Label (FaceWindow, text="Status...")
	LFaceData.place (x=0, y=525)

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
	CAnims.grid(row=1, column=1)
	BAnims = Button (FAnims, text="repeat", command=lambda: animPlay(AnimLast))
	BAnims.grid (row=1, column=2)
	
	LEmpty40 = Label (FAnims, text="")
	LEmpty40.grid(row=1, column=4)
	BInfrared = Button (FAnims, text="infrared", command = lambda: infrared (robot, BInfrared)) 
	BInfrared.grid(row=1, column=5)
	
	LEmpty50 = Label (FAnims, text="")
	LEmpty50.grid(row=1, column=6)
	BColorImage = Button (FAnims, text="color", command = lambda: colorImage (robot, BColorImage)) 
	BColorImage.grid(row=1, column=7)
	
	FAnims.pack (side=BOTTOM)
		
	# FCamera = Frame(width=900)
	# FCamera.pack (side=BOTTOM)
		
	# --- event handlers etc. 
		
	top.bind ("<Key>", keyPressed)	
	
	if (args.tap != 0):
		robot.add_event_handler(cozmo.objects.EvtObjectTapped, on_cube_tapped) 	
		robot.world.enable_block_tap_filter(True)
	
	if (args.dfac != 0):
		buttonCubeWindowDisConnect(robot)
		BCubeDisConnect.config (state = DISABLED)
		
	if (StartMap):
		BCanvas.invoke()
	
	# start background process(es) 
	top.after (1000, lambda: tick(top, robot))

	# start GUI
	top.mainloop()
	
#---------------------------------start-working-------------------------
# parse arguments 
parser = argparse.ArgumentParser(description="Simple graphic interface for Cozmo")
parser.add_argument("--viewer", type=str, default=0, help="0 = no viewer (default), 1 = Camera, 2 = 3D, 4 = 2D map, combinations are possible like 5=Camera+2Dmap")
parser.add_argument("--dfac", type=int, default=0, help="1.. disconnect from all cubes. Save cube batteries.")
parser.add_argument("--docc", type=int, default=1, help="1 (default) ...drive off charger contacts, 0 ... stay on charger contacts")
parser.add_argument("--tap",  type=int, default=1, help="1 (default) ...enable tapping cubes, 0 ...disable tapping cubes")
parser.add_argument("--debug", type=int, default=0, help="enable debug messages on console. 0 (default) ... no debug messages, greater number = more messages")
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
	StartMap = True
else:
	StartMap = False


if (args.docc == 0):
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
DriveMethod = "DriveStraight"

#### global variables for Luc's charger code
# Pitch value when head is horizonal, calculated later.
pitch_threshold = 0
PI = 3.14159265359


		
# global variables for the GUI
# when we refer to a control from outside robotMainProgram, like changing the color of a button, 
# we need to have it global. 
# We cannot yet set them up because we need "robot" to be passed as a parameter, and this will be known in robotMainProgram. 
# Furthermore, they must reside in robotMainProgram. Otherwise the viewers cannot be used. 
# For now, they are integers an will be assigned the appropriate type later. 
top 					= 0
LDist 					= 0
EDist 					= 0
ESpeed					= 0
LAng 					= 0
EAng 					= 0
BMethodDriveStraight	= 0
BMethodGoToPose			= 0
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
LMotionWindowStatusBar	= 0
LStatusBar				= 0
CAnims					= 0
BPlayFree				= 0
CubesConnected			= True
BCubeDisConnect			= 0


# start main program
#cozmo.robot.Robot.drive_off_charger_on_connect = False  # Cozmo can stay on charger for now 
cozmo.run_program(robotMainProgram, use_3d_viewer=Use3D, use_viewer=UseCam)
