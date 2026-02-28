import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

class DelaunayTriangulation:
    points = [(2,4),(5.3,4.5),(18,29),(12.5,23.7)]
    mes_couleurs = ListedColormap(['orange', 'mediumpurple', 'blue', 'chartreuse'])
    def __init__(self):
        self._points = self.points

        self.triangles = []

    def triangulate(self):
        self.points = np.array(self._points)
        abscisses = self.points[:, 0]
        ordonnees = self.points[:, 1]
        colone=abscisses**2+ordonnees**2
        colone_1=np.ones(len(self.points))
        matrice=np.column_stack((abscisses,ordonnees,colone,colone_1))
        determinant=np.linalg.det(matrice)
        if determinant>0:
            self.triangles.append((0, 1, 3))
            self.triangles.append([1, 2, 3])
        else:
            self.triangles.append([0, 1, 2])
            self.triangles.append([0, 2, 3])


    def calculer_centre(self,indice_triangle):
        triangle = self.triangles[indice_triangle]
        x1, y1 = self.points[triangle[0]]
        x2, y2 = self.points[triangle[1]]
        x3, y3 = self.points[triangle[2]]
        A = np.array([[x1, y1, 1], [x2, y2, 1], [x3, y3, 1]])
        B = np.array([[-(x1**2 + y1**2)], [-(x2**2 + y2**2)], [-(x3**2 + y3**2)]])
        C = np.linalg.solve(A, B)
        Ox = -C[0][0] / 2
        Oy = -C[1][0]  / 2
        return (Ox, Oy)

    

    def tracer_rayon(self, centre, indice_A, indice_B) :
        point_A = self.points[indice_A]
        point_B = self.points[indice_B]
        dx = point_B[0] - point_A[0]
        dy = point_B[1] - point_A[1]
        vecteur_x = dy
        vecteur_y = -dx
        Valeur_fin_x = centre[0] + 100 * vecteur_x
        Valeur_fin_y = centre[1] + 100 * vecteur_y
        plt.plot([centre[0], Valeur_fin_x], [centre[1], Valeur_fin_y], 'r')

    
    def colorer_fond(self):
        distances=[]
        ligne_x = np.linspace(-5, 25, 500)
        ligne_y = np.linspace(-5, 35, 500)
        X,Y = np.meshgrid(ligne_x, ligne_y)
        for point in self.points:
            distance =  (X-point[0])**2 + (Y-point[1])**2
            distances.append(distance)
        z=np.argmin(distances, axis=0)
        plt.pcolormesh(X, Y, z, cmap=self.mes_couleurs, zorder=0)
    
    
    def afficher_voronoi(self):
        self.colorer_fond()
        centre1=self.calculer_centre(0)
        centre2=self.calculer_centre(1)
        plt.scatter(self.points[:, 0], self.points[:, 1], c='white',edgecolors='black', zorder=1)
        plt.scatter(centre1[0], centre1[1], c='r',edgecolors='black', zorder=2)
        plt.scatter(centre2[0], centre2[1], c='r',edgecolors='black', zorder=2)
        plt.plot([centre1[0], centre2[0]], [centre1[1], centre2[1]], 'r', zorder=3)
        self.tracer_rayon(centre1, 0, 1)
        self.tracer_rayon(centre2, 1, 2)
        self.tracer_rayon(centre2, 2, 3)
        self.tracer_rayon(centre1, 3, 0)
        plt.title('Diagramme de Voronoi')
        plt.xlabel('X-axis')    
        plt.ylabel('Y-axis')
        plt.grid()
        plt.xlim(-5, 25)
        plt.ylim(-5, 35)
        plt.show()

        
       