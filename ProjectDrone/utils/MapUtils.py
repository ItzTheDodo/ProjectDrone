from math import pi, log, tan, exp, atan, log2, floor
import urllib.request
from PIL import Image
import io
import geocoder
import os


class MapGen:

    def __init__(self, runtime, long, lat, width, height, bbox=None, zoom=10, token="pk.eyJ1IjoiaXR6dGhlZG9kbyIsImEiOiJja21naGV2c2UyODh0Mm9xbGVpYWNoajZlIn0.IexDbEd-Xq2clktGwciO-Q"):

        self.runtime = runtime
        self.lat = lat
        self.long = long
        self.zoom0 = 512
        self.zoom = zoom
        self.token = token
        self.bbox = bbox
        self.width = width
        self.height = height
        self.latest = None

    def getZoom(self):
        return self.zoom

    def setZoom(self, z):
        self.zoom = z

    def getLatitude(self):
        return self.lat

    def getLongatude(self):
        return self.long

    def setLatitude(self, lat):
        self.lat = lat

    def setLongatude(self, long):
        self.long = long

    def _g2p(self, lat, long, zoom):
        return (
            # x
            self.zoom0 * (2 ** zoom) * (1 + long / 180) / 2,
            # y
            self.zoom0 / (2 * pi) * (2 ** zoom) * (pi - log(tan(pi / 4 * (1 + lat / 90))))
        )

    # pixel to geo
    def _p2g(self, x, y, zoom):
        return (
            # lat
            (atan(exp(pi - y / self.zoom0 * (2 * pi) / (2 ** zoom))) / pi * 4 - 1) * 90,
            # lon
            (x / self.zoom0 * 2 / (2 ** zoom) - 1) * 180,
        )

    def getMapByBbox(self, bbox):
        TOP, LEFT, BOTTOM, RIGHT, z = None, None, None, None, None
        (left, bottom, right, top) = bbox

        assert(-90 <= bottom < top <= 90)
        assert(-180 <= left < right <= 180)

        (w, h) = (self.width, self.height)
        (lat, lon) = ((top + bottom) / 2, (left + right / 2))
        snap_dyad = (lambda a, b: (lambda x, scale=(2 ** floor(log2(abs(b - a) / 4))): (round(x / scale) * scale)))
        lat = snap_dyad(bottom, top)(lat)
        lon = snap_dyad(left, right)(lon)

        for zoom in range(16, 0, -1):
            (x0, y0) = self._g2p(lat, lon, zoom)
            (TOP, LEFT) = self._p2g(x0 - w / 2, y0 - h / 2, zoom)
            (BOTTOM, RIGHT) = self._p2g(x0 + w / 2, y0 + h / 2, zoom)

            if LEFT <= left < right <= RIGHT:
                if BOTTOM <= bottom < top <= TOP:
                    break
            z = zoom

        params = {
            'style': "streets-v10",
            'lat': lat,
            'lon': lon,
            'token': self.token,
            'zoom': z,
            'w': w,
            'h': h,
            'retina': "@2x",
        }
        url_template = "https://api.mapbox.com/styles/v1/mapbox/{style}/static/{lon},{lat},{zoom}/{w}x{h}{retina}?access_token={token}&attribution=false&logo=false"
        url = url_template.format(**params)

        with urllib.request.urlopen(url) as res:
            img = Image.open(io.BytesIO(res.read()))
        (W, H) = img.size
        assert((W, H) in [(w, h), (2 * w, 2 * h)])

        cur_img = img.crop((round(W * (left - LEFT) / (RIGHT - LEFT)), round(H * (top - TOP) / (BOTTOM - TOP)), round(W * (right - LEFT) / (RIGHT - LEFT)), round(H * (bottom - TOP) / (BOTTOM - TOP)),))
        self.latest = cur_img
        return cur_img

    def getMap(self):
        params = {
            'style': "streets-v10",
            'lat': self.lat,
            'lon': self.long,
            'token': self.token,
            'zoom': self.zoom,
            'w': self.width,
            'h': self.height,
            'retina': "@2x",
        }
        url_template = "https://api.mapbox.com/styles/v1/mapbox/{style}/static/{lon},{lat},{zoom}/{w}x{h}{retina}?access_token={token}&attribution=false&logo=false"
        url = url_template.format(**params)
        with urllib.request.urlopen(url) as res:
            img = Image.open(io.BytesIO(res.read()))
        self.latest = img
        return img

    def getLatestMapImg(self):
        return self.latest

    def getCurrentClientLocation(self):
        loc = geocoder.ip("me").latlng
        if loc is None:
            raise Exception("Not connected to Internet..")
        return loc

    def saveLatest(self, name="map_item_%s"):
        high = 0
        tempname = name.split("_")[:len(name.split("_")) - 1]
        cur_name = ""
        for x in tempname:
            cur_name += x + "_"
        for i in os.listdir(self.runtime.DATAFOLDER.getImgItemsFolder()):
            if os.path.isfile(os.path.join(self.runtime.DATAFOLDER.getImgItemsFolder(), i)) and str(i.split(".")[0]).__contains__(cur_name):
                cur_lev = int(str(i.split(".")[0]).split("_")[2])
                if cur_lev >= high:
                    high = cur_lev + 1
        name = os.path.join(self.runtime.DATAFOLDER.getImgItemsFolder(), name % str(high))
        self.latest.save("%s.png" % name, "PNG")


def get_current_client_location_latlng():
    return geocoder.ip("me").latlng


def latlongtometersppix(lat, zoom):
    conversion_table = {
        0: {0: 78271.484, 20: 73551.136, 40: 59959.436, 60: 39135.742, 80: 13591.701},
        1: {0: 39135.742, 20: 36775.568, 40: 29979.718, 60: 19567.871, 80: 6795.850},
        2: {0: 19567.871, 20: 18387.784, 40: 14989.859, 60: 9783.936, 80: 3397.925},
        3: {0: 9783.936, 20: 9193.892, 40: 7494.929, 60: 4891.968, 80: 1698.963},
        4: {0: 4891.968, 20: 4596.946, 40: 3747.465, 60: 2445.984, 80: 849.481},
        5: {0: 2445.984, 20: 2298.473, 40: 1873.732, 60: 1222.992, 80: 424.741},
        6: {0: 1222.992, 20: 1149.237, 40: 936.866, 60: 611.496, 80: 212.370},
        7: {0: 611.496, 20: 574.618, 40: 468.433, 60: 305.748, 80: 106.185},
        8: {0: 305.748, 20: 287.309, 40: 234.217, 60: 152.874, 80: 53.093},
        9: {0: 152.874, 20: 143.655, 40: 117.108, 60: 76.437, 80: 26.546},
        10: {0: 76.437, 20: 71.827, 40: 58.554, 60: 38.218, 80: 13.273},
        11: {0: 38.218, 20: 35.914, 40: 29.277, 60: 19.109, 80: 6.637},
        12: {0: 19.109, 20: 17.957, 40: 14.639, 60: 9.555, 80: 3.318},
        13: {0: 9.555, 20: 8.978, 40: 7.319, 60: 4.777, 80: 1.659},
        14: {0: 4.777, 20: 4.489, 40: 3.660, 60: 2.389, 80: 0.830},
        15: {0: 2.389, 20: 2.245, 40: 1.830, 60: 1.194, 80: 0.415},
        16: {0: 1.194, 20: 1.122, 40: 0.915, 60: 0.597, 80: 0.207},
        17: {0: 0.597, 20: 0.561, 40: 0.457, 60: 0.299, 80: 0.104},
        18: {0: 0.299, 20: 0.281, 40: 0.229, 60: 0.149, 80: 0.052},
        19: {0: 0.149, 20: 0.140, 40: 0.114, 60: 0.075, 80: 0.026},
        20: {0: 0.075, 20: 0.070, 40: 0.057, 60: 0.037, 80: 0.013},
        21: {0: 0.037, 20: 0.035, 40: 0.029, 60: 0.019, 80: 0.006},
        22: {0: 0.019, 20: 0.018, 40: 0.014, 60: 0.009, 80: 0.003}
    }
    cur_conv = conversion_table[zoom]
    if lat == 0:
        return cur_conv[0]
    elif 20 >= lat >= -20:
        return cur_conv[20]
    elif 40 >= lat >= -40:
        return cur_conv[40]
    elif 60 >= lat >= -60:
        return cur_conv[60]
    else:
        return cur_conv[80]
