import math

class laser_turtle:
    """ Implémentation d'un module inspiré de Turtle pour commande
    d'une machine à découpe et gravure laser """
    def __init__(self, width, height):
        """ Une image vectorielle est créée de taille width x height en millimètres
        la tortue a une position x,y (point 0,0 en haut à gauche), et une orientation (heading)
        L'image contient 2 calques, un pour la découpe, un pour le dessin """
        self.turtle_x = 0
        self.turtle_y = 0
        self.turtle_heading = 90
        self.turtle_cut = False
        self.turtle_draw = True
        self.width = width
        self.height = height
        self.draw = ""
        self.cut = ""

    def move_to(self, x, y):
        """ Déplace la tortue à une position absolue (x,y), sans dessiner """
        self.turtle_x, self.turtle_y = x, y

    def get_position(self):
        """ Renvoie la position courante de la tortue sous forme d'un couple (x,y) """
        return self.turtle_x, self.turtle_y

    def get_x(self):
        """ Renvoie la position horizontale courante de la tortue """
        return self.turtle_x

    def get_y(self):
        """ Renvoie la position verticale courante de la tortue """
        return self.turtle_y
        
    def set_heading(self, angle):
        """ Oriente la tortue à un angle absolu (0 pour Nord) Sens horaire. """
        self.turtle_heading = angle % 360

    def get_heading(self):
        """ Renvoie l'orientation courante de la tortue """
        return self.turtle_heading

    def rotate(self, angle):
        """ Pivote la tortue d'un angle relatif (positif dans le sens horaire) """
        self.turtle_heading = (self.turtle_heading + angle) % 360

    def left(self, angle=90):
        """ Pivote la tortue à gauche d'un angle donné (90 par défaut)"""
        self.rotate(-angle)
        
    def right(self, angle=90):
        """ Pivote la tortue à droite d'un angle donné (90 par défaut)"""
        self.rotate(angle)
        
    def forward(self, d):
        """ Avance la tortue d'une distance d, en générant un chemin de type ligne """
        dx = d * math.cos ((self.turtle_heading - 90)*math.pi/180)
        dy = d * math.cos ((self.turtle_heading - 180)*math.pi/180)
        if self.turtle_draw :
            self.draw += "<path fill='none' stroke='black' stroke-width='0.2' d='M " + str(self.turtle_x) +"," + str(self.turtle_y) + " l " + str(dx) + " " + str(dy) + "'></path>\n"
        if self.turtle_cut :
            self.cut += "<path fill='none' stroke='red' stroke-width='0.2' d='M " + str(self.turtle_x) +"," + str(self.turtle_y) + " l " + str(dx) + " " + str(dy) + "'></path>\n"
        self.turtle_x = self.turtle_x + dx
        self.turtle_y = self.turtle_y + dy

    def backward(self,d):
        """ Recule la tortue d'une distance d, en générant un chemin de type ligne """
        self.forward(-d)
        
    def turn(self, r, a):
        """ Fait parcourir à la tortue un arc de cercle de rayon r et d'angle a """
        tour = 1 if a >= 360 else -1 if a <= -360 else 0
        a = a % 360 if a >= 0 else a % 360 - 360
        alpha = self.turtle_heading + 90 if a >= 0 else self.turtle_heading - 90
        cx = self.turtle_x + r * math.sin(alpha*math.pi/180)
        cy = self.turtle_y - r * math.cos(alpha*math.pi/180)
        dx = cx - self.turtle_x + (self.turtle_x - cx)* math.cos(a*math.pi/180) - (self.turtle_y - cy)* math.sin(a*math.pi/180)
        dy = cy - self.turtle_y + (self.turtle_y - cy)* math.cos(a*math.pi/180) + (self.turtle_x - cx)* math.sin(a*math.pi/180)
        if tour != 0 :
            if self.turtle_draw :
                self.draw += "<circle fill='none' stroke='black' stroke-width='0.2' cx="+ str(cx) +" cy="+ str(cy) +" r="+ str(r) +"></circle>\n"
            if self.turtle_cut :
                self.draw += "<circle fill='none' stroke='red' stroke-width='0.2' cx="+ str(cx) +" cy="+ str(cy) +" r="+ str(r) +"></circle>\n"
        if self.turtle_draw :
            self.draw += "<path fill='none' stroke='black' stroke-width='0.2' d='M"+ str(self.turtle_x) +"," + str(self.turtle_y) + " a " + str(r) + " " + str(r) + " 0 " + (" 1 " if abs(a)>=180 else " 0 ") + (" 1 " if a>=0 else " 0 ") + str(dx) + " " + str(dy) + "'></path>\n"
        if self.turtle_cut :
            self.cut += "<path fill='none' stroke='red' stroke-width='0.2' d='M"+ str(self.turtle_x) +"," + str(self.turtle_y) + " a " + str(r) + " " + str(r) + " 0 " + (" 1 " if abs(a)>=180 else " 0 ") + (" 1 " if a>=0 else " 0 ") + str(dx) + " " + str(dy) + "'></path>\n"
        self.turtle_x = self.turtle_x + dx
        self.turtle_y = self.turtle_y + dy
        self.turtle_heading = self.turtle_heading + a

    def draw_on(self):
        """ Positionne la tortue en position de dessin """
        self.turtle_draw = True
        self.turtle_cut = False

    def draw_off(self):
        """ Remonte la tortue """
        self.turtle_cut = False
        self.turtle_draw = False

    def cut_on(self):
        """ Positionne la tortue en position de découpe """
        self.turtle_cut = True
        self.turtle_draw = False

    def cut_off(self):
        """ Remonte la tortue """
        self.turtle_cut = False
        self.turtle_draw = False

    def to_svg(self, turtle=True):
        """ Renvoie le dessin vectoriel en svg, avec ou sans la tortue """
        s = "<svg width='"+str(self.width)+"mm' height='"+str(self.height)+"mm' viewBox='0 0 "+str(self.width)+" "+str(self.height)+"' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' version='1.2' baseProfile='tiny'>\n"
        if turtle:
            s += "<defs>  <g id='curseur'  width='100' height='100'><path fill='none' stroke='green' stroke-width='2' d='M50,10 a 2 2 0  0  0 -1.532088886237956 0.7144247806269213'></path><path fill='none' stroke='green' stroke-width='2' d='M48.46791111376204,10.71442478062692 a 30 30 0  0  0 -6.5628992967969 14.074182960588262'></path><path fill='none' stroke='green' stroke-width='2' d='M41.90501181696514,24.78860774121518 a 10 10 0  0  1 -3.4202014332566866 5.923962654520478'></path><path fill='none' stroke='green' stroke-width='2' d='M38.48481038370846,30.71257039573566 a 20 20 0  0  0 -25.711504387461574 0.0'></path><path fill='none' stroke='green' stroke-width='2' d='M12.773305996246883,30.71257039573566 l 3.276608177155967 2.294305745404184'></path><path fill='none' stroke='green' stroke-width='2' d='M16.04991417340285,33.00687614113984 a 20 20 0  0  1 16.647909629071336 2.9354756400015236'></path><path fill='none' stroke='green' stroke-width='2' d='M32.69782380247419,35.94235178114136 a 30 30 0  0  0 -2.9994288199638195 34.28362829059617'></path><path fill='none' stroke='green' stroke-width='2' d='M29.698394982510372,70.22598007173752 l -5.142300877492315 6.128355544951824'></path><path fill='none' stroke='green' stroke-width='2' d='M24.556094105018058,76.35433561668935 a 5 5 0  1  0 8.160349234517083 5.713938048432693'></path><path fill='none' stroke='green' stroke-width='2' d='M32.71644333953514,82.06827366512205 l 2.5000000000000004 -4.330127018922194'></path><path fill='none' stroke='green' stroke-width='2' d='M35.21644333953514,77.73814664619985 a 25 25 0  0  0 14.809906636301196 8.550503583141719'></path><path fill='none' stroke='green' stroke-width='2' d='M47,13 a 2 2 0  0  1 -2.2855752193730803 3.2641396938068326'></path><path fill='none' stroke='green' stroke-width='2' d='M42,31 l 4.698463103929543 1.7101007166283442'></path><path fill='none' stroke='green' stroke-width='2' d='M46.69846310392954,32.71010071662835 l 0.6945927106677217 3.939231012048832'></path><path fill='none' stroke='green' stroke-width='2' d='M47.39305581459726,36.649331728677176 l -3.0641777724759116 2.5711504387461575'></path><path fill='none' stroke='green' stroke-width='2' d='M44.328878042121346,39.220482167423334 l -7.878462024097664 -1.3891854213354424'></path><path fill='none' stroke='green' stroke-width='2' d='M36.45041601802368,37.831296746087894 l 7.878462024097664 1.3891854213354433'></path><path fill='none' stroke='green' stroke-width='2' d='M44.328878042121346,39.220482167423334 l 1.7101007166283442 4.698463103929543'></path><path fill='none' stroke='green' stroke-width='2' d='M46.03897875874969,43.918945271352875 l -3.2139380484326967 3.83022221559489'></path><path fill='none' stroke='green' stroke-width='2' d='M42.825040710317,47.74916748694776 l -10.0 6.123233995736766e-16'></path><path fill='none' stroke='green' stroke-width='2' d='M32.825040710317,47.74916748694776 l 10.0 6.123233995736766e-16'></path><path fill='none' stroke='green' stroke-width='2' d='M42.825040710317,47.74916748694776 l 3.000000000000001 5.196152422706632'></path><path fill='none' stroke='green' stroke-width='2' d='M45.825040710317,52.945319909654394 l -2.9999999999999987 5.196152422706632'></path><path fill='none' stroke='green' stroke-width='2' d='M42.825040710317,58.141472332361026 l -9.84807753012208 1.7364817766693041'></path><path fill='none' stroke='green' stroke-width='2' d='M32.976963180194915,59.87795410903033 l 9.84807753012208 -1.736481776669303'></path><path fill='none' stroke='green' stroke-width='2' d='M42.825040710317,58.141472332361026 l 3.2139380484326967 3.83022221559489'></path><path fill='none' stroke='green' stroke-width='2' d='M46.03897875874969,61.97169454795591 l -0.8682408883346515 4.92403876506104'></path><path fill='none' stroke='green' stroke-width='2' d='M45.17073787041504,66.89573331301695 l -6.92820323027551 4.000000000000001'></path><path fill='none' stroke='green' stroke-width='2' d='M38.24253464013953,70.89573331301695 l 6.92820323027551 -3.9999999999999982'></path><path fill='none' stroke='green' stroke-width='2' d='M45.17073787041504,66.89573331301695 l 3.464101615137755 2.0000000000000004'></path><path fill='none' stroke='green' stroke-width='2' d='M48.634839485552796,68.89573331301695 l 0.6945927106677217 3.939231012048832'></path><path fill='none' stroke='green' stroke-width='2' d='M49.329432196220516,72.83496432506578 l -2.499999999999999 4.330127018922194'></path><path fill='none' stroke='green' stroke-width='2' d='M50,10 a 2 2 0  0  1 1.532088886237956 0.7144247806269213'></path><path fill='none' stroke='green' stroke-width='2' d='M51.53208888623796,10.71442478062692 a 30 30 0  0  1 6.5628992967969015 14.074182960588265'></path><path fill='none' stroke='green' stroke-width='2' d='M58.09498818303486,24.788607741215188 a 10 10 0  0  0 3.420201433256689 5.923962654520478'></path><path fill='none' stroke='green' stroke-width='2' d='M61.51518961629154,30.712570395735668 a 20 20 0  0  1 25.711504387461574 0.0'></path><path fill='none' stroke='green' stroke-width='2' d='M87.22669400375312,30.712570395735668 l -3.2766081771559663 2.294305745404184'></path><path fill='none' stroke='green' stroke-width='2' d='M83.95008582659716,33.006876141139855 a 20 20 0  0  0 -16.647909629071336 2.935475640001534'></path><path fill='none' stroke='green' stroke-width='2' d='M67.30217619752582,35.94235178114139 a 30 30 0  0  1 2.9994288199638266 34.28362829059617'></path><path fill='none' stroke='green' stroke-width='2' d='M70.30160501748965,70.22598007173755 l 5.142300877492315 6.128355544951824'></path><path fill='none' stroke='green' stroke-width='2' d='M75.44390589498197,76.35433561668938 a 5 5 0  1  1 -8.160349234517076 5.713938048432693'></path><path fill='none' stroke='green' stroke-width='2' d='M67.2835566604649,82.06827366512208 l -2.500000000000002 -4.330127018922194'></path><path fill='none' stroke='green' stroke-width='2' d='M64.7835566604649,77.73814664619988 a 25 25 0  0  1 -14.80990663630119 8.550503583141715'></path><path fill='none' stroke='green' stroke-width='2' d='M53,13 a 2 2 0  0  0 2.2855752193730803 3.2641396938068326'></path><path fill='none' stroke='green' stroke-width='2' d='M58,31 l -4.698463103929542 1.7101007166283442'></path><path fill='none' stroke='green' stroke-width='2' d='M53.30153689607046,32.71010071662835 l -0.6945927106677212 3.939231012048832'></path><path fill='none' stroke='green' stroke-width='2' d='M52.60694418540274,36.649331728677176 l 3.064177772475912 2.5711504387461575'></path><path fill='none' stroke='green' stroke-width='2' d='M55.671121957878654,39.220482167423334 l 7.878462024097664 -1.3891854213354424'></path><path fill='none' stroke='green' stroke-width='2' d='M63.54958398197632,37.831296746087894 l -7.878462024097664 1.3891854213354433'></path><path fill='none' stroke='green' stroke-width='2' d='M55.671121957878654,39.220482167423334 l -1.7101007166283435 4.698463103929543'></path><path fill='none' stroke='green' stroke-width='2' d='M53.96102124125031,43.918945271352875 l 3.2139380484326967 3.83022221559489'></path><path fill='none' stroke='green' stroke-width='2' d='M57.174959289683,47.74916748694776 l 10.0 6.123233995736766e-16'></path><path fill='none' stroke='green' stroke-width='2' d='M67.174959289683,47.74916748694776 l -10.0 6.123233995736766e-16'></path><path fill='none' stroke='green' stroke-width='2' d='M57.174959289683,47.74916748694776 l -2.9999999999999987 5.196152422706632'></path><path fill='none' stroke='green' stroke-width='2' d='M54.174959289683,52.945319909654394 l 3.000000000000001 5.196152422706632'></path><path fill='none' stroke='green' stroke-width='2' d='M57.174959289683,58.141472332361026 l 9.84807753012208 1.7364817766693041'></path><path fill='none' stroke='green' stroke-width='2' d='M67.02303681980509,59.87795410903033 l -9.84807753012208 -1.736481776669303'></path><path fill='none' stroke='green' stroke-width='2' d='M57.174959289683,58.141472332361026 l -3.2139380484326967 3.83022221559489'></path><path fill='none' stroke='green' stroke-width='2' d='M53.96102124125031,61.97169454795591 l 0.8682408883346521 4.92403876506104'></path><path fill='none' stroke='green' stroke-width='2' d='M54.82926212958496,66.89573331301695 l 6.92820323027551 4.000000000000001'></path><path fill='none' stroke='green' stroke-width='2' d='M61.75746535986047,70.89573331301695 l -6.928203230275509 -3.9999999999999982'></path><path fill='none' stroke='green' stroke-width='2' d='M54.82926212958496,66.89573331301695 l -3.464101615137755 2.0000000000000004'></path><path fill='none' stroke='green' stroke-width='2' d='M51.365160514447204,68.89573331301695 l -0.6945927106677212 3.939231012048832'></path><path fill='none' stroke='green' stroke-width='2' d='M50.670567803779484,72.83496432506578 l 2.5000000000000004 4.330127018922194'></path></g></defs>"
        s += "<g id='draw'>\n"
        s += self.draw
        s += "</g>\n"
        s += "<g id='cut'>\n"
        s += self.cut
        s += "</g>\n"
        if turtle:
            s += "<g id='turtle'>\n"
            s += "<use href='#curseur' transform='translate("+str(self.turtle_x-5)+","+str(self.turtle_y-5)+") scale(0.1, 0.1) rotate("+str(self.turtle_heading)+",50,50)'/>"
            s += "</g>\n"
        s += "</svg>\n"
        return s

    def export_svg(self, nom):
        """ Enregistre le dessin vectoriel en svg sans la tortue dans le fichier nom.svg """
        f = open(nom+".svg", mode="w", encoding="utf-8")
        f.write(self.to_svg(False))
        f.close()

    def _repr_svg_(self):
        """ Affichage pour Ipython et notebook jupyter """
        return self.to_svg()

""" Fin du module : laser_turtle """
