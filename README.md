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

### How it Works

It took me a while to decide on an approach for generating the land masses. I didn't want to just generate some simplex noise, threshold it and render it. I wanted to actually compute a polygonal shape that I could do further operations on. So here's how that works...

- generate a layer of simplex noise with several octaves, with decreasing values as the edge of the image is approached
- fill the screen with randomly positioned points evenly spaced using the poisson disc algorithm
- filter the poisson points to those where the corresponding noise value is above some threshold
- take these points and compute a "concave" hull or alpha shape with them

Shapely's `buffer` function is used heavily for padding or cleaning up shapes.

I also wrote an `xkcdify` function to add some perturbations to some of the polygons, namely the different water color gradations.
