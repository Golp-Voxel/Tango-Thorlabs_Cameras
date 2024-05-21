# Thorlabs Cam - Tango Device Server



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
