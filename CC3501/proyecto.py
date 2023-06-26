# coding=utf-8
# Tarea 3: Máximo Flores Valenzuela
# RUT: 21.123.385-0 Sección 1 CC3501 2023-1

import sys
import os
import pyglet
import numpy as np

import libs.shaders as sh
import libs.transformations as tr
import libs.scene_graph as sg

from libs.gpu_shape import createGPUShape
from libs.obj_handler import read_OBJ2
from libs.assets_path import getAssetPath

from OpenGL.GL import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WIDTH, HEIGHT = 800, 800
PROJECTIONS = [
    tr.ortho(-8, 8, -8, 8, 0.001, 150),
    tr.perspective(45, float(WIDTH)/float(HEIGHT), 0.1, 100)
]
UNIFORM = np.array([0.0, 0.0, 0.0, 1.0])

ASSETS = {
    "pochita_obj": getAssetPath("pochita3.obj"),
    "pochita_tex": getAssetPath("pochita.png"),
    "house": getAssetPath("house.obj"),
    "floor_obj": getAssetPath("floor.obj"),
    "floor_tex": getAssetPath("floor.png"),
    "car_obj": getAssetPath("car.obj"),
    "tree_obj": getAssetPath("tree.obj"),
    "shadow_tex": getAssetPath("shadow.png"),
    "bus_obj": getAssetPath("bus.obj"),
    "cat_obj": getAssetPath("cat.obj")
}

TEX_PARAMS = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]

class Controller(pyglet.window.Window):
    def __init__(self, width, height, title=f"Tarea 3 - Máximo Flores Valenzuela"):
        super().__init__(width, height, title)
        self.total_time = 0.0

class SceneGraph:
    def __init__(self) -> None:
        # Seteamos el pipeline y los parámetros de textura
        self.pipeline = sh.SimpleTextureModelViewProjectionShaderProgram()
        self.root = sg.SceneGraphNode("root")

        # Nave (forma y textura)
        nave_shape = self.createTextureShape("pochita_obj", "pochita_tex")
        nave_shadow = self.createTextureShape("pochita_obj", "shadow_tex")
        self.naves = sg.SceneGraphNode("naves")

        # Nave del frente
        self.nave_front = sg.SceneGraphNode("nave_front")
        self.nave_front.childs += [nave_shape]
        # Atrás a la izq.
        self.nave_back_left = sg.SceneGraphNode("nave_back_left")
        self.nave_back_left.childs += [nave_shape]
        # Atrás a la der.
        self.nave_back_right = sg.SceneGraphNode("nave_back_right")
        self.nave_back_right.childs += [nave_shape]

        self.naves.childs += [self.nave_front, self.nave_back_left, self.nave_back_right]
        self.root.childs += [self.naves]

        # Sombras de las naves
        """
        self.shadows = sg.SceneGraphNode("shadows")
        self.front_shadow = sg.SceneGraphNode("front_shadow")
        self.front_shadow.childs += [nave_shadow]
        self.back_left_shadow = sg.SceneGraphNode("back_left_shadow")
        self.back_left_shadow.childs += [nave_shadow]
        self.back_right_shadow = sg.SceneGraphNode("back_right_shadow")
        self.back_right_shadow.childs += [nave_shadow]

        self.shadows.childs += [self.front_shadow, self.back_left_shadow, self.back_right_shadow]
        self.root.childs += [self.shadows]"""

        # Elementos de la escena
        # Casa
        casa_shape = self.createTextureShape("house", None)
        self.casa = sg.SceneGraphNode("casa")
        transform = [tr.uniformScale(0.9), tr.translate(1, 0, -2)]
        self.casa.transform = tr.matmul(transform)
        self.casa.childs += [casa_shape]
        self.root.childs += [self.casa]

        # Auto
        auto_shape = self.createTextureShape("car_obj", None)
        self.car = sg.SceneGraphNode("car")
        transform = [tr.uniformScale(0.9), tr.translate(2, 0, 4), tr.rotationX(3 * np.pi / 2)]
        self.car.transform = tr.matmul(transform)
        self.car.childs += [auto_shape]
        self.root.childs += [self.car]

        # Bus
        bus_shape = self.createTextureShape("bus_obj", None)
        self.bus = sg.SceneGraphNode("bus")
        transform = [tr.uniformScale(0.1), tr.translate(50, 0, -30), tr.rotationY(np.pi), tr.rotationX(3 * np.pi / 2)]
        self.bus.transform = tr.matmul(transform)
        self.bus.childs += [bus_shape]
        self.root.childs += [self.bus]

        # Arbol
        arbol_shape = self.createTextureShape("tree_obj", None)
        self.tree = sg.SceneGraphNode("tree")
        transform = [tr.uniformScale(0.1), tr.translate(-18, 0, 20)]
        self.tree.transform = tr.matmul(transform)
        self.tree.childs += [arbol_shape]
        self.root.childs += [self.tree]

        # Piso
        floor_shape = self.createTextureShape("floor_obj", None)
        self.floor = sg.SceneGraphNode("floor_obj")
        transform = [tr.scale(3, 0.2, 3), tr.translate(0, -2, 0)]
        self.floor.transform = tr.matmul(transform)
        self.floor.childs += [floor_shape]
        self.root.childs += [self.floor]

        # Gato
        cat_shape = self.createTextureShape("cat_obj", None)
        self.cat = sg.SceneGraphNode("cat")
        transform = [tr.uniformScale(5), tr.translate(1, 0, 0.5)]
        self.cat.transform = tr.matmul(transform)
        self.cat.childs += [cat_shape]
        self.root.childs += [self.cat]

    # createTextureShape: str str -> GPUShape
    # Recibe dos strings referenciando al objeto y su textura y devuelve
    # la instancia de GPUShape con la textura aplicada
    def createTextureShape(self, asset, texture):
        shape = createGPUShape(self.pipeline, read_OBJ2(ASSETS[asset]))
        if texture is not None:
            tex = ASSETS[texture]
            # Ponemos la textura en la shape
            shape.texture = sh.textureSimpleSetup(tex, *TEX_PARAMS)

        return shape

class Camera:
    def __init__(self, at, eye, up) -> None:
        # Parámetros de visión de la cámara
        self.eye = eye
        self.at = at
        self.up = up
        self.view = tr.lookAt(eye, at, up)

        # Base cartesiana
        self.x = self.eye[0] ** 2
        self.y = self.eye[1] ** 2
        self.z = self.eye[2] ** 2

        # Proy. ortogonal por defecto
        self.opt_proj = 0
        self.projection = PROJECTIONS[self.opt_proj]

    # update: Actualiza los parámetros de la cámara, siguiendo
    # los movimientos de la nave ship.
    def update(self, ship):
        [x, y, z] = ship.coords
        
        # Proyección ortogonal
        if self.opt_proj == 0:
            # La posición de la cámara se actualiza en función del movimiento
            self.eye[0] = self.x + x
            self.eye[1] = self.y + y
            self.eye[2] = self.z + z

            # Actualizamos la dirección de visión a las coordenadas de la nave
            self.at[0] = x
            self.at[1] = y
            self.at[2] = z

            self.view = tr.lookAt(self.eye, self.at, self.up)
        # Proyección en perspectiva
        else:
            # Seguimos a la nave y recuperamos las coordenadas x, y, z
            # de la transformación
            self.eye = np.array(tr.matmul([
                tr.translate(x, y, z),
                tr.rotationY(ship.rot_theta),
                tr.translate(-5.0, 2-5*np.sin(ship.rot_phi), 0.0),
                np.array([0.0, 0.0, 0.0, 1.0])
            ])[0:3])

            # Quiero mirar hacia la nave
            self.view = tr.lookAt(self.eye, ship.coords, self.up)

    def change_projection(self, ship):
        # Cambiamos la proyección según se pulse la tecla C
        self.opt_proj = (self.opt_proj + 1) % 2
        self.projection = PROJECTIONS[self.opt_proj]

        self.update(ship)

class Movement:
    def __init__(self, coords=None, xlim=30, ylim=30, zlim=15) -> None:
        # Coordenadas de la nave
        self.coords = coords
        if self.coords is None:
            self.coords = np.array([0.0, 0.0, 0.0])

        # Calibración de la rotación (tolerancia)
        self.tol = 0.05

        # Limites del mapa
        self.xlim = xlim
        self.ylim = ylim
        self.zlim = zlim

        # El movimiento se define en base al eje x
        self.x = 0

        self.rot_theta = 0
        self.rot_phi = 0

        # Ojo que theta está definido desde el centro de la esfera
        # en la escena. Y en las coordenadas esféricas, se define
        # como el ángulo que cae, por eso debe ser pi/2 - theta.
        self.theta = self.rot_theta
        self.phi = self.rot_phi

        # Rapidez de movimiento y rapidez de retroceso
        self.scale_speed = 0.25
        self.knockback = self.scale_speed / 10

    def update(self):
        # Actualizamos las rotaciones por ángulo
        self.rot_theta += self.theta * self.tol
        self.rot_phi += self.phi * self.tol
        [x, y, z] = self.coords

        # Si |x| <= xlim, está dentro de los límites del mapa. Actualizamos
        # y hacemos la transformación de cartesianas a esféricas
        if abs(x) <= self.xlim:
            self.coords[0] += self.x * np.cos(self.rot_phi) * np.cos(self.rot_theta) * self.scale_speed
        # En cualquier otro caso, está fuera de los límites
        elif x >= self.xlim:
            self.coords[0] -= self.knockback
        else:
            self.coords[0] += self.knockback

        # Análogo para las demás coordenadas
        if abs(y) <= self.ylim:
            # OBS: Como up = Y, entonces se comporta como el eje Z
            self.coords[1] += self.x * np.sin(self.rot_phi) * self.scale_speed
        elif y >= self.ylim:
            self.coords[1] -= self.knockback
        else:
            self.coords[1] += self.knockback

        if abs(z) <= self.zlim:
            self.coords[2] += self.x * np.sin(self.rot_theta) * np.cos(self.rot_phi) * self.scale_speed
        elif z >= self.zlim:
            self.coords[2] -= self.knockback
        else:
            self.coords[2] += self.knockback

# Parámetros de la cámara, modificar para cambiar perspectiva inicial
cam_at = np.array([0.0, 0.0, 0.0])
# Alejamos la posición inicial para que renderice el escenario bien
cam_eye = np.array([5.0, 5.0, 5.0])
# El vector hacia arriba debe coincidir con el eje Y
cam_up = np.array([0.0, 1.0, 0.0])

# Creamos lo necesario para que la escena funcione bien
controller = Controller(width=WIDTH, height=HEIGHT)
scgraph = SceneGraph()
camera = Camera(cam_at, cam_eye, cam_up)
movement = Movement()

# Con el setup, instanciamos el controlador de la ventana
glClearColor(0.1, 0.1, 0.1, 1.0)
glEnable(GL_DEPTH_TEST)
glUseProgram(scgraph.pipeline.shaderProgram)

# Apretar una tecla
@controller.event
def on_key_press(symbol, modifiers):
    # A y D son rotaciones en el eje Z
    if symbol == pyglet.window.key.A:
        movement.rot_phi -= 1
    if symbol == pyglet.window.key.D:
        movement.rot_phi += 1

    # W y S es avanzar o retroceder
    if symbol == pyglet.window.key.W:
        movement.x += 1
    if symbol == pyglet.window.key.S:
        movement.x -= 1

    # Para cambiar la perspectiva
    if symbol == pyglet.window.key.C:
        camera.change_projection(movement)
        
    # Para cerrar la ventana
    if symbol == pyglet.window.key.ESCAPE:
        controller.close()

# Soltar una tecla
@controller.event
def on_key_release(symbol, modifiers):
    # Hacemos lo contrario para detener el movimiento
    if symbol == pyglet.window.key.A:
        movement.rot_phi += 1
    if symbol == pyglet.window.key.D:
        movement.rot_phi -= 1
    if symbol == pyglet.window.key.W:
        movement.x -= 1
    if symbol == pyglet.window.key.S:
        movement.x += 1

# What happens when the user moves the mouse
@controller.event
def on_mouse_motion(x, y, dx, dy):
    if dy > 0:
        movement.rot_theta = 0.1
    if dy < 0:
        movement.rot_theta = 0.1

@controller.event
def on_draw():
    controller.clear()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Primero actualizamos el movimiento
    movement.update()

    rot_matrix = [tr.rotationY(-movement.rot_theta), tr.rotationZ(movement.rot_phi)]
    move_matrix = [tr.translate(movement.coords[0], movement.coords[1], movement.coords[2])]

    # Para posicionar las naves de atrás
    scgraph.nave_back_left.transform = [tr.translate(-2, -0.5, 0)]
    scgraph.nave_back_right.transform = [tr.translate(-2, 0.5, 0)]

    # Aplastamiento para las sombras
    """
    scaling = 0.001    
    flattening = [tr.scale(0.1, 0.1, scaling)]
    front = sg.findPosition(scgraph.naves, "nave_front")
    x, y = front[0][0], front[1][0]
    scgraph.front_shadow.transform = tr.matmul([ \
            tr.translate(x, y, scaling), 
            flattening, 
            rot_matrix, 
            UNIFORM
        ])

    back_left = sg.findPosition(scgraph.naves, "nave_back_left")
    x, y = back_left[0][0][0], back_left[0][1][0]
    scgraph.back_left_shadow.transform = tr.matmul([ \
            tr.translate(x, y, scaling), 
            flattening, 
            rot_matrix, 
            UNIFORM
        ])

    back_right = sg.findPosition(scgraph.naves, "nave_back_right")
    x, y = back_right[0][0][0], back_right[0][1][0]
    scgraph.back_left_shadow.transform = tr.matmul([ \
            tr.translate(x, y, scaling), 
            flattening, 
            rot_matrix, 
            UNIFORM
        ])"""

    scgraph.naves.transform = tr.matmul([move_matrix+rot_matrix])

    # Actualizamos la cámara para que siga a las naves
    camera.update(movement)
    view = camera.view

    glUniformMatrix4fv(glGetUniformLocation(scgraph.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(scgraph.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    sg.drawSceneGraphNode(scgraph.root, scgraph.pipeline, "model")

# Each time update is called, on_draw is called again
# That is why it is better to draw and update each one in a separated function
# We could also create 2 different gpuQuads and different transform for each
# one, but this would use more memory
def update(dt, controller):
    controller.total_time += dt

if __name__ == '__main__':
    # Try to call this function 60 times per second
    pyglet.clock.schedule(update, controller)
    # Set the view
    pyglet.app.run()
