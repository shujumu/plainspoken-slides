# Photo motion and export

Read this when the output needs an editable PPTX, native photo crossfades, or playback verification.

## Three ways to use fading

| Effect | What it changes | When to use it |
| --- | --- | --- |
| Between-slide Fade | The outgoing slide blends into the next slide | Keep continuity between slides in a section |
| Same-slide photo crossfade | The incoming picture gains opacity over an already visible picture | Move from place to event, before to after, or context to a key visual |
| Object fade-in | A photo, chart annotation, or text group appears while the slide stays in place | Give the audience time to read in the right order |

A checker can confirm the target and timing exist in the file. A still preview shows only the finished composition. It cannot show the blend or prove which effects a player will reproduce.

## Build a same-slide crossfade

1. Put the outgoing photo below the incoming photo. Align their visible frames and choose a purposeful crop for each. Use an embedded picture or a slide-local group that holds a picture as the incoming object. PowerPoint's actual slide-background fill is suitable for a fixed backdrop, but an animation must target a movable slide object.
2. Place a separate, stationary gradient scrim above both pictures and the text above it. Select the scrim for legibility on both images and through the overlap. Keep the text and photo editable as separate objects.
3. Apply an entrance Fade to the incoming picture. Keep the outgoing picture visible underneath; when the incoming photo has a transparent region, fill or crop the incoming frame intentionally. Time the headline to join the photo, without forcing an additional click when the presenter expects automatic entry on the slide. Around 0.7–1.2 seconds for a scene change and 0.3–0.6 seconds for text are useful starting points. Retain manual slide advance unless the user asks for a self-running deck.
4. Make the primary visual change easy to see. Keep credits visible only when their attribution stays correct. A combined credit can name both photos when both are present in the blend.

## PPT Master route

The workflow was exercised with [PPT Master v6.10.0](https://github.com/hugohe3/ppt-master/releases/tag/v6.10.0). Load and follow the installed version's own routing and commands. Respect a different backend if the user chose one.

In a flat SVG-first project, use one stable root group for each animated photo and its own bounds. If a full-bleed group intentionally sits underneath other groups, declare its structural framing role using the exporter’s documented semantic marker. For PPT Master v6.10.0, a `data-pptx-role="decoration"` slide-local group is overlap-exempt and still animatable when explicitly named in `animations.json`. Do not mark the photo as an actual slide background if it must animate. Avoid wrappers that export with no animation target.

Example for a pair of native photo layers and a separate title:

```xml
<g id="photo-before" data-pptx-role="decoration" data-pptx-bounds="0 0 1280 720">
  <image href="../images/site.jpg" x="0" y="0" width="1280" height="720" preserveAspectRatio="xMidYMid slice"/>
</g>
<g id="photo-after" data-pptx-role="decoration" data-pptx-bounds="0 0 1280 720">
  <image href="../images/event.jpg" x="0" y="0" width="1280" height="720" preserveAspectRatio="xMidYMid slice"/>
</g>
```

Keep the scrim and visible `headline` outside these groups. Declare both images in the project resource plan, with adaptive cropping if they use `slice`. Add motion overrides for the actual SVG basename and group IDs:

```json
{
  "defaults": {
    "transition": {"effect": "fade", "duration": 0.5},
    "animation": {"effect": "none"}
  },
  "slides": {
    "P02-scene": {
      "groups": {
        "photo-after": {"effect": "entrance_fade", "order": 1, "duration": 1.0, "trigger": "after-previous"},
        "headline": {"effect": "entrance_fade", "order": 2, "duration": 0.4, "trigger": "with-previous", "delay": 0.25}
      }
    }
  }
}
```

Run the route’s project, SVG and animation checks before exporting, and renew the final SVG quality report after any SVG edit. On the verified version, common commands are:

```sh
python <ppt-master-dir>/scripts/project_manager.py validate <project-dir>
python <ppt-master-dir>/scripts/svg_quality_checker.py <project-dir> --canonical-authoring --stage final --json
python <ppt-master-dir>/scripts/animation_config.py validate <project-dir>
python <ppt-master-dir>/scripts/total_md_split.py <project-dir>
python <ppt-master-dir>/scripts/finalize_svg.py <project-dir>
python <ppt-master-dir>/scripts/svg_to_pptx.py <project-dir>
```

Use the note splitter only when the project uses the total-notes flow. Follow the installed route for any earlier quality gates and for export flags. For instance, native charts need eligible markers and the native-chart export option. If a selected exporter cannot write native motion, preserve the editable static layout and disclose the limitation, or switch to an authorized backend that can.

## Acceptance checks

- Open the exported deck and inspect its actual fonts, crops, page count, notes and sources. A web-rendered SVG preview and a PowerPoint-rendered slide can differ.
- Use the checker for package evidence. With `--require-photo-fade 2`, the file must contain an entrance Fade targeting a native picture or a group that contains an embedded picture on slide 2. This includes a picture with a fade on a white background. It does not establish that two layered pictures actually blend.
- For a representative crossfade, play the deck with animations enabled in the intended player. Look for the outgoing picture alone, an intermediate frame with both scenes visible, and the incoming picture settled. If the host permits exporting a short sample from PowerPoint, inspect early, middle, and late frames. Treat checking the timing XML and seeing the motion as separate results.
- Verify offline opening and image display whenever portability matters. Verify playback on another player only when you have that player. When a tool or player is unavailable, report the strongest check completed.
