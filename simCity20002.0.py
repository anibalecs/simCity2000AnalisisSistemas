import random
import time
import threading

class Cuadricula:
    def __init__(self, x, y, tipo):
        self.x = x
        self.y = y
        self.tipo = tipo  #agua, tierra, via, casa
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
        self.tiempo_construccion = 5

    def construccion_lista(self):
        self.obra = False
        print("Construccion completada!")

    def generar_dinero(self):
        return 30

class Via(Construccion):
    def __init__(self):
        super().__init__(costo=50)

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
                print(f"Casa comprada en ({cuadricula.x}, {cuadricula.y})")
                time.sleep(casa.tiempo_construccion)
                casa.construccion_lista()
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
                print(f"Via construida en ({cuadricula.x}, {cuadricula.y})")
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
                print(f"Construccion en ({cuadricula.x}, {cuadricula.y}) demolida")
            else:
                print("Dinero insuficiente")
        else:
            print("No hay nada para demoler aqui")

class Terremoto:
    def __init__(self, intensidad=3):
        self.intensidad = intensidad

    def destruir_construcciones(self, mapa):
        print("Terremoto! Algunas construcciones fueron destruidas")
        for _ in range(self.intensidad):
            x, y = random.randint(0, 9), random.randint(0, 9)
            if(mapa[x][y].construccion):
                mapa[x][y].demoler()
                print(f"Construcción en ({x}, {y}) destruida")

class Juego:
    def __init__(self, jugador):
        self.mapa = [[self.crear_cuadricula(x, y) for y in range(10)] for x in range(10)]
        self.jugador = jugador

    def crear_cuadricula(self, x, y):
        tipo = random.choice(["tierra", "agua"])
        return Cuadricula(x, y, tipo)

    def mostrar_mapa(self):
        simbolos = {"tierra": "T", "agua": "A", "via": "V", "casa": "C"}
        for fila in self.mapa:
            print(" ".join([simbolos[cuadricula.tipo] for cuadricula in fila]))

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

    def turno(self):
        while not self.juego_terminado:
            self.mostrar_mapa()
            print(f"Dinero: {self.jugador.dinero}")
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
        while True:
            time.sleep(300) #cada tantos segundos da plata por casa
            for fila in self.mapa:
                for cuadricula in fila:
                    if(cuadricula.tipo == "casa" and cuadricula.construccion):
                        self.jugador.dinero += cuadricula.construccion.generar_dinero()
            print("\n Actualizacion por ingresos:")
            self.mostrar_mapa()

    def terremoto_random(self):
        while not self.juego_terminado:
            time.sleep(random.randint(1000, 1500)) #terremoto random cada tantos o tantos segundos
            terremoto = Terremoto()
            terremoto.destruir_construcciones(self.mapa)
            print("\nActualizacion de mapa por terremoto:")
            self.mostrar_mapa()

if(__name__ == "__main__"):
    nombre = input("Ingrese su nombre: ")
    jugador = Jugador(nombre)
    juego = Juego(jugador)

    #inicia hilos para ingresos y terremotos
    threading.Thread(target = juego.ingresos_jugador, daemon = True).start()
    threading.Thread(target = juego.terremoto_random, daemon = True).start()

    juego.turno()