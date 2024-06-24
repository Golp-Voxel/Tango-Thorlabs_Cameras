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

To complete the installation, it is necessary to copy the `ThorlabsC.bat` template and change the paths to the installation folder. And the command to run the `tango-env\Scripts\activate` script. 

Then copy the `setting.ini` template and fill in the path to the dlls for the Thorlabs.




## Available commands
- [ListCameras](#ListCameras)
- [ConnectCamera](#ConnectCamera)
- [SetRoi](#SetRoi)
- [SetGain](#SetGain)
- [SetExpousureTimeUS](#SetExpousureTimeUS)
- [SetFramesPerTriggerZeroForUnlimited](#SetFramesPerTriggerZeroForUnlimited)
- [SetImagePollTimeoutMS](#SetImagePollTimeoutMS)
- [GetPhotoJSON](#GetPhotoJSON)

### ListCameras

``` python
ListCameras()
```
This command will list all the Cameras connected to the PC.

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

``` python
SetGain(gain)
```

```
ROI = {"CamName":<user choice>,
       "gain": 5.5}
```

### SetExpousureTimeUS

``` python
SetExpousureTimeUS(timeUS)
```

### SetFramesPerTriggerZeroForUnlimited

``` python
SetFramesPerTriggerZeroForUnlimited(continuousMode)
```

### SetImagePollTimeoutMS


``` python
SetImagePollTimeoutMS(imagePollTimeout)
```

### GetPhotoJSON

``` python
GetPhotoJSON(CamName)
```

## Avaible Attributes

```
'Cam_1', 'Cam_2', 'Cam_3', 'Cam_4'
```

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
camara_device.get_command_list()
# Result = ['ConnectCamera', 'GetPhotoJSON', 'ListCameras', 'SetExpousureTimeUS', 'SetFramesPerTriggerZeroForUnlimited', 'SetGain', 'SetImagePollTimeoutMS', 'SetRoi']

# This function list all the cameras connected to the PC
camara_device.ListCameras() 

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
J = camara_device.GetPhotoJSON("C1")
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
camara_device.SetRoi(string_roi)

# Collect a Image from Camera "C1"
J = camara_device.GetPhotoJSON("C1")
nd_image_array = json.loads(J)

array_p = np.array(nd_image_array["Image"])
plt.imshow(array_p)
```
