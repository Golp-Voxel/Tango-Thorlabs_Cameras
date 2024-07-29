# -*- coding: utf-8 -*-
#
# This file is part of the ThorlabsC project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

"""
Zelux Thorlabs Camera

This class is to integrate a Zelux Thorlabs Camera.
After installing the Server on the jive/astor you will need to use the Wizard tool 
to difine the proparties of that particular device.
"""

# PROTECTED REGION ID(ThorlabsC.system_imports) ENABLED START #
# PROTECTED REGION END #    //  ThorlabsC.system_imports

# PyTango imports
import tango
from tango import DebugIt
from tango.server import run
from tango.server import Device
from tango.server import attribute, command
from tango.server import device_property
from tango import AttrQuality, DispLevel, DevState
from tango import AttrWriteType, PipeWriteType
# Additional import
# PROTECTED REGION ID(ThorlabsC.additionnal_import) ENABLED START #

import pylablib as pll
from pylablib.devices import Thorlabs
Thorlabs.list_cameras_tlcam()
import numpy as np
import os
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, OPERATION_MODE

import time
from threading import Thread
import configparser
config_info = configparser.ConfigParser()
config_info.read('setting.ini')


pll.par["devices/dlls/thorlabs_tlcam"] = str(config_info['DEFAULT']['DLL'])

stop_threads = True

# PROTECTED REGION END #    //  ThorlabsC.additionnal_import

__all__ = ["ThorlabsC", "main"]


class ThorlabsC(Device):
    """
    This class is to integrate a Zelux Thorlabs Camera.
    After installing the Server on the jive/astor you will need to use the Wizard tool 
    to difine the proparties of that particular device.

    **Properties:**

    - Device Property
        CameraID
            - Type:'str'
    """
    # PROTECTED REGION ID(ThorlabsC.class_variable) ENABLED START #
    my_thread = None
    CAM = None
    sdk =  TLCameraSDK()
    # PROTECTED REGION END #    //  ThorlabsC.class_variable

    # -----------------
    # Device Properties
    # -----------------

    CameraID = device_property(
        dtype='str',
        mandatory=True
    )

    # ----------
    # Attributes
    # ----------

    ExposureTime = attribute(
        dtype='DevUShort',
        access=AttrWriteType.READ_WRITE,
        label="Exposure time of the camera",
        unit="ms",
        display_unit="ms",
        doc="Exposure time of the camera  in ms ",
    )

    Gain = attribute(
        dtype='DevDouble',
        access=AttrWriteType.READ_WRITE,
    )

    ROI = attribute(
        dtype=('DevUShort',),
        access=AttrWriteType.READ_WRITE,
        max_dim_x=4,
    )

    Image = attribute(
        dtype=(('DevUShort',),),
        max_dim_x=1440, max_dim_y=1080,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initializes the attributes and properties of the ThorlabsC."""
        Device.init_device(self)
        self._exposure_time = 0
        self._gain = 0.0
        self._r_oi = (0,)
        self._image = ((0,),)
        # PROTECTED REGION ID(ThorlabsC.init_device) ENABLED START #
        self.info_stream("\r Try to start the Thorlabs Driver \r")
        print(self.CameraID)
        available_cameras = self.sdk.discover_available_cameras()
        if len(available_cameras) > 1:
            self.ConnectCamera()
        else:
            msg = "No Camera connected!!"
            self.info_stream(msg)
            print(msg)
            self.set_state(DevState.FAULT)

        
        # PROTECTED REGION END #    //  ThorlabsC.init_device

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(ThorlabsC.always_executed_hook) ENABLED START #
        # PROTECTED REGION END #    //  ThorlabsC.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(ThorlabsC.delete_device) ENABLED START #
        self.CAM.disarm()
        # PROTECTED REGION END #    //  ThorlabsC.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_ExposureTime(self):
        # PROTECTED REGION ID(ThorlabsC.ExposureTime_read) ENABLED START #
        """Return the ExposureTime attribute."""
        return self._exposure_time
        # PROTECTED REGION END #    //  ThorlabsC.ExposureTime_read
    def write_ExposureTime(self, value):
        # PROTECTED REGION ID(ThorlabsC.ExposureTime_write) ENABLED START #
        """Set the ExposureTime attribute."""
        pass
        # PROTECTED REGION END #    //  ThorlabsC.ExposureTime_write
    def read_Gain(self):
        # PROTECTED REGION ID(ThorlabsC.Gain_read) ENABLED START #
        """Return the Gain attribute."""
        return self._gain
        # PROTECTED REGION END #    //  ThorlabsC.Gain_read
    def write_Gain(self, value):
        # PROTECTED REGION ID(ThorlabsC.Gain_write) ENABLED START #
        """Set the Gain attribute."""
        pass
        # PROTECTED REGION END #    //  ThorlabsC.Gain_write
    def read_ROI(self):
        # PROTECTED REGION ID(ThorlabsC.ROI_read) ENABLED START #
        """Return the ROI attribute."""
        return self._r_oi
        # PROTECTED REGION END #    //  ThorlabsC.ROI_read
    def write_ROI(self, value):
        # PROTECTED REGION ID(ThorlabsC.ROI_write) ENABLED START #
        """Set the ROI attribute."""
        pass
        # PROTECTED REGION END #    //  ThorlabsC.ROI_write
    def read_Image(self):
        # PROTECTED REGION ID(ThorlabsC.Image_read) ENABLED START #
        """Return the Image attribute."""
        return self._image
        # PROTECTED REGION END #    //  ThorlabsC.Image_read
    # --------
    # Commands
    # --------


    @command(
        dtype_out='DevString',
    )
    @DebugIt()
    def StartAcqusition(self):
        # PROTECTED REGION ID(ThorlabsC.StartAcqusition) ENABLED START #
        """
        This command start the loop of acquiring a image from the camera
        :rtype: PyTango.DevString
        """
        global stop_threads               
        stop_threads = False
        self.my_thread = Thread(target = self.get_image)
        
        self.set_state(DevState.RUNNING)
        self.my_thread.start()
        # self.set_state(DevState.ON)
        
        return ""
        # PROTECTED REGION END #    //  ThorlabsC.StartAcqusition

    @command(
        dtype_in='DevString',
        doc_in="A JSON converted in to a string with the following structure",
    )
    @DebugIt()
    def ChangeParameters(self, argin):
        # PROTECTED REGION ID(ThorlabsC.ChangeParameters) ENABLED START #
        """
            This command allows the user to change multiple parameters of the camera at the same time such as:
            Exposure Time
            ROI
            Gain
        :param argin: A JSON converted in to a string with the following structure
        :type argin: PyTango.DevString

        :rtype: PyTango.DevVoid
        """
        pass
        # PROTECTED REGION END #    //  ThorlabsC.ChangeParameters

    @command(
    )
    @DebugIt()
    def StopAcqusition(self):
        # PROTECTED REGION ID(ThorlabsC.StopAcqusition) ENABLED START #
        """
        Stops the loop that takes images
        :rtype: PyTango.DevVoid
        """
        global stop_threads               
        stop_threads = True
        try:
            self.my_thread.join()
            self.set_state(DevState.ON)
        except:
            print("Cloud not join the theard maybe none exist.")
        # self.set_state(DevState.OFF)

        pass
        # PROTECTED REGION END #    //  ThorlabsC.StopAcqusition

    @command(
    )
    @DebugIt()
    def Snap(self):
        # PROTECTED REGION ID(ThorlabsC.Snap) ENABLED START #
        """
        Takes a image and send it to the user
        :rtype: PyTango.DevVoid
        """
        global stop_threads
        if stop_threads:
            self.get_image()
        else:
            print("It is on the Acqusition mode")
        pass
        # PROTECTED REGION END #    //  ThorlabsC.Snap

# ----------
# Run server
# ----------

# PROTECTED REGION ID(ThorlabsC.custom_code) ENABLED START #
    def get_image(self):
        while True:
            # self._image = np.random.randint(1000, size=(100, 100))
            NUM_FRAMES = 1  # adjust to the desired number of frames     

            self.CAM.issue_software_trigger()

            for i in range(NUM_FRAMES):
                frame = self.CAM.get_pending_frame_or_null()
                if frame is not None:
                    # print("frame #{} received!".format(frame.frame_count))

                    frame.image_buffer  # .../ perform operations using the data from image_buffer

                    #  NOTE: frame.image_buffer is a temporary memory buffer that may be overwritten during the next call
                    #        to get_pending_frame_or_null. The following line makes a deep copy of the image data:
                    # image_buffer_copy = np.copy(frame.image_buffer)
                    self._image = np.array(frame.image_buffer,dtype = np.uint16)
                else:
                    print("timeout reached during polling, program exiting...")
            global stop_threads
            if stop_threads:
                break


    def ConnectCamera(self):
        try:
            self.CAM = self.sdk.open_camera(str(self.CameraID)) 
            self.CAM.exposure_time_us = 1100  # set exposure to 1.1 ms
            self.CAM.frames_per_trigger_zero_for_unlimited = 0  # start camera in continuous mode
            self.CAM.image_poll_timeout_ms = 500  # 1 second polling timeout
            #old_roi = CAMS.roi  # store the current roi
            self.CAM.arm(2)
            self.set_status("Thorlabs CAMS Driver is ON")
            self.set_state(DevState.ON)
        except:
            self.info_stream("The camera "+str(self.CameraID))
            try:
                available_cameras = self.sdk.discover_available_cameras()
            except:
                available_cameras = None
            self.info_stream("Camera detected: ")
            for i in available_cameras:
                self.info_stream(i)
# PROTECTED REGION END #    //  ThorlabsC.custom_code


def main(args=None, **kwargs):
    """Main function of the ThorlabsC module."""
    # PROTECTED REGION ID(ThorlabsC.main) ENABLED START #
    return run((ThorlabsC,), args=args, **kwargs)
    # PROTECTED REGION END #    //  ThorlabsC.main

# PROTECTED REGION ID(ThorlabsC.custom_functions) ENABLED START #
# PROTECTED REGION END #    //  ThorlabsC.custom_functions


if __name__ == '__main__':
    main()
