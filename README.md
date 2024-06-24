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
- [GetPhotoJSON](###GetPhotoJSON)

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
import matplotlib.pyplot as plt
Thorlabs_Camera = tango.DeviceProxy(<Thorlabs_Tango_location_on_the_database>)
print(Thorlabs_Camera.state())
# Change this time out if need
Thorlabs_Camera.set_timeout_millis(9000) 

# This function returns a list with all the command aviable on the device server
Thorlabs_Camera.get_command_list()
#['list_cameras', 'set_roi', 'set_gain', 'set_image_poll_timeout_ms']

Image = Thorlabs_Camera.Image_foto
plt.imshow(Image)
```
