include <BOSL2/std.scad>
include <BOSL2/screws.scad>

module draw_part() {
    diff() {
        cuboid([26, 24, 10], rounding=1, edges=["Z"], anchor=BOT) {
          position(TOP) back(3.5) xcopies(l=21, n=2) ycopies(l=12.5, n=2)
            cuboid([4, 4, 2], rounding=1, edges=["Z"], anchor=BOT)
              tag("remove") position(TOP) screw_hole("M2", length=12, anchor=TOP)
                position(BOT) nut_trap_inline(2);
          tag("remove") position(TOP) down(1) screw_hole("1/4-20", length=20, anchor=TOP)
            position(TOP) nut_trap_side(15, poke_len=20, anchor=TOP);
        }
    }
}

// Called in fit-test.scad and printable.scad.
// #draw_part();
