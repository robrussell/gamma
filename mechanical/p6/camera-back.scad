$fn=64;
// Back cover for gammacam P6 camera head.
difference() {
  union() {
    linear_extrude(height=7)
      offset(r=2.5)
        square([33,33],center=true);
    // Walls
    linear_extrude(height=5)
      difference() {
        offset(r=2.5+2)
          square([33,33],center=true);
        offset(r=2.5)
          square([33,33],center=true);
      }
    }
    // Main PCB recess
    translate([0,7.5,5])
      linear_extrude(height=5)
        square([26,29],center=true);
    // TRS jack recess
    translate([4,2,1])
      linear_extrude(height=6)
        square([18,7],center=true);
    // Outer screw holes
    translate([0,0,-1])
      linear_extrude(height=10)
        union()
          for(x=[-15,15])
            for(y=[-15,15])
              translate([x,y])
                circle(d=2.6);
    // Inner screw holes
    translate([0,0,-1])
      linear_extrude(height=10)
        union()
          for(x=[-10.5,10.5])
            for(y=[-4.5,8])
              translate([x,y])
                circle(d=1.7);
    // Side notch
    translate([18, 2, -1])
      linear_extrude(height=10)
        square([12,18], center=true);
}
