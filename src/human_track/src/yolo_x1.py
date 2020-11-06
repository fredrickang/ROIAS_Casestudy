#!/usr/bin/env python
# -*- coding: utf-8 -*-

####################################################################
# 프로그램명 : yolo_x1.py
# 작 성 자 : 자이트론
# 생 성 일 : 2020년 08월 12일
# 본 프로그램은 상업 라이센스에 의해 제공되므로 무단 배포 및 상업적 이용을 금합니다.
####################################################################

import rospy, time
from sensor_msgs.msg import LaserScan
from darknet_ros_msgs.msg import BoundingBoxes
from xycar_motor.msg import xycar_motor
from ar_track_alvar_msgs.msg import AlvarMarkers
import signal
import sys
import os

def signal_handler(sig, frame):
    os.system('killall -9 python rosout')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

steering_pub = None
box_data = []
lidar_data = []
ar_data = []

ack_msg = xycar_motor()
person = None

def init_node():
    global steering_pub
    rospy.init_node('human_track')
    rospy.Subscriber('/darknet_ros/bounding_boxes', BoundingBoxes, callback)
    rospy.Subscriber('/ar_pose_marker',AlvarMarkers, callback_ar)
    steering_pub = rospy.Publisher('xycar_motor', xycar_motor, queue_size=1)

def exit_node():
    print('finished')

def breakout():
    for back_cnt in range(10):
        drive(50,-2)
        time.sleep(0.1)

def go():
    for back_cnt in range(10):
        drive(-50,2)
        time.sleep(0.1)

def drive(angle, speed):
    global steering_pub
    ack_msg.header.stamp = rospy.Time.now()
    ack_msg.angle = angle 
    ack_msg.speed = speed
    steering_pub.publish(ack_msg)

def callback(msg):
    global box_data
    box_data = msg

def callback_lidar(data):
    global lidar_data
    lidar_data = data.ranges

def callback_ar(msg):
    global ar_data
    ar_data = msg

def stare_who(last_pos, nearest_pos, person_box):
    center = (person_box.xmax + person_box.xmin) / 2

    if abs(last_pos-center) < abs(last_pos-nearest_pos) :
        return center

    return nearest_pos

def detect_lidar():
    global lidar_data
    ok = 0

    if len(lidar_data) != 360:
        return True
    for degree in range(0,180):
        if lidar_data[degree] < 0.3:
            ok += 1
        if ok > 3:
            return True
    return False

if __name__ == '__main__':
    init_node()
    FarAway = 1000000
    Count = 10
    Threshold = 60

    cnt = 10
    last_pos = 0
    time.sleep(15)
    
    boxes_before = -1
    while not rospy.is_shutdown():
        nearest_pos = FarAway
        boxes = box_data
        
        if not ar_data:
            continue
        
        if not boxes:
            continue
        
        print("Localization", ar_data)
        hit = False
        for i in range(len(boxes.bounding_boxes)):
            if boxes.bounding_boxes[i].Class == 'person':
                 hit = True

        if hit:
            print("Person detected", time.time())
            drive(0,0)
        else:
            print("Something else", time.time())
            drive(0,2)
        
        '''
                if last_pos == 0:
                    last_pos = (boxes.bounding_boxes[i].xmax + boxes.bounding_boxes[i].xmin)/2
                    nearest_pos = last_pos
                    print "new person : ", nearest_pos
                else:
                    nearest_pos = stare_who(last_pos, nearest_pos, boxes.bounding_boxes[i])

        if nearest_pos == FarAway :
            cnt -= 1
            time.sleep(0.1)
            if cnt < 0 :
                last_pos = 0
                qq = (abs(last_pos - nearest_pos) > Threshold)
                if qq and detect_lidar():
                    breakout()
                elif qq and (detect_lidar() == False):
                    go()
        else:
            cnt = Count
            last_pos = nearest_pos
            angle = int(50.0*((320.0 - last_pos)/320.0)) * -1
            if detect_lidar():
                drive(angle, 0)
                time.sleep(0.1)
            else:
                drive(angle, 2)
        
        '''
        
    rospy.on_shutdown(exit_node)


