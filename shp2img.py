# convert a shapefile to a raster bumpmap based on a shp attribute
# note: shapely is a thing that exists and you should probably use that
# instead of pyshp
import shapefile
import Image, ImageDraw
import sys
from optparse import OptionParser

# command-line options
parser = OptionParser()
parser.add_option('-f', '--filename', dest='filename',
                  default='shp/footprints',
                  help='shapefile to convert (omit extension)')
parser.add_option('-o', '--out',
                  dest='outfile', default=sys.stdout,
                  help='png outfile (defaults to stdout)')
parser.add_option('-s', '--show_columns',
                  action='store_true',
                  dest='show_columns', default=False,
                  help='show attribute column indices/headers and exit')
parser.add_option('-c', '--column',
                  dest='column', type='int',
                  help='selected attribute\'s column index')
parser.add_option('-w', '--width',
                  dest='width', default=2048, type='int',
                  help='output width (height will scale proportionally)')
parser.add_option('-e', '--extension',
                  dest='ext', default='PNG',
                  help='output file type (defaults to PNG)')
parser.add_option('-b', '--sf_buildings',
                  action='store_true',
                  dest='buildings', default=False,
                  help='for use with the sf building footprints data')
(options, args) = parser.parse_args()


# shp_filename = 'shp/mars_merc_3dia_g'
sf = shapefile.Reader(options.filename)

# COLUMNS
# XXX FIX: for building heights, you're going to need z_min+(z_max-z_min)
# which should place the vertex where it needs to go wrt terrain elevation (elev + height)
z_min = 38
z_max = 39
minheight = 10
maxheight = 11
hmin = z_min
hmax = z_max
#col = 2   # MARS contours!

def calc_height(record):
    # calculate height
    #return record[hmin] + (record[hmax]-record[hmin])
    return record[hmax] - record[hmin]

def interpolate(value, dr):
    # linear interpolation
    d = dr['domain']
    r = dr['range']
    return r[0] + ((value-d[0])/(d[1]-d[0])) * (r[1]-r[0])

def draw_heightmap(column):
    
    bbox = sf.bbox
    shapes = sf.shapeRecords()

    width = options.width
    # make height proportional to original width
    w_diff = bbox[2] - bbox[0]
    h_diff = bbox[3] - bbox[1]
    height = int(h_diff / w_diff * width)
    # arguments for the linear interpolation function:
    x_args = {'domain': [bbox[0], bbox[2]], 'range': [0, width ]}
    y_args = {'domain': [bbox[1], bbox[3]], 'range': [height, 0]}

    # map heights to a range of 2-255 (red value)
    if (options.buildings):
        heights = [calc_height(shape.record) for shape in shapes]
    else:
        heights = [shape.record[column] for shape in shapes]
    
    fill = {'domain': [min(heights), max(heights)], 'range': [2, 255]}

    im = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(im)

    for shape in shapes:
        if (options.buildings):
            height = calc_height(shape.record)
        else:
            height = shape.record[column]
        # do a linear interpolation of lnglats to fit inside our drawing frame
        #                       tuples for draw.polygon
        points = map(
                     lambda (lng, lat): 
                        tuple([
                              interpolate(lng, x_args), 
                              interpolate(lat, y_args)
                        ]), 
                        shape.shape.points
        )
        draw.polygon(points, fill=int(interpolate(height, fill)))
        # draw.line(points, fill=int(li(height, fill)))

    del draw

    im.save(options.outfile, options.ext)

if __name__ == '__main__':
    if (options.show_columns):
        for (i,e) in enumerate(sf.fields[1:]): 
            print i, ':', e
        sys.exit()
    else:
        draw_heightmap(options.column)
        sys.exit()


