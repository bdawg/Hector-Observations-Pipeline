circular_magnet_radius                     = 6.2
rectangle_magnet_width                     = 12.4
rectangle_magnet_length                    = 22.0
circular_rectangle_magnet_distance         = 10.0
circular_rectangle_magnet_center_distance  = (circular_magnet_radius + circular_rectangle_magnet_distance
                                              + rectangle_magnet_length / 2.0)
HECTOR_plate_center_coordinate             = [0.0,0.0]
HECTOR_plate_radius                        = 226.0 # previous value=260.0
robot_arm_length                           = 14.50
robot_arm_width                            = 10
circular_magnet_pickuparea_length          = robot_arm_length
circular_magnet_pickuparea_width           = (3.0 * robot_arm_width / 2.0) + circular_magnet_radius
rectangle_magnet_pickuparea_length         = robot_arm_length

if (robot_arm_width < ((rectangle_magnet_length - robot_arm_width) / 2)):
    rectangle_magnet_pickuparea_width = (robot_arm_width + rectangle_magnet_length) / 2
elif (robot_arm_width >= ((rectangle_magnet_length - robot_arm_width) / 2)):
    rectangle_magnet_pickuparea_width = 2 * robot_arm_width
#rectangle_magnet_pickuparea_width          = 0.5 * (rectangle_magnet_length + 3.0 * robot_arm_width)

# robot file center coordinates, depending on the mechanical mounting of the plate
robot_center_x = 329.5
robot_center_y = 300