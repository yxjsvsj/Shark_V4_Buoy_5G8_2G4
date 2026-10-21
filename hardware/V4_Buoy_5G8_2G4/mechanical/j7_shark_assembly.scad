$fn = 40;

pcb_x = 26;
pcb_y = 46;
hull_id = 35;
hull_len = 120;
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
    color("#1f6f3f") translate([-pcb_x/2, -pcb_y/2, -1.6]) cube([pcb_x, pcb_y, 1.6]);
}

module connector() {
    color("#b87333") translate([-conn_l/2, pcb_y/2-conn_w, 0]) rounded_box(conn_l, conn_w, conn_h, 0.5);
    for (x=[-5:2:5]) color("#303030") translate([x, pcb_y/2-conn_w/2, conn_h]) cylinder(r=0.35, h=0.1);
}

module cable(points, r) {
    for (i=[0:len(points)-2]) hull() {
        translate(points[i]) sphere(r=r);
        translate(points[i+1]) sphere(r=r);
    }
}

module shark_hull() {
    color("#7fb8d8", 0.18) translate([0,0,-15]) rotate([90,0,0]) cylinder(d=hull_id, h=hull_len, center=true);
}

module gland() {
    color("#555555") translate([0, pcb_y/2+12, 3]) rotate([90,0,0]) cylinder(d=10, h=14, center=true);
}

module cable_run() {
    z0 = conn_h + 8;
    p = [for (a=[0:5:90]) [0, pcb_y/2+3 + bend_r - bend_r*cos(a), z0 + bend_r*sin(a)]];
    q = [for (z=[z0+bend_r:10:z0+bend_r+45]) [0, pcb_y/2+3 + bend_r, z]];
    cable(concat(p, q), cable_r);
}

pcb();
connector();
shark_hull();
gland();
cable_run();
