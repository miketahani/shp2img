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
parser.add_option('-g', '--greyscale',
                  action='store_true',
                  dest='greyscale', default=False,
                  help='greyscale heightmap')
(options, args) = parser.parse_args()



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
    
    lng_min, lat_min, lng_max, lat_max = sf.bbox
    shapes = sf.shapeRecords()

    width = options.width
    # make height proportional to width
    w_diff = lng_max - lng_min
    h_diff = lat_max - lat_min
    height = int(h_diff / w_diff * width)
    # arguments for the linear interpolation function:
    x = {'domain': [lng_min, lng_max], 'range': [0, width ]}
    y = {'domain': [lat_min, lat_max], 'range': [height, 0]}

    # map heights to a range of 2-255 (red value)
    # leaves green and blue channels open for other data
    if (options.buildings):
        heights = [calc_height(shape.record) for shape in shapes]
    else:
        heights = [shape.record[column] for shape in shapes]
    
    fill = {'domain': [min(heights), max(heights)], 'range': [2, 255]}

    im = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(im)

    for shape in shapes:
        # do a linear interpolation of lnglats to fit inside our drawing frame
        points = [
            tuple([
                  interpolate(lng, x), 
                  interpolate(lat, y)
            ]) 
            for (lng, lat) in shape.shape.points
        ]

        if (options.buildings):
            height = calc_height(shape.record)
        else:
            height = shape.record[column]

        color = int(interpolate(height, fill))
        if (options.greyscale): color = tuple([color]*3)
        
        draw.polygon(points, fill=color)
        # draw.line(points, fill=color)

    del draw

    im.save(options.outfile, options.ext)

if __name__ == '__main__':

    # load shapefile
    sf = shapefile.Reader(options.filename)

    if (options.show_columns):
        for (i,e) in enumerate(sf.fields[1:]): 
            print i, ':', e
        sys.exit()
    else:
        draw_heightmap(options.column)
        sys.exit()


