include <BOSL2/std.scad>
include <BOSL2/screws.scad>

module pcb_tray() {
    diff() {
      cuboid([57, 66, 3], rounding=1.5, edges=["Z"], anchor=BOT) {
        tag("remove") xflip_copy(offset=12) yflip_copy(offset=15)
          position(BOT) cuboid([18, 21, 8], rounding=1.5, edges=["Z"], anchor=BOT);
        position(TOP) rect_tube(size=[57, 66], rounding=1.5, irounding=1.5, wall=7.5, h=3, anchor=BOT)
          xflip_copy(offset=24.5) yflip_copy(offset=29)
            cuboid([8, 8, 5], rounding=1.5, edges=["Z"], anchor=BOT)
              tag("remove") position(TOP) screw_hole("M2.5", length=8, anchor=TOP)
                position(BOT) nut_trap_inline(2, anchor=TOP);
      }
    }
}

module tslot_connection() {
  diff() {
    xcopies(l=75, n=2)
      cuboid([30, 20, 3], rounding=1.5, edges=["Z"], anchor=BOT) {
        // Bit that fits inside the T-slot.
        position(BOT) cuboid([30, 6, 4], rounding=1.5, edges=["Z"], anchor=TOP);
        // Shoulders with holes for the T-nuts.
        tag("remove") position(TOP) screw_hole("M5", length=3, anchor=TOP)
          // Cutout for the head of the T-nut.
          position(BOT) cube([6, 6, 4], anchor=TOP);
      }
  }
}

module draw_part() {
  tslot_connection();
  pcb_tray();
}

// Called in fit-test.scad and printable.scad.
// #draw_part();
