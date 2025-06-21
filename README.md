# Thorlabs Cam - Tango Device Server

After cloning this repository with the following command

```
git clone https://github.com/Golp-Voxel/Tango_Thorlabs.git
```

It is necessary to create the `tango-env` using the following command:

```
python -m venv tango-env
```

After activating it you can install all the models to run this tool by using the command:

```
pip install -r Requirements.txt
```

To complete the installation, it is necessary to copy the `ThorlabsC.bat` template and change the paths to the installation folder. And the command to activate the env created `tango-env\Scripts\activate`.

Also you need to dowload the `thoirlabs_tsi_sdk` folder from [here](https://www.thorlabs.com/software/THO/ThorCam/Programming/Scientific_Camera_Interfaces_Windows-2.1.zip) you will find a zip named `thorlabs_tsi_camera_python_sdk_package` in the folder `Scientific Camera Interfaces\SDK\Python Toolkit` inside that zip you will find the folder `thoirlabs_tsi_sdk` move it to the root of the repo.

For the `Native_64_lib` you must copy the `setting.ini.temp` and remove the `.temp`. In that `ini` is where you can specify where is your `Native_64_lib` this can be extrated from the same zip above in the `Scientific Camera Interfaces\SDK\Native Toolkit\dlls` you could copy the folder `Native_64_lib` to the root of the clone. Other option is finding where your `ThorCams` is and pasting the path to it, normaly you can find it in `C:\Program Files\Thorlabs\Scientific Imaging\ThorCam`.
 Just remember to change the `\` to `//`.


Then copy the `setting.ini` template and fill in the path to the dlls for the Thorlabs.


If you get an error of the module `ftdxxx` it is solved by:
```
pip uninstall pyft232
```



## Available commands
- [ListCameras](#ListCameras)
- [ConnectCamera](#ConnectCamera)
- [SetRoi](#SetRoi)
- [SetGain](#SetGain)
- [SetExpousureTimeUS](#SetExpousureTimeUS)
- [SetFramesPerTriggerZeroForUnlimited](#SetFramesPerTriggerZeroForUnlimited)
- [SetImagePollTimeoutMS](#SetImagePollTimeoutMS)
- [GetPhotoJSON](#GetPhotoJSON)
- [DisconnectCam](#DisconnectCam)

### ListCameras

This command will list all the Cameras connected to the PC.
``` python
ListCameras()
```

Returning the ID of the camera such as: '17946'(`<listCameras info>`),

### ConnectCamera

```python
ConnectCamera(infoCamera)
```
To connect a Camera the user need to send a string with the following information:
```
{
    "Cam":<listCameras info>,
    "CamName":<user choice>,
    "exposure_us":1100,
    "frames_per_trigger":0,
    "poll_timeout_ms":500
}
```

### SetRoi

Region of Interest used by the camera. ROI is represented by two (x, y) coordinates that specify
an upper left coordinate and a lower right coordinate.

``` python
SetRoi(ROI)
```

```
ROI = {"CamName":<user choice>,
       "upper_left_x_pixels": 0,
       "upper_left_y_pixels": 0,
       "lower_right_x_pixels":1400, 
       "lower_right_y_pixels":1400}
```


### SetGain

Gain refers to the scaling of pixel values up or down for a given amount of light. This scaling is applied prior to digitization. The units of measure for Gain can vary by camera. Please consult the data sheet for the specific camera model.

``` python
SetGain(gain)
```

```
ROI = {"CamName":<user choice>,
       "gain": 5.5}
```

### SetExpousureTimeUS

The time, in microseconds (us), that charge is integrated on the image sensor.
To convert milliseconds to microseconds, multiply the milliseconds by 1,000. To convert microseconds to milliseconds, divide the microseconds by 1,000.

IMPORTANT: After issuing a software trigger, it is recommended to wait at least 300ms before setting

``` python
SetExposureTimeUS(timeUS)
```

```
timeUS = {"CamName":<user choice>,
       "exposure_time_us": 5.5}
```


### SetFramesPerTriggerZeroForUnlimited


The number of frames generated per software or hardware trigger can be unlimited or finite. If set to zero, the camera will self-trigger indefinitely, allowing a continuous video feed. If set to one or higher, a single software or hardware trigger will generate only the prescribed number of frames and then stop.

``` python
SetFramesPerTriggerZeroForUnlimited(continuousMode)
```

```
continuousMode = {"CamName":<user choice>,
       "continuousMode": 0}
```

### SetImagePollTimeoutMS

If the SDK could not get an image within the timeout, None will be returned instead.

``` python
SetImagePollTimeoutMS(imagePollTimeout)
```


```
imagePollTimeout = {"CamName":<user choice>,
       "imagePollTimeout": 500}
```

### GetPhotoJSON
Polls the camera for an image. This method will block for at most image_poll_timeout milliseconds.
The Frame that is retrieved will have an image_buffer field to access the pixel data.


``` python
GetPhotoJSON(CamName)
```

CamName is a single string with the same name passed on the [ConnectCamera](#ConnectCamera) function.


This function returns a JSON where the image will be in the key "Image", so to get the image you can use the following code:

``` python
nd_image_array = json.loads(GetPhotoJSON(CamName))
array_p = np.array(nd_image_array["Image"])
plt.imshow(array_p)
```
### DisconnectCam

Disconnects the Thorlabs Camera.

``` python
DisconnectCam(CamName)
```
CamName is a single string with the same name passed on the [ConnectCamera](#ConnectCamera) function.


## Exemple of Tango Client code to take a photo
```python
import tango
import json
import matplotlib.pyplot as plt
Thorlabs_Camera = tango.DeviceProxy(<Thorlabs_Tango_location_on_the_database>)
print(Thorlabs_Camera.state())
# Change this time out if need
Thorlabs_Camera.set_timeout_millis(9000) 

# This function returns a list with all the command aviable on the device server
Thorlabs_Camera.get_command_list()
# Result = ['ConnectCamera', 'GetPhotoJSON', 'ListCameras', 'SetExpousureTimeUS', 'SetFramesPerTriggerZeroForUnlimited', 'SetGain', 'SetImagePollTimeoutMS', 'SetRoi']

# This function list all the cameras connected to the PC
Thorlabs_Camera.ListCameras() 

# Change the "Cam" to the ID that you want to connect to
# The "CamName" can be change to any name that the user wants and this will be use to identify.
JSON_CAM = {"Cam":"17946",
            "CamName":"C1",
            "exposure_us":1100,
            "frames_per_trigger":0,
            "poll_timeout_ms":500}

string_cam = json.dumps(JSON_CAM)

Thorlabs_Camera.ConnectCamera(string_cam)

# Collect a Image from Camera "C1"
J = Thorlabs_Camera.GetPhotoJSON("C1")
nd_image_array = json.loads(J)

array_p = np.array(nd_image_array["Image"])
plt.imshow(array_p)


#Change the ROI of the "C1"
ROI_ = {"CamName":"C1",
            "upper_left_x_pixels": 0,
            "upper_left_y_pixels": 0,
            "lower_right_x_pixels":1400, 
            "lower_right_y_pixels":1400}

string_roi = json.dumps(ROI_)
# print(JSON_CAM)
Thorlabs_Camera.SetRoi(string_roi)

# Collect a Image from Camera "C1"
J = Thorlabs_Camera.GetPhotoJSON("C1")
nd_image_array = json.loads(J)

array_p = np.array(nd_image_array["Image"])
plt.imshow(array_p)
```


# References

- [ThorCam™ Software for Scientific and Compact USB Cameras](https://www.thorlabs.com/software_pages/ViewSoftwarePage.cfm?Code=ThorCam)