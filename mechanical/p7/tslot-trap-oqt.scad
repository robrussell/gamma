include <BOSL2/std.scad>
include <BOSL2/screws.scad>

module draw_part() {
    diff() {
        up(3) cube([50, 20, 8], anchor=BOT) {
            // Bit that fits inside the T-slot.
            position(BOT) cube([50, 6, 4], anchor=TOP);
            // Middle bit for the camera mount.
            tag("remove") position(BOT) nut_trap_side(15, "1/4-20", spin=90, anchor=BOT)
                screw_hole(length=20, anchor=BOT);
            // Shoulders with holes for the T-nuts.
            tag("remove") xcopies(l=40, n=2)
                // Lowered shoulder.
                position(TOP) cube([15, 20, 4], anchor=TOP)
                    position(BOT) #screw_hole("M5", length=6, anchor=TOP)
                        // Cutout for the head of the T-nut.
                        position(BOT) cube([6, 6, 3], anchor=TOP);
        }
    }
}

// Called in fit-test.scad and printable.scad.
// #draw_part();
