# coding=utf-8
# Tarea 4: Máximo Flores Valenzuela
# RUT: 21.123.385-0 Sección 1 CC3501 2023-1

import sys
import os
import pyglet
import numpy as np
import random

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
TEX_PARAMS = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
EPSILON = 1

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
    "cat_obj": getAssetPath("cat.obj"),
    "sphere_obj": getAssetPath("sphere.obj")
}

puntaje = 0
# Debe ser un número grande para minimizar siempre
record = 1e9

def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T

def hermiteMatrix(P1, P2, T1, T2):
    G = np.concatenate((P1, P2, T1, T2), axis=1)
    Mh = np.array([[1, 0, -3, 2], [0, 0, 3, -2], [0, 1, -2, 1], [0, 0, -1, 1]])

    return np.matmul(G, Mh)

def evalCurve(M, N):
    ts = np.linspace(0.0, 1.0, N)
    curve = np.ndarray(shape=(N, 3), dtype=float)
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T

    return curve

def distanceXZ(p, q):
    [x1, y1, z1] = p
    [x2, y2, z2] = q

    dx = np.square(x1 - x2)
    dz = np.square(z1 - z2)

    return np.sqrt(dx + dz)

def collision(p, q, r):
    return distanceXZ(p, q) <= r

# Entrega el mapeo de esféricas a cartesianas según el sist. de coords.
def cartesianMapping(R, theta, phi):
    x = R * np.sin(theta) * np.cos(phi)
    # OBS: Como up = Y, entonces se comporta como el eje Z
    y = R * np.sin(phi)
    z = R * np.cos(theta) * np.cos(phi)

    return np.array([x, y, z])

def computeRecord():
    global record
    with open('records.txt', 'r') as f:
        lines = f.readlines()
        # Borramos el salto de línea del final
        lines = [line.strip() for line in lines]
        for line in lines:
            current = float(line)
            record = min(record, current)

# Genera un número random en una unión disjunta de dos intervalos
def disjointRandom(I1, I2):
    [first_inf, first_sup] = I1
    [second_inf, second_sup] = I2

    rand_bool = random.random() < 0.5
    return random.randint(first_inf, first_sup) if rand_bool else random.randint(second_inf, second_sup)

class Controller(pyglet.window.Window):
    def __init__(self, width, height, title=f"Tarea 4 - Máximo Flores Valenzuela"):
        super().__init__(width, height, title)
        
        self.total_time = 0.0
        self.can_reset = False
        self.set_exclusive_mouse(True)

    def reset(self, ship, graph, point):
        # Volvemos a setearlo a falso para que no pueda reintentar in-game
        self.can_reset = False

        global puntaje
        # Reiniciamos toda la escena
        self.total_time = 0.0
        puntaje = 0
        
        [x, y, z] = ship.coords
        theta = ship.rot_theta
        phi = ship.rot_phi
        angle_x = ship.angle_x

        translate_matrix = [tr.translate(-x, -y, -z)]
        rot_matrix = [
            tr.rotationX(-phi), 
            tr.rotationY(-theta), 
            tr.rotationZ(-angle_x)
        ]
        graph.naves.transform = tr.matmul(translate_matrix+rot_matrix)

        # Reiniciamos todos los valores de la nave
        ship.x = 0
        ship.rot_theta = 0
        ship.rot_phi = 0
        ship.angle_x = 0
        ship.theta = 0
        ship.phi = 0
        ship.alpha = 0

        # Por último, volvemos a dibujar un punto para que no esté 
        # en la misma posición
        point.draw(graph)

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
        transform = [tr.uniformScale(0.1), tr.translate(50, 0, -30), tr.rotationY(np.pi), tr.rotationX(3 * np.pi / 2), tr.rotationY(np.pi / 2)]
        self.bus.transform = tr.matmul(transform)
        self.bus.childs += [bus_shape]
        self.root.childs += [self.bus]

        # Arbol
        arbol_shape = self.createTextureShape("tree_obj", None)
        self.tree = sg.SceneGraphNode("tree")
        transform = [tr.uniformScale(0.1), tr.translate(-18, 0, 20), tr.rotationX(np.pi / 2)]
        self.tree.transform = tr.matmul(transform)
        self.tree.childs += [arbol_shape]
        self.root.childs += [self.tree]

        # Piso
        floor_shape = self.createTextureShape("floor_obj", None)
        self.floor = sg.SceneGraphNode("floor_obj")
        transform = [tr.scale(3, 0.2, 3), tr.translate(0, -2, 0), tr.rotationY(np.pi / 2)]
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
        self.opt_proj = 1
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
                tr.translate(0.0, 2.0, -7.0),
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
    def __init__(self, coords=None, xlim=21.5, ylim=20, zlim=21.5) -> None:
        # Coordenadas de la nave
        self.coords = coords
        if self.coords is None:
            # Le damos un poco de altura para que no toque el suelo
            self.coords = np.array([0.0, 0.0, 0.0])

        # Calibración de la rotación (tolerancia)
        self.tol = 0.1

        # Limites del mapa
        self.xlim = xlim
        self.ylim = ylim
        self.zlim = zlim

        # El movimiento se define en base al eje x
        self.x = 0

        self.rot_theta = 0
        self.rot_phi = 0
        self.angle_x = 0

        # Ojo que theta está definido desde el centro de la esfera
        # en la escena. Y en las coordenadas esféricas, se define
        # como el ángulo que cae, por eso debe ser pi/2 - theta.
        self.theta = 0
        self.phi = 0
        # El ángulo relacionado con la pirueta
        self.alpha = 0

        # Rapidez de movimiento y rapidez de retroceso
        self.movement_speed = 0.125
        self.angle_speed = 1.75e-2
        # No asustarse. Este fue a puro ensayo y error.
        self.knockback = (self.movement_speed + self.angle_speed) / 10

    def update(self, graph, point):
        global puntaje
        [x, y, z] = self.coords

        # Las transformaciones se hacen por frame
        rotation = [tr.rotationX(self.rot_phi), tr.rotationY(self.rot_theta), tr.rotationZ(self.angle_x)]
        movement = [tr.translate(x, y, z)]
        graph.naves.transform = tr.matmul(movement+rotation)

        self.rot_theta += self.theta * self.angle_speed
        self.rot_phi += self.phi * self.angle_speed
        self.angle_x += self.alpha * self.angle_speed

        # Para ver las colisiones con el punto
        p = point.getPosition()

        if p is not None and collision(self.coords, p, EPSILON):
            puntaje += 5
            point.draw(graph)

        # Hacemos la pirueta hasta que llegemos a 2pi
        if self.angle_x > 2 * np.pi:  
            self.alpha = 0
            self.angle_x = 0

        # Hacemos el mapeo a coordenadas cartesianas
        [dx, dy, dz] = cartesianMapping(self.x * self.movement_speed, self.rot_theta, self.rot_phi)

        # Si |x| <= xlim, está dentro de los límites del mapa.
        if np.abs(x) <= self.xlim:
            self.coords[0] += dx
        # En cualquier otro caso, está fuera de los límites
        elif x >= self.xlim:
            self.coords[0] = self.xlim
        else:
            self.coords[0] = -self.xlim

        # Análogo para las demás coordenadas
        if 0 <= self.coords[1] <= self.ylim:
            self.coords[1] += dy
        elif y >= self.ylim:
            self.coords[1] = self.ylim
        else:
            self.coords[1] = -self.ylim 

        if np.abs(self.coords[2]) <= self.zlim:
            self.coords[2] += dz
        elif z >= self.zlim:
            self.coords[2] = self.zlim
        else:
            self.coords[2] = -self.zlim

        # Evita problemas de asignación de ángulo con el mouse
        self.phi = 0
    
    def debug(self):
        [x, y, z] = self.coords
        print("(x, y, z) = ({}, {}, {})".format(x, y, z))

class Route:
    def __init__(self) -> None:
        self.route = []
        self.directions = []
        self.special_points = []
        self.curve = np.ndarray(shape=(0, 3), dtype=float)
        self._play = False
        self.N = 25
        # n es la iteración actual en el recorrido de las curvas de Hermite
        self.n = 0

    def save(self, ship):
        # Agregamos la posición y dirección inicial
        [x, y, z] = ship.coords
        self.route.append(np.array([x, y, z]))
        self.directions.append(np.array([ship.rot_theta, ship.rot_phi]))

        points = len(self.route)
        # Necesitamos más de un punto para crear una curva
        if points > 1:
            # Extraemos los dos últimos puntos de la lista
            [prev_last, last] = self.route[-2:]

            # A partir de esta información, creamos los puntos
            P1 = np.array([prev_last]).T
            P2 = np.array([last]).T

            [x1, y1, z1] = prev_last
            [x2, y2, z2] = last

            dx = np.square(x1 - x2)
            dy = np.square(y1 - y2)
            dz = np.square(z1 - z2)

            R = np.sqrt(dx + dy + dz)

            # Extraemos la información de las últimas 2 direcciones
            [prev_last, last] = self.directions[-2:]

            [theta1, phi1] = prev_last
            [theta2, phi2] = last 

            T1 = np.array([cartesianMapping(R, theta1, phi1)]).T
            T2 = np.array([cartesianMapping(R, theta2, phi2)]).T

            GMh = hermiteMatrix(P1, P2, T1, T2)
            curve = evalCurve(GMh, 100)
            self.curve = np.concatenate((self.curve, curve), axis = 0)

            last_point = len(self.curve) - 1
            self.special_points.append(last_point)

    def play(self, ship, graph, point):
        # len(self.curve) va directamente relacionado con N, el número
        # de iteraciones para cada spline
        total_points = len(self.curve)
        if self._play and total_points != 0:
            # Si llegamos al último punto, recorrimos toda la curva
            if self.n == total_points-1:
                self.n = 0

            # Actualizamos la posición de la nave
            for i in range(0, 3):
                ship.coords[i] = self.curve[self.n][i]

            # Si no es un punto de cambio de curva, hacemos el movimiento
            # Ojo que los índices que indican cambios son múltiplos de N-1
            if self.n % (self.N - 1) != 0:
                dx = self.curve[self.n+1][0] - self.curve[self.n][0]
                dy = self.curve[self.n+1][1] - self.curve[self.n][1]
                dz = self.curve[self.n+1][2] - self.curve[self.n][2]

                dist3d = np.sqrt(np.square(dx) + np.square(dy) + np.square(dz))
                dist2d = np.sqrt(np.square(dx) + np.square(dy))

                # Usando el mapeo inverso. Update: Arregla los casos borde.
                ship.rot_theta = np.arccos(dz / dist3d) if dist3d != 0 else 0
                ship.rot_phi = np.sign(dy) * np.arccos(dx / dist2d) if dist2d != 0 else 0

        ship.update(graph, point)
        self.n += 1
                
    # Sólo para propósitos de testing, y no debe ser invocada en el envío final
    def debug(self):
        if len(self.route) > 0:
            print("Added point: {}".format(self.route[-1]))
            print("Direction: {}".format(self.directions[-1]))

class Point:
    def __init__(self) -> None:
        # Para detectar colisiones 
        self.position = np.array([])
        self.first_visit = True

    def draw(self, graph):
        sphere_shape = graph.createTextureShape("sphere_obj", None)

        # Posiciones aleatorias de los puntos
        pos_x = disjointRandom([-18, -7], [7, 18])
        pos_z = disjointRandom([-18, -7], [7, 18])

        # Creamos un nodo por cada esfera (son independientes)
        transform = []
        
        if self.first_visit:
            graph.sphere = sg.SceneGraphNode("sphere")
            graph.sphere.childs = [sphere_shape]
            graph.root.childs += [graph.sphere]
            self.first_visit = False

        transform += [tr.translate(pos_x, 0, pos_z), tr.uniformScale(0.25)]
        self.position = np.array([pos_x, 0, pos_z])

        graph.sphere.transform = tr.matmul(transform)

    # Para obtener la última posición
    def getPosition(self):
        if len(self.position) == 0:
            return None
    
        return self.position

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
route = Route()
point = Point()
point.draw(scgraph)
# Calculamos el récord actual
computeRecord()

# Con el setup, instanciamos el controlador de la ventana
glClearColor(0.1, 0.1, 0.1, 1.0)
glEnable(GL_DEPTH_TEST)
glUseProgram(scgraph.pipeline.shaderProgram)

@controller.event
def on_key_press(symbol, modifiers):
    # Para cerrar la ventana
    if symbol == pyglet.window.key.ESCAPE:
        controller.close()

    if controller.can_reset and symbol == pyglet.window.key.R:
        controller.reset(movement, scgraph, point)

    # Reproducción de ruta
    if symbol == pyglet.window.key._1:
        route.n = 0
        route._play = not route._play

    if symbol == pyglet.window.key.TAB:
        movement.debug()

    # El modo reproducción desactiva las opciones de abajo
    if route._play:
        return
    
    # Pirueta
    if symbol == pyglet.window.key.P:
        movement.alpha = 1

    # W y S es avanzar o retroceder
    if symbol == pyglet.window.key.W:
        movement.x += 1
    if symbol == pyglet.window.key.S:
        movement.x -= 1

    # A y D son rotaciones en el plano XZ
    if symbol == pyglet.window.key.A:
        movement.theta += 1
    if symbol == pyglet.window.key.D:
        movement.theta -= 1

@controller.event
def on_key_release(symbol, modifiers):
    if route._play:
        return

    # Hacemos lo contrario para detener el movimiento
    if symbol == pyglet.window.key.A:
        movement.theta -= 1
    if symbol == pyglet.window.key.D:
        movement.theta += 1
    if symbol == pyglet.window.key.W:
        movement.x -= 1
    if symbol == pyglet.window.key.S:
        movement.x += 1

@controller.event
def on_draw():
    global puntaje, record

    controller.clear()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glUseProgram(scgraph.pipeline.shaderProgram)

    # Vemos si la ruta se puede reproducir en cada frame
    route.play(movement, scgraph, point)

    # Luego, actualizamos el movimiento
    movement.update(scgraph, point)

    # Para posicionar las naves de atrás
    scgraph.nave_back_left.transform = [tr.translate(-0.75, 0, -1.0)]
    scgraph.nave_back_right.transform = [tr.translate(0.75, 0, -1.0)]

    # Actualizamos la cámara para que siga a las naves
    camera.update(movement)
    view = camera.view

    glUniformMatrix4fv(glGetUniformLocation(scgraph.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(scgraph.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    sg.drawSceneGraphNode(scgraph.root, scgraph.pipeline, "model")

    points_label = pyglet.text.Label("Puntaje: {}".format(puntaje),
                          font_name='Times New Roman',
                          font_size=22,
                          x=30, y=9.9*HEIGHT//10,
                          anchor_x='left', anchor_y='top')
    
    time_label = pyglet.text.Label("Tiempo: {:.2f} | Récord: {:.2f}".format(controller.total_time, record),
                          font_name='Times New Roman',
                          font_size=22,
                          x=30, y=9.5*HEIGHT//10,
                          anchor_x='left', anchor_y='top')
    
    glUseProgram(0)
    glDisable(GL_DEPTH_TEST)

    curr_time = controller.total_time
    if not controller.can_reset and puntaje == 100 and curr_time < 60:
        PPS = (100 / 5) / 60
        winner_label = pyglet.text.Label("Qué crack B)\n PPS: {:.2f}".format(PPS),
            font_name='Times New Roman',
            font_size=30,
            x=WIDTH//2, y=3.5*HEIGHT//4,
            anchor_x='center', anchor_y='top')
        
        personal_time = "%.2f" % round(controller.total_time, 2)
        with open('records.txt', 'a') as f:
            f.write(personal_time)
            f.write('\n')
        
        record = min(record, float(personal_time))
        winner_label.draw()
        controller.can_reset = True

    elif not controller.can_reset and puntaje < 100 and curr_time >= 60:
        loser_label = pyglet.text.Label("Perdiste :( qué triste",
            font_name='Times New Roman',
            font_size=30,
            x=WIDTH//2, y=3.5*HEIGHT//4,
            anchor_x='center', anchor_y='top')
        
        loser_label.draw()
        controller.can_reset = True

    points_label.draw()
    time_label.draw()

# Each time update is called, on_draw is called again
def update(dt, controller):
    controller.total_time += dt

if __name__ == '__main__':
    # Try to call this function 60 times per second
    pyglet.clock.schedule(update, controller)
    pyglet.app.run()
