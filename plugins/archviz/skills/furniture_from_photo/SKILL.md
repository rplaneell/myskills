---
name: furniture_from_photo
description: Turn photos of a piece of furniture plus its real measurements into a true size 3D model (.glb) with a verified error. Use when the owner sends furniture photos, a product link or sizes and wants a 3D model of it.
---

# Furniture from photo

## Collect, once, in one message
1. 3 to 6 photos: front, side, three quarter, top if possible. Plain background, even light, camera at half the object's height, no extreme wide angle (see docs/PHOTO_GUIDE.md).
2. Real size in metres: width, depth, height. Two are enough, three are better.
3. Which side is the front, where it will stand, source and licence.

## Choose the route, best first
1. A real model exists (product page 3D view, the owner's catalogue, Sketchfab with CC0 or CC BY). Use it: a real model beats a generated one.
2. Generate from photos with TRELLIS or Hunyuan3D 2 (see docs/GENERATORS.md). Needs an NVIDIA GPU with enough video memory, or a hosted Hugging Face Space. Cloud sessions without a GPU or without access to Hugging Face cannot do this: say so, do not fake it.
3. Simple shapes (table, shelf, box cabinet, armchair with a plain frame): build from the measurements and say it is simplified. `venv/bin/python tools/build_parts.py specs/NAME.parts.json OUT.glb` builds boxes from a spec and textures them with patches cut from the photo (see specs/Tornsborg.parts.json). Mark every part as taken from the drawing or estimated from the photo, then run intake with `--model-kind "simplified build"`.

## Verify, always
1. `venv/bin/python tools/intake.py FILE NAME --width W --depth D --height H --source "..." --licence "..." --photo BEST_PHOTO` (on Windows use `venv/Scripts/python`). The photo lets intake check the colour and add a texture cut from the photo when the model has none. It needs a plain background; with a busy background it says so and adds nothing. Add `--project` to also fit the photo's camera and paint the photo itself onto the faces it sees (tools/project_photo.py): the model then looks like the photo from the photo's angle (the viewer has a Photo angle button). It reports the outline overlap (IoU); below 0.85 it projects nothing and says why. It is not a scan, and hidden sides keep the surface tile.
2. Read the verdict: pass (3 percent or less), warn (up to 6), reject (more). Never stretch a rigid object to hide a bad shape; regenerate. `--stretch` is for soft goods only.
3. Read the lines Triangles, Texture, Colour and Accepted. A model is accepted only with a size verdict of pass or warn, 200000 triangles or fewer (intake reduces the mesh and records it), a texture, and a colour that is not "different" (delta E above 20). A photo made tile is a surface sample, not a projection of the whole photo, so say so in the report.
4. `venv/bin/python tools/viewer.py models/NAME/NAME.glb --photo BEST_PHOTO --open` opens a page where the owner can turn the textured model, see the photo beside it and read the errors. Always give the owner this page.
5. `venv/bin/python tools/preview.py models/NAME/NAME.glb` and look at the sheet: proportions against the photos, front faces minus Y (use `--rotate` if not), stands on the floor.
6. Commit the model, meta.json and CATALOG.md row.

## Report to the owner
A table: piece, wanted size, achieved size, error percent, source, licence, verdict. Say plainly what is real, generated or simplified.
