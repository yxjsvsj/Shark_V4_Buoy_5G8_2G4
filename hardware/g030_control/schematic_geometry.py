from __future__ import annotations

from collections import defaultdict


def cross(a, b, c):
    return (b["x"] - a["x"]) * (c["y"] - a["y"]) - (b["y"] - a["y"]) * (c["x"] - a["x"])


def on_segment(a, b, p, eps=1e-6):
    if abs(cross(a, b, p)) > eps:
        return False
    return (
        min(a["x"], b["x"]) - eps <= p["x"] <= max(a["x"], b["x"]) + eps
        and min(a["y"], b["y"]) - eps <= p["y"] <= max(a["y"], b["y"]) + eps
    )


def segments_contact(s1, s2, eps=1e-6):
    a = {"x": s1["x1"], "y": s1["y1"]}
    b = {"x": s1["x2"], "y": s1["y2"]}
    c = {"x": s2["x1"], "y": s2["y1"]}
    d = {"x": s2["x2"], "y": s2["y2"]}
    o1 = cross(a, b, c)
    o2 = cross(a, b, d)
    o3 = cross(c, d, a)
    o4 = cross(c, d, b)
    if abs(o1) <= eps and on_segment(a, b, c, eps):
        return "endpoint" if c == a or c == b else "overlap"
    if abs(o2) <= eps and on_segment(a, b, d, eps):
        return "endpoint" if d == a or d == b else "overlap"
    if abs(o3) <= eps and on_segment(c, d, a, eps):
        return "endpoint" if a == c or a == d else "overlap"
    if abs(o4) <= eps and on_segment(c, d, b, eps):
        return "endpoint" if b == c or b == d else "overlap"
    if (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0):
        return "cross"
    return None


def check(segments, pins):
    conflicts = []
    by_net = defaultdict(list)
    for seg in segments:
        by_net[seg["net"]].append(seg)
    for i, s1 in enumerate(segments):
        for s2 in segments[i + 1 :]:
            if s1["net"] == s2["net"]:
                continue
            kind = segments_contact(s1, s2)
            if kind:
                conflicts.append(
                    {
                        "type": kind,
                        "nets": [s1["net"], s2["net"]],
                        "segments": [
                            [s1["ref"], s1["pin"], s1["x1"], s1["y1"], s1["x2"], s1["y2"]],
                            [s2["ref"], s2["pin"], s2["x1"], s2["y1"], s2["x2"], s2["y2"]],
                        ],
                    }
                )
    for seg in segments:
        ends = [
            {"x": seg["x1"], "y": seg["y1"]},
            {"x": seg["x2"], "y": seg["y2"]},
        ]
        for pin in pins:
            if pin["ref"] == seg["ref"] and str(pin["pin"]) == str(seg["pin"]):
                continue
            if pin["net"] == seg["net"]:
                continue
            for end in ends:
                if on_segment(
                    {"x": seg["x1"], "y": seg["y1"]},
                    {"x": seg["x2"], "y": seg["y2"]},
                    {"x": pin["x"], "y": pin["y"]},
                ):
                    conflicts.append(
                        {
                            "type": "pin_contact",
                            "nets": [seg["net"], pin["net"]],
                            "pin": [pin["ref"], pin["pin"], pin["x"], pin["y"]],
                            "segment": [seg["ref"], seg["pin"], seg["x1"], seg["y1"], seg["x2"], seg["y2"]],
                        }
                    )
                break
    per_net = {}
    for net, segs in sorted(by_net.items()):
        per_net[net] = {
            "segments": len(segs),
            "pins": len([p for p in pins if p["net"] == net]),
        }
    return {
        "ok": not conflicts,
        "segments": len(segments),
        "nets": len(by_net),
        "conflicts": conflicts,
        "perNet": per_net,
    }
