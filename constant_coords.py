from points import Point

# Landmasses
TAIWAN_COLOR = "yellowgreen"
JAPAN_COLOR = "white"
CHINA_COLOR = "indianred"
OTHER_COLOR = "dimgrey"

TAIWAN_POINTS = [Point(21.93, 120.71, lon_lat=True), Point(21.90, 120.86, lon_lat=True),
                 Point(22.29, 120.89, lon_lat=True), Point(22.75, 121.17, lon_lat=True),
                 Point(24.00, 121.65, lon_lat=True), Point(24.54, 121.87, lon_lat=True),
                 Point(24.84, 121.83, lon_lat=True), Point(25.01, 122.00, lon_lat=True),
                 Point(25.30, 121.55, lon_lat=True), Point(25.024, 121.05, lon_lat=True),
                 Point(24.60, 120.73, lon_lat=True), Point(23.80, 120.18, lon_lat=True),
                 Point(23.10, 120.04, lon_lat=True), Point(22.54, 120.32, lon_lat=True)]

ORCHID_ISLAND_POINTS = [Point(22.08, 121.50, lon_lat=True), Point(22.09, 121.57, lon_lat=True),
                        Point(22.04, 121.57, lon_lat=True), Point(22.02, 121.60, lon_lat=True),
                        Point(22.00, 121.69, lon_lat=True), Point(22.03, 121.54, lon_lat=True),
                        Point(22.06, 121.50, lon_lat=True)]

GREEN_ISLAND_POINTS = [Point(22.68, 121.47, lon_lat=True), Point(22.68, 121.51, lon_lat=True),
                       Point(22.63, 121.51, lon_lat=True), Point(22.65, 121.47, lon_lat=True)]

PENGHU_COUNTRY_POINTS = [Point(23.68, 119.60, lon_lat=True), Point(23.60, 119.68, lon_lat=True),
                         Point(23.56, 119.69, lon_lat=True), Point(23.51, 119.61, lon_lat=True),
                         Point(23.56, 119.47, lon_lat=True), Point(23.65, 119.52, lon_lat=True)]

WANGAN_POINTS = [Point(23.36, 119.49, lon_lat=True), Point(23.39, 119.49, lon_lat=True),
                 Point(23.39, 119.51, lon_lat=True), Point(23.37, 119.51, lon_lat=True),
                 Point(23.37, 119.52, lon_lat=True), Point(23.37, 119.52, lon_lat=True),
                 Point(23.35, 119.51, lon_lat=True)]

QIMEI_POINTS = [Point(23.22, 119.45, lon_lat=True), Point(23.19, 119.43, lon_lat=True),
                Point(23.21, 119.41, lon_lat=True)]

YONAGUNI_POINTS = [Point(24.45, 122.93, lon_lat=True), Point(24.47, 122.96, lon_lat=True),
                   Point(24.47, 123.01, lon_lat=True), Point(24.46, 123.04, lon_lat=True),
                   Point(24.44, 123.01, lon_lat=True), Point(24.44, 122.95, lon_lat=True)]

TAKETOMI_POINTS = [Point(24.31, 123.66, lon_lat=True), Point(24.44, 123.77, lon_lat=True),
                   Point(24.364, 123.939, lon_lat=True), Point(24.257, 123.877, lon_lat=True)]

ISHIGAKE_POINTS = [Point(24.429, 124.071, lon_lat=True), Point(24.454, 124.157, lon_lat=True),
                   Point(24.456, 124.215, lon_lat=True), Point(24.609, 124.311, lon_lat=True),
                   Point(24.602, 124.341, lon_lat=True), Point(24.490, 124.283, lon_lat=True),
                   Point(24.348, 124.244, lon_lat=True), Point(24.327, 124.141, lon_lat=True),
                   Point(24.367, 124.113, lon_lat=True), Point(24.400, 124.142, lon_lat=True),
                   Point(24.418, 124.086, lon_lat=True)]

MIYAKOJIMA_POINTS = [Point(24.824, 125.136, lon_lat=True), Point(24.865, 125.164, lon_lat=True),
                     Point(24.940, 125.240, lon_lat=True), Point(24.725, 125.463, lon_lat=True),
                     Point(24.716, 125.241, lon_lat=True)]

OKINAWA_POINTS = [Point(26.082, 127.656, lon_lat=True), Point(26.218, 127.659, lon_lat=True),
                  Point(26.302, 127.759, lon_lat=True), Point(26.430, 127.714, lon_lat=True),
                  Point(26.577, 127.988, lon_lat=True), Point(26.723, 127.749, lon_lat=True),
                  Point(26.679, 128.099, lon_lat=True), Point(26.868, 128.254, lon_lat=True),
                  Point(26.783, 128.328, lon_lat=True), Point(26.444, 127.950, lon_lat=True),
                  Point(26.394, 128.006, lon_lat=True), Point(26.163, 127.832, lon_lat=True)]

OKINOERABUJIMA_POINTS = [Point(27.437, 128.712, lon_lat=True), Point(27.331, 128.567, lon_lat=True),
                         Point(27.375, 128.520, lon_lat=True), Point(27.405, 128.535, lon_lat=True),
                         Point(27.397, 128.562, lon_lat=True)]

TOKUNOSHIMA_POINTS = [Point(27.894, 128.969, lon_lat=True), Point(27.816, 128.968, lon_lat=True),
                      Point(27.770, 129.037, lon_lat=True), Point(27.671, 128.986, lon_lat=True),
                      Point(27.724, 128.881, lon_lat=True)]

AMAMI_OSHIMA_POINTS = [Point(28.249, 129.136, lon_lat=True), Point(28.368, 129.344, lon_lat=True),
                       Point(28.528, 129.686, lon_lat=True), Point(28.439, 129.719, lon_lat=True),
                       Point(28.241, 129.442, lon_lat=True), Point(28.215, 129.476, lon_lat=True),
                       Point(28.112, 129.367, lon_lat=True)]

YAKUSHIMA_POINTS = [Point(30.382, 130.375, lon_lat=True), Point(30.450, 130.509, lon_lat=True),
                    Point(30.377, 130.671, lon_lat=True), Point(30.229, 130.563, lon_lat=True)]

TANEGASHIMA_POINTS = [Point(30.362, 130.857, lon_lat=True), Point(30.662, 130.945, lon_lat=True),
                      Point(30.832, 131.059, lon_lat=True), Point(30.603, 131.053, lon_lat=True)]

KOREA_POINTS = [Point(34.382635296628266, 126.1105936433172, lon_lat=True),
                Point(34.283897291817006, 126.72869474423958, lon_lat=True),
                Point(34.8147862758336, 128.44754879324768, lon_lat=True),
                Point(34.666106922426835, 128.6397890487289, lon_lat=True),
                Point(35.055818803797955, 128.77548805259792, lon_lat=True),
                Point(35.06507513295652, 129.0129613093688, lon_lat=True),
                Point(36.049414003089616, 129.60099032613473, lon_lat=True),
                Point(36.12252266586377, 129.39744182033112, lon_lat=True),
                Point(37.22897033265078, 129.35220881904146, lon_lat=True),
                Point(38.60276796020003, 128.3570827906683, lon_lat=True),  # Right side border
                Point(39.22746826972953, 127.4184981196537, lon_lat=True),
                Point(40.85492641510266, 129.7479976860726, lon_lat=True),
                Point(41.51024592280302, 129.6349151828484, lon_lat=True),
                Point(42.30134275308864, 130.65265771186637, lon_lat=True),
                Point(43.02478186744697, 129.97416269252105, lon_lat=True),  # N Korea
                Point(39.81192015777447, 124.12779727582893, lon_lat=True),
                Point(39.50722297163861, 125.2925470590384, lon_lat=True),
                Point(38.10617579665901, 124.68190154162761, lon_lat=True),
                Point(37.740443461568674, 125.37170481129533, lon_lat=True),
                Point(37.731500450396815, 126.1180493325752, lon_lat=True),
                Point(37.740443375169086, 126.16328222811846, lon_lat=True),  # Left side border
                Point(36.97643996172249, 126.67215349262747, lon_lat=True),
                Point(36.777433290343886, 126.1293574771512, lon_lat=True),
                Point(35.627722046101404, 126.49122148746869, lon_lat=True),
                Point(34.33993969567544, 126.1293574771512, lon_lat=True),
                ]

JEJUDO_POINTS = [Point(33.522375907040484, 126.90759969506134, lon_lat=True),
                 Point(33.299521222070986, 126.85218991209356, lon_lat=True),
                 Point(33.299521222070986, 126.85218991209356, lon_lat=True),
                 Point(33.32898761892358, 126.17216075748912, lon_lat=True),
                 Point(33.4641845509088, 126.31246328374174, lon_lat=True),
                 Point(33.568364256062075, 126.81228862632128, lon_lat=True)
                 ]

JAPAN_POINTS = [Point(30.9983546671584, 130.66796919843003, lon_lat=True),
                Point(31.383794150026738, 131.41374581831766, lon_lat=True),
                Point(32.79875267280593, 132.00415230906208, lon_lat=True),
                Point(32.72035768620527, 133.0451321743219, lon_lat=True),
                Point(33.26766930690371, 134.19487112998203, lon_lat=True),
                Point(33.48175354770972, 135.7796464472433, lon_lat=True),
                Point(34.26862129392442, 136.90607988353196, lon_lat=True),
                Point(34.62736856984831, 138.87928087166372, lon_lat=True),
                Point(34.924119125728744, 139.96304519589916, lon_lat=True),
                Point(35.697504808899325, 140.84865493201576, lon_lat=True),
                Point(39.5626661634206, 142.05791223488617, lon_lat=True),
                Point(41.433822238113564, 141.46465055255817, lon_lat=True),
                Point(41.92614021766031, 143.27739453909015, lon_lat=True),
                Point(43.37246443182011, 145.8152364984633, lon_lat=True),
                Point(43.61912234915943, 145.22005957211516, lon_lat=True),
                Point(44.3470007892962, 145.35863501939224, lon_lat=True),
                Point(44.111999644422205, 144.2777463252725, lon_lat=True),
                Point(45.530584506201116, 141.92658290313864, lon_lat=True),
                Point(45.45604381940658, 141.00404816196055, lon_lat=True),
                Point(44.311204165553235, 141.69544523664806, lon_lat=True),
                Point(43.31415655603065, 140.3329910632108, lon_lat=True),
                Point(42.13223825272934, 139.4116903848445, lon_lat=True),
                Point(41.415713782568446, 140.0953292392304, lon_lat=True),
                Point(40.55095287763475, 139.85513179728352, lon_lat=True),
                Point(38.72991905202092, 139.65188780794387, lon_lat=True),
                Point(38.31069833746245, 138.5063307771203, lon_lat=True),
                Point(37.46495334490187, 136.76951850458136, lon_lat=True),
                Point(35.97339321518993, 135.9724071800993, lon_lat=True),
                Point(35.462508926835774, 132.70963446809083, lon_lat=True),
                Point(34.321965600620814, 130.8762665776979, lon_lat=True),
                Point(33.93532205206851, 130.8924318421183, lon_lat=True),
                Point(33.28905417084183, 129.37734013915494, lon_lat=True),
                Point(32.57570599758474, 129.78382811783425, lon_lat=True),
                Point(31.258359044464704, 130.2457462754244, lon_lat=True),
                ]

CHINA_POINTS = [Point(18.50888529440916, 108.69305618407309, lon_lat=True),
                Point(18.24118199609531, 109.59976174622189, lon_lat=True),
                Point(18.8429259014646, 110.4157967521558, lon_lat=True),
                Point(19.97364328408359, 111.05049064565996, lon_lat=True),
                Point(20.42747316271644, 110.51654181461677, lon_lat=True),
                Point(21.3873993146714, 110.77847897701531, lon_lat=True),
                Point(22.99181081810761, 116.59146908101371, lon_lat=True),
                Point(24.554166859076226, 118.57018558783436, lon_lat=True),
                Point(25.448931298161217, 119.826736628606, lon_lat=True),
                Point(26.159998507727916, 119.7369829828366, lon_lat=True),
                Point(28.267030328440345, 121.6577110023018, lon_lat=True),
                Point(29.96066622714138, 122.42959235591866, lon_lat=True),
                Point(30.30221889731248, 121.20894297487474, lon_lat=True),
                Point(30.596242203251776, 121.1550907874131, lon_lat=True),
                Point(30.827737805852507, 122.05262724510713, lon_lat=True),
                Point(32.02248525344326, 121.81926776610668, lon_lat=True),
                Point(32.629229620984276, 120.86787912095103, lon_lat=True),
                Point(34.255333695655224, 120.31179869819853, lon_lat=True),
                Point(34.890896625150134, 119.32450870460055, lon_lat=True),
                Point(36.031300018362714, 120.25794671368276, lon_lat=True),
                Point(36.9018060488687, 122.47708626734375, lon_lat=True),
                Point(37.44610557239777, 122.65853691339265, lon_lat=True),
                Point(37.868605176968394, 120.91874542480622, lon_lat=True),
                Point(37.68300157878378, 120.3103520821717, lon_lat=True),
                Point(37.13191052214833, 119.49916095865902, lon_lat=True),
                Point(37.378282711901996, 118.89076761602446, lon_lat=True),
                Point(37.86838622659373, 119.13265542029377, lon_lat=True),
                Point(38.639487702261405, 117.68105025190263, lon_lat=True),
                Point(39.20415971736636, 118.17203435297611, lon_lat=True),
                Point(39.088271239052496, 118.6416713192203, lon_lat=True),
                Point(40.854945344213974, 121.18198036390481, lon_lat=True),
                Point(40.46630175032113, 122.18529570088104, lon_lat=True),
                Point(39.764328544492344, 121.33141030770977, lon_lat=True),
                Point(39.89547663058136, 124.25596777932132, lon_lat=True),
                Point(42.97046854532111, 129.9951987981382, lon_lat=True),
                Point(43.53289325051917, 117.98130022180558, lon_lat=True),
                Point(41.89547663058136, 108.69305618407309, lon_lat=True), ]

PHILIPPINES_POINTS = [Point(15.000, 120.035, lon_lat=True),
                      Point(16.256, 119.709, lon_lat=True),
                      Point(16.470, 119.973, lon_lat=True),
                      Point(16.0514, 120.190, lon_lat=True),
                      Point(16.175, 120.397, lon_lat=True),
                      Point(18.483, 120.569, lon_lat=True),
                      Point(18.677, 120.863, lon_lat=True),
                      Point(18.270, 121.936, lon_lat=True),
                      Point(18.597, 122.174, lon_lat=True),
                      Point(17.125, 122.455, lon_lat=True),
                      Point(15.000, 121.499, lon_lat=True), ]

MEDIAN_ZONE = [Point(40.000, 110.000, lon_lat=True), Point(40.000, 120.647, lon_lat=True),
               Point(27.000, 122.000, lon_lat=True), Point(23.000, 118.000, lon_lat=True),
               Point(19.949, 110.000, lon_lat=True), ]

A_ALL_ZONES = [Point(15.000, 110.000, lon_lat=True), Point(15.000, 150.000, lon_lat=True), Point(45.000, 150.000, lon_lat=True), Point(45.000, 110.000, lon_lat=True), ]
B_TAIWAN_CONT = [Point(25.690, 121.492, lon_lat=True), Point(25.005, 122.466, lon_lat=True), Point(21.800, 121.316, lon_lat=True), Point(21.466, 120.610, lon_lat=True), Point(22.978, 119.532, lon_lat=True), Point(23.907, 119.663, lon_lat=True), Point(25.120, 120.539, lon_lat=True), ]
C_TAIWAN_TERRITORIAL = [Point(25.491, 121.564, lon_lat=True), Point(24.978, 122.263, lon_lat=True), Point(21.897, 121.140, lon_lat=True), Point(21.686, 120.617, lon_lat=True), Point(22.966, 119.814, lon_lat=True), Point(23.764, 119.885, lon_lat=True), Point(25.019, 120.715, lon_lat=True), ]
D_JAPAN_CONT = [Point(45.000, 150.000, lon_lat=True), Point(41.413, 143.904, lon_lat=True), Point(31.421, 140.221, lon_lat=True), Point(33.581, 137.458, lon_lat=True), Point(31.120, 132.149, lon_lat=True), Point(25.7423, 128.223, lon_lat=True), Point(26.284, 126.331, lon_lat=True), Point(29.977, 128.874, lon_lat=True), Point(32.592, 128.083, lon_lat=True), Point(34.812, 129.153, lon_lat=True), Point(36.676, 132.970, lon_lat=True), Point(38.473, 137.879, lon_lat=True), Point(42.099, 138.837, lon_lat=True), Point(45.000, 140.635, lon_lat=True), ]
E_JAPAN_TERRITORIAL = [Point(45.000, 148.879, lon_lat=True), Point(41.632, 143.878, lon_lat=True), Point(31.876, 139.942, lon_lat=True), Point(34.225, 138.191, lon_lat=True), Point(32.386, 133.229, lon_lat=True), Point(30.395, 131.388, lon_lat=True), Point(25.920, 128.040, lon_lat=True), Point(26.315, 126.500, lon_lat=True), Point(27.954, 128.673, lon_lat=True), Point(30.897, 129.665, lon_lat=True), Point(32.574, 128.401, lon_lat=True), Point(34.776, 129.220, lon_lat=True), Point(36.475, 133.136, lon_lat=True), Point(38.341, 138.135, lon_lat=True), Point(42.120, 139.163, lon_lat=True), Point(45.000, 140.920, lon_lat=True),]
F_FILIPINO_CONT = [Point(15.000, 119.623, lon_lat=True), Point(16.507, 119.376, lon_lat=True), Point(20.987, 121.346, lon_lat=True), Point(20.841, 122.350, lon_lat=True), Point(17.135, 122.920, lon_lat=True), Point(15.000, 122.574, lon_lat=True), ]
G_FILIPINO_TERRITORIAL = [Point(15.000, 119.845, lon_lat=True), Point(16.420, 119.586, lon_lat=True), Point(20.907, 121.569, lon_lat=True), Point(20.837, 122.140, lon_lat=True), Point(17.131, 122.730, lon_lat=True), Point(15.000, 122.368, lon_lat=True), ]
H_OUTSIDE_10_DASH = [Point(45.000, 124.152, lon_lat=True), Point(39.734, 124.152, lon_lat=True), Point(34.89, 122.91, lon_lat=True), Point(30.62, 125.95, lon_lat=True), Point(28.25, 125.02, lon_lat=True), Point(26.01, 125.55, lon_lat=True), Point(25.26, 122.87, lon_lat=True), Point(24.25, 122.43, lon_lat=True), Point(22.27, 123.48, lon_lat=True), Point(17.32, 116.41, lon_lat=True), Point(15.00, 116.28, lon_lat=True), Point(15.000, 150.000, lon_lat=True), Point(45.000, 150.000, lon_lat=True), ]
# I_INSIDE_10_DASH = [Point(21.477, 110.000, lon_lat=True), Point(24.974, 117.975, lon_lat=True), Point(30.864, 120.911, lon_lat=True), Point(38.712, 117.105, lon_lat=True), Point(39.734, 124.152, lon_lat=True), Point(34.89, 122.91, lon_lat=True), Point(30.62, 125.95, lon_lat=True), Point(28.25, 125.02, lon_lat=True), Point(26.01, 125.55, lon_lat=True), Point(25.26, 122.87, lon_lat=True), Point(24.25, 122.43, lon_lat=True), Point(22.27, 123.48, lon_lat=True), Point(17.32, 116.41, lon_lat=True), Point(15.00, 116.28, lon_lat=True), Point(15.000, 110.000, lon_lat=True), ]
I_INSIDE_10_DASH = [Point(28.055, 120.393, lon_lat=True), Point(25.26, 122.87, lon_lat=True), Point(24.25, 122.43, lon_lat=True), Point(22.27, 123.48, lon_lat=True), Point(20.874, 120.437, lon_lat=True), Point(23.397, 116.561, lon_lat=True), ]
J_TAIWAN_FILIPINO = [Point(21.643, 121.326, lon_lat=True), Point(21.069, 121.606, lon_lat=True), Point(19.487, 120.966, lon_lat=True), Point(21.672, 120.422, lon_lat=True), ]
K_TAIWAN_JAPAN = [Point(25.218, 122.328, lon_lat=True), Point(25.200, 122.910, lon_lat=True), Point(24.464, 122.611, lon_lat=True), Point(23.334, 122.405, lon_lat=True), Point(23.334, 121.870, lon_lat=True), Point(24.503, 122.231, lon_lat=True), ]
L_INSIDE_MEDIAN_LINE = [Point(45.000, 110.000, lon_lat=True), Point(45.000, 120.647, lon_lat=True), Point(27.000, 122.000, lon_lat=True), Point(23.000, 118.000, lon_lat=True), Point(19.949, 110.000, lon_lat=True), ]






