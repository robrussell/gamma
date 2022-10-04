$fn = 64;

// Lens cap designed to fit Arducam 120 Degree Ultra Wide Angle CS Lens (LN051).

 module CircularArray(
   r,
   h,
   numbers
   ){

   for(i = [0:numbers-1]){
      translate([r*cos(2*PI/numbers*i), r*sin(2*PI/numbers*i), h/2])
         rotate(360/numbers*i)
         linear_extrude(h){
            square(size=[3,3], center=true);
         }
      }
   }

union() {
  // Base
  translate([0,0,0.5]) 
    cylinder(h=1, d=30, center=true);
  // Inner support
  difference() {
    // Circle resting on the lens barrel.
    translate([0,0,3+0.5])
      cylinder(h=6, d=29, center=true);
    // Subtract a circle the diameter of the lens itself.
    cylinder(h=20, d=24, center=true);
  }
  // Grippers
  difference() {
    linear_extrude(height=12)
      for(s=[0:30:360]) {
        rotate(a=s, v=[0,0,1])
          translate([14.75,0,0])
            offset(r=0.4)
              polygon([[-0.5,-3], [0.5,-0.5], [0.5,0.5], [-0.5,3]]);
      }
    // Subtract a circle the diameter of the lens barrel.
    translate([0,0,8]) 
      cylinder(h=13, d=28, center=true);
  }
}
