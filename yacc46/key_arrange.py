# usage:
# ```
# cd(r"path\to\this\file\dir")
# import key_arrange
# key_arrange.arrange_keys()
# ```

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
import pcbnew
import math

pcb = pcbnew.GetBoard()

def FindModuleByReference(ref):
    module = pcb.FindModuleByReference(ref)
    if module is None:
        raise ValueError("ref {} not found".format(ref))
    return module

switch_refs = {
    "left": ["SW"+str(i) for i in range(1,23+1)],
    "right": ["SW"+str(i) for i in range(24,46+1)]
}

switch_corresponds = {
    "SW1": "SW28",
    "SW2": "SW27",
    "SW3": "SW26",
    "SW4": "SW25",
    "SW5": "SW24",

    "SW6": "SW35",
    "SW7": "SW34",
    "SW8": "SW33",
    "SW9": "SW32",
    "SW10": "SW31",
    "SW11": "SW30",
    "SW12": "SW29",

    "SW13": "SW42",
    "SW14": "SW41",
    "SW15": "SW40",
    "SW16": "SW39",
    "SW17": "SW38",
    "SW18": "SW37",
    "SW19": "SW36",

    "SW20": "SW45",
    "SW21": "SW44",
    "SW22": "SW43",
    "SW23": "SW46",
    }

def print_modules_left_switches():
    for r in switch_refs["left"]:
        m = FindModuleByReference(r)
        print("ref:", m.GetReference(), ", pos:", m.GetPosition(), ", pos[mm]:", pcbnew.ToMM(m.GetPosition()))

def move_left_switches_origin():
    for r in switch_refs["left"]:
        m = FindModuleByReference(r)
        print("ref:", m.GetReference(), ", pos:", m.GetPosition())
        m.SetPosition(pcbnew.wxPointMM(0, 0))
        m.SetOrientationDegrees(0)

def move_right_modules_left_mirror(x_center, module_corresponts):
    for rl, rr in module_corresponts.items():
        ml = FindModuleByReference(rl)
        mr = FindModuleByReference(rr)
        l_pos = pcbnew.ToMM(ml.GetPosition())
        l_ori = ml.GetOrientationDegrees()
        r_pos = pcbnew.wxPointMM(x_center * 2 - l_pos[0], l_pos[1])
        r_ori = 360 - l_ori
        mr.SetPosition(r_pos)
        mr.SetOrientationDegrees(r_ori)

class MyPosition(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, MyPosition):
            return MyPosition(self.x + other.x, self.y + other.y)
        if isinstance(other, tuple):
            return self + MyPosition(*other)
        raise RuntimeError("Unknown object type: " + str(type(other)))

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, MyPosition):
            return self + (-1 * other)
        if isinstance(other, tuple):
            return self + (-1 * MyPosition(*other))

    def __rsub__(self, other):
        return self - other

    def __mul__(self, other):
        return MyPosition(self.x * other, self.y * other)

    def __rmul__(self, other):
        return self * other

    def __str__(self):
        return "({:.2f}, {:.2f})".format(self.x, self.y)

class SwitchPosition(MyPosition):
    U_mm = 19.05
    def __init__(self, x, y, angle_deg):
        super(SwitchPosition, self).__init__(x, y)
        self._set_angle(angle_deg)

    def _set_angle(self, angle_deg):
        self.angle_deg = angle_deg
        self.angle_rad = math.radians(angle_deg)

    def change_angle(self, angle_deg):
        return SwitchPosition(self.x, self.y, angle_deg)

    def right(self, u):
        return SwitchPosition(
            self.x + u * math.cos(self.angle_rad),
            self.y + u * math.sin(self.angle_rad),
            self.angle_deg)

    def up(self, u):
        return SwitchPosition(
            self.x + u * math.cos(math.pi / 2 - self.angle_rad),
            self.y - u * math.sin(math.pi / 2 - self.angle_rad),
            self.angle_deg
        )

    def __add__(self, other):
        p = super(SwitchPosition, self).__add__(other)
        return SwitchPosition(p.x, p.y, self.angle_deg)
    
    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        p = super(SwitchPosition, self).__sub__(other)
        return SwitchPosition(p.x, p.y, self.angle_deg)

    def __rsub__(self, other):
        return self - other

    def __mul__(self, other):
        p = super(SwitchPosition, self).__mul__(other)
        return SwitchPosition(p.x, p.y, self.angle_deg)

    def __rmul__(self, other):
        return self * other

    def __str__(self):
        return "({:.2f}, {:.2f} angle: {})".format(self.x, self.y, self.angle_deg)
    
    def to_mm(self):
        return self * self.U_mm


def arrange_left():
    P = MyPosition
    SP = SwitchPosition
    # base_pos: SW14
    base_pos = P(52.8, 51.575)
    sw_pos_u = {
        # col 1
        "SW1": SP(0, 0, 0),
        "SW7": SP(0, 1, 0),
        "SW14": SP(0, 2, 0),
        # col0
        "SW6": SP(-1, 0.75, 0),
        "SW13": SP(-1, 1.75, 0)
    }

    # col2
    col2_orientation = 6
    sw_pos_u["SW15"] = sw_pos_u["SW14"].right(0.5).up(0.1).change_angle(col2_orientation).right(0.5).up(0.5)
    sw_pos_u["SW8"] = sw_pos_u["SW15"].up(1)
    sw_pos_u["SW2"] = sw_pos_u["SW8"].up(1)

    # col3
    col3_orientation = 10
    sw_pos_u["SW16"] = sw_pos_u["SW15"].right(0.5).change_angle(col3_orientation).right(0.5).up(0.5)
    sw_pos_u["SW9"] = sw_pos_u["SW16"].up(1)
    sw_pos_u["SW3"] = sw_pos_u["SW9"].up(1)

    # col4
    sw_pos_u["SW4"] = sw_pos_u["SW3"].right(1).up(-0.25)
    sw_pos_u["SW10"] = sw_pos_u["SW4"].up(-1)
    sw_pos_u["SW17"] = sw_pos_u["SW10"].up(-1)

    # col5
    sw_pos_u["SW5"] = sw_pos_u["SW4"].right(1).up(-0.125)
    sw_pos_u["SW11"] = sw_pos_u["SW5"].up(-1)
    sw_pos_u["SW18"] = sw_pos_u["SW11"].up(-1)

    # col6
    sw_pos_u["SW12"] = sw_pos_u["SW11"].right(1).up(-0.125)
    sw_pos_u["SW19"] = sw_pos_u["SW12"].up(-1)

    # thumb
    sw_pos_u["SW21"] = sw_pos_u["SW18"].right(-0.5).up(-0.5).change_angle(18).right(0.5).up(-0.5)
    sw_pos_u["SW20"] = sw_pos_u["SW21"].right(-0.5).up(-0.5).change_angle(10).right(-0.5).up(0.5)
    sw_pos_u["SW22"] = sw_pos_u["SW21"].right(0.5).up(-0.5).change_angle(26).right(0.5).up(0.5)
    sw_pos_u["SW23"] = sw_pos_u["SW21"].up(-1)

    # u -> mm
    sw_pos_mm = {r: v.to_mm() + base_pos for r, v in sw_pos_u.items()}
    # # dbg: print
    # for r in sorted(sw_pos_mm.keys()):
    #     print("{}: {}".format(r, sw_pos_mm[r]))

    # move
    for r, pos in sw_pos_mm.items():
        m = FindModuleByReference(r)
        m.SetPosition(pcbnew.wxPointMM(pos.x, pos.y))
        m.SetOrientationDegrees(-pos.angle_deg)

def arrange_diodes():
    for i in range(1, 46+1):
        r = "SW" + str(i)
        sw = FindModuleByReference("SW" + str(i))
        d = FindModuleByReference("D" + str(i))
        angle = -sw.GetOrientationDegrees()
        tmp_pos = pcbnew.ToMM(sw.GetPosition())
        sw_pos = MyPosition(tmp_pos[0], tmp_pos[1])
        d_pos = sw_pos + SwitchPosition(0, 0, angle).right(0.43).up(-0.05).to_mm()
        d.SetPosition(pcbnew.wxPointMM(d_pos.x, d_pos.y))
        d.SetOrientationDegrees(90 - angle)

def arrange_leds(center):
    led_corresponds = {
        "LED1": "LED14",
        "LED2": "LED13",
        "LED3": "LED12",
        "LED4": "LED11",
        "LED5": "LED10",
        "LED6": "LED9",
        "LED7": "LED8",
    }
    led_positions = {
        "LED1": MyPosition(148.30, 36.80),
        "LED2": MyPosition(91.60, 40.00),
        "LED3": MyPosition(58.75, 40.60),
        "LED4": MyPosition(47.30, 78.95),
        "LED5": MyPosition(76.20, 93.60),
        "LED6": MyPosition(109.7, 112.00),
        "LED7": MyPosition(147.10, 126.70)
    }

    for ref, pos in led_positions.items():
        led = FindModuleByReference(ref)
        led.SetPosition(pcbnew.wxPointMM(pos.x, pos.y))
    move_right_modules_left_mirror(center, led_corresponds)

def arrange_holes(center):
    hole_corresponds = {
        "H1": "H12",
        "H2": "H11",
        "H3": "H10",
        "H4": "H9",
        "H5": "H8",
        "H6": "H7",
        "H13": "H14",
    }
    hole_positions = {
        "H1": MyPosition(132.00, 131.05),
        "H2": MyPosition( 84.40, 100.65),
        "H3": MyPosition( 42.00,  95.65),
        "H4": MyPosition( 34.70,  46.25),
        "H5": MyPosition( 86.25,  28.95),
        "H6": MyPosition(142.00,  29.00),
        "H13": MyPosition(152.0, 58.2),
    }

    for ref, pos in hole_positions.items():
        hole = FindModuleByReference(ref)
        if hole is None:
            raise ValueError("ref {} not found.".format(ref))
        hole.SetPosition(pcbnew.wxPointMM(pos.x, pos.y))
    move_right_modules_left_mirror(center, hole_corresponds)

def arrange_keys():
    HandsGap_mm = 14.4

    arrange_left()
    # decide center
    sw12 = FindModuleByReference("SW12")
    tmp_pos = pcbnew.ToMM(sw12.GetPosition())
    sw12_pos = MyPosition(tmp_pos[0], tmp_pos[1])
    left_rightcorner = sw12_pos + SwitchPosition(0, 0, -sw12.GetOrientationDegrees()).right(0.5).up(0.5).to_mm()
    center = math.ceil(left_rightcorner.x + HandsGap_mm / 2.0)
    print("center: {}".format(center))

    #arrange right
    move_right_modules_left_mirror(center, switch_corresponds)

    arrange_diodes()
    arrange_leds(center)
    arrange_holes(center)

def main():
    arrange_keys()

