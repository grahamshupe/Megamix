#!/usr/bin/python3

import sys
import time
import numpy as np
from scipy.spatial.transform import Rotation as R
from interpreter.interpreter import InterpreterHelper


IP = "192.168.56.101"

# Constant tool parameters:
GRAB_Z = -0.048
HOVER_Z = -0.032
TOOL_ROTATION = [3.137, -0.217, 0.036]
VACUUM_PORT = 0

# Board edges:
POS_X = -0.259
NEG_X = -0.520
POS_Y = 0.152
NEG_Y = -0.101

IDLE_POSE = [-0.390, 0.0, 0.08] + TOOL_ROTATION  # Arm will sit directly above the board



# With a checker piece, the Z coordinate is -0.0466m. Don't set Z less than this
# The farthest board square is at coordinate x=-0.410,y=-0.388,z=-0.0466,rx=2.638,ry=1.711,rz=-0.061
# Distance between each square is about 37mm

# -- PRIVATE METHODS: --

"""Returns a string representing a URscript pose array"""
def _genPoseFromCoords(x, y, z):
    pose = [x, y, z] + TOOL_ROTATION
    return "p" + str(pose)

"""Returns a string representing a URscript pose array
pose should be an array of 6 floats"""
def _genPose(pose):
    return "p" + str(pose)

"""Move to the specified pose.
pose should be a URscript pose array as a string
See the URscript manual for descriptions of a, v, t, and r.
blocking will block the process until the move is complete"""
def _moveToPose(pose, a=0.5, v=0.5, t=0, r=0, blocking=True):
    interpreter.execute_command(f"movej({pose},a={a},v={v},t={t},r={r})")
    #print("move started at " + str(time.time()))
    if blocking:
        while interpreter.get_unexecuted_count() > 0:
            time.sleep(0.1)
    #print("move finished at " + str(time.time()))

"""Set digital out either on or off"""
def _setIO(id, on):
    interpreter.execute_command(f"set_standard_digital_out({id},{on})")

# """Get the base frame coordinates of the given square"""
# def _getSquareCoordinates(x, y):
#     square_x = NEG_X + (x * ((NEG_X - POS_X) / 7))
#     square_y = NEG_Y + (y * ((NEG_Y - POS_Y) / 7))
#     return (square_x, square_y)


# -- PUBLIC METHODS: --

def movePiece(x1 = 0, y1 = 0, x2 = 0, y2 = 0, side = 0):
    """Moves a piece from board square (x1,y1) to (x2,y2).
    If side is not 0, the piece is placed off of the board:
    if side is <0, the piece is placed on the NEG_Y side,
    if side is >0, the piece is placed on the POS_Y side.

    x and y should be in terms of the board squares and be between 0-7.
    Square (0, 0) is the square at (NEG_X, NEG_Y)"""
    # Translate coordinates:
    start_x = NEG_X + abs(x1 * (NEG_X - POS_X) / 7)
    start_y = NEG_Y + abs(y1 * (NEG_Y - POS_Y) / 7)
    if side < 0:
        end_x = POS_X - abs(x2 * ((NEG_X - POS_X) / 7))
        end_y = NEG_Y - abs((NEG_X - POS_X) / 7) * 2
    elif side > 0:
        end_x = POS_X - abs(x2 * ((NEG_X - POS_X) / 7))
        end_y = POS_Y + abs((NEG_X - POS_X) / 7) * 2
    else:
        end_x = NEG_X + abs(x2 * ((NEG_X - POS_X) / 7))
        end_y = NEG_Y + abs(y2 * ((NEG_Y - POS_Y) / 7))

    # Pick up piece:
    _moveToPose(_genPoseFromCoords(start_x, start_y, HOVER_Z))
    _moveToPose(_genPoseFromCoords(start_x, start_y, GRAB_Z))
    _setIO(VACUUM_PORT, True)
    time.sleep(0.4)
    _moveToPose(_genPoseFromCoords(start_x, start_y, HOVER_Z))

    # Drop piece:
    _moveToPose(_genPoseFromCoords(end_x, end_y, HOVER_Z))
    _moveToPose(_genPoseFromCoords(end_x, end_y, GRAB_Z))
    _setIO(VACUUM_PORT, False)
    time.sleep(0.4)
    _moveToPose(_genPoseFromCoords(end_x, end_y, HOVER_Z))

    _moveToPose(_genPose(IDLE_POSE))



if __name__ == "__main__":
    print("Connecting....")
    interpreter = InterpreterHelper(IP)
    interpreter.connect()
    print("Connected!")
    time.sleep(1.)

    input("Make a move...")
    # I go to 3, 4
    movePiece(5, 2, 4, 3)
    input("Make a move...")
    # I go to 4, 3 (jump)
    movePiece(6, 3, 4, 1)
    movePiece(5, 2, side=-1)




    interpreter.end_interpreter()
