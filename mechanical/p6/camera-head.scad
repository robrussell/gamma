$fn=64;
// Camera head for gammacam P6. Back cover in camera-cover.scad.
// Mounting box which mates the Raspberry Pi HQ camera to the 
// Arducam B0091 CSI-to-HDMI Adapter.
difference() {
  union() {
    // Back
    linear_extrude(height=2)
      offset(r=2.5)
        square([33,33],center=true);
    // Walls
    translate([0,0,-10])
      linear_extrude(height=18)
        difference() {
          offset(r=2.5+2)
            square([33,33],center=true);
          offset(r=2.5)
            square([33,33],center=true);
          // Bottom notch
          translate([-11,-22])
            square([22,8]);
        }
    // Outer screw bosses
    linear_extrude(height=5)
      union()
        for(x=[-15.5,15.5])
          for(y=[-15.5,15.5])
            translate([x,y])
              offset(r=2.5)
                square(2.5, center=true);
    // Fill in on sides
    for(x=[-16, 16])
      translate([x, 0, -8])
        linear_extrude(height=8)
          square([6,40], center=true);
    // HDMI connector
    translate([0,16,-6.5])
      difference() {
        linear_extrude(height=6.5)
          offset(r=2.5)
            square([18.5, 17], center=true);
        translate([0,3,-1])
          linear_extrude(height=10)
            offset(r=2.5)
              square([14, 17], center=true);
      }
    // Inner screw bosses, fit around FFP cable
    translate([0,4.5,-6.5])
      linear_extrude(height=6.5)
        for(x=[-11, 11])
          translate([x,-15])
            square([4, 17], center=true);
    }
    // Top notch (near HDMI)
    translate([0,0,-11])
      linear_extrude(height=12)
        translate([0,26])
          square([26,15],center=true);
    // Top notch (near test points)
    translate([0,0,-1])
      linear_extrude(height=12)
        translate([0,26])
          square([22,15],center=true);
    // Bottom notch (near FFP cable)
    translate([0,0,-12])
      linear_extrude(height=22)
        translate([0,-18])
          square([23,15],center=true);
    // TRS jack recess
    translate([17.5,2,-11])
      linear_extrude(height=8)
        square([10,18],center=true);
    // Outer screw holes
    translate([0,0,-12])
      linear_extrude(height=18)
        union()
          for(x=[-15,15])
            for(y=[-15,15])
              translate([x,y])
                circle(d=2.6);
    // Inner screw holes
    translate([0,0,-10])
      linear_extrude(height=20)
        union()
          for(x=[-10.5,10.5])
            for(y=[-4.5,8])
              translate([x,y])
                circle(d=1.7);
}
