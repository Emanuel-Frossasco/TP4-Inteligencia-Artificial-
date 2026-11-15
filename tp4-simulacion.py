import math
import time

class HoughRectasPuro:
    def __init__(self, ancho=10, alto=10, paso_theta=10):
        self.ancho = ancho
        self.alto = alto
        self.paso_theta = paso_theta
        # Muestreo angular theta en [0, 180) grados
        self.thetas = [math.radians(deg) for deg in range(0, 180, paso_theta)]
        self.n_thetas = len(self.thetas)
        # Diagonal máxima: rho en [-rho_max, +rho_max]
        self.rho_max = math.ceil(math.sqrt((ancho - 1) ** 2 + (alto - 1) ** 2))
        self.n_rhos = 2 * self.rho_max + 1
        # Acumulador 2D (filas: rho, columnas: theta)
        self.acumulador = [[0] * self.n_thetas for _ in range(self.n_rhos)]
    def procesar(self, imagen):
        self.acumulador = [[0] * self.n_thetas for _ in range(self.n_rhos)]
        for y in range(self.alto):
            for x in range(self.ancho):
                if imagen[y][x] == 1:
                    for idx_theta, th in enumerate(self.thetas):
                        rho = x * math.cos(th) + y * math.sin(th)
                        rho_idx = int(round(rho)) + self.rho_max   
                        if 0 <= rho_idx < self.n_rhos:
                            self.acumulador[rho_idx][idx_theta] += 1
    def celdas_mas_votadas(self, n=3):
        """Lista de (votos, theta_grados, rho) ordenada de mayor a menor."""
        celdas = []
        for r_idx in range(self.n_rhos):
            for t_idx in range(self.n_thetas):
                celdas.append((self.acumulador[r_idx][t_idx],
                               t_idx * self.paso_theta,
                               r_idx - self.rho_max))
        celdas.sort(key=lambda c: (-c[0], c[1], c[2]))
        return celdas[:n]
    def obtener_maximo(self):
        votos, theta, rho = self.celdas_mas_votadas(1)[0]
        return theta, rho, votos

class HoughCircunferenciasPuro:
    def __init__(self, ancho=10, alto=10, radio_nominal=3.0):
        self.ancho = ancho
        self.alto = alto
        self.radio = radio_nominal
        self.acumulador = [[0] * ancho for _ in range(alto)]
    def procesar(self, imagen, paso_phi=5):
        self.acumulador = [[0] * self.ancho for _ in range(self.alto)]
        angulos = [math.radians(deg) for deg in range(0, 360, paso_phi)]
        for y in range(self.alto):
            for x in range(self.ancho):
                if imagen[y][x] == 1:
                    for phi in angulos:
                        x0 = int(round(x - self.radio * math.cos(phi)))
                        y0 = int(round(y - self.radio * math.sin(phi)))
                        if 0 <= x0 < self.ancho and 0 <= y0 < self.alto:
                            self.acumulador[y0][x0] += 1
    def celdas_maximas(self):
        maximo = max(max(fila) for fila in self.acumulador)
        celdas = [(x0, y0) for y0 in range(self.alto) for x0 in range(self.ancho)
                  if self.acumulador[y0][x0] == maximo]
        return celdas, maximo
    def obtener_maximo(self):
        celdas, maximo = self.celdas_maximas()
        return celdas[0][0], celdas[0][1], maximo
    def piso_fuera_del_pico(self, x_pico, y_pico):
        piso = 0
        for y0 in range(self.alto):
            for x0 in range(self.ancho):
                if max(abs(x0 - x_pico), abs(y0 - y_pico)) > 1:
                    piso = max(piso, self.acumulador[y0][x0])
        return piso

def imagen_vacia(ancho=10, alto=10):
    return [[0] * ancho for _ in range(alto)]
def generar_aro(cx, cy, radio, ancho=10, alto=10):
    img = imagen_vacia(ancho, alto)
    for y in range(alto):
        for x in range(ancho):
            if abs(math.hypot(x - cx, y - cy) - radio) < 0.5:
                img[y][x] = 1
    return img
def poner(img, puntos, valor):
    for (y, x) in puntos:
        img[y][x] = valor
def contar(img):
    return sum(sum(fila) for fila in img)
def imprimir_matriz(mat, titulo):
    print(f"\n--- {titulo} ---")
    for fila in mat:
        print(" " + " ".join("X" if v == 1 else "." for v in fila))
def imprimir_acumulador(acc, titulo):
    print(f"\n--- {titulo} ---")
    print("      " + " ".join(f"{x:3d}" for x in range(len(acc[0]))) + "   <- x0")
    for y, fila in enumerate(acc):
        print(f" y0={y} " + " ".join(f"{v:3d}" for v in fila))
def medir_ms(funcion, repeticiones=100):
    t0 = time.perf_counter()
    for _ in range(repeticiones):
        funcion()
    return (time.perf_counter() - t0) / repeticiones * 1000.0
def detectar_circulo(img, radio, paso_phi=5):
    h = HoughCircunferenciasPuro(len(img[0]), len(img), radio)
    h.procesar(img, paso_phi)
    celdas, votos = h.celdas_maximas()
    return h, celdas, votos

if __name__ == "__main__":
    linea = "=" * 70
    print(linea)
    print("UNIVERSIDAD SIGLO 21 - TRABAJO PRACTICO N° 4")
    print("TRANSFORMADA DE HOUGH EN PYTHON (RECTAS Y CIRCUNFERENCIAS)")
    print(linea)
    print("\nENSAYO 1: HOUGH DE RECTAS")
    img_recta = imagen_vacia()
    poner(img_recta, [(3, x) for x in range(2, 8)], 1)     
    poner(img_recta, [(1, 8), (7, 1)], 1)                  
    imprimir_matriz(img_recta, "Entrada: arista del block con ruido (y = 3)")
    h_recta = HoughRectasPuro(10, 10, paso_theta=10)
    h_recta.procesar(img_recta)
    th, rho, votos = h_recta.obtener_maximo()
    top = h_recta.celdas_mas_votadas(3)
    img_solo_ruido = imagen_vacia()
    poner(img_solo_ruido, [(1, 8), (7, 1)], 1)
    h_ruido = HoughRectasPuro(10, 10, 10)
    h_ruido.procesar(img_solo_ruido)
    ruido_max = max(max(f) for f in h_ruido.acumulador)
    print("\nRESULTADO HOUGH RECTAS")
    print(f"Acumulador: {h_recta.n_rhos} filas (rho) x {h_recta.n_thetas} columnas (theta)")
    print(f"Pico: theta = {th} grados, rho = {rho} px, {votos} votos (de 6 puntos de la recta)")
    print(f"Ecuacion inferida: y = {rho}" if th == 90 else f"Normal a {th} grados, rho = {rho}")
    print(f"2.º puesto (celda vecina): theta = {top[1][1]}, rho = {top[1][2]} ({top[1][0]} votos)")
    print(f"Maximo de votos por ruido aislado: {ruido_max}")
    print("\nEfecto del paso angular (recta y = x; esperado: theta = 135, rho = 0):")
    img_diag = imagen_vacia()
    poner(img_diag, [(i, i) for i in range(2, 8)], 1)
    for paso in (10, 5, 1):
        h = HoughRectasPuro(10, 10, paso)
        h.procesar(img_diag)
        t, r, v = h.obtener_maximo()
        print(f"  paso {paso:2d} grados -> theta = {t:3d}, rho = {r:2d}, votos = {v}")
    img_vert = imagen_vacia()
    poner(img_vert, [(y, 4) for y in range(2, 8)], 1)
    h = HoughRectasPuro(10, 10, 10)
    h.procesar(img_vert)
    t, r, v = h.obtener_maximo()
    print(f"Recta vertical x = 4 (sin singularidad en polares): theta = {t}, rho = {r}, votos = {v}")
    print("\n" + linea)
    print("ENSAYO 2: HOUGH DE CIRCUNFERENCIAS (R conocido = 3 px)")
    print(linea)
    CX, CY, R = 5, 5, 3.0
    img_aro = generar_aro(CX, CY, R)
    teoricos = contar(img_aro)
    rotura = [(4, 8), (5, 8), (6, 8)]                       
    ruido = [(1, 8), (8, 1), (0, 0)]                        
    poner(img_aro, rotura, 0)
    poner(img_aro, ruido, 1)
    imprimir_matriz(img_aro, "Entrada: aro C (centro 5,5; R = 3) con rotura y ruido")
    print(f"Pixeles teoricos del aro: {teoricos} | faltantes: {len(rotura)} "
          f"({len(rotura) / teoricos:.0%}) | ruido: {len(ruido)} | activos: {contar(img_aro)}")
    h_circ, celdas, votos_c = detectar_circulo(img_aro, R)
    cx, cy = celdas[0]
    piso = h_circ.piso_fuera_del_pico(cx, cy)
    imprimir_acumulador(h_circ.acumulador, "Acumulador de centros candidatos (x0, y0)")
    print("\nRESULTADO HOUGH CIRCUNFERENCIAS")
    print(f"Centro inferido del aro 'A': X = {cx:.2f}, Y = {cy:.2f}")
    print(f"Votos del pico:              {votos_c}")
    print(f"Mayor valor fuera del pico:  {piso} votos (relacion {votos_c / piso:.1f} : 1)")
    print(f"Celdas empatadas en el maximo: {len(celdas)}")
    desvio = math.hypot(cx - CX, cy - CY)
    print("Localización: " + ("EXACTA (coincide con el centro teórico 5,5)" if desvio == 0
                              else f"desvío de {desvio:.2f} px respecto del centro teorico 5,5"))
    print("\n" + linea)
    print("ENSAYO 3: TRASLACION DEL ARO (R = 3, mismos defectos relativos)")
    print(linea)
    for (cx_t, cy_t) in ((5, 5), (3, 4), (6, 6), (8, 5)):
        img_t = generar_aro(cx_t, cy_t, R)
        n_visibles = contar(img_t)
        _, cel, v = detectar_circulo(img_t, R)
        empate = f" | EMPATE de {len(cel)} celdas" if len(cel) > 1 else ""
        print(f"Real ({cx_t},{cy_t}) | {n_visibles:2d} px visibles | detectado {cel[0]} | {v:2d} votos{empate}")
    print("\n" + linea)
    print("ENSAYO 4: SENSIBILIDAD AL RADIO NOMINAL ASUMIDO (aro real R = 3)")
    print(linea)
    img_base = generar_aro(CX, CY, R)
    for r_asumido in (2.0, 2.5, 3.0, 3.5, 4.0):
        _, cel, v = detectar_circulo(img_base, r_asumido)
        print(f"R asumido = {r_asumido:.1f} px -> pico {v:2d} votos | {len(cel)} celda(s) en el maximo | primera {cel[0]}")
    print("\n" + linea)
    print("TIEMPOS DE EJECUCION (imagen de 10 x 10, promedio de 100 corridas)")
    print(linea)
    t_rec = medir_ms(lambda: (h_recta.procesar(img_recta), h_recta.obtener_maximo()))
    t_cir = medir_ms(lambda: (h_circ.procesar(img_aro, 5), h_circ.obtener_maximo()))
    print(f"Hough de rectas:          {t_rec:.3f} ms")
    print(f"Hough de circunferencias: {t_cir:.3f} ms")
    print(linea)