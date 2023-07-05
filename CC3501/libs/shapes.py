import numpy as np


class Shape:
    def __init__(self, vertices, indices):
        self.vertices = vertices
        self.indices = indices

    def __str__(self):
        return "vertices: " + str(self.vertices) + "\n"\
            "indices: " + str(self.indices)


def createTextureQuad(nx, ny):

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
    #   positions        texture
        -0.5, -0.5, 0.0,  0, ny,
         0.5, -0.5, 0.0, nx, ny,
         0.5,  0.5, 0.0, nx, 0,
        -0.5,  0.5, 0.0,  0, 0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         0, 1, 2,
         2, 3, 0]

    return Shape(vertices, indices)


def createTextureCube(nx, ny):

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
    #   positions         texture coordinates
    # Z+
        -0.5, -0.5,  0.5, 0, ny,
         0.5, -0.5,  0.5, nx, ny,
         0.5,  0.5,  0.5, nx, 0,
        -0.5,  0.5,  0.5, 0, 0,

    # Z-
        -0.5, -0.5, -0.5, 0, ny,
         0.5, -0.5, -0.5, nx, ny,
         0.5,  0.5, -0.5, nx, 0,
        -0.5,  0.5, -0.5, 0, 0,

    # X+
         0.5, -0.5, -0.5, 0, ny,
         0.5,  0.5, -0.5, nx, ny,
         0.5,  0.5,  0.5, nx, 0,
         0.5, -0.5,  0.5, 0, 0,

    # X-
        -0.5, -0.5, -0.5, 0, ny,
        -0.5,  0.5, -0.5, nx, ny,
        -0.5,  0.5,  0.5, nx, 0,
        -0.5, -0.5,  0.5, 0, 0,

    # Y+
        -0.5,  0.5, -0.5, 0, ny,
         0.5,  0.5, -0.5, nx, ny,
         0.5,  0.5,  0.5, nx, 0,
        -0.5,  0.5,  0.5, 0, 0,

    # Y-
        -0.5, -0.5, -0.5, 0, ny,
         0.5, -0.5, -0.5, nx, ny,
         0.5, -0.5,  0.5, nx, 0,
        -0.5, -0.5,  0.5, 0, 0
        ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0,  # Z+
          7, 6, 5, 5, 4, 7,  # Z-
          8, 9,10,10,11, 8,  # X+
         15,14,13,13,12,15,  # X-
         19,18,17,17,16,19,  # Y+
         20,21,22,22,23,20]  # Y-

    return Shape(vertices, indices)


def rubiksCube():

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
    #   positions         texture coordinates
    # Z+
        -0.5, -0.5,  0.5, 1/3, 2/4,
         0.5, -0.5,  0.5, 2/3, 2/4,
         0.5,  0.5,  0.5, 2/3, 1/4,
        -0.5,  0.5,  0.5, 1/3, 1/4,

    # Z-
        -0.5, -0.5, -0.5, 1/3, 4/4,
         0.5, -0.5, -0.5, 2/3, 4/4,
         0.5,  0.5, -0.5, 2/3, 3/4,
        -0.5,  0.5, -0.5, 1/3, 3/4,

    # X+
         0.5, -0.5, -0.5, 0/3, 2/4,
         0.5,  0.5, -0.5, 1/3, 2/4,
         0.5,  0.5,  0.5, 1/3, 1/4,
         0.5, -0.5,  0.5, 0/3, 1/4,

    # X-
        -0.5, -0.5, -0.5, 2/3, 2/4,
        -0.5,  0.5, -0.5, 3/3, 2/4,
        -0.5,  0.5,  0.5, 3/3, 1/4,
        -0.5, -0.5,  0.5, 2/3, 1/4,

    # Y+
        -0.5,  0.5, -0.5, 1/3, 1/4,
         0.5,  0.5, -0.5, 2/3, 1/4,
         0.5,  0.5,  0.5, 2/3, 0/4,
        -0.5,  0.5,  0.5, 1/3, 0/4,

    # Y-
        -0.5, -0.5, -0.5, 1/3, 3/4,
         0.5, -0.5, -0.5, 2/3, 3/4,
         0.5, -0.5,  0.5, 2/3, 2/4,
        -0.5, -0.5,  0.5, 1/3, 2/4
        ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0,  # Z+
          7, 6, 5, 5, 4, 7,  # Z-
          8, 9,10,10,11, 8,  # X+
         15,14,13,13,12,15,  # X-
         19,18,17,17,16,19,  # Y+
         20,21,22,22,23,20]  # Y-

    return Shape(vertices, indices)


def minecraftCube():

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
    #   positions         texture coordinates
    # Z+
        -0.5, -0.5,  0.5, 1/4, 2/3,
         0.5, -0.5,  0.5, 2/4, 2/3,
         0.5,  0.5,  0.5, 2/4, 1/3,
        -0.5,  0.5,  0.5, 1/4, 1/3,

    # Z-
        -0.5, -0.5, -0.5, 3/4, 2/3,
         0.5, -0.5, -0.5, 4/4, 2/3,
         0.5,  0.5, -0.5, 4/4, 1/3,
        -0.5,  0.5, -0.5, 3/4, 1/3,

    # X+
         0.5, -0.5, -0.5, 1/4, 3/3,
         0.5,  0.5, -0.5, 2/4, 3/3,
         0.5,  0.5,  0.5, 2/4, 2/3,
         0.5, -0.5,  0.5, 1/4, 2/3,

    # X-
        -0.5, -0.5, -0.5, 1/4, 3/3,
        -0.5,  0.5, -0.5, 2/4, 3/3,
        -0.5,  0.5,  0.5, 2/4, 2/3,
        -0.5, -0.5,  0.5, 1/4, 2/3,

    # Y+
        -0.5,  0.5, -0.5, 1/4, 3/3,
         0.5,  0.5, -0.5, 2/4, 3/3,
         0.5,  0.5,  0.5, 2/4, 2/3,
        -0.5,  0.5,  0.5, 1/4, 2/3,

    # Y-
        -0.5, -0.5, -0.5, 1/4, 3/3,
         0.5, -0.5, -0.5, 2/4, 3/3,
         0.5, -0.5,  0.5, 2/4, 2/3,
        -0.5, -0.5,  0.5, 1/4, 2/3
        ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0,  # Z+
          7, 6, 5, 5, 4, 7,  # Z-
          8, 9,10,10,11, 8,  # X+
         15,14,13,13,12,15,  # X-
         19,18,17,17,16,19,  # Y+
         20,21,22,22,23,20]  # Y-

    return Shape(vertices, indices)


def read_OFF(filename, color):
    vertices = []
    normals = []
    faces = []

    with open(filename, 'r') as file:
        line = file.readline().strip()
        assert line == "OFF"

        line = file.readline().strip()
        aux = line.split(' ')

        numVertices = int(aux[0])
        numFaces = int(aux[1])

        for _ in range(numVertices):
            aux = file.readline().strip().split(' ')
            vertices += [float(coord) for coord in aux[0:]]

        vertices = np.asarray(vertices)
        vertices = np.reshape(vertices, (numVertices, 3))
        # print(f'Vertices shape: {vertices.shape}')

        normals = np.zeros((numVertices,3), dtype=np.float32)
        # print(f'Normals shape: {normals.shape}')

        for i in range(numFaces):
            aux = file.readline().strip().split(' ')
            aux = [int(index) for index in aux[0:]]
            faces += [aux[1:]]

            vecA = [vertices[aux[2]][0] - vertices[aux[1]][0], vertices[aux[2]][1] - vertices[aux[1]][1], vertices[aux[2]][2] - vertices[aux[1]][2]]
            vecB = [vertices[aux[3]][0] - vertices[aux[2]][0], vertices[aux[3]][1] - vertices[aux[2]][1], vertices[aux[3]][2] - vertices[aux[2]][2]]

            res = np.cross(vecA, vecB)
            normals[aux[1]][0] += res[0]
            normals[aux[1]][1] += res[1]
            normals[aux[1]][2] += res[2]

            normals[aux[2]][0] += res[0]
            normals[aux[2]][1] += res[1]
            normals[aux[2]][2] += res[2]

            normals[aux[3]][0] += res[0]
            normals[aux[3]][1] += res[1]
            normals[aux[3]][2] += res[2]
        # print(faces)
        norms = np.linalg.norm(normals, axis=1)
        normals = normals/norms[:, None]

        color = np.asarray(color)
        color = np.tile(color, (numVertices, 1))

        vertexData = np.concatenate((vertices, color), axis=1)
        vertexData = np.concatenate((vertexData, normals), axis=1)

        # print(vertexData.shape)

        indices = []
        vertexDataF = []
        index = 0

        for face in faces:
            vertex = vertexData[face[0],:]
            vertexDataF += vertex.tolist()
            vertex = vertexData[face[1],:]
            vertexDataF += vertex.tolist()
            vertex = vertexData[face[2],:]
            vertexDataF += vertex.tolist()

            indices += [index, index + 1, index + 2]
            index += 3

    return Shape(vertexDataF, indices)
