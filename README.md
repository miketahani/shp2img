![sf building footprints data](https://raw.github.com/miketahani/shp2img/master/example_output.png)

### Description

An ultra-hacky one-off to generate multi-channel heightmaps from shapefiles using 1-3 attributes. 
Useful for creating heightmaps for GL shaders. Mostly a way for me to learn how to use 
PIL and read shapefiles.

Currently only works with WGS84-projected shapefiles that contain polygons.

### Requirements
Requires pyshp (`easy_install pyshp`) and PIL.

### Usage


    Usage: shp2img.py -f filename --rgb=attr1,attr2,attr3 [options]

    Options:
      -h, --help            show this help message and exit
      --rgb=CHANNELS        one attribute per channel (r,g,b -> attr1,attr2,attr3)
      -f FILENAME, --filename=FILENAME
                            shapefile to convert (omit extension)
      -o OUTFILE, --out=OUTFILE
                            outfile name (defaults to stdout)
      -s SIZE, --size=SIZE  max output dimension. width/height will scale
                            proportionally. (defaults to 2048)
      -e EXT, --extension=EXT
                            output file type (defaults to PNG)
      -c, --show_columns    show attributes and exit

    Channels Usage:
      you must define a shapefile attribute for each r,g,b color channel.
      leave placeholders for unused channels.

      ex: --rgb=attr1,attr2,attr3 (all three channels)
          --rgb=attr1,, (red)
          --rgb=,attr2, (green)
          --rgb=,,attr3 (blue)
