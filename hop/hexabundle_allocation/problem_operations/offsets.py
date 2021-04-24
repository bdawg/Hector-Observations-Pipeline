from ..general_operations.trigonometry import rotational_matrix,convert_degrees_to_radians, convert_radians_to_degrees
from ..hector.constants import robot_center_x,robot_center_y
from math import atan,sin,cos
import numpy as np
import pandas as pd
import csv
import string
import sys
import re

# Adjusting offset to move circular magnet closer to OR far from rectangular magnet
def hexaPositionOffset(all_magnets,offsetFile):

    df = pd.read_excel(offsetFile,usecols=['Name','P','Q'])
    df.dropna(subset = ['Q'], inplace=True)
    print(df)

    offset_distance = 0.0  # to be derived from excel file

    for i in all_magnets:

        if i.__class__.__name__ == 'rectangular_magnet' and i.index == 5:

            # getting the orientation of rectangular magnet with respect to North(up)
            ang = i.orientation

            # check to adjust angle within 0 to -360 range
            # if ang < 360:
            #     ang = ang + 360

            print('orientation_rectangular = '+str(ang))
            azAngs = convert_radians_to_degrees(i.azAngs)
            print('azAngs_rectangular = '+str(azAngs))
            ang_azAngs = convert_radians_to_degrees(i.rectangular_magnet_input_orientation)
            print('ang_azAngs_rectangular = ' + str(ang_azAngs))

            rectangular_centre = i.center
            print(rectangular_centre)


    for i in all_magnets:

        if i.__class__.__name__ == 'circular_magnet' and i.index == 5:

            # adjusting the angle to ensure movement is about the rectangular magnet's centre axis
            angle_adjusted = 450+ang

            # check to adjust angle within 0 to 360 range
            if angle_adjusted > 360:
                angle_adjusted = angle_adjusted - 360

            rotation_matrix_circle = rotational_matrix(convert_degrees_to_radians(angle_adjusted))

            # subtracting offset distance moves circular magnet upwards toward plate edge
            # (P-perpendicular movement to rectangular magnet)
            i.center = (i.center[0] - rotation_matrix_circle[1][0] * offset_distance, \
                                      i.center[1] - rotation_matrix_circle[1][1] * offset_distance)

            # subtracting offset distance moves circular magnet closer to rectangular
            # (Q-parallel movement to rectangular magnet)
            i.center = (i.center[0] - rotation_matrix_circle[0][0] * offset_distance, \
                                      i.center[1] - rotation_matrix_circle[0][1] * offset_distance)
            i.offset = offset_distance

            print('orientation_circular = ' + str(i.orientation))
            azAngs = convert_radians_to_degrees(i.azAngs)
            # print('azAngs_circular=' + str(azAngs))

            circular_centre = i.center
            print(circular_centre)

    angle = 90 + convert_radians_to_degrees(atan(abs(rectangular_centre[1]-circular_centre[1])/abs(rectangular_centre[0]-circular_centre[0])))
    print(angle)

    return all_magnets

## Created as a standalone function for the robot, so should not be required to implement in this pipeline
# thermal expansion related offset which will move the magnet pair as a whole based on certain coefficients
def magnetPair_radialPositionOffset(plate_file):

    ## read off a certain table from csv file or derived off some equations and calculations to identify the magnet pair
    ## to be adjusted with the determined offset values, VARIABLE 'offset_distance' used for testing function's usability

    offset_radialDistance = 20  # to be derived

    # T_observed > T_configured then radial inward movement by magnet
    # T_observed < T_configured then radial outward movement by magnet
    # ΔT = T_configured - T_observed
    # coeff. of thermal expansion, α=  1.2 × 10−6 K^(−1),[Common grades of Invar, measured between 20 °C and 100 °C]
    # L = L_initial x ( 1 + α ⋅ ΔT)

    # store magnet pair index and offset distance accordingly, to be derived
    magnetPair_offset = [(1,2)]
    # magnetPair_offset = [(14,-30),(4,-30),(12,-30),(9,-30)] # +ve value makes radial outward movement, and -ve value for radial inward movement

    csv_input = pd.read_csv(plate_file,skipinitialspace=True)
    # print(pd.read_csv(plate_file, index_col=0, nrows=0).columns.tolist())
    csv_input['magnetPair_offset'] = '0.000'
    csv_input.to_csv(plate_file, index=False, sep=' ', quoting=csv.QUOTE_NONE,escapechar=' ')
    # csv_input = pd.read_csv(plate_file, header=0)
    # csv_input['Berries'] = '0.000'
    # csv_input.to_csv(plate_file, index=False, sep=' ', quoting=csv.QUOTE_NONE, escapechar=' ')

    csv_read = pd.read_csv(plate_file)
    # print(csv_read)

    # r = csv.reader(open(plate_file))
    # row0 = next(r)
    # row0.append('berry')
    #
    # for item in r:
    #     item.append(item[0])
    #     print(item)

    return plate_file, magnetPair_offset

## Created as a standalone function for the robot, so should not be required to implement in this pipeline
# radial Position offset being adjusted in the extract_data.py file before all_magnets are being produced
def radialPositionOffset(list_of_probes,magnetPair_offset):

    # iterating through each magnet in the offset list and the probes list
    for item in magnetPair_offset:
        for each_probe in list_of_probes:

            # looking for match of items in offset and probes list
            if item[0] == each_probe.index:

                ### TEST PRINT
                print(each_probe.circular_magnet_center)

                # calculating the angle of the magnet with respect to x-axis
                theta = atan(each_probe.circular_magnet_center[1] / each_probe.circular_magnet_center[0])

                # calculating sine and cosine angle adjustment to offset distance for the radial movement
                # x values in positive range and -ve range move in opposite radial directions, so this step ensure same direction movement
                if each_probe.circular_magnet_center[0] >= 0:
                    each_probe.circular_magnet_center = (each_probe.circular_magnet_center[0] + (cos(theta) * item[1]), \
                                                         each_probe.circular_magnet_center[1] + (sin(theta) * item[1]))
                else:
                    each_probe.circular_magnet_center = (each_probe.circular_magnet_center[0] - (cos(theta) * item[1]), \
                                                         each_probe.circular_magnet_center[1] - (sin(theta) * item[1]))

                ### TEST PRINT
                print('RADIAL OFFSET CHANGEEE')
                print(each_probe.circular_magnet_center)

    return list_of_probes

def magnetOffsets_asColumns_toFile():

    #


    return