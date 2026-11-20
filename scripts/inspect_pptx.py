"""Inspect native slide, media, and entrance-fade structure without modifying a deck."""

import argparse
import json
import posixpath
import sys
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile


NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "cx": "http://schemas.microsoft.com/office/drawing/2014/chartex",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def tag(prefix, name):
    return f"{{{NS[prefix]}}}{name}"


def read_xml(package, part):
    return ET.fromstring(package.read(part))


def relationships(package, part):
    directory, filename = posixpath.split(part)
    rels_part = posixpath.join(directory, "_rels", filename + ".rels")
    try:
        root = read_xml(package, rels_part)
    except KeyError:
        return {}
    return {node.get("Id"): node for node in root.findall("rel:Relationship", NS)}


def internal_target(source, rel, part_names):
    if rel is None or rel.get("TargetMode") == "External":
        return None
    target = unquote(rel.attrib["Target"])
    if target.startswith("/"):
        path = posixpath.normpath(target.lstrip("/"))
    else:
        path = posixpath.normpath(posixpath.join(posixpath.dirname(source), target))
    return path if path in part_names else None


def relationship_kind(rel):
    return rel.get("Type", "").rsplit("/", 1)[-1] if rel is not None else ""


def speaker_notes_present(package, source, rels, part_names):
    for rel in rels.values():
        if relationship_kind(rel) != "notesSlide":
            continue
        notes = internal_target(source, rel, part_names)
        if notes:
            for shape in read_xml(package, notes).findall(".//p:sp", NS):
                placeholder = shape.find("p:nvSpPr/p:nvPr/p:ph", NS)
                if placeholder is not None and placeholder.get("type") == "body":
                    if any(t.text and t.text.strip() for t in shape.findall("p:txBody//a:t", NS)):
                        return True
    return False


def embedded_pictures(shape, embedded_by_id):
    result = set()
    for picture in shape.iter(tag("p", "pic")):
        for blip in picture.findall("p:blipFill/a:blip", NS):
            part = embedded_by_id.get(blip.get(tag("r", "embed")))
            if part:
                result.add(part)
    return result


def fade_targets(slide, embedded_by_id):
    by_id = {}
    for shape in slide.iter():
        info = shape.find("./*/p:cNvPr", NS)
        if info is not None:
            by_id[info.get("id")] = (shape, info.get("name", ""))
    targets = []
    for effect in slide.findall(".//p:timing//p:animEffect", NS):
        if effect.get("transition") != "in" or effect.get("filter", "").lower() != "fade":
            continue
        for target in effect.findall("p:cBhvr/p:tgtEl/p:spTgt", NS):
            shape_id = target.get("spid")
            if shape_id in by_id:
                shape, name = by_id[shape_id]
                targets.append({
                    "shape_id": shape_id,
                    "shape_name": name,
                    "contains_embedded_picture": bool(embedded_pictures(shape, embedded_by_id)),
                })
    return targets


def transition_name(slide):
    transition = slide.find(".//p:transition", NS)
    if transition is not None:
        for child in transition:
            name = child.tag.rsplit("}", 1)[-1]
            if name not in ("sndAc", "extLst"):
                return name
    return None


def summarize_slide(package, part, number, part_names):
    slide = read_xml(package, part)
    rels = relationships(package, part)
    embedded_by_id = {
        rid: internal_target(part, rel, part_names)
        for rid, rel in rels.items()
        if relationship_kind(rel) == "image"
    }
    chart_count = (
        len(slide.findall(".//p:graphicFrame//c:chart", NS))
        + len(slide.findall(".//p:graphicFrame//cx:chart", NS))
    )
    return {
        "number": number,
        "part": part,
        "transition": transition_name(slide),
        "speaker_notes": speaker_notes_present(package, part, rels, part_names),
        "embedded_images": sorted(embedded_pictures(slide, embedded_by_id)),
        "native_chart_count": chart_count,
        "has_animation_timing": slide.find("p:timing", NS) is not None,
        "entrance_fades": fade_targets(slide, embedded_by_id),
    }


def inspect(path):
    with ZipFile(path) as package:
        part_names = set(package.namelist())
        presentation = "ppt/presentation.xml"
        manifest = read_xml(package, presentation)
        rels = relationships(package, presentation)
        slides = []
        for number, slide_id in enumerate(manifest.findall("p:sldIdLst/p:sldId", NS), 1):
            rel = rels.get(slide_id.get(tag("r", "id")))
            part = internal_target(presentation, rel, part_names)
            if not part or relationship_kind(rel) != "slide":
                raise ValueError(f"Slide {number} has no readable slide part")
            slides.append(summarize_slide(package, part, number, part_names))
        if not slides:
            raise ValueError("Presentation contains no slides in its slide list")
    return {
        "slide_count": len(slides),
        "embedded_image_count": len({name for s in slides for name in s["embedded_images"]}),
        "slides": slides,
    }


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--expect-slides", type=positive_int)
    parser.add_argument("--require-photo-fade", type=positive_int, action="append", default=[],
                        metavar="SLIDE", help="Require an entrance Fade targeting an embedded photo on this slide. Repeat as needed.")
    parser.add_argument("--json", action="store_true", help="Print the result as JSON.")
    args = parser.parse_args()
    try:
        report = inspect(args.pptx)
    except (BadZipFile, ET.ParseError, KeyError, OSError, ValueError) as exc:
        print(f"Cannot inspect {args.pptx}: {exc}", file=sys.stderr)
        return 2

    slides = report["slides"]
    errors = []
    if args.expect_slides is not None and len(slides) != args.expect_slides:
        errors.append(f"Expected {args.expect_slides} slides, found {len(slides)}.")
    for number in sorted(set(args.require_photo_fade)):
        if number > len(slides):
            errors.append(f"Slide {number} does not exist.")
        elif not any(f["contains_embedded_picture"] for f in slides[number - 1]["entrance_fades"]):
            errors.append(f"Slide {number} has no entrance Fade targeting an embedded picture.")
    if args.json:
        print(json.dumps({**report, "errors": errors}, ensure_ascii=False, indent=2))
    else:
        print(f"{len(slides)} slides · {report['embedded_image_count']} distinct embedded image parts")
        for slide in slides:
            photo_fades = [f["shape_name"] or f["shape_id"] for f in slide["entrance_fades"]
                           if f["contains_embedded_picture"]]
            print(
                f"{slide['number']:02d}  transition={slide['transition'] or 'none'}  "
                f"notes={'yes' if slide['speaker_notes'] else 'no'}  "
                f"timing={'yes' if slide['has_animation_timing'] else 'no'}  "
                f"images={len(slide['embedded_images'])}  charts={slide['native_chart_count']}  "
                f"photo fades={', '.join(photo_fades) or '-'}"
            )
        for problem in errors:
            print(problem, file=sys.stderr)
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
