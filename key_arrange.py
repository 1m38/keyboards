from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
import pcbnew
import math

pcb = pcbnew.GetBoard()

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

led_corresponds = {
    "LED1": "LED14",
    "LED2": "LED13",
    "LED3": "LED12",
    "LED4": "LED11",
    "LED5": "LED10",
    "LED6": "LED9",
    "LED7": "LED8",
}

hole_corresponds = {
    "HOLE1": "HOLE12",
    "HOLE2": "HOLE11",
    "HOLE3": "HOLE10",
    "HOLE4": "HOLE9",
    "HOLE5": "HOLE8",
    "HOLE6": "HOLE7",
}

def print_modules_left_switches():
    for r in switch_refs["left"]:
        m = pcb.FindModuleByReference(r)
        print("ref:", m.GetReference(), ", pos:", m.GetPosition(), ", pos[mm]:", pcbnew.ToMM(m.GetPosition()))

def move_left_switches_origin():
    for r in switch_refs["left"]:
        m = pcb.FindModuleByReference(r)
        print("ref:", m.GetReference(), ", pos:", m.GetPosition())
        m.SetPosition(pcbnew.wxPointMM(0, 0))
        m.SetOrientationDegrees(0)

def move_right_modules_left_mirror(x_center, module_corresponts):
    for rl, rr in module_corresponts.items():
        ml = pcb.FindModuleByReference(rl)
        mr = pcb.FindModuleByReference(rr)
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
        self.set_angle(angle_deg)

    def set_angle(self, angle_deg):
        self.angle_deg = angle_deg
        self.angle_rad = math.radians(angle_deg)
        return self

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
    sw_pos_u = {}
    # col1
    sw_pos_u.update({
        "SW1": SP(0, 0, 0),
        "SW7": SP(0, 1, 0),
        "SW14": SP(0, 2, 0)
    })

    # col0
    sw_pos_u.update({
        "SW6": SP(-1, 0.75, 0),
        "SW13": SP(-1, 1.75, 0)
    })

    # col2
    col2_orientation = 6
    sw_pos_u["SW15"] = sw_pos_u["SW14"].right(0.5).set_angle(col2_orientation).right(0.5).up(0.5)
    sw_pos_u["SW8"] = sw_pos_u["SW15"].up(1)
    sw_pos_u["SW2"] = sw_pos_u["SW8"].up(1)

    # col3
    col3_orientation = 10
    sw_pos_u["SW16"] = sw_pos_u["SW15"].right(0.5).set_angle(col3_orientation).right(0.5).up(0.5)
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
    sw_pos_u["SW21"] = sw_pos_u["SW18"].right(-0.5).up(-0.5).set_angle(18).right(0.5).up(-0.5)
    sw_pos_u["SW20"] = sw_pos_u["SW21"].right(-0.5).up(-0.5).set_angle(10).right(-0.5).up(0.5)
    sw_pos_u["SW22"] = sw_pos_u["SW21"].right(0.5).up(-0.5).set_angle(26).right(0.5).up(0.5)
    sw_pos_u["SW23"] = sw_pos_u["SW21"].up(-1)

    # u -> mm
    sw_pos_mm = {r: v.to_mm() + base_pos for r, v in sw_pos_u.items()}
    # # dbg: print
    # for r in sorted(sw_pos_mm.keys()):
    #     print("{}: {}".format(r, sw_pos_mm[r]))

    # move
    for r, pos in sw_pos_mm.items():
        m = pcb.FindModuleByReference(r)
        m.SetPosition(pcbnew.wxPointMM(pos.x, pos.y))
        m.SetOrientationDegrees(-pos.angle_deg)

def arrange_diodes():
    for i in range(1, 46+1):
        r = "SW" + str(i)
        sw = pcb.FindModuleByReference("SW" + str(i))
        d = pcb.FindModuleByReference("D" + str(i))
        angle = -sw.GetOrientationDegrees()
        tmp_pos = pcbnew.ToMM(sw.GetPosition())
        sw_pos = MyPosition(tmp_pos[0], tmp_pos[1])
        d_pos = sw_pos + SwitchPosition(0, 0, angle).right(0.43).up(-0.05).to_mm()
        d.SetPosition(pcbnew.wxPointMM(d_pos.x, d_pos.y))
        d.SetOrientationDegrees(90 - angle)

def arrange_keys():
    HandsGap_mm = 5

    arrange_left()
    # decide center
    sw12 = pcb.FindModuleByReference("SW12")
    tmp_pos = pcbnew.ToMM(sw12.GetPosition())
    sw12_pos = MyPosition(tmp_pos[0], tmp_pos[1])
    left_rightcorner = sw12_pos + SwitchPosition(0, 0, -sw12.GetOrientationDegrees()).right(0.5).up(0.5).to_mm()
    center = left_rightcorner.x + HandsGap_mm / 2.0
    print("center: {}".format(center))

    #arrange right
    move_right_modules_left_mirror(center, switch_corresponds)
    move_right_modules_left_mirror(center, led_corresponds)

    arrange_diodes()



