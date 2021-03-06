# convert a shapefile to a raster bumpmap based on a shp attribute
# note: shapely is a thing that exists and you should probably use that
# instead of pyshp
import shapefile
import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import sys
from optparse import OptionParser

def load_shapefile(filename):
    return shapefile.Reader(filename)

def interpolate(value, dr):
    # linear interpolation
    d = dr['domain']
    r = dr['range']
    domain_delta = d[1]-d[0]
    if domain_delta == 0: return r[0]
    return r[0] + ((value-d[0])/domain_delta) * (r[1]-r[0])

def draw_heightmap(channels):

    # lng_min, lat_min, lng_max, lat_max = shp.bbox
    lng_min, lat_max, lng_max, lat_min = shp.bbox
    shapes = shp.shapeRecords()

    width = options.size
    # make height proportional to width
    # NOTE: this only semi-works with WGS84 bc of a near-1:1 grid scale, otherwise we'd need to project
    w_diff = abs(lng_max - lng_min)
    h_diff = abs(lat_max - lat_min)
    height = int(h_diff / w_diff * width)
    if height > width:
        width = int(w_diff / h_diff * width)
        height = options.size
    # arguments for the linear interpolation function:
    x = {'domain': [lng_min, lng_max], 'range': [0, width ]}
    y = {'domain': [lat_min, lat_max], 'range': [0, height]}

    # all values for selected attributes (unless the channel is empty (None))
    heights = [[shape.record[col] for shape in shapes] if col else None for col in channels]
    # arguments for linear interpolation (one for each channel)
    # FIXME should figure out a faster way to bail to range[0] when the domain delta == 0
    fills = [{'domain': [min(h), max(h)], 'range': [1, 255]} if h else None for h in heights] 
    
    im = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(im)

    for shape in shapes:
        # do a linear interpolation of lnglats to fit inside our drawing frame
        points = [(interpolate(lng, x), interpolate(lat, y)) for (lng, lat) in shape.shape.points]

        channel_heights = [
            int(interpolate(shape.record[col], fills[i])) if col else 0 
            for (i, col) in enumerate(channels)
        ]
        color = tuple(channel_heights)

        draw.polygon(points, fill=color)
        # draw.line(points, fill=color)

    del draw

    im.save(options.outfile, options.ext)

if __name__ == '__main__':

    # command-line options
    class CustomParser(OptionParser):
        def format_epilog(self, formatter):
            return self.epilog

    epilog = '\n'.join([
        '',
        'Channels Usage:',
        '  you must define a shapefile attribute for each r,g,b color channel.',
        '  leave placeholders for unused channels.',
        '',
        '  ex: --rgb=attr1,attr2,attr3 (all three channels)',
        '      --rgb=attr1,, (red)',
        '      --rgb=,attr2, (green)',
        '      --rgb=,,attr3 (blue)',
        ''
        'NOTE: the shapefile attribute must be NUMERIC',
        ''
    ])

    parser = CustomParser('Usage: %prog -f filename --rgb=attr1,attr2,attr3 [options]', epilog=epilog)
    add_option = parser.add_option

    add_option('--rgb',
               dest='channels', type='str',
               help='one attribute per channel (r,g,b -> attr1,attr2,attr3)')
    add_option('-f', '--filename', 
               dest='filename',
               help='shapefile to convert (omit extension)')
    add_option('-o', '--out',
               dest='outfile', default=sys.stdout,
               help='outfile name (defaults to stdout)')
    add_option('-s', '--size',
               dest='size', default=2048, type='int',
               help='max output dimension. width/height will scale proportionally. (defaults to 2048)')
    add_option('-e', '--extension',
               dest='ext', default='PNG',
               help='output file type (defaults to PNG)')
    add_option('-c', '--show_columns',
               action='store_true',
               dest='show_columns', default=False,
               help='show attributes and exit')

    (options, args) = parser.parse_args()

    # load shapefile
    shp = load_shapefile(options.filename)

    columns = {col[0]: i for (i, col) in enumerate(shp.fields[1:])}

    if options.show_columns:
        for col in columns: print col

    else:
        if not options.channels:
            parser.error('missing channels')
        if not options.filename:
            parser.error('no input file specified')

        channels = [columns[c] if (c and c in columns) else None for c in options.channels.split(',')[:3]]
        valid_channels = filter(None, channels)

        # if no user-defined attributes matched the shapefile, we can't build a heightmap
        if not valid_channels:
            parser.error('no matching attributes found')

        draw_heightmap(channels)
    
    sys.exit()


