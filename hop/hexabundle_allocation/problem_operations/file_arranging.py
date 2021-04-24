import matplotlib.pyplot as plt
import pandas as pd
pd.options.mode.chained_assignment = None  # disabled warning about writes making it back to the original frame
import numpy as np
import csv
import re
import time

# arranging the guides files in consistent format with hexas files
def arrange_guidesFile(fileNameHexa,fileNameGuides, guide_outputFile):

    # getting count of lines to skip at top of file, which contain other information
    with open(fileNameGuides) as f:
        line = f.readline()
        skipline_count = 0
        while line.startswith('#'):
            line = f.readline()
            skipline_count += 1

    df = pd.read_csv(fileNameGuides, sep = ' ', skiprows=skipline_count)
    df['probe'] = 0
    print(df)

    # df = pd.read_csv(fileNameGuides,sep=' ')
    # df.columns = ['probe', 'x', 'y', 'rads', 'angs', 'azAngs', 'angs_azAng']
    with open(fileNameHexa) as f:
        line = f.readline()
        skipline_count = 0
        while line.startswith('#'):
            line = f.readline()
            skipline_count += 1

    df1 = pd.read_csv(fileNameHexa,sep=' ', skiprows=skipline_count)
    print(df1)

    mask = df1['probe'] < 22
    df_new = df1[mask]

    # reading the index value of last hex probe to get count of hexa probes
    hexaCount = int(df_new['probe'][df_new.index[-1]]) + 1

    # probe numbering for the guid probes, counting onward from hexa count
    for i in range(len(df['probe'])):
        df['probe'][i] = int(hexaCount + i)

    probe_number = list(df['probe'])
    circular_magnet_center_x = list(df['x'])
    circular_magnet_center_y = list(df['y'])
    rads = list(df['grads'])
    angs = list(df['gangs'])
    azAngs = list(df['gazAngs'])
    rectangle_magnet_input_orientation = list(df['gangs_gazAng'])

    IDs = galaxyORstar = Re = mu_1re = Mstar = [float('NaN')] * len(probe_number)

    guideFileList = [probe_number, \
    IDs, \
    circular_magnet_center_x, \
    circular_magnet_center_y, \
    rads, \
    angs, \
    azAngs, \
    rectangle_magnet_input_orientation, \
    galaxyORstar, \
    Re, \
    mu_1re, \
    Mstar ]

    df.to_csv(guide_outputFile, index=False, sep=' ')

    return df, guideFileList


# merging the hexas and guides file to create one plate file with all the magnets
def merge_hexaAndGuides(fileNameHexa, df_guideFile, plate_file):

    with open(fileNameHexa) as f:
        line = f.readline()
        skipline_count = 0
        while line.startswith('#'):
            line = f.readline()
            skipline_count += 1

    df1 = pd.read_csv(fileNameHexa,sep=' ', skiprows=skipline_count)

    mask = df1['probe'] < 22
    df_new = df1[mask]

    df_plateFile = pd.concat([df_new, df_guideFile], sort=False)

    df_plateFile.fillna('NA', inplace=True)

    df_plateFile.to_csv(plate_file, index=False, sep=' ', quoting=csv.QUOTE_NONE, escapechar=' ')


# creating the robotFile array for
def create_robotFileArray(positioning_array,robotFile,newrow,fully_blocked_magnets_dictionary):

    # guide probes do not have ID, so they are allocated a large negative integer
    positioning_array[:, 8] = [i if i != 'nan' else -999999 for i in positioning_array[:, 8]]
    for i in range(len(positioning_array[:, 8])):
        positioning_array[:, 8][i] = round(float(positioning_array[:, 8][i]))

    # an array for the robot file is created which is sorted based on the placement order numbering
    robotFilearray = sorted(positioning_array, key=lambda x: x[6])

    # the title row is inserted at the first row of the array
    robotFilearray = np.insert(robotFilearray, 0, np.array(newrow), 0)

    # add the reposition column to robot file by using the fully blocked magnets dictionary
    robotFilearray = add_repositionCol_to_robotFile(positioning_array,robotFilearray,fully_blocked_magnets_dictionary)

    # TEST PRINT
    print(robotFilearray)

    # write the robot file array into the CSV file for the robot
    with open(robotFile, 'w+') as robotFile:
        writer = csv.writer(robotFile, delimiter=' ')
        writer.writerows(robotFilearray)

    return positioning_array,robotFilearray

def add_repositionCol_to_robotFile(positioning_array,robotFilearray,fully_blocked_magnets_dictionary):

    # Creates a list containing w lists, each of h item/s, all filled with 0
    w, h = len(positioning_array[:, 8]) + 1, 1
    nameColumn = [['[0]' for x in range(w)] for y in range(h)]

    # creating a magnet name column, which will be used to refer to when repositioning magnets are required
    for i in range(1,len(robotFilearray)):

        # rectangular magnet being named as 'R01,R02...R27'
        if hasNumbers(robotFilearray[i][1]):
            nameColumn[0][i] = robotFilearray[i][1]

        # circular magnet being named as 'Mag01,Gre02...Blu27'
        else:
            x = np.int16(robotFilearray[i][9])
            nameColumn[0][i] = robotFilearray[i][1] + str('%02d' % x)

    # TEST PRINT
    print(nameColumn)

    # transposing the list to a column with a title assigned
    nameColumn[0][0] = 'Magnet_title'
    nameColumn = np.transpose(nameColumn)

    # add the 'list' column to the robot file array in desired position
    robotFilearray = np.hstack((robotFilearray[:, :8], nameColumn, robotFilearray[:, 8:]))

    # Creates a list containing w lists, each of h item/s, all filled with 0
    w, h = len(positioning_array[:, 9]) + 1, 1
    rePosition_col = [['[0]' for x in range(w)] for y in range(h)]

    # filling out the created list with the blocked magnets dictionary in order with the robot file array
    for each_magnet in fully_blocked_magnets_dictionary:
        for i in range(len(robotFilearray)):

            # checking for match of blocked magnets with robotfile array
            if (robotFilearray[i][0] + ' ' + str(robotFilearray[i][10])) == each_magnet:
                for j in range(len(fully_blocked_magnets_dictionary[each_magnet])):

                    # formatting as required for the rePosition column
                    if j>0:
                        rePosition_col[0][i] += '_'
                    else:
                        rePosition_col[0][i] = '['

                    # checking for match of each blocking magnet with robotfile array to add to rePosition column
                    for k in range(len(robotFilearray)):
                        if robotFilearray[k][0]+' '+str(robotFilearray[k][10]) == fully_blocked_magnets_dictionary[each_magnet][j]:
                            rePosition_col[0][i] += str(robotFilearray[k][8])

                # formatting as required for the rePosition column
                rePosition_col[0][i] += ']'

    # transposing the list to a column with a title assigned
    rePosition_col[0][0] = 'rePosition_magnets'
    rePosition_col = np.transpose(rePosition_col)

    ## TEST PRINTs
    # print(rePosition_col)
    # print(rePosition_col.shape)
    # print(robotFilearray.shape)

    # add the 'list' column to the robot file array in desired position
    robotFilearray = np.hstack((robotFilearray[:, :9], rePosition_col, robotFilearray[:, 9:]))

    return robotFilearray

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def positioningArray_adjust_and_mergetoFile(positioning_array, plate_file, outputFile, newrow, newrow_circular):

    # splitting positioning array into circular
    positioning_array_circular = np.vsplit(positioning_array, 2)[0]

    # adding the title row and getting rid of some columns not required
    positioning_array_circular = np.insert(positioning_array_circular, 0, np.array(newrow_circular), 0)
    positioning_array_circular = np.delete(positioning_array_circular, [2, 3, 4, 5, 9, 10,11], 1)

    # splitting positioning array to keep only rectangular ones
    positioning_array = np.vsplit(positioning_array, 2)[1]

    # adding the title row and getting rid of some columns not required
    positioning_array = np.insert(positioning_array, 0, np.array(newrow), 0)
    positioning_array = np.delete(positioning_array, [2, 3, 4, 5, 8, 11], 1)

    # index for keeping count
    index = 0

    # Open the input_file in read mode and output_file in write mode
    with open(plate_file, 'r') as read_obj, \
            open(outputFile, 'w+', newline='') as write_obj:

        # Create a csv.reader object from the input file object
        csv_reader = csv.reader(read_obj)

        # Create a csv.writer object from the output file object
        csv_writer = csv.writer(write_obj)

        print(positioning_array_circular)

        # Read each row of the input csv file as list
        for row in csv_reader:
            roww_circular = np.array2string(positioning_array_circular[index], separator=' ',formatter={'str_kind': lambda x: x})
            roww = np.array2string(positioning_array[index], separator=' ', formatter={'str_kind': lambda x: x})

            # Append the default text in the row / list
            row.append(str(roww).replace('[', ' ').rstrip(']'))
            row.append(str(roww_circular).replace('[', ' ').rstrip(']'))

            # Add the updated row / list to the output file
            csv_writer.writerow(row)

            # updating index count
            index += 1

    return positioning_array,positioning_array_circular

# final files being formatted to maintain consistency
def finalFiles(outputFile, fileNameHexa):

    df3 = pd.read_csv(outputFile, header=0)

    df1 = pd.read_csv(fileNameHexa,sep=' ')

    mask = df1['probe'] < 22
    df_new = df1[~mask]

    df_tileOutput = pd.concat([df3, df_new], sort=False)

    df_tileOutput.fillna('NA', inplace=True)

    df_tileOutput.to_csv(outputFile, index=False, sep=' ', quoting=csv.QUOTE_NONE, escapechar=' ')

    # df4 = pd.read_csv(robotFile, header=0, error_bad_lines=False)
    # df4.to_csv(robotFile, index=False, sep=' ', quoting=csv.QUOTE_NONE, escapechar=' ')
