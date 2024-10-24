import random
import time
import threading

class Cuadricula:
    def __init__(self, x, y, tipo):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.construccion = None

    def via_vecino(self, mapa):
        vecinos = [(self.x - 1, self.y), (self.x + 1, self.y), 
                   (self.x, self.y - 1), (self.x, self.y + 1)]
        for vx, vy in vecinos:
            if 0 <= vx < 10 and 0 <= vy < 10 and mapa[vx][vy].tipo == "via":
                return True
        return False

    def demoler(self):
        self.tipo = "tierra"
        self.construccion = None

class Construccion:
    def __init__(self, costo):
        self.costo = costo

class Casa(Construccion):
    def __init__(self):
        super().__init__(costo=100)
        self.obra = True
        self.tiempo_construccion = 30 #120 luego

    def construccion_lista(self):
        self.obra = False

    def generar_dinero(self):
        if(not self.obra):
            return 30
        return 0

class Via(Construccion):
    def __init__(self):
        super().__init__(costo=50)
        self.obra = True
        self.tiempo_construccion = 15 #60 luego

    def construccion_lista(self):
        self.obra = False

class Jugador:
    def __init__(self, nombre, dinero_inicial=750):
        self.nombre = nombre
        self.dinero = dinero_inicial

    def comprar_casa(self, cuadricula, mapa):
        if(cuadricula.tipo == "agua"):
            print("No se puede construir en el agua")
            return
        if(cuadricula.tipo == "tierra" and cuadricula.via_vecino(mapa)):
            casa = Casa()
            if(self.dinero >= casa.costo):
                self.dinero -= casa.costo
                cuadricula.tipo = "casa"
                cuadricula.construccion = casa
                print(f"Casa comprada en ({cuadricula.y}, {cuadricula.x})")

                threading.Thread(target=juego.construir_casa_async, args=(cuadricula,), daemon=True).start() #hilo para la obra
            else:
                print("Dinero insuficiente")
        else:
            print("No se puede construir una casa aqui")

    def construir_via(self, cuadricula):
        if(cuadricula.tipo == "agua"):
            print("No se puede construir en el agua")
            return
        if(cuadricula.tipo == "tierra"):
            via = Via()
            if(self.dinero >= via.costo):
                self.dinero -= via.costo
                cuadricula.tipo = "via"
                cuadricula.construccion = via
                print(f"Via en construccion en ({cuadricula.y}, {cuadricula.x})") #invertido

                threading.Thread(target=juego.construir_via_async, args=(cuadricula,), daemon=True).start()
            else:
                print("Dinero insuficiente")
        else:
            print("No se puede construir una via aqui")

    def demoler(self, cuadricula):
        if(cuadricula.construccion):
            costo_demolicion = 20
            if(self.dinero >= costo_demolicion):
                self.dinero -= costo_demolicion
                cuadricula.demoler()
                print(f"Construccion en ({cuadricula.y}, {cuadricula.x}) demolida") #invertido
            else:
                print("Dinero insuficiente")
        else:
            print("No hay nada para demoler aqui")

class Terremoto:
    def __init__(self, intensidad=3):
        self.intensidad = intensidad

    def destruir_construcciones(self, mapa, actualizaciones, lock):
        destruido = False
        with lock:
            for _ in range(self.intensidad):
                x, y = random.randint(0, 9), random.randint(0, 9)
                if(mapa[x][y].construccion):
                    mapa[x][y].demoler()
                    actualizaciones.append(f"Construcción en ({x}, {y}) destruida")
                    destruido = True
            if(not destruido):
                actualizaciones.append("Terremoto! Pero no se destuyo ninguna construccion")

class Juego:
    def __init__(self, jugador):
        self.mapa = [[self.crear_cuadricula(x, y) for y in range(10)] for x in range(10)]
        self.jugador = jugador
        self.juego_terminado = False
        self.actualizaciones = []
        self.lock = threading.Lock()

    def crear_cuadricula(self, x, y):
        tipo = random.choice(["tierra", "agua"])
        return Cuadricula(x, y, tipo)

    def obtener_cuadricula(self):
        while True:
            try:
                x = int(input("Ingrese la coordenada en X (0-9): "))
                y = int(input("Ingrese la coordenada en Y (0-9): "))
                if(0 <= x < 10 and 0 <= y < 10):
                    return self.mapa[y][x]  #se invierte para que x quede como fila y y como columna
                else:
                    print("Coordenadas invalidas, intente nuevamente")
            except ValueError:
                print("Ingreso invalido, ingrese numeros entre 0 y 9")

    def verificar_dinero(self):
        if(self.jugador.dinero <= 0):
            print(f"{self.jugador.nombre}, fin del juego. Te has quedado sin dinero")
            self.juego_terminado = True

    def construir_casa_async(self, cuadricula):
        casa = cuadricula.construccion
        print(f"Construcción de casa iniciada en ({cuadricula.y}, {cuadricula.x})")
        
        time.sleep(casa.tiempo_construccion)
        with self.lock:
            casa.construccion_lista()
            self.actualizaciones.append(f"Construccion completa. Casa en ({cuadricula.y}, {cuadricula.x}) finalizada")

    def construir_via_async(self, cuadricula):
        via = cuadricula.construccion
        time.sleep(via.tiempo_construccion)
        with self.lock:
            via.construccion_lista()
            self.actualizaciones.append(f"Construccion completada. Via en ({cuadricula.y}, {cuadricula.x}) finalizada")

    def mostrar(self):
        simbolos = {"tierra": "T", "agua": "A", "via": "V", "casa": "C"}
        for fila in self.mapa:
            fila_simbolos = []
            for cuadricula in fila:
                if(cuadricula.construccion and cuadricula.construccion.obra):
                    fila_simbolos.append("O")
                else:
                    fila_simbolos.append(simbolos[cuadricula.tipo])
            print(" ".join(fila_simbolos))
        print(f"Dinero: {self.jugador.dinero}")

    def turno(self):
        while not self.juego_terminado:
            with self.lock:
                for mensaje in self.actualizaciones:
                    print(mensaje)
                self.actualizaciones.clear()

            self.mostrar()
            accion = input("Menu (casa, via, demoler, terremoto, salir): ").strip().lower()

            if(accion == "salir"):
                print(f"Gracias por jugar {self.jugador.nombre}.")
                break

            elif(accion in ["casa", "via", "demoler"]):
                cuadricula = self.obtener_cuadricula()
                if(accion == "casa"):
                    self.jugador.comprar_casa(cuadricula, self.mapa)
                elif(accion == "via"):
                    self.jugador.construir_via(cuadricula)
                elif(accion == "demoler"):
                    self.jugador.demoler(cuadricula)
            else:
                print("Accion no valida, intente de nuevo")

            self.verificar_dinero()

    def ingresos_jugador(self):
        while not self.juego_terminado:
            time.sleep(30)
            with self.lock:
                ingreso = sum(
                    c.construccion.generar_dinero() 
                    for fila in self.mapa for c in fila if c.tipo == "casa"
                )
                if ingreso > 0:
                    self.jugador.dinero += ingreso
                    self.actualizaciones.append(f"Ingresos recibidos: {ingreso}")

    def terremoto_random(self):
        while not self.juego_terminado:
            time.sleep(random.randint(60, 100))
            terremoto = Terremoto()
            terremoto.destruir_construcciones(self.mapa, self.actualizaciones, self.lock)

if(__name__ == "__main__"):
    nombre = input("Ingrese su nombre: ")
    jugador = Jugador(nombre)
    juego = Juego(jugador)

    #inicia hilos para ingresos y terremotos, esto permite que se ejecuten en paralelo y con el daemon permite que se ejecuten en segundo plano y asi continue el turno
    threading.Thread(target = juego.ingresos_jugador, daemon = True).start()
    threading.Thread(target = juego.terremoto_random, daemon = True).start()

    juego.turno()