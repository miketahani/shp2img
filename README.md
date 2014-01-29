ultra-hacky one-off to generate heightmaps from shapefiles. useful for creating
heightmaps for use in shaders (3d/glsl). mostly a way for me to learn how to use 
PIL and read shapefiles.

requires pyshp (`easy_install pyshp`) and PIL

Usage: shp2img.py [options]

Options:
  -h, --help            show this help message and exit
  -f FILENAME, --filename=FILENAME
                        shapefile to convert (omit extension)
  -o OUTFILE, --out=OUTFILE
                        png outfile (defaults to stdout)
  -s, --show_columns    show attribute column indices/headers and exit
  -c COLUMN, --column=COLUMN
                        selected attribute's column index
  -w WIDTH, --width=WIDTH
                        output width (height will scale proportionally)
  -e EXT, --extension=EXT
                        output file type (defaults to PNG)
  -b, --sf_buildings    for use with the sf building footprints data