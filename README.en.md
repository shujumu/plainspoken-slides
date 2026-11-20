# Plainspoken Slides · 最直白的汇报PPT

[中文](README.md) · [MIT](LICENSE)

An Agent Skill for turning Word documents, notes, and data into an editable PowerPoint briefing. Ground the story with real photos, make one point per slide, and connect key scenes with native crossfades. Use it for project updates, case studies, proposal reviews, and class presentations.

## Install

From your project directory, run the following command with the [skills CLI](https://github.com/vercel-labs/skills). It installs the skill in the project scope for Codex.

```sh
npx skills add shujumu/plainspoken-slides --skill plainspoken-slides -a codex
```

For a manual install, download the repository, name the folder `plainspoken-slides`, and copy the whole folder into your project's `.agents/skills/` or your user's `~/.agents/skills/`. Open a new Codex session and invoke `$plainspoken-slides`. Other [Agent Skills](https://agentskills.io/specification) hosts can load the folder from their own skill directory.

- Web image research requires a host with browser or search access. You can also provide the images yourself.
- PPTX creation requires a local or connected presentation exporter. [PPT Master](https://github.com/hugohe3/ppt-master) is the recommended route. The native photo crossfade workflow was exercised with [v6.10.0](https://github.com/hugohe3/ppt-master/releases/tag/v6.10.0).
- The bundled checker requires Python 3.9 or newer. Use the target presentation player to confirm live playback or render a motion sample.

## Example prompt

> Use $plainspoken-slides. Read the attached pilot report and implementation plan and make an editable 15-slide PPTX for a project review. Explain the initial bottleneck, what each party did, the verified outcomes, and the next target. Find and credit real official photos. Use photo backgrounds on the cover and chapter breaks, and crossfade from the worksite to the launch event on the same slide. Embed the photos for offline presentation, include speaker notes, and keep the budget chart editable.

For revisions, give the preservation and change scope, for example, “Keep the facts and slide order. Rework the photo backgrounds on slides 1, 5, and 12, and check the playback of the crossfade on slide 5.”

## Workflow

| Step | Output and check |
| --- | --- |
| 1. Set the brief | Confirm source files, audience, length, names, dates, and playback environment |
| 2. Outline the story | Assign one point per slide, trace key facts, and label measurements, estimates, and targets |
| 3. Research images | Verify the parent page, captions, creator, and usage terms before selecting the original |
| 4. Design and build | Use photo-led anchors, readable evidence slides, native text and shapes, and editable charts |
| 5. Animate the key scenes | Place two photographs in the same frame, fade the incoming picture in, and keep an independent scrim behind the text |
| 6. Export and verify | Check the actual file, review rendered slides, and inspect a representative motion sequence at its start, midpoint, and end |

A **slide Fade** takes place between slides. A **photo crossfade** takes place between two pictures on the same slide. Separate, editable PowerPoint layers make it possible to adjust the composition, title, and animation timing after delivery.

See [Research and storyboarding](references/research-and-storyboard.md) and [Photo motion and export](references/photo-motion-and-export.md) for the full workflow.

## Inspect a built deck

Run this from the repository and substitute your actual file and slide numbers.

```sh
python scripts/inspect_pptx.py "report.pptx" --expect-slides 15 --require-photo-fade 5
```

The script reports slide order, transitions, speaker notes, embedded images, chart objects, animations, and targets. Use `--json` for machine-readable output. Missing requested slide counts or photo fades produce a nonzero exit code. This checks the presence of native animation and its target. Play or render the deck to verify the visible crossfade.

## License and credits

The skill, documentation, and scripts are released under the [MIT License](LICENSE). Photos, data, and brand assets obtained separately retain their own terms. PPT Master is maintained independently by its upstream project. [PPT Master](https://github.com/hugohe3/ppt-master) · [Agent Skills specification](https://agentskills.io/specification)
