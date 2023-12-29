$fn = 64;

// Tray to secure devices on frame built from 15mm rod. Centers of holes are
// approximately 180mm apart. Tray is wide enough to hold the TP Link
// TL-SG108 8-port switch, approximately 155mm.

// axis - rotation axis for the primary shape
//        X-aligned: [0, 1, 0], u is y, v is z
//        Y-aligned: [1, 0, 0], u is x, v is z
//        Z-aligned: [0, 0, 0], u is x, v is y
// min_u, max_u, step_u, min_v, max_v, step_v -
//        Minimum, maximum, increment size for
//        each axis. For example, if Z-aligned then
//        u is the x-axis and v is the y-axis.
//        These just set up for loops for each 
//        axis.
module punchouts(axis, min_u, step_u, max_u, min_v, step_v, max_v) {
  if (true) { // Set to true for punchouts, false for fast renders.
    for (u=[min_u:step_u:max_u]) {
      for (v=[min_v:step_v * 2:max_v]) {
        rotate(a=90, v=axis)
          translate([u, v, 0])
            cylinder(h=6, r=6, center=true, $fn=6);
        if (((step_u / 2) + u < max_u) && (v + step_v < max_v)) {
          rotate(a=90, v=axis) 
            translate([ (step_u / 2) + u, v + step_v, 0])
              cylinder(h=6, r=6, center=true, $fn=6);
        }
      }
    }
  }
}

difference() {
    union() {
        // Bottom
        linear_extrude(height = 2)
          offset(r=3)
            square([ 168, 74], center = true);
        // Walls
        linear_extrude(height = 16) difference() {
            square([ 165, 80 ], center = true);
            square([ 165 - 4, 90 ], center = true);
        }
        // Tabs for 15mm rod.
        for (x=[-90+8.5,90-8.5]) {
          translate([ x, 0, 1])
            cylinder(h=2, r=18, center=true, $fn=64);
        }
    }
    // Holes for 15mm rod.
    for (x=[-90,90]) {
      translate([ x, 0, 0])
        cylinder(h=6, r=7.5, center=true, $fn=64);
    }
    for (x=[-80, 80]) {
      translate([x, 0, 0]) 
        rotate(a=90, v=[1, 0, 0])
          punchouts([0, 1, 0], -30, 15, 30, 8, 10, 16);
    }
    // Z-aligned holes
    punchouts([0, 0, 0], -70, 20, 70, -30, 10, 30);
}
