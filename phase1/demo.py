from voronoi import DelaunayTriangulation

mon_interface = DelaunayTriangulation()
mon_interface.triangulate()
mon_interface.calculer_centre(0)
mon_interface.calculer_centre(1)    
mon_interface.afficher_voronoi()