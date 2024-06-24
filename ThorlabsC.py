'''
Cameras: 
    Set-up gain                                             Done
    Set-up the exposure time                                Done
    Acquire a frame                                         Done
    Set binning                                             ????
    Set ROI                                                 Done


'''


import pylablib as pll
from pylablib.devices import Thorlabs
Thorlabs.list_cameras_tlcam()
import numpy as np
import os
import cv2
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, OPERATION_MODE
import json

import configparser

import tango
from tango import AttrQuality, AttrWriteType, DevState, DispLevel, AttReqType, Database
from tango.server import Device, attribute, command
from tango.server import class_property, device_property


# _____________ Check if this is need to work _____________
db = Database()
try:
   prop = db.get_property('ORBendPoint', 'Pool/' + instance_name)
   orb_end_point = prop['Pool/' + instance_name][0]
   os.environ["ORBendPoint"] = orb_end_point
except:
   pass

# _________________________________________________________
config_info = configparser.ConfigParser()
config_info.read('setting.ini')


pll.par["devices/dlls/thorlabs_tlcam"] = str(config_info['DEFAULT']['DLL'])


class ThorlabsC(Device):
    CAMS = {}
    Image_Photo_V2_Cam = ""
    sdk =  TLCameraSDK()
    my_camera_ready = False

    host = device_property(dtype=str, default_value="localhost")
    port = class_property(dtype=int, default_value=10000)


    def init_device(self):
        super().init_device()
        self.info_stream(f"Connection details: {self.host}:{self.port}")
        self.set_state(DevState.ON)
        self.set_status("Thorlabs CAMS Driver is ON, you need to connect a camera")

    def init_device_old(self):
        super().init_device()
        self.info_stream(f"Connection details: {self.host}:{self.port}")
        self.set_state(DevState.ON)
        self.info_stream("\r Try to start the Thorlabs Driver \r")
        available_cameras = self.sdk.discover_available_cameras()
        if len(available_cameras) < 1:
            self.info_stream("no cameras detected")
        else:
            self.info_stream("A camera detected")
            self.CAMS = self.sdk.open_camera(available_cameras[0])  
            try:
                # Check if te camera is disarmend
                self.CAMS.disarm()
            except:
                print("All good")
            self.CAMS.exposure_time_us = 1100  # set exposure to 1.1 ms
            self.CAMS.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
            self.CAMS.image_poll_timeout_ms = 500  # 1 second polling timeout
            #old_roi = CAMS.roi  # store the current roi
            """
            uncomment the line below to set a region of interest (ROI) on the camera
            """
            #camera.roi = (50, 50, 1200, 1000)  # set roi to be at origin point (100, 100) with a width & height of 500

            """
            uncomment the lines below to set the gain of the camera and read it back in decibels
            """
            #if camera.gain_range.max > 0:
            #    db_gain = 6.0
            #    gain_index = camera.convert_decibels_to_gain(db_gain)
            #    camera.gain = gain_index
            #    print(f"Set camera gain to {camera.convert_gain_to_decibels(camera.gain)}")

            self.CAMS.arm(2)
            self.set_status("Thorlabs CAMS Driver is ON")

    def delete_device(self):
        self.CAMS.disarm()
        return 


    Cam_1 = attribute(
        label="Image Thorlabs",
        dtype=((int,),),
        #data_format = tango.AttrDataFormat.IMAGE,
        max_dim_x=1440,
        max_dim_y=1440,
        fget="get_image_1",
    )
    

    Cam_2 = attribute(
        label="Image Thorlabs",
        dtype=((int,),),
        #data_format = tango.AttrDataFormat.IMAGE,
        max_dim_x=1440,
        max_dim_y=1440,
        fget="get_image_2",
    )


    Cam_3 = attribute(
        label="Image Thorlabs",
        dtype=((int,),),
        #data_format = tango.AttrDataFormat.IMAGE,
        max_dim_x=1440,
        max_dim_y=1440,
        fget="get_image_3",
    )

    Cam_4 = attribute(
        label="Image Thorlabs",
        dtype=((int,),),
        #data_format = tango.AttrDataFormat.IMAGE,
        max_dim_x=1440,
        max_dim_y=1440,
        fget="get_image_4",
    )



    # def get_image(self):
    #     NUM_FRAMES = 1  # adjust to the desired number of frames     

    #     self.CAMS.issue_software_trigger()

    #     for i in range(NUM_FRAMES):
    #         frame = self.CAMS.get_pending_frame_or_null()
    #         if frame is not None:
    #             #print("frame #{} received!".format(frame.frame_count))

    #             frame.image_buffer  # .../ perform operations using the data from image_buffer

    #             #  NOTE: frame.image_buffer is a temporary memory buffer that may be overwritten during the next call
    #             #        to get_pending_frame_or_null. The following line makes a deep copy of the image data:
    #             # image_buffer_copy = np.copy(frame.image_buffer)
    #             image_buffer_copy = np.array(frame.image_buffer,dtype = np.uint8)
    #         else:
    #             print("timeout reached during polling, program exiting...")
    #             break
    #     #print(image_buffer_copy.shape)
    #     return image_buffer_copy
    

    def get_image_1(self):
        NUM_FRAMES = 1  # adjust to the desired number of frames     

        self.CAMS["Cam_1"]["Serial"].issue_software_trigger()

        for i in range(NUM_FRAMES):
            frame = self.CAMS["Cam_1"]["Serial"].get_pending_frame_or_null()
            if frame is not None:
                #print("frame #{} received!".format(frame.frame_count))

                frame.image_buffer  # .../ perform operations using the data from image_buffer

                #  NOTE: frame.image_buffer is a temporary memory buffer that may be overwritten during the next call
                #        to get_pending_frame_or_null. The following line makes a deep copy of the image data:
                # image_buffer_copy = np.copy(frame.image_buffer)
                image_buffer_copy = np.array(frame.image_buffer,dtype = np.uint8)
            else:
                print("timeout reached during polling, program exiting...")
                break
        #print(image_buffer_copy.shape)
        return image_buffer_copy
    
    def get_image_2(self):
        NUM_FRAMES = 1  # adjust to the desired number of frames     

        self.CAMS["Cam_2"]["Serial"].issue_software_trigger()

        for i in range(NUM_FRAMES):
            frame = self.CAMS["Cam_2"]["Serial"].get_pending_frame_or_null()
            if frame is not None:
                #print("frame #{} received!".format(frame.frame_count))

                frame.image_buffer  # .../ perform operations using the data from image_buffer

                #  NOTE: frame.image_buffer is a temporary memory buffer that may be overwritten during the next call
                #        to get_pending_frame_or_null. The following line makes a deep copy of the image data:
                # image_buffer_copy = np.copy(frame.image_buffer)
                image_buffer_copy = np.array(frame.image_buffer,dtype = np.uint8)
            else:
                print("timeout reached during polling, program exiting...")
                break
        #print(image_buffer_copy.shape)
        return image_buffer_copy
    

    def get_image_3(self):
        NUM_FRAMES = 1  # adjust to the desired number of frames     

        self.CAMS["Cam_3"]["Serial"].issue_software_trigger()

        for i in range(NUM_FRAMES):
            frame = self.CAMS["Cam_3"]["Serial"].get_pending_frame_or_null()
            if frame is not None:
                #print("frame #{} received!".format(frame.frame_count))

                frame.image_buffer  # .../ perform operations using the data from image_buffer

                #  NOTE: frame.image_buffer is a temporary memory buffer that may be overwritten during the next call
                #        to get_pending_frame_or_null. The following line makes a deep copy of the image data:
                # image_buffer_copy = np.copy(frame.image_buffer)
                image_buffer_copy = np.array(frame.image_buffer,dtype = np.uint8)
            else:
                print("timeout reached during polling, program exiting...")
                break
        #print(image_buffer_copy.shape)
        return image_buffer_copy
    
    def get_image_4(self):
        NUM_FRAMES = 1  # adjust to the desired number of frames     

        self.CAMS["Cam_4"]["Serial"].issue_software_trigger()

        for i in range(NUM_FRAMES):
            frame = self.CAMS["Cam_4"]["Serial"].get_pending_frame_or_null()
            if frame is not None:
                #print("frame #{} received!".format(frame.frame_count))

                frame.image_buffer  # .../ perform operations using the data from image_buffer

                #  NOTE: frame.image_buffer is a temporary memory buffer that may be overwritten during the next call
                #        to get_pending_frame_or_null. The following line makes a deep copy of the image data:
                # image_buffer_copy = np.copy(frame.image_buffer)
                image_buffer_copy = np.array(frame.image_buffer,dtype = np.uint8)
            else:
                print("timeout reached during polling, program exiting...")
                break
        #print(image_buffer_copy.shape)
        return image_buffer_copy    

    

    def get_image_select_cam(self,Cam):
        NUM_FRAMES = 1  # adjust to the desired number of frames     

        self.CAMS[Cam]["Serial"].issue_software_trigger()

        for i in range(NUM_FRAMES):
            frame = self.CAMS[Cam]["Serial"].get_pending_frame_or_null()
            if frame is not None:
                #print("frame #{} received!".format(frame.frame_count))

                frame.image_buffer  # .../ perform operations using the data from image_buffer

                #  NOTE: frame.image_buffer is a temporary memory buffer that may be overwritten during the next call
                #        to get_pending_frame_or_null. The following line makes a deep copy of the image data:
                # image_buffer_copy = np.copy(frame.image_buffer)
                image_buffer_copy = np.array(frame.image_buffer,dtype = np.uint8)
            else:
                print("timeout reached during polling, program exiting...")
                break
        #print(image_buffer_copy.shape)
        return image_buffer_copy

    @command(dtype_out=str)
    def ListCameras(self):
        available_cameras = self.sdk.discover_available_cameras()
        print_cam = ""
        if len(available_cameras) < 1:
            return "no cameras detected"
        else:
            for i in available_cameras:
                print_cam += i
                print_cam += ", "
            return print_cam[0:-2]
        


    # The user will pass a string that is going to be converted to a JSON 
    # with the Camera that they want to connect and the name they want to call it.
    # It is also possible to send the expousure time, etc if none give it is set with deafault valeus.
    @command(dtype_in=str,dtype_out=str)  
    def ConnectCamera(self,infoCamera):
        # print(infoCamera)
        Info =  json.loads(infoCamera)
        print(Info)
        available_cameras = self.sdk.discover_available_cameras()
        if len(available_cameras) < 1:
            self.info_stream("no cameras detected")
            return "no cameras detected"
        else:
            if Info["Cam"] in available_cameras:
                if "Attribute" in Info.keys():
                    self.info_stream("A camera detected")
                    self.CAMS[Info["Attribute"]] = {'Serial': self.sdk.open_camera(Info["Cam"])}
                    try:
                        # Check if te camera is disarmend
                        self.CAMS.disarm()
                    except:
                        print("All good")
                    if "exposure_us" in Info.keys():
                        self.CAMS[Info["Attribute"]]["Serial"].exposure_time_us = Info["exposure_us"]  # set exposure to 1.1 ms
                    else:
                        self.CAMS[Info["Attribute"]]["Serial"].exposure_time_us = 1100  # set exposure to 1.1 ms
                    if "frames_per_trigger" in Info.keys():
                        self.CAMS[Info["Attribute"]]["Serial"].frames_per_trigger_zero_for_unlimited = Info["frames_per_trigger"]  # start camera in continuous mode
                    else:
                        self.CAMS[Info["Attribute"]]["Serial"].frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
                       
                    if "poll_timeout_ms" in Info.keys():  
                        self.CAMS[Info["Attribute"]]["Serial"].image_poll_timeout_ms = Info["poll_timeout_ms"]  # 1 second polling timeout
                    else:
                        self.CAMS[Info["Attribute"]]["Serial"].image_poll_timeout_ms = 500  # 1 second polling timeout
                        # old_roi = CAMS.roi  # store the current roi
                    self.CAMS[Info["Attribute"]["Serial"]].arm(2)

                    
                elif "CamName" in Info.keys():
                    self.info_stream("A camera detected")
                    self.CAMS[Info["CamName"]] ={'Serial': self.sdk.open_camera(Info["Cam"])}
                    try:
                        # Check if te camera is disarmend
                        self.CAMS[Info["CamName"]]["Serial"].disarm()
                    except:
                        print("All good")
                    
                    if "exposure_us" in Info.keys():  
                        self.CAMS[Info["CamName"]]["Serial"].exposure_time_us = Info["exposure_us"]  
                    else:
                        self.CAMS[Info["CamName"]]["Serial"].exposure_time_us = 1100  # set exposure to 1.1 ms
                    if "frames_per_trigger" in Info.keys():
                        self.CAMS[Info["CamName"]]["Serial"].frames_per_trigger_zero_for_unlimited = Info["frames_per_trigger"]  # start camera in continuous mode
                    else:
                        self.CAMS[Info["CamName"]]["Serial"].frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
                    
                    if "poll_timeout_ms" in Info.keys():  
                        self.CAMS[Info["CamName"]]["Serial"].image_poll_timeout_ms = Info["poll_timeout_ms"]  # 1 second polling timeout
                    else:
                        self.CAMS[Info["CamName"]]["Serial"].image_poll_timeout_ms = 500  # 1 second polling timeout
                    
                        # old_roi = CAMS.roi  # store the current roi
                    self.CAMS[Info["CamName"]]["Serial"].arm(2)
                else:
                    return "The JSON sent those not contain the key 'Attribute' or 'CamName' "
        return "Camera test"
    



    @command(dtype_in=str, dtype_out=str)
    def SetRoi(self,ROI):
        ROI =  json.loads(ROI)
        self.CAMS[ROI["CamName"]]["Serial"].disarm()
        self.CAMS[ROI["CamName"]]["Serial"].roi = (int(ROI["upper_left_x_pixels"]), int(ROI['upper_left_y_pixels']), int(ROI['lower_right_x_pixels']),int( ROI['lower_right_y_pixels']))
        self.CAMS[ROI["CamName"]]["Serial"].arm(2)
        string_out = str(ROI["upper_left_x_pixels"])+", "+str(ROI['upper_left_y_pixels'])+", "+str(ROI['lower_right_x_pixels'])+", "+str(ROI['lower_right_y_pixels'])
        return "CAMS "+ ROI["CamName"]+" was set roi to "+ string_out+"\n"
    


    @command(dtype_in=str, dtype_out=str)
    def SetGain(self,gain):
        gain =  json.loads(gain)
        if self.CAMS[gain["CamName"]]["Serial"].gain_range.max > 0:
            # db_gain = 6.0
            gain_index = self.CAMS[gain["CamName"]]["Serial"].convert_decibels_to_gain(gain)
            self.CAMS[gain["CamName"]]["Serial"].gain = gain_index

        return f"Set camera gain to {self.CAMS.convert_gain_to_decibels(self.CAMS.gain)}"


    @command(dtype_in=str, dtype_out=str)
    def SetExpousureTimeUS(self,parameter):
        parameter = json.loads(parameter)
        self.CAMS[parameter["CamName"]]["Serial"].exposure_time_us = parameter["exposure_time_us"]  # set exposure to 1.1 ms
        return "CAMS "+ " was set exposure time "+ str(parameter["exposure_time_us"]) +" us\n"
            
    @command(dtype_in=str, dtype_out=str)      
    def SetFramesPerTriggerZeroForUnlimited(self,continuousMode):
        continuousMode = json.loads(continuousMode)
        self.CAMS[continuousMode["CamName"]]["Serial"].frames_per_trigger_zero_for_unlimited = continuousMode["continuousMode"]  # start camera in continuous mode
        return "CAMS "+ " was set frames per trigger zero or unlimited "+ str(continuousMode["continuousMode"]) +"\n"
        
    @command(dtype_in=str, dtype_out=str)       
    def SetImagePollTimeoutMS(self,imagePollTimeout):
        imagePollTimeout = json.loads(imagePollTimeout)
        self.CAMS[imagePollTimeout["CamName"]]["Serial"].image_poll_timeout_ms = imagePollTimeout["imagePollTimeout"]  # 1 second polling timeout
        return "CAMS "+ " was set image poll timeout "+ str(imagePollTimeout["imagePollTimeout"]) +" ms\n"

    # # This command saves a image on the local PC where the driver is installed 
    # @command(dtype_in=str, dtype_out=str)    
    # def GetLocalPhoto(self, photoName):        
    #     image_array = self.get_image()
    #     if photoName == "":
    #         filename="tango_works.jpg"
    #     else:
    #         filename=photoName
    #     cv2.imwrite(filename,image_array)
    #     #cv2.imshow("Image From TSI Cam", nd_image_array)            
    #     cv2.waitKey(0)
    #     return filename+" was taken"
        
    @command(dtype_in=str, dtype_out=str)    
    def GetPhotoJSON(self,Cam):
        if Cam in self.CAMS:
            send_JSON = {"Image":self.get_image_select_cam(Cam).tolist()}
            
            return json.dumps(send_JSON)
        else:
            return "No Camera with the name: " + Cam
   
        
if __name__ == "__main__":
    ThorlabsC.run_server()
