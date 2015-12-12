## Pirate Maps

Procedurally generated pirate treasure maps. X marks the spot!

![Example](http://i.imgur.com/9c0RMuj.png)

### Dependencies

I used several excellent third party libraries...

- `cairo` for rendering
- `colour` for color interpolation
- `noise` for simplex noise
- `Pillow` for saving debug images of noise layers
- `pyhull` for delaunay triangulation
- `Shapely` for all kinds of 2D geometry operations

### How to Run

The script will generate several random maps and save them as PNG files.

    git clone https://github.com/fogleman/PirateMap.git
    cd PirateMap
    pip install -r requirements.txt
    python main.py
