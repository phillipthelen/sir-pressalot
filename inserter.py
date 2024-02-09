# %%
from build123d import *
from ocp_vscode import *
import math

# %%



# %%

profile = import_step("2020_profile.step")

profile_size = 20
carriage_thickness = 3
carriage_height = 15
carriage_profile_gap=0.3
carriage_aligner_inset=0.75

cable_holder_height = 10
cable_holder_thickness = 5
cable_holder_arm_thickness = 4
cable_holder_length = 14
cable_holder_indent = 2
cable_holder_indent_width = 5
cable_velcro_width = 7

front_carriage_thickness = 8
front_carriage_height = 70
roller_screw_diameter = 5.35
carriage_wheel_horizontal_spacing = profile_size + 16.2
front_carriage_width = carriage_wheel_horizontal_spacing + 12
front_carriage_tensioner_height = 18
front_carriage_tensioner_width = 15
arm_screw_spacing = 50

solder_arm_length = 70
solder_arm_plate_thickness = 2
solder_arm_thickness = 8
solder_arm_tool_screws_distance = 30

lever_length = 110
lever_secondary_length = 55
lever_thickness = 4
lever_width = 10
pivot_hole_offset = 35

screw_diameter = 3.4
screw_head_diameter = 6
insert_diameter = 4.6
insert_height = 4
insert_undersizing = 0.2
square_nut_size = 6.6
square_nut_thickness = 2.1
bearing_diameter = 6.1
bearing_thickness = 2.6

solder_iron_diameter = 9
solder_iron_holder_thickness = 0.8
solder_iron_holder_height = solder_arm_tool_screws_distance

foot_thickness = 7
foot_length = 80
foot_width = 18
foot_angle = 40
foot_brace_bottom_length = 10
foot_brace_top_length = 20

def make_insert_hole(plane, depth):
    with BuildPart() as insert_hole:
        with BuildSketch(plane) as hole:
            Circle(screw_diameter/2)
        extrude(amount=-depth)
        with BuildSketch(plane) as insert:
            Circle(insert_diameter/2 - insert_undersizing)
        extrude(amount=-insert_height)
    return insert_hole

            
solder_mount_locations = (profile_size/3, -carriage_height/3), (-profile_size/3, -carriage_height/3), (0, carriage_height/3)

with BuildSketch() as profile_slot:
    add(profile.faces().sort_by(Axis.Z)[-1])
    offset(amount=0.2)
    with Locations((0, -9.2), (0, 9.2)):
        Rectangle(10, 2)
    with Locations((0, -profile_size/2), (0, profile_size/2)):
        Rectangle(6, 5, mode=Mode.SUBTRACT)
    with Locations((-9.2, 0), (9.2, 0)):
        Rectangle(2, 10)
    with Locations((-profile_size/2, 0), (profile_size/2, 0)):
        Rectangle(5, 6, mode=Mode.SUBTRACT)

with BuildSketch() as profile_slot_carriage:
    add(profile.faces().sort_by(Axis.Z)[-1])
    offset(amount=carriage_profile_gap)
    with Locations((0, -9.3), (0, 9.3)):
        Rectangle(10, 2.4)
    with Locations((0, -profile_size/2), (0, profile_size/2)):
        Rectangle(6, 5, mode=Mode.SUBTRACT)
    with Locations((-9.3, 0), (9.3, 0)):
        Rectangle(2.4, 10)
    with Locations((-profile_size/2, 0), (profile_size/2, 0)):
        Rectangle(5, 6, mode=Mode.SUBTRACT)


def make_solder_mount_holes(plane, depth):
    mount_locations = [(0, x, y) for x, y in solder_mount_locations]
    with BuildPart() as solder_mount_holes:
        with Locations(mount_locations):
            add(make_insert_hole(plane, depth))
    return solder_mount_holes

def make_hook(plane):
    with BuildPart() as hook:
        with BuildSketch(plane):
            Rectangle(6, 5)
        extrude(amount=5)
        side = faces().sort_by(Axis.Y)[0]
        with BuildSketch(side):
            with Locations((0, 1)):
                Rectangle(2, 3)
            with Locations((1.5, 2)):
                Rectangle(3, 1.5)
            chamfer(vertices(), 0.2)
        extrude(amount=-6, mode=Mode.SUBTRACT)
        with BuildSketch(side):
            with Locations((-3, 0.85)):
                Triangle(b=1.5, a=5, C=90, rotation=90)
        extrude(amount=-6, mode=Mode.ADD)
    return hook

with BuildPart() as tnut:
    with BuildSketch(profile.faces().sort_by(Axis.Z)[-1]):
        with Locations((0, 6.2)):
            Rectangle(profile_size, 4.2)
        add(profile_slot, mode=Mode.SUBTRACT)
        with Locations((8, 5), (-8, 5)):
            Rectangle(5, 4, mode=Mode.SUBTRACT)
    extrude(amount=insert_diameter + 5)
    add(make_insert_hole(faces().sort_by(Axis.Y)[0], 4.5), mode=Mode.SUBTRACT)

with BuildPart() as main_carriage:
    with BuildSketch(profile.faces().sort_by(Axis.Z)[-1].offset(-20)) as sketch:
        Rectangle(profile_size + (2*carriage_thickness), profile_size + (2*carriage_thickness))
        add(profile_slot_carriage, mode=Mode.SUBTRACT)
        Rectangle(profile_size - (2*carriage_aligner_inset), profile_size - (2*carriage_aligner_inset), mode=Mode.SUBTRACT)
    extrude(amount=-carriage_height, mode=Mode.ADD)
    with BuildSketch(faces().sort_by(Axis.X)[0]):
        Circle(screw_diameter/2)
    extrude(amount=-carriage_thickness - carriage_aligner_inset, mode=Mode.SUBTRACT)
    fillet(edges().filter_by(Axis.Z).group_by(Axis.Y)[0], 3)
    fillet(edges().filter_by(Axis.Z).group_by(Axis.Y)[-1], 3)

    add(make_insert_hole(faces().sort_by(Axis.Y)[-1], carriage_thickness + carriage_aligner_inset), mode=Mode.SUBTRACT)
    add(make_hook(faces().sort_by(Axis.X)[-1]))

front_carriage_back = None
front_carriage_side = None

with BuildPart() as front_carriage:
    with BuildSketch(Plane.YZ.offset(11)) as sketch:
        Rectangle(front_carriage_width, front_carriage_height)
    extrude(amount=front_carriage_thickness, mode=Mode.ADD)
    front = faces().sort_by(Axis.X)[-1]
    back = faces().sort_by(Axis.X)[0]
    front_carriage_back = back

    left_wheel_locations = ((-carriage_wheel_horizontal_spacing/2, front_carriage_height/2 - 6), 
                    (-carriage_wheel_horizontal_spacing/2, -front_carriage_height/2 + 6))
    with BuildSketch(back):
        with Locations((0, 0), (0, -arm_screw_spacing/2), (0, arm_screw_spacing/2)):
            Circle(screw_diameter/2)
        with Locations(left_wheel_locations):
            Circle(roller_screw_diameter/2)
        with Locations((carriage_wheel_horizontal_spacing/2, 0)):
            Circle(7/2)
    extrude(amount=-carriage_height, mode=Mode.SUBTRACT)

    for loc in left_wheel_locations:
        with BuildSketch(back) as ex24_sk:
            with Locations(loc):
                Circle(12/2)
        with BuildSketch(back.offset(8)) as ex24_sk2:
            with Locations(loc):
                Circle(8/2)
        loft()

    side = faces().sort_by(Axis.Y)[-1]
    front_carriage_side = side
    with BuildSketch(side):
        Rectangle(front_carriage_tensioner_height, front_carriage_thickness)
        with PolarLocations(front_carriage_tensioner_height/2 + 0.8, 2):
            Triangle(a=front_carriage_thickness/2, A=45, B=45, rotation=45)
    extrude(amount=-front_carriage_tensioner_width, mode=Mode.SUBTRACT)
 
    add(make_hook(faces().sort_by(Axis.Z)[-1]))

    right_edges = edges().filter_by(Axis.X).group_by(Axis.Y)[-1]
    fillet(right_edges.sort_by(Axis.Z)[0], 16)
    fillet(right_edges.sort_by(Axis.Z)[-1], 6)

    with BuildSketch(side):
        with Locations((front_carriage_tensioner_height/2 - 3, 0), (-front_carriage_tensioner_height/2 + 3, 0), (front_carriage_height/2 - 5, 0)):
            Circle(screw_diameter/2)
    extrude(amount=-front_carriage_tensioner_width - 10, mode=Mode.SUBTRACT)

    with BuildSketch(side.offset(-front_carriage_tensioner_width - 4)):
        with Locations((front_carriage_tensioner_height/2 - 3, 0), (-front_carriage_tensioner_height/2 + 3, 0), (front_carriage_height/2 - 5, 0)):
            with Locations((0, -square_nut_size/2)):
                Rectangle(square_nut_size, square_nut_size)
            Rectangle(square_nut_size, square_nut_size)
    extrude(amount=-square_nut_thickness, mode=Mode.SUBTRACT)

    with BuildSketch(side.offset(-6)):
        with Locations((front_carriage_height/2 - 5, 0)):
            with Locations((0, -square_nut_size/2)):
                Rectangle(square_nut_size, square_nut_size)
            Rectangle(square_nut_size, square_nut_size)
    extrude(amount=-square_nut_thickness, mode=Mode.SUBTRACT)

    with BuildSketch(side):
        with Locations((front_carriage_height/2 - 5, 0)):
            Circle(screw_head_diameter/2)
    extrude(amount=-2, mode=Mode.SUBTRACT)


    with BuildSketch(back):
        with Locations(left_wheel_locations):
            Circle(roller_screw_diameter/2)
    extrude(amount=8, mode=Mode.SUBTRACT)

    fillet(edges().filter_by(Axis.X).group_by(Axis.Y)[0], 6)

    with BuildSketch(side.offset(-front_carriage_width/2 + (profile_size/2 + carriage_thickness) + 0.2)):
        with Locations((front_carriage_height/2 - 5, 0)):
            Rectangle(bearing_diameter*2, 10)
    extrude(amount=-lever_thickness - 0.3, mode=Mode.SUBTRACT)


mid = (arm_screw_spacing+insert_diameter*2)/2

points = [
    (0, -insert_diameter*2),
    (0, arm_screw_spacing+insert_diameter*2),
    (-20, arm_screw_spacing+insert_diameter*2 + 10),
    (-solder_arm_length, mid+solder_arm_tool_screws_distance/2+insert_diameter),
    (-solder_arm_length, mid-solder_arm_tool_screws_distance/2-insert_diameter),
    (-20, -10),
    (0, 0)
]

with BuildPart() as solder_arm:
    with BuildSketch(Plane.XZ):
        with BuildLine():
            Polyline(*points)
        make_face()
    extrude(amount=solder_arm_thickness)
    offset(amount=-solder_arm_thickness, openings=faces().filter_by(Axis.Y))

    back = faces().sort_by(Axis.X)[-1]
    top_mount = make_insert_hole(back, 20)
    top_mount.part.move(Location((0, 0, arm_screw_spacing/2)))
    add(top_mount, mode=Mode.SUBTRACT)
    bottom_mount = make_insert_hole(back, 20)
    bottom_mount.part.move(Location((0, 0, -arm_screw_spacing/2)))
    add(bottom_mount, mode=Mode.SUBTRACT)
    add(make_insert_hole(back, 20), mode=Mode.SUBTRACT)

    front = faces().sort_by(Axis.X)[0]
    top_tool = make_insert_hole(front, 20)
    top_tool.part.move(Location((0, 0, solder_arm_tool_screws_distance/2)))
    add(top_tool, mode=Mode.SUBTRACT)
    bottom_tool = make_insert_hole(front, 20)
    bottom_tool.part.move(Location((0, 0, -solder_arm_tool_screws_distance/2)))
    add(bottom_tool, mode=Mode.SUBTRACT)

    z_edges = edges().filter_by(Axis.Z).group_by(Axis.X)[-1]
    z_edges.extend(edges().filter_by(Axis.Z).group_by(Axis.X)[0])
    chamfer(faces().filter_by(Axis.Y).edges().filter_by(lambda e: e not in z_edges), 1.5)
solder_arm.part.move(Location((profile_size/2 + front_carriage_thickness + 1, -solder_arm_thickness/2, 40.5), 180))

with BuildPart() as solder_holder:
    with BuildSketch(solder_arm.faces().sort_by(Axis.X)[-1]):
        Rectangle(solder_arm_tool_screws_distance + insert_diameter*2, solder_arm_thickness)
    extrude(amount=5.5)
    bottom = faces().sort_by(Axis.Z)[0]
    chamfer(edges().filter_by(Axis.X).group_by(Axis.Z)[-1], 1.5)
    chamfer(edges().filter_by(Axis.X).group_by(Axis.Z)[0], 1.5)
    with BuildSketch(bottom):
        with Locations((0, 1.75+solder_iron_diameter/2)):
            Circle((solder_iron_diameter + solder_iron_holder_thickness*2)/2)
    extrude(amount=-solder_iron_holder_height)
    with BuildSketch(bottom):
        with Locations((0, 1.75+solder_iron_diameter/2)):
            Circle(9/2)
        with Locations((0, 1.75 + solder_iron_diameter)):
            Rectangle(4, 6)
    extrude(amount=-solder_iron_holder_height, mode=Mode.SUBTRACT)
    with BuildSketch(faces().sort_by(Axis.X)[0]):
        with Locations((solder_arm_tool_screws_distance/2, 0), (-solder_arm_tool_screws_distance/2, 0)):
            Circle(screw_diameter/2, )
    extrude(amount=-10, mode=Mode.SUBTRACT)
    with BuildSketch(faces().sort_by(Axis.X)[0].offset(-0.5)):
        with Locations((solder_arm_tool_screws_distance/2, 0), (-solder_arm_tool_screws_distance/2, 0)):
            Circle(screw_head_diameter/2, )
    extrude(amount=-7, mode=Mode.SUBTRACT)
    with BuildSketch(bottom.offset(-solder_arm_tool_screws_distance)):
        with Locations((0, 2+solder_iron_diameter/2)):
            Rectangle(9, 9)
    extrude(amount=-solder_iron_holder_height, mode=Mode.SUBTRACT)

with BuildPart() as front_carriage_tensioner:
    with BuildSketch(front_carriage_side):
            Rectangle(front_carriage_tensioner_height, front_carriage_thickness)
            with PolarLocations(front_carriage_tensioner_height/2 + 0.75, 2):
                Triangle(a=front_carriage_thickness/2 - 0.15, A=45, B=45, rotation=45)
            with Locations((front_carriage_tensioner_height/2 - 3, 0), (-front_carriage_tensioner_height/2 + 3, 0)):
                Circle(screw_diameter/2, mode=Mode.SUBTRACT)
    extrude(amount=-front_carriage_tensioner_width, mode=Mode.ADD)

    with BuildSketch(front_carriage_back):
        with Locations((carriage_wheel_horizontal_spacing/2 - 1, 0)):
            Circle(12/2)
    with BuildSketch(front_carriage_back.offset(8)):
        with Locations((carriage_wheel_horizontal_spacing/2 - 1, 0)):
            Circle(8/2)
    loft()

    with BuildSketch(front_carriage_back):
        with Locations((carriage_wheel_horizontal_spacing/2 - 1, 0)):
            Circle(roller_screw_diameter/2)
    extrude(amount=8, both=True, mode=Mode.SUBTRACT)

with BuildPart() as cable_holder:
    with BuildSketch(profile.faces().sort_by(Axis.Z)[-1]) as sketch:
        with Locations((0, -profile_size/2)):
            Rectangle(profile_size - 6, cable_holder_thickness)
        add(profile_slot, mode=Mode.SUBTRACT)
        Rectangle(profile_size - (2*carriage_aligner_inset), profile_size - (2*carriage_aligner_inset), mode=Mode.SUBTRACT)
    extrude(amount=-cable_holder_height, mode=Mode.ADD)

    with BuildSketch(faces().sort_by(Axis.Y)[0]) as front:
        with Locations((0, -cable_holder_height/2 + cable_holder_arm_thickness/2)):
            Rectangle(profile_size - 6, cable_holder_arm_thickness)
    extrude(amount=cable_holder_length)
    with BuildSketch(faces().filter_by(Axis.Y).sort_by(Axis.Y)[1]):
        Circle(screw_diameter/2)
    extrude(amount=-carriage_thickness - carriage_aligner_inset, mode=Mode.SUBTRACT)
    with BuildSketch(faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]):
        with Locations((0, -cable_holder_length/2 + cable_holder_indent_width/2 + 1)):
            Rectangle(profile_size, cable_holder_indent_width)
    extrude(amount=-cable_holder_indent, mode=Mode.SUBTRACT)
    fillet(edges().filter_by(Axis.X).group_by(Axis.Z)[2].sort_by(Axis.X)[-1], 1)
    fillet(edges().filter_by(Axis.X).group_by(Axis.Z)[1], cable_holder_indent*0.9)
    with BuildSketch(faces().filter_by(Axis.Z).group_by(Axis.Z)[-2].sort_by(Axis.Y)[-1]):
        Rectangle(cable_velcro_width, 2)
    extrude(amount=-cable_holder_thickness, mode=Mode.SUBTRACT)

with BuildPart() as lever:
    with BuildSketch(main_carriage.faces().sort_by(Axis.Y)[-1]):
        with Locations((lever_length/2 - bearing_diameter, 0)):
            Rectangle(lever_length, lever_width)
        Circle(screw_diameter/2, mode=Mode.SUBTRACT)
        with Locations((pivot_hole_offset, 0), (lever_length - (bearing_diameter*2), 0)):
            Circle(screw_diameter/2, mode=Mode.SUBTRACT)
    extrude(amount=lever_thickness, mode=Mode.ADD)
    with BuildSketch(main_carriage.faces().sort_by(Axis.Y)[-1]):
        Circle(bearing_diameter/2)
        with Locations((pivot_hole_offset, 0)):
            Circle(bearing_diameter/2)
    extrude(amount=bearing_thickness, mode=Mode.SUBTRACT)
    fillet(edges().filter_by(Axis.Y), 4)

with BuildPart() as lever_secondary:
    with BuildSketch(main_carriage.faces().sort_by(Axis.Y)[-1].offset(-lever_thickness)):
        with Locations((pivot_hole_offset, 0)):
            with Locations((0, lever_secondary_length/2 - bearing_diameter)):
                Rectangle(lever_width, lever_secondary_length)
            Circle(screw_diameter/2, mode=Mode.SUBTRACT)
            with Locations((0, lever_secondary_length - (bearing_diameter*2))):
                Circle(screw_diameter/2, mode=Mode.SUBTRACT)
    extrude(amount=lever_thickness, mode=Mode.ADD)
    with BuildSketch(main_carriage.faces().sort_by(Axis.Y)[-1].offset(-lever_thickness)):
        with Locations((pivot_hole_offset, 0)):
            with Locations((0, lever_secondary_length - (bearing_diameter*2))):
                Circle(bearing_diameter/2)
    extrude(amount=bearing_thickness, mode=Mode.SUBTRACT)
    fillet(edges().filter_by(Axis.Y), 4)

def make_brace(plane, top_length, screw_count):
    with BuildPart() as brace:
            with BuildSketch(plane):
                Rectangle(profile_size-4, foot_brace_bottom_length)
            extrude(amount=top_length)
            with BuildSketch(faces().sort_by(Axis.X)[0]):
                with Locations(Location((0, 0), 0)):
                    with Locations(Location((-foot_brace_bottom_length/2, top_length/2), 20)):
                        Rectangle(20, 30, align=(Align.MAX, Align.MAX))
            extrude(amount=-20, mode=Mode.SUBTRACT)
            with BuildSketch(faces().sort_by(Axis.Y)[-1].offset(-3)):
                Rectangle(profile_size-8, 20)
            extrude(amount=-10, mode=Mode.SUBTRACT)
            with BuildSketch(faces().sort_by(Axis.Y)[-1]):
                with Locations((0, top_length/4), (0, -top_length/4)) if screw_count == 2 else Locations((0, 0)):
                    Circle(screw_diameter/2)
            extrude(amount=-20, mode=Mode.SUBTRACT)
    return brace

with BuildPart() as foot:
    with BuildSketch(Plane.XY):
        Rectangle(profile_size + foot_brace_bottom_length*2 + 0.4, profile_size + foot_brace_bottom_length*2 + 0.4)
        fillet(vertices().group_by(Axis.X)[-1], 8)
        with Locations(Location((-profile_size/2 - foot_brace_bottom_length - 0.2, profile_size/2 + foot_brace_bottom_length + 0.2), 90-foot_angle)):
            Rectangle(foot_length, foot_width, align=(Align.MIN, Align.MAX))
        with Locations(Location((-profile_size/2 - foot_brace_bottom_length - 0.2, -profile_size/2 - foot_brace_bottom_length - 0.2), -90+foot_angle)):
            Rectangle(foot_length, foot_width, align=(Align.MIN, Align.MIN))
        add(profile_slot, mode=Mode.SUBTRACT)
        Rectangle(profile_size/2, profile_size/2, mode=Mode.SUBTRACT)
    extrude(amount=foot_thickness)
    fillet(edges().filter_by(Axis.Z).sort_by(Axis.Y)[:2], 6)
    fillet(edges().filter_by(Axis.Z).sort_by(Axis.Y)[-2:], 6)

    with BuildSketch(faces().filter_by(Axis.X).sort_by(Axis.X)[0]):
        Rectangle(profile_size + foot_brace_bottom_length*2 + 0.4, foot_thickness)
    extrude(amount=15)
    fillet(edges().filter_by(Axis.Z).sort_by(Axis.X)[:2], 8)

    left_brace = make_brace(Plane.XY, foot_brace_top_length, 2)
    left_brace.part.move(Location((0, -profile_size/2 - foot_brace_bottom_length/2 + 0.2, foot_thickness)))
    add(left_brace)

    right_brace = make_brace(Plane.XY, foot_brace_top_length, 2)
    right_brace.part.move(Location((0, profile_size/2 + foot_brace_bottom_length/2 - 0.2, foot_thickness), 180))
    add(right_brace)

    back_brace = make_brace(Plane.XY, foot_brace_top_length, 2)
    back_brace.part.move(Location((-profile_size/2 - foot_brace_bottom_length/2 - 0.2, 0, foot_thickness), -90))
    add(back_brace)

    back_brace = make_brace(Plane.XY, foot_brace_top_length/2, 1)
    back_brace.part.move(Location((profile_size/2 + foot_brace_bottom_length/2 + 0.2, 0, foot_thickness), 90))
    add(back_brace)

front_carriage.part.move(Location((0, 0, 70)))
front_carriage_tensioner.part.move(Location((0, 0, 70)))
tnut.part.move(Location((0, 0, -10)))

with BuildPart() as tester:
    with BuildSketch(Plane.XY):
            Rectangle(8, 30)
    extrude(amount=5)
    top = faces().sort_by(Axis.Z)[-1]
    for x in range(0, 5):
        with BuildSketch(top) as hole:
            with Locations((0, -12.5 + x * 6)):
                Circle(screw_diameter/2)
        extrude(amount=-5, mode=Mode.SUBTRACT)
        with BuildSketch(top) as insert:
            with Locations((0, -12.5 + x * 6)):
                Circle(insert_diameter/2 - (insert_undersizing - 0.1*x))
        extrude(amount=-insert_height, mode=Mode.SUBTRACT)

reset_show()
show(profile, main_carriage, cable_holder, front_carriage, front_carriage_tensioner, tnut, lever, lever_secondary, foot, solder_arm, solder_holder, reset_camera=Camera.KEEP, measure_tools=True, colors=["black", "orange"])

front_carriage.part.export_stl("front_carriage.stl")
front_carriage_tensioner.part.export_stl("front_carriage_tensioner.stl")
solder_arm.part.export_stl("arm.stl")
solder_holder.part.export_stl("holder.stl")
tnut.part.export_stl("tnut.stl")
main_carriage.part.export_stl("main_carriage.stl")
cable_holder.part.export_stl("cable_holder.stl")
lever.part.export_stl("lever.stl")
lever_secondary.part.export_stl("lever_secondary.stl")
foot.part.export_stl("foot.stl")
tester.part.export_stl("tester.stl")