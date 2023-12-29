$fn=64;

// Bracket to secure the Arducam B0091 CSI-to-HDMI Adapter board above the
// Raspberry Pi 4B USB-A ports.

difference() {
  union() {
    // Walls
    linear_extrude(height=2)
      difference() {
        offset(r=2.5+2)
          square([56,85],center=true);
      offset(r=2.5+2)
        translate([-27,-18,0])
          square([85,60],center=true);
    }
    // HDMI connector riser
    translate([15,27+16,0])
      difference() {
        linear_extrude(height=6.5)
          square([23.5, 22], center=true);
      }
    // Inner screw bosses, fit around FFP cable
    translate([15,27+4.5,0])
      linear_extrude(height=6.5) {
        for(x=[11,-11])
          translate([x,-9])
            square([5, 5], center=true);
        for(x=[12.5,-12.5])
          translate([x, 2])
            square([2, 26], center=true);
      }
    }
    // Top notch (near HDMI)
    translate([15,27,0])
      linear_extrude(height=12)
        translate([0,26])
          square([27,15],center=true);
    // Inner screw holes
    translate([15,27,-1])
      linear_extrude(height=10)
        union()
          for(x=[-10.5,10.5])
            for(y=[-4.5,8])
              translate([x,y])
                circle(d=1.7);
    // HDMI connector cutout
    translate([15,27+17,0])
        translate([0,3,-1])
          linear_extrude(height=10)
            square([19, 22], center=true);
    // FFP cable cutout
    #translate([15, 4, -2])
      linear_extrude(height=5)
        square([24, 10], center=true);
    // Holes for RPi mounting
    for(hole=[[-24.5,-39], [-24.5,19], [24.5,-39], [24.5,19]])
      #translate([hole[0], hole[1], -5])
        cylinder(d=2.8, h=20);
}
