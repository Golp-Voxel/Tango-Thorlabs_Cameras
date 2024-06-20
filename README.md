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

``` python
ListCameras()
```
This command will list all the Cameras connected to the PC.

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
    "poll_timeout_ms":500,
}
```

``` python
SetRoi(parameterArray)
```

``` python
SetGain(gain)
```

``` python
SetExpousureTimeUS(timeUS)
```

``` python
SetFramesPerTriggerZeroForUnlimited(continuousMode)
```

``` python
SetImagePollTimeoutMS(imagePollTimeout)
```

``` python
GetLocalPhoto(photoName)
```

``` python
GetPhotoJSON()
```

## Avaible Attributes

```
Image_Photo
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
