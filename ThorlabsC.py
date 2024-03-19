import pylablib as pll
pll.par["devices/dlls/thorlabs_tlcam"] = "C://Users//User//Desktop//Golpe_Voxel//Intromentos//Thorlabs//Native_64_lib"
from pylablib.devices import Thorlabs
Thorlabs.list_cameras_tlcam()
import numpy as np
import os
import cv2
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, OPERATION_MODE
import json

import tango
from tango import AttrQuality, AttrWriteType, DevState, DispLevel, AttReqType, Database
from tango.server import Device, attribute, command
from tango.server import class_property, device_property

db = Database()
try:
   prop = db.get_property('ORBendPoint', 'Pool/' + instance_name)
   orb_end_point = prop['Pool/' + instance_name][0]
   os.environ["ORBendPoint"] = orb_end_point
except:
   pass

class ThorlabsC(Device):
    _my_current = 2.3456
    _my_range = 0.0
    _my_compliance = 0.0
    _output_on = False
    _available_cameras = ""
    _my_cam = None
    _my_camera_ready = False

    host = device_property(dtype=str, default_value="localhost")
    port = class_property(dtype=int, default_value=10000)

    def init_device(self):
        super().init_device()
        self.info_stream(f"Power supply connection details: {self.host}:{self.port}")
        self.set_state(DevState.ON)
        self.set_status("Power supply is ON")
        self.info_stream("\r Power supply is ON \r")
        with TLCameraSDK() as sdk:
            available_cameras = sdk.discover_available_cameras()
            if len(available_cameras) < 1:
                self.info_stream("no cameras detected")
            else:
                self.info_stream("A camera detected")

    current = attribute(
        label="Current",
        dtype=float,
        display_level=DispLevel.EXPERT,
        access=AttrWriteType.READ_WRITE,
        unit="A",
        format="8.4f",
        min_value=0.0,
        max_value=8.5,
        min_alarm=0.1,
        max_alarm=8.4,
        min_warning=0.5,
        max_warning=8.0,
        fget="get_current",
        fset="set_current",
        doc="the power supply current",
    )

    noise = attribute(
        label="Noise",
        dtype=((float,),),
        max_dim_x=1450,
        max_dim_y=1450,
        fget="get_noise",
    )

    Image_foto = attribute(
        label="Image Thorlabs",
        dtype=((int,),),
        #data_format = tango.AttrDataFormat.IMAGE,
        max_dim_x=1080,
        max_dim_y=1440,
        fget="get_image",
    )

    @attribute
    def voltage(self):
        return 10.0

    def get_current(self):
        return self._my_current

    def set_current(self, current):
        print("Current set to %f" % current)
        self._my_current = current

    def get_noise(self):
        a = np.random.random_sample((1100, 1100))
        print(type(a))
        return a
    
    def get_image(self):
        NUM_FRAMES = 1  # adjust to the desired number of frames


        with TLCameraSDK() as sdk:
            available_cameras = sdk.discover_available_cameras()
            if len(available_cameras) < 1:
                print("no cameras detected")

            with sdk.open_camera(available_cameras[0]) as camera:
                camera.exposure_time_us = 1100  # set exposure to 1.1 ms
                camera.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
                camera.image_poll_timeout_ms = 500  # 1 second polling timeout
                old_roi = camera.roi  # store the current roi
                """
                uncomment the line below to set a region of interest (ROI) on the camera
                """
                camera.roi = (350, 350, 1200, 1200)  # set roi to be at origin point (100, 100) with a width & height of 500

                """
                uncomment the lines below to set the gain of the camera and read it back in decibels
                """
                #if camera.gain_range.max > 0:
                #    db_gain = 6.0
                #    gain_index = camera.convert_decibels_to_gain(db_gain)
                #    camera.gain = gain_index
                #    print(f"Set camera gain to {camera.convert_gain_to_decibels(camera.gain)}")

                camera.arm(2)

                camera.issue_software_trigger()

                for i in range(NUM_FRAMES):
                    frame = camera.get_pending_frame_or_null()
                    if frame is not None:
                        print("frame #{} received!".format(frame.frame_count))

                        frame.image_buffer  # .../ perform operations using the data from image_buffer

                        #  NOTE: frame.image_buffer is a temporary memory buffer that may be overwritten during the next call
                        #        to get_pending_frame_or_null. The following line makes a deep copy of the image data:
                        image_buffer_copy = np.copy(frame.image_buffer)
                    else:
                        print("timeout reached during polling, program exiting...")
                        break
                camera.disarm()
                camera.roi = old_roi  # reset the roi back to the original roi
        print(image_buffer_copy.shape)
        return image_buffer_copy


    # def get_image(self):
    #     with TLCameraSDK() as sdk:
    #         available_cameras = sdk.discover_available_cameras()
    #         with sdk.open_camera(available_cameras[0]) as camera:
    #             camera.exposure_time_us = 1000  # set exposure to 11 ms
    #             camera.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
    #             camera.image_poll_timeout_ms = 500  # 1 second polling timeout
        
    #             camera.arm(2)
        
    #             camera.issue_software_trigger()
        
    #             frame = camera.get_pending_frame_or_null()
    #             if frame is not None:
    #                 print("frame #{} received!".format(frame.frame_count))
    #                 frame.image_buffer
    #                 image_buffer_copy = np.copy(frame.image_buffer)
    #                 numpy_shaped_image = image_buffer_copy.reshape(camera.image_height_pixels, camera.image_width_pixels)
    #                 nd_image_array = np.full((camera.image_height_pixels, camera.image_width_pixels, 3), 0, dtype=np.uint8)
    #                 nd_image_array[:,:,0] = numpy_shaped_image
    #                 nd_image_array[:,:,1] = numpy_shaped_image
    #                 nd_image_array[:,:,2] = numpy_shaped_image


    #                 send_JSON = {"Image":nd_image_array.tolist()}
    #                 #cv2.imwrite(filename,nd_image_array)
    #                 #cv2.imshow("Image From TSI Cam", nd_image_array)
    #             else:
    #                 print("Unable to acquire image, program exiting...")
    #                 exit()
                        
    #                 #cv2.waitKey(0)
    #             camera.disarm()
    #             print("getimage_new function")
    #             print(type(nd_image_array[:,:,0]))
    #             return nd_image_array[:,:,0]

    # @command(dtype_out=str)
    # def int_cam(self):
    #     with TLCameraSDK() as sdk:
    #         available_cameras = sdk.discover_available_cameras()
    #         with sdk.open_camera(available_cameras[0]) as camera:
    #             self._my_cam =camera
    #             self._my_cam.exposure_time_us = 10000  # set exposure to 11 ms
    #             self._my_cam.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
    #             self._my_cam.image_poll_timeout_ms = 1000  # 1 second polling timeout

    #             self._my_cam.arm(2)

    #             self._my_cam.issue_software_trigger()
    #             self._my_camera_ready = True
    #     return "Cam init"
    
    # @command(dtype_out=str)
    # def close_cam(self):
    #     self._my_cam.disarm()
    #     return "Camera Closed"

    @command(dtype_in=str, dtype_out=str)    
    def get_foto(self, name):
        with TLCameraSDK() as sdk:
            available_cameras = sdk.discover_available_cameras()
            with sdk.open_camera(available_cameras[0]) as camera:
                camera.exposure_time_us = 10000  # set exposure to 11 ms
                camera.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
                camera.image_poll_timeout_ms = 1000  # 1 second polling timeout
        
                camera.arm(2)
        
                camera.issue_software_trigger()
        
                frame = camera.get_pending_frame_or_null()
                if frame is not None:
                    print("frame #{} received!".format(frame.frame_count))
                    frame.image_buffer
                    image_buffer_copy = np.copy(frame.image_buffer)
                    numpy_shaped_image = image_buffer_copy.reshape(camera.image_height_pixels, camera.image_width_pixels)
                    nd_image_array = np.full((camera.image_height_pixels, camera.image_width_pixels, 3), 0, dtype=np.uint8)
                    nd_image_array[:,:,0] = numpy_shaped_image
                    nd_image_array[:,:,1] = numpy_shaped_image
                    nd_image_array[:,:,2] = numpy_shaped_image
                    if name == "":
                        filename="tango_works.jpg"
                    else:
                        filename=name
                    cv2.imwrite(filename,nd_image_array)
                    #cv2.imshow("Image From TSI Cam", nd_image_array)
                else:
                    print("Unable to acquire image, program exiting...")
                    exit()
                    
                cv2.waitKey(0)
                camera.disarm()
            return filename+" was taken"
        
    @command(dtype_out=str)    
    def get_foto_JSON(self):
        with TLCameraSDK() as sdk:
            available_cameras = sdk.discover_available_cameras()
            with sdk.open_camera(available_cameras[0]) as camera:
                camera.exposure_time_us = 10000  # set exposure to 11 ms
                camera.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
                camera.image_poll_timeout_ms = 1000  # 1 second polling timeout
        
                camera.arm(2)
        
                camera.issue_software_trigger()
        
                frame = camera.get_pending_frame_or_null()
                if frame is not None:
                    print("frame #{} received!".format(frame.frame_count))
                    frame.image_buffer
                    image_buffer_copy = np.copy(frame.image_buffer)
                    numpy_shaped_image = image_buffer_copy.reshape(camera.image_height_pixels, camera.image_width_pixels)
                    nd_image_array = np.full((camera.image_height_pixels, camera.image_width_pixels, 3), 0, dtype=np.uint8)
                    nd_image_array[:,:,0] = numpy_shaped_image
                    nd_image_array[:,:,1] = numpy_shaped_image
                    nd_image_array[:,:,2] = numpy_shaped_image


                    send_JSON = {"Image":nd_image_array.tolist()}
                    #cv2.imwrite(filename,nd_image_array)
                    #cv2.imshow("Image From TSI Cam", nd_image_array)
                else:
                    print("Unable to acquire image, program exiting...")
                    exit()
                    
                #cv2.waitKey(0)
                camera.disarm()
            return json.dumps(send_JSON)
    range = attribute(label="Range", dtype=float)

    @range.setter
    def range(self, new_range):
        self._my_range = new_range

    @range.getter
    def current_range(self):
        return self._my_range, time(), AttrQuality.ATTR_WARNING

    @range.is_allowed
    def can_range_be_changed(self, req_type):
        if req_type == AttReqType.WRITE_REQ:
            return not self._output_on
        return True

    compliance = attribute(label="Compliance", dtype=float)

    @compliance.read
    def compliance(self):
        return self._my_compliance

    @compliance.write
    def new_compliance(self, new_compliance):
        self._my_compliance = new_compliance

    @command(dtype_in=bool, dtype_out=bool)
    def output_on_off(self, on_off):
        self._output_on = on_off
        return self._output_on
        
if __name__ == "__main__":
    ThorlabsC.run_server()



#  Because we are using the 'with' statement context-manager, disposal has been taken care of.
