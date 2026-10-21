$fn = 40;

pcb_x = 30;
pcb_y = 30;
shell_d = 55;
shell_h = 70;
conn_l = 13.9;
conn_w = 4.5;
conn_h = 8;
cable_od = 5.5;
cable_r = cable_od / 2;
bend_r = 30;

module rounded_box(x, y, z, r=1) {
    hull() {
        for (dx=[-x/2+r, x/2-r], dy=[-y/2+r, y/2-r])
            translate([dx, dy, 0]) cylinder(r=r, h=z);
    }
}

module pcb() {
    color("#1f6f3f") translate([-pcb_x/2, -pcb_y/2, 4]) cube([pcb_x, pcb_y, 1.6]);
}

module connector() {
    color("#b87333") translate([-conn_l/2, -pcb_y/2-conn_w, 4]) rounded_box(conn_l, conn_w, conn_h, 0.5);
    for (x=[-5:2:5]) color("#303030") translate([x, -pcb_y/2-conn_w/2, 4+conn_h]) cylinder(r=0.35, h=0.1);
}

module cable(points, r) {
    for (i=[0:len(points)-2]) hull() {
        translate(points[i]) sphere(r=r);
        translate(points[i+1]) sphere(r=r);
    }
}

module shell() {
    color("#7fb8d8", 0.18) cylinder(d=shell_d, h=shell_h);
    color("#555555") translate([0,0,-2]) cylinder(d=14, h=8);
    color("#555555") translate([0,0,shell_h-3]) cylinder(d=22, h=5);
}

module vtx() {
    color("#aa2222") translate([-12, 4, 34]) cube([25, 25, 5]);
    color("#bbbbbb") translate([0, 18, 39]) cylinder(d=1.2, h=22);
}

module cable_run() {
    z0 = 12;
    p = [for (a=[0:5:90]) [0, -pcb_y/2-conn_w-3 - (bend_r - bend_r*cos(a)), z0 + bend_r*sin(a)]];
    q = [for (z=[z0+bend_r:10:z0+bend_r+18]) [0, -pcb_y/2-conn_w-3-bend_r, z]];
    cable(concat(p, q), cable_r);
}

shell();
pcb();
connector();
vtx();
cable_run();
