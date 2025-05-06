import pyglet
from . import server
from threading import Thread, Lock
import json
import numpy as np
import trimesh
from trimesh.viewer import windowed
import os

view_lock = Lock()


def display_help():
    from tkinter import Tk, Label

    text_l = [
        "",
        "Key        Action",
        "---------------------------------------------",
        "a            Toggle axis.",
        "c            Toggle culling.",
        "f            Toggle fullscreen.",
        "g            Toggle grid.",
        "h, ? or ESC  View/dismiss this help.",
        "q            Quit CAD Viewer.",
        "w            Toggle wireframe.",
        "z            Reset view.",
        "LEFT         Move to the previous object.",
        "RIGHT        Move to the next object.",
        "SHIFT-m      Launch meshlab on current object.",
        "SHIFT-LEFT   Rotate image left.",
        "SHIFT-RIGHT  Rotate image right.",
        "SHIFT-UP     Rotate image up.",
        "SHIFT-DOWN   Rotate image down.",
        "",
    ]
    longest = 0
    for t in text_l:
        if longest < len(t):
            longest = len(t)
    root = Tk()

    def keydown(e):
        ch = e.char
        if ch == "h" or ch == "?" or ord(ch) == 27 or ord(ch) == 13:
            root.destroy()

    root.bind("<KeyPress>", keydown)

    x = (longest) * 14
    y = (len(text_l) + 10) * 14
    root.geometry(f"{x}x{y}")
    root.title("CAD Viewer Help")
    text = Label(
        root,
        height=len(text_l),
        justify="left",
        text="\n".join(text_l),
        font=("Courier", 14, "bold"),
    )
    text.pack(padx=10, pady=10)
    root.mainloop()


display_needed = False
cur_idx = 0
meshes = []
titles = []


class MySceneViewer(trimesh.viewer.windowed.SceneViewer):
    def __init__(self, scene, **kwargs):
        super().__init__(scene, **kwargs)

    def on_key_press(self, symbol, modifiers):
        global cur_idx, meshes, display_needed
        ctrl = modifiers & pyglet.window.key.MOD_CTRL
        shift = modifiers & pyglet.window.key.MOD_SHIFT
        if symbol == pyglet.window.key.W:
            self.toggle_wireframe()
        elif symbol == pyglet.window.key.Z:
            self.reset_view()
        elif symbol == pyglet.window.key.C:
            self.toggle_culling()
        elif symbol == pyglet.window.key.A:
            self.toggle_axis()
        elif symbol == pyglet.window.key.G:
            self.toggle_grid()
        elif symbol == pyglet.window.key.Q:
            self.on_close()
        elif symbol == pyglet.window.key.M:
            if shift:
                tmpfile = (
                    "/tmp/cadviewer_tmp.obj"  # LATER surely I can do better for temp?
                )
                saved = False
                view_lock.acquire()
                if len(meshes) > 0:
                    trimesh.exchange.export.export_mesh(meshes[cur_idx], tmpfile, "obj")
                    saved = True
                view_lock.release()
                if saved:
                    os.system("meshlab " + tmpfile)
            return  # Doesn't really work right, supress.
        elif symbol == pyglet.window.key.F:
            self.toggle_fullscreen()
        elif symbol == pyglet.window.key.H or symbol == pyglet.window.key.QUESTION:
            Thread(target=display_help, daemon=True).start()

        if symbol in [
            pyglet.window.key.LEFT,
            pyglet.window.key.RIGHT,
            pyglet.window.key.DOWN,
            pyglet.window.key.UP,
        ]:
            if ctrl or shift:
                super().on_key_press(symbol, modifiers)
                return
            mlen = len(meshes)
            if symbol == pyglet.window.key.LEFT:
                if mlen > 1:
                    view_lock.acquire()
                    cur_idx = (cur_idx - 1) % mlen
                    display_needed = True
                    view_lock.release()
            elif symbol == pyglet.window.key.RIGHT:
                if mlen > 1:
                    view_lock.acquire()
                    cur_idx = (cur_idx + 1) % mlen
                    display_needed = True
                    view_lock.release()
            elif symbol == pyglet.window.key.DOWN:
                pass
            elif symbol == pyglet.window.key.UP:
                pass


def _queue_handler():
    global display_needed, meshes, titles, cur_idx
    while True:
        data = server.viewQueue.get()
        view_lock.acquire()
        try:
            obj = json.loads(data)
            if "clear" in obj:
                meshes = []
                titles = []
                display_needed = True
                cur_idx = 0
            else:
                display_needed = True
                vertices = np.array(obj["vertices"], np.float64)
                faces = np.array(obj["faces"], np.int64)
                mesh = trimesh.Trimesh(vertices, faces)
                mesh.visual.vertex_colors = obj["color"]
                meshes.append(mesh)
                titles.append(obj["title"])
                cur_idx = len(meshes) - 1
        except Exception as err:
            print("Exception:", err)
            pass
        view_lock.release()


server.start_server()
Thread(target=_queue_handler, daemon=True).start()


window = None

cur_mesh = None


def cb(scene: trimesh.Scene):
    global display_needed, meshes, titles, cur_mesh, window
    changed = False
    view_lock.acquire()
    if display_needed:
        scene.delete_geometry(cur_mesh)
        if len(meshes) > 0:
            window.set_caption(
                f"CAD Viewer - #{cur_idx+1} of {len(meshes)} - {titles[cur_idx]}"
            )
            mesh = meshes[cur_idx]
            scene2 = trimesh.Scene(mesh)
            window._initial_camera_transform = scene2.camera_transform
            scene = window.scene = window._scene = scene2
            cur_mesh = scene.add_geometry(mesh)
            window.reset_view()
            # window.view["ball"].scroll(-(mesh.bounds[1,1]-mesh.bounds[0,1])*0.2)
            # window.scene.camera_transform = window.view["ball"].pose
        else:
            window.set_caption(f"CAD Viewer - #0 of 0")
        changed = True
        display_needed = False
    view_lock.release()
    return changed


def main():
    global cur_mesh, window
    scene = trimesh.Scene()
    cur_mesh = scene.add_geometry(trimesh.creation.box((100, 100, 100)))
    window = MySceneViewer(
        scene,
        callback=cb,
        callback_period=1.0,
        start_loop=False,
        background=(173, 216, 230, 255),
        smooth=False,
    )
    scene.delete_geometry(cur_mesh)
    window.set_caption(f"CAD Viewer - #0 of 0")

    pyglet.app.run()
