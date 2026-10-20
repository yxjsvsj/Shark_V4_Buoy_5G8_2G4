$fn = 48;
show_buoy = true;

connector_length = 13.9;
connector_width = 4.5;
mated_height = 8.0;
cable_od = 5.5;
cable_r = cable_od / 2;
bend_r = 30;
board_x = 26;
board_y = 46;
buoy_d = 55;
buoy_h = 70;

module rounded_box(x, y, z, r=0.4) {
    hull() {
        for (dx=[-x/2+r, x/2-r], dy=[-y/2+r, y/2-r])
            translate([dx, dy, 0])
                cylinder(r=r, h=z);
    }
}

module cable_tube(points, r) {
    for (i=[0:len(points)-2])
        hull() {
            translate(points[i]) sphere(r=r);
            translate(points[i+1]) sphere(r=r);
        }
}

module cable_path(z_start=8) {
    p = [for (a=[0:5:90])
        [0, bend_r - bend_r*cos(a), z_start + 10 + bend_r*sin(a)]];
    q = [for (y=[bend_r:10:85]) [0, y, z_start + 10 + bend_r]];
    cable_tube(concat(p, q), cable_r);
}

module board() {
    color("#1f6f3f")
        translate([-board_x/2, -board_y/2, -1.6])
            cube([board_x, board_y, 1.6]);
}

module connector_envelope() {
    color("#b87333", 0.9)
        translate([-connector_length/2, -connector_width/2, 0])
            rounded_box(connector_length, connector_width, mated_height, 0.5);
    for (x=[-5:2:5])
        color("#303030")
            translate([x, 0, mated_height])
                cylinder(r=0.35, h=0.1);
}

module cable() {
    color("#202020", 0.95) cable_path();
}

module buoy_shell() {
    color("#7fb8d8", 0.18)
        translate([0, 0, -8])
            cylinder(d=buoy_d, h=buoy_h);
}

module dimensions() {
    color("#ffcc00")
        translate([0, -12, 0])
            cube([connector_length, 0.4, 0.2]);
    color("#ffcc00")
        translate([0, -15, 0])
            cube([0.4, 0.4, mated_height]);
}

board();
connector_envelope();
cable();
if (show_buoy) buoy_shell();
dimensions();
