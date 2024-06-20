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
    _my_current = 2.3456
    _my_range = 0.0
    _my_compliance = 0.0
    _output_on = False
    _available_cameras = ""
    CAMARA = None
    sdk =  TLCameraSDK()
    my_camera_ready = False

    host = device_property(dtype=str, default_value="localhost")
    port = class_property(dtype=int, default_value=10000)

    def init_device(self):
        super().init_device()
        self.info_stream(f"Connection details: {self.host}:{self.port}")
        self.set_state(DevState.ON)
        self.info_stream("\r Try to start the Thorlabs Driver \r")
        available_cameras = self.sdk.discover_available_cameras()
        if len(available_cameras) < 1:
            self.info_stream("no cameras detected")
        else:
            self.info_stream("A camera detected")
            self.CAMARA = self.sdk.open_camera(available_cameras[0])  
            try:
                # Check if te camera is disarmend
                self.CAMARA.disarm()
            except:
                print("All good")
            self.CAMARA.exposure_time_us = 1100  # set exposure to 1.1 ms
            self.CAMARA.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
            self.CAMARA.image_poll_timeout_ms = 500  # 1 second polling timeout
            #old_roi = CAMARA.roi  # store the current roi
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

            self.CAMARA.arm(2)
            self.set_status("Thorlabs Camara Driver is ON")

    def __del__(self):
        self.CAMARA.disarm()
        return 

    # current = attribute(
    #     label="Current",
    #     dtype=float,
    #     display_level=DispLevel.EXPERT,
    #     access=AttrWriteType.READ_WRITE,
    #     unit="A",
    #     format="8.4f",
    #     min_value=0.0,
    #     max_value=8.5,
    #     min_alarm=0.1,
    #     max_alarm=8.4,
    #     min_warning=0.5,
    #     max_warning=8.0,
    #     fget="get_current",
    #     fset="set_current",
    #     doc="the power supply current",
    # )

    # noise = attribute(
    #     label="Noise",
    #     dtype=((float,),),
    #     max_dim_x=1450,
    #     max_dim_y=1450,
    #     fget="get_noise",
    # )

    Image_Photo = attribute(
        label="Image Thorlabs",
        dtype=((int,),),
        #data_format = tango.AttrDataFormat.IMAGE,
        max_dim_x=1440,
        max_dim_y=1440,
        fget="get_image",
    )

    # @attribute
    # def voltage(self):
    #     return 10.0

    # def get_current(self):
    #     return self._my_current

    # def set_current(self, current):
    #     print("Current set to %f" % current)
    #     self._my_current = current

    # def get_noise(self):
    #     a = np.random.random_sample((1100, 1100))
    #     print(type(a))
    #     return a
    
    def get_image(self):
        NUM_FRAMES = 1  # adjust to the desired number of frames     

        self.CAMARA.issue_software_trigger()

        for i in range(NUM_FRAMES):
            frame = self.CAMARA.get_pending_frame_or_null()
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
        Info =  json.loads(infoCamera)
        available_cameras = self.sdk.discover_available_cameras()
        if len(available_cameras) < 1:
            self.info_stream("no cameras detected")
        else:
            if Info["Cam"] in available_cameras:
                self.info_stream("A camera detected")
                self.CAMARA[Info["CamName"]] = self.sdk.open_camera(Info["Cam"])  
                try:
                    # Check if te camera is disarmend
                    self.CAMARA.disarm()
                except:
                    print("All good")
                self.CAMARA[Info["CamName"]].exposure_time_us = 1100  # set exposure to 1.1 ms
                self.CAMARA[Info["CamName"]].frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
                self.CAMARA[Info["CamName"]].image_poll_timeout_ms = 500  # 1 second polling timeout
                #old_roi = CAMARA.roi  # store the current roi

    @command(dtype_in=(int,), dtype_out=str)
    def SetRoi(self,ROI):
        self.CAMARA.disarm()
        self.CAMARA.roi = (ROI[0], ROI[1], ROI[2], ROI[3])
        self.CAMARA.arm(2)
        return "CAMARA "+ " was set roi to "+ str(ROI[0])+", "+str(ROI[1])+", "+str(ROI[2])+", "+str(ROI[3]) +"\n"
    

    @command(dtype_in=float, dtype_out=str)
    def SetGain(self,gain):
        if self.CAMARA.gain_range.max > 0:
            # db_gain = 6.0
            gain_index = self.CAMARA.convert_decibels_to_gain(gain)
            self.CAMARA.gain = gain_index

        return f"Set camera gain to {self.CAMARA.convert_gain_to_decibels(self.CAMARA.gain)}"


    @command(dtype_in=int, dtype_out=str)
    def SetExpousureTimeUS(self,parameter):
        self.CAMARA.exposure_time_us = parameter  # set exposure to 1.1 ms
        return "CAMARA "+ " was set exposure time "+ str(parameter) +" us\n"
            
    @command(dtype_in=int, dtype_out=str)      
    def SetFramesPerTriggerZeroForUnlimited(self,continuousMode):
        self.CAMARA.frames_per_trigger_zero_for_unlimited = continuousMode  # start camera in continuous mode
        return "CAMARA "+ " was set frames per trigger zero or unlimited "+ str(continuousMode) +"\n"
        
    @command(dtype_in=int, dtype_out=str)       
    def SetImagePollTimeoutMS(self,imagePollTimeout):
        self.CAMARA.image_poll_timeout_ms = imagePollTimeout  # 1 second polling timeout
        return "CAMARA "+ " was set image poll timeout "+ str(imagePollTimeout) +" ms\n"

    # This command saves a image on the local PC where the driver is installed 
    @command(dtype_in=str, dtype_out=str)    
    def GetLocalPhoto(self, photoName):        
        image_array = self.get_image()
        if photoName == "":
            filename="tango_works.jpg"
        else:
            filename=photoName
        cv2.imwrite(filename,image_array)
        #cv2.imshow("Image From TSI Cam", nd_image_array)            
        cv2.waitKey(0)
        return filename+" was taken"
        
    @command(dtype_out=str)    
    def GetPhotoJSON(self):

        send_JSON = {"Image":self.get_image().tolist()}
            
        return json.dumps(send_JSON)
   
        
if __name__ == "__main__":
    ThorlabsC.run_server()
