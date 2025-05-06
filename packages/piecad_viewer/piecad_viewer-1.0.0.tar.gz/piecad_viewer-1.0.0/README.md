# Viewer for "Easy as Pie" CAD (Piecad)

[Piecad](https://github.com/briansturgill/Piecad) is a CAD API used to construct 3D models in [Python](https://www.python.org).
Its primary focus is the creation of models for 3D printing.

To use Piecad-Viewer, run `piecad-viewer` and then use the `view` function in Piecad,  which works like a 3d `print` (also does 2D).
Piecad-Viewer allows you to see the output from multiple `view` calls.

Type `h` in the Piecad-Viewer window for a list of commands.

To install:

```sh
pip install piecad_viewer

# This will install the script:
piecad_viewer

```

## CREDITS

Piecad viewer is based on [trimesh](https://github.com/mikedh/trimesh)'s viewer, which in
turn is based on version 1 of [pyglet](https://github.com/pyglet/pyglet).
