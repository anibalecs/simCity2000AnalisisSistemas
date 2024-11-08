import random
import time
import threading

class Cuadricula:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.estructura = None
        self.en_obra = False

    def via_vecino(self, mapa):
        vecinos = [(self.x - 1, self.y), (self.x + 1, self.y), (self.x, self.y - 1), (self.x, self.y + 1)]
        for vx, vy in vecinos:
            if not (0 <= vx < len(mapa) and 0 <= vy < len(mapa[0])):
                return False
            vecino = mapa[vx][vy]
            if not isinstance(vecino.estructura, Via) or vecino.en_obra:
                return False
        return True

class Tierra(Cuadricula):
    pass

class Agua(Cuadricula):
    pass

class Construccion:
    def __init__(self, costo, duracion_obra, impuesto):
        self.costo = costo
        self.duracion_obra = duracion_obra
        self.impuesto = impuesto
        self.obra = True

    def generar_ingreso(self):
        return self.impuesto if not self.obra else 0

    def finalizar_construccion(self):
        self.obra = False

class Casa(Construccion):
    def __init__(self):
        super().__init__(costo=100, duracion_obra=30, impuesto=30)

class Via(Construccion):
    def __init__(self):
        super().__init__(costo=50, duracion_obra=15, impuesto=0)

class Jugador:
    def __init__(self, nombre, dinero_inicial=750):
        self.nombre = nombre
        self.dinero = dinero_inicial

    def construir(self, cuadricula, construccion, mapa):
        if cuadricula.estructura is not None:
            print("Ya hay una estructura en esta ubicación.")
            return
        if isinstance(cuadricula, Agua):
            print("No se puede construir en el agua.")
            return
        if isinstance(construccion, Casa) and not cuadricula.via_vecino(mapa):
            print("Una casa debe estar junto a cuatro vías que estén terminadas.")
            return
        if self.dinero < construccion.costo:
            print("Dinero insuficiente para construir.")
            return

        self.dinero -= construccion.costo
        cuadricula.estructura = construccion
        cuadricula.en_obra = True
        print(f"Construcción de {type(construccion).__name__} en ({cuadricula.y}, {cuadricula.x}) iniciada.")
        threading.Thread(target=juego.construir_async, args=(cuadricula,)).start()

    def demoler(self, cuadricula):
        if cuadricula.en_obra:
            print("No se puede demoler una obra en construcción.")
            return

        
        if isinstance(cuadricula.estructura, Casa):
            costo_demolicion = 50  
        elif isinstance(cuadricula.estructura, Via):
            costo_demolicion = 25  
        else:
            print("No hay nada para demoler aquí o dinero insuficiente.")
            return

        
        if isinstance(cuadricula.estructura, Via):
            vecinos = [
                (cuadricula.x - 1, cuadricula.y),
                (cuadricula.x + 1, cuadricula.y),
                (cuadricula.x, cuadricula.y - 1),
                (cuadricula.x, cuadricula.y + 1),
            ]
            for vx, vy in vecinos:
                if 0 <= vx < len(juego.mapa) and 0 <= vy < len(juego.mapa[0]):
                    vecino = juego.mapa[vx][vy]
                    if isinstance(vecino.estructura, Casa):
                        print("No se puede demoler la vía, ya que está adyacente a una casa.")
                        return

        if self.dinero >= costo_demolicion:
            self.dinero -= costo_demolicion
            cuadricula.estructura = None
            cuadricula.en_obra = False
            print(f"Construcción en ({cuadricula.y}, {cuadricula.x}) demolida. Costo de demolición: {costo_demolicion}.")
        else:
            print("Dinero insuficiente para demoler.")


class Terremoto:
    def __init__(self, intensidad=3):
        self.intensidad = intensidad

    def destruir_construcciones(self, mapa, actualizaciones, lock):
        with lock:
            destrucciones_realizadas = 0
            while destrucciones_realizadas < self.intensidad:
                x, y = random.randint(0, len(mapa) - 1), random.randint(0, len(mapa[0]) - 1)
                cuadricula = mapa[x][y]

                
                if cuadricula.estructura is not None:
                    cuadricula.estructura = None
                    cuadricula.en_obra = False
                    actualizaciones.append(f"Construcción en ({x}, {y}) destruida por terremoto.")
                    destrucciones_realizadas += 1

            
            for fila in mapa:
                for cuadricula in fila:
                    
                    if isinstance(cuadricula.estructura, Casa) and not cuadricula.via_vecino(mapa):
                        cuadricula.estructura = None
                        cuadricula.en_obra = False
                        actualizaciones.append(f"Casa en ({cuadricula.x}, {cuadricula.y}) demolida por falta de vías adyacentes.")

class Juego:
    def __init__(self, jugador):
        self.mapa = [[self.crear_cuadricula(x, y) for y in range(10)] for x in range(10)]
        self.jugador = jugador
        self.juego_terminado = False
        self.actualizaciones = []
        self.lock = threading.Lock()
        

        self.hilo_ingresos = threading.Thread(target=self.ingresos_jugador)
        self.hilo_terremoto = threading.Thread(target=self.evento_terremoto)
        self.hilo_ingresos.start()
        self.hilo_terremoto.start()
    
    def evento_terremoto(self):
        terremoto = Terremoto(intensidad=3)
        while not self.juego_terminado:
            time.sleep(180)  
            terremoto.destruir_construcciones(self.mapa, self.actualizaciones, self.lock)
            self.actualizaciones.append("¡Un terremoto ha golpeado la ciudad!")

    def crear_cuadricula(self, x, y):
        tipo = random.choice([Tierra, Agua])
        return tipo(x, y)

    def ingresos_jugador(self):
        while not self.juego_terminado:
            with self.lock:
                for fila in self.mapa:
                    for cuadricula in fila:
                        if isinstance(cuadricula.estructura, Casa) and not cuadricula.en_obra and cuadricula.estructura:
                            ingreso = cuadricula.estructura.generar_ingreso()
                            self.jugador.dinero += ingreso
                            self.actualizaciones.append(f"Ingreso generado en casa en ({cuadricula.y}, {cuadricula.x}): +{ingreso} dinero.")
            time.sleep(60)  

    

    def obtener_cuadricula(self):
        while True:
            try:
                x = int(input("Ingrese la coordenada en X (0-9): "))
                y = int(input("Ingrese la coordenada en Y (0-9): "))
                if 0 <= x < 10 and 0 <= y < 10:
                    return self.mapa[x][y]
                else:
                    print("Coordenadas inválidas. Intente nuevamente.")
            except ValueError:
                print("Ingreso inválido. Ingrese números entre 0 y 9.")

    def construir_async(self, cuadricula):
        time.sleep(cuadricula.estructura.duracion_obra)
        with self.lock:
            cuadricula.estructura.finalizar_construccion()
            cuadricula.en_obra = False
            self.actualizaciones.append(f"{type(cuadricula.estructura).__name__} en ({cuadricula.y}, {cuadricula.x}) finalizada.")

    def turno(self):
        while not self.juego_terminado:
            with self.lock:
                for mensaje in self.actualizaciones:
                    print(mensaje)
                self.actualizaciones.clear()
            self.mostrar()
            accion = input("Menu (casa, via, demoler, salir): ").strip().lower()
            if accion == "salir":
                print(f"Gracias por jugar {self.jugador.nombre}.")
                self.juego_terminado = True
                break
            elif accion in ["casa", "via", "demoler"]:
                cuadricula = self.obtener_cuadricula()
                if accion == "casa":
                    self.jugador.construir(cuadricula, Casa(), self.mapa)
                elif accion == "via":
                    self.jugador.construir(cuadricula, Via(), self.mapa)
                elif accion == "demoler":
                    self.jugador.demoler(cuadricula)
            else:
                print("Acción no válida. Intente de nuevo.")

    def mostrar(self):
        simbolos = {"Tierra": "T", "Agua": "A", "Via": "V", "Casa": "C"}
        for fila in self.mapa:
            fila_simbolos = [
                "O" if b.en_obra else simbolos[type(b.estructura).__name__] if b.estructura else simbolos[type(b).__name__]
                for b in fila
            ]
            print(" ".join(fila_simbolos))
        print(f"Dinero: {self.jugador.dinero}")

if __name__ == "__main__":
    nombre = input("Ingrese su nombre: ")
    jugador = Jugador(nombre)
    juego = Juego(jugador)
    

    juego.turno()
    

    juego.hilo_ingresos.join()
    juego.hilo_terremoto.join()
    print("Fin del juego.")