# Formpix Module
For interacting with a formPix instance easily.

## Install in Python project
```bash
pip install formpix
```

## Example script
```python
import formpix

formpix.login(
    "ADDRESS OF FORMPIX INSTANCE HERE, NO '/'... ",
    "GET AN API KEY FROM THE FORMBAR INSTANCE THE FORMPIX IS CONNECTED TO"
)

formpix.fill('#ff0000', 0, 10)
```

## Methods

```python
# Connect to formpix
formpix.login(formpixURL, formbarAPIkey)

# Fill length of bar with color
formpix.fill(color, start, length)

# Fill length of bar with two color gradient
formpix.gradient(start_color, end_color, start, length)

# Set a single pixel to a color
formpix.set_pixel(location, color)

# Set an array of pixels (as pixel objects)
# { "pixel_number": integer, "color": #hexcolor }
formpix.set_pixels(pixels)

# Display text on the board extension
formpix.say(text, color, bgcolor)

# Get a list of 'bgm' or 'sfx' on the formpix
# type is 'bgm' or 'sfx'
formpix.get_sounds(type)

# Play a bgm or sound on the formpix
# Use 'None' for the parameter you don't want to use
formpix.play_sound(sfx, bgm)
```