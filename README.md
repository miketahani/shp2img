### what?

ultra-hacky one-off to generate multi-channel heightmaps from shapefiles using 1-3 attributes. 
useful for creating heightmaps for shaders (3d/glsl). mostly a way for me to learn how to use 
PIL and read shapefiles.

### requirements
requires pyshp (`easy_install pyshp`) and PIL

### usage

    Usage: shp2img.py --rgb=attr1,attr2,attr3 [options]

    Options:
      -h, --help            show this help message and exit
      --rgb=CHANNELS        one attribute per channel (r,g,b -> attr1,attr2,attr3)
      -f FILENAME, --filename=FILENAME
                            shapefile to convert (omit extension)
      -o OUTFILE, --out=OUTFILE
                            outfile name (defaults to stdout)
      -w WIDTH, --width=WIDTH
                            output width (height will scale proportionally)
      -e EXT, --extension=EXT
                            output file type (defaults to PNG)
      -s, --show_columns    show attributes and exit

    Channels Usage:
      you must define a shapefile attribute per r,g,b color channel.
      leave placeholders for unused channels.

      ex: --rgb=attr1,attr2,attr3 (all three channels)
          --rgb=attr1,, (red)
          --rgb=,attr2, (green)
          --rgb=,,attr3 (blue)