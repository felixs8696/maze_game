HORIZONTAL_WALL = u"\u2501"
HORIZONTAL_BORDER = u"\u2509"
VERTICAL_WALL = u"\u2503"
VERTICAL_BORDER = u"\u250B"
TOP_LEFT_CORNER = u"\u250F"
TOP_RIGHT_CORNER = u"\u2513"
BOTTOM_LEFT_CORNER = u"\u2517"
BOTTOM_RIGHT_CORNER = u"\u251B"
CROSS_WALL = u"\u254B"
SAFE_TILE_DOT = u"\u00B7"
EMPTY = " "

EXIT_LEFT = u'\u25C2'
EXIT_RIGHT = u'\u25B8'
EXIT_UP = u'\u25B4'
EXIT_DOWN = u'\u25BE'

CS_UDLR = u"\u254B"
CS_ULR = u"\u253B"
CS_DLR = u"\u2533"
CS_UDL = u"\u252B"
CS_UDR = u"\u2523"

CS_UL = BOTTOM_RIGHT_CORNER
CS_UR = BOTTOM_LEFT_CORNER
CS_DL = TOP_RIGHT_CORNER
CS_DR = TOP_LEFT_CORNER

CS_LR = HORIZONTAL_WALL
CS_UD = VERTICAL_WALL

CS_U = VERTICAL_WALL
CS_D = VERTICAL_WALL
CS_L = HORIZONTAL_WALL
CS_R = HORIZONTAL_WALL


def _get_wall_cross_section_map():
    wall_cross_section_map = {}
    t = True
    f = False
    wall_cross_section_map[(t, t, t, t)] = CS_UDLR
    wall_cross_section_map[(t, f, t, t)] = CS_ULR
    wall_cross_section_map[(f, t, t, t)] = CS_DLR
    wall_cross_section_map[(t, t, t, f)] = CS_UDL
    wall_cross_section_map[(t, t, f, t)] = CS_UDR
    wall_cross_section_map[(t, f, t, f)] = CS_UL
    wall_cross_section_map[(t, f, f, t)] = CS_UR
    wall_cross_section_map[(f, t, t, f)] = CS_DL
    wall_cross_section_map[(f, t, f, t)] = CS_DR
    wall_cross_section_map[(f, f, t, t)] = CS_LR
    wall_cross_section_map[(t, t, f, f)] = CS_UD
    wall_cross_section_map[(t, f, f, f)] = CS_U
    wall_cross_section_map[(f, t, f, f)] = CS_D
    wall_cross_section_map[(f, f, t, f)] = CS_L
    wall_cross_section_map[(f, f, f, t)] = CS_R
    return wall_cross_section_map


WALL_CROSS_SECTION_MAP = _get_wall_cross_section_map()
