import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from abc import ABC, abstractmethod
from datetime import datetime

# ==========================================================
# 1. MANEJO DE LOGS Y EXCEPCIONES PERSONALIZADAS
# ==========================================================
logging.basicConfig(
    filename='software_fj.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class SoftwareFJError(Exception):
    """Clase base para excepciones del sistema."""
    pass

class ValidacionError(SoftwareFJError):
    """Errores en la entrada de datos."""
    pass

class OperacionInvalidaError(SoftwareFJError):
    """Errores en lógica de negocio o servicios."""
    pass

# ==========================================================
# 2. ARQUITECTURA ORIENTADA A OBJETOS (MODELO)
# ==========================================================

class EntidadBase(ABC):
    """Clase abstracta que representa entidades generales."""
    def __init__(self, id_sistema):
        self._id_sistema = id_sistema  # Atributo protegido

    @abstractmethod
    def obtener_detalle(self):
        pass

class Cliente(EntidadBase):
    """Encapsulación de datos personales con validaciones estrictas."""
    def __init__(self, id_cliente, nombre, correo):
        super().__init__(id_cliente)
        if not nombre or len(nombre) < 3:
            raise ValidacionError(f"Nombre inválido: {nombre}")
        if "@" not in correo or "." not in correo:
            raise ValidacionError(f"Correo electrónico inválido: {correo}")
        
        self.__nombre = nombre  # Atributo privado
        self.__correo = correo  # Atributo privado

    @property
    def nombre(self):
        return self.__nombre

    def obtener_detalle(self):
        return f"Cliente: {self.__nombre} | Email: {self.__correo}"

class Servicio(ABC):
    """Clase abstracta Servicio con métodos polimórficos."""
    def __init__(self, nombre, precio_base):
        self.nombre = nombre
        self.precio_base = precio_base

    @abstractmethod
    def calcular_costo(self, cantidad, **kwargs):
        pass

    @abstractmethod
    def describir(self):
        pass

# --- ESPECIALIZACIONES (HERENCIA Y POLIMORFISMO) ---

class ReservaSalas(Servicio):
    def calcular_costo(self, horas, limpieza=False):
        # Simulación de sobrecarga con parámetros opcionales
        total = self.precio_base * horas
        if limpieza:
            total += 50.0
        return total

    def describir(self):
        return f"SALA: {self.nombre}"

class AlquilerEquipos(Servicio):
    def calcular_costo(self, dias, cantidad=1):
        if cantidad <= 0:
            raise OperacionInvalidaError("La cantidad de equipos debe ser mayor a 0.")
        return (self.precio_base * dias) * cantidad

    def describir(self):
        return f"EQUIPO: {self.nombre}"

class AsesoriaEspecializada(Servicio):
    def calcular_costo(self, horas, nivel="basico"):
        tarifas = {"basico": 1.0, "premium": 1.5, "senior": 2.0}
        if nivel not in tarifas:
            raise OperacionInvalidaError(f"Nivel '{nivel}' no existe.")
        return (self.precio_base * horas) * tarifas[nivel]

    def describir(self):
        return f"ASESORÍA: {self.nombre}"

class Reserva:
    """Integra cliente y servicio con manejo avanzado de excepciones."""
    def __init__(self, id_reserva, cliente, servicio, duracion):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "PENDIENTE"

    def procesar(self, **kwargs):
        try:
            if self.duracion <= 0:
                raise OperacionInvalidaError("La duración debe ser mayor a cero.")
            
            costo_final = self.servicio.calcular_costo(self.duracion, **kwargs)
            self.estado = "CONFIRMADA"
            
            info = f"Reserva {self.id_reserva} OK | {self.cliente.nombre} | Total: ${costo_final:.2f}"
            logging.info(info)
            return info

        except (ValidacionError, OperacionInvalidaError) as e:
            self.estado = "FALLIDA"
            logging.error(f"Error en Reserva {self.id_reserva}: {str(e)}")
            # Encadenamiento de excepciones
            raise OperacionInvalidaError("Fallo en procesamiento de reserva") from e
        except Exception as e:
            logging.critical(f"Error crítico: {str(e)}")
            raise
        finally:
            print(f"Intento de reserva {self.id_reserva} finalizado con estado: {self.estado}")

# ==========================================================
# 3. INTERFAZ GRÁFICA (GUI)
# ==========================================================

class SoftwareFJApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - Sistema Integral de Gestión")
        self.root.geometry("850x600")

        # Almacenamiento en memoria
        self.clientes = []
        self.servicios = [
            ReservaSalas("Sala de Juntas VIP", 80),
            AlquilerEquipos("Laptop Gamer High-End", 40),
            AsesoriaEspecializada("Consultoría Cloud", 150)
        ]

        self._setup_ui()
        self._ejecutar_simulacion_10_pasos()

    def _setup_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Pestaña Clientes
        self.tab_clientes = ttk.Frame(notebook)
        notebook.add(self.tab_clientes, text="Gestionar Clientes")
        
        ttk.Label(self.tab_clientes, text="Nombre:").grid(row=0, column=0, padx=10, pady=10)
        self.ent_nombre = ttk.Entry(self.tab_clientes)
        self.ent_nombre.grid(row=0, column=1)

        ttk.Label(self.tab_clientes, text="Email:").grid(row=1, column=0, padx=10, pady=10)
        self.ent_email = ttk.Entry(self.tab_clientes)
        self.ent_email.grid(row=1, column=1)

        ttk.Button(self.tab_clientes, text="Registrar", command=self.registrar_cliente).grid(row=2, column=0, columnspan=2, pady=10)

        # Pestaña Reservas
        self.tab_reservas = ttk.Frame(notebook)
        notebook.add(self.tab_reservas, text="Crear Reserva")

        ttk.Label(self.tab_reservas, text="Seleccionar Cliente:").grid(row=0, column=0, padx=10, pady=10)
        self.combo_clientes = ttk.Combobox(self.tab_reservas, state="readonly")
        self.combo_clientes.grid(row=0, column=1)

        ttk.Label(self.tab_reservas, text="Servicio:").grid(row=1, column=0, padx=10, pady=10)
        self.combo_servicios = ttk.Combobox(self.tab_reservas, values=[s.nombre for s in self.servicios], state="readonly")
        self.combo_servicios.grid(row=1, column=1)

        ttk.Label(self.tab_reservas, text="Duración (Cant):").grid(row=2, column=0, padx=10, pady=10)
        self.ent_duracion = ttk.Entry(self.tab_reservas)
        self.ent_duracion.grid(row=2, column=1)

        ttk.Button(self.tab_reservas, text="Procesar", command=self.procesar_reserva).grid(row=3, column=0, columnspan=2, pady=10)

        # Pestaña Logs
        self.tab_logs = ttk.Frame(notebook)
        notebook.add(self.tab_logs, text="Historial (Logs)")
        self.log_view = scrolledtext.ScrolledText(self.tab_logs, height=15)
        self.log_view.pack(fill='both', expand=True, padx=10, pady=10)
        ttk.Button(self.tab_logs, text="Actualizar Logs", command=self.actualizar_logs).pack(pady=5)

    def registrar_cliente(self):
        try:
            c = Cliente(len(self.clientes)+1, self.ent_nombre.get(), self.ent_email.get())
            self.clientes.append(c)
            self.actualizar_combos()
            messagebox.showinfo("Éxito", f"Cliente {c.nombre} registrado.")
        except ValidacionError as e:
            messagebox.showwarning("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error Crítico", "Error interno del sistema.")

    def procesar_reserva(self):
        try:
            idx_cli = self.combo_clientes.current()
            idx_srv = self.combo_servicios.current()
            duracion = float(self.ent_duracion.get() or 0)

            if idx_cli < 0 or idx_srv < 0: raise ValidacionError("Seleccione cliente y servicio.")

            res = Reserva(datetime.now().strftime("%H%M%S"), self.clientes[idx_cli], self.servicios[idx_srv], duracion)
            resultado = res.procesar()
            messagebox.showinfo("Reserva Confirmada", resultado)
        except (ValidacionError, OperacionInvalidaError, ValueError) as e:
            messagebox.showerror("Error de Reserva", str(e))
        finally:
            self.actualizar_logs()

    def actualizar_combos(self):
        self.combo_clientes['values'] = [c.nombre for c in self.clientes]

    def actualizar_logs(self):
        try:
            with open('software_fj.log', 'r', encoding='utf-8') as f:
                self.log_view.delete(1.0, tk.END)
                self.log_view.insert(tk.END, f.read())
                self.log_view.see(tk.END)
        except FileNotFoundError:
            self.log_view.insert(tk.END, "No hay logs registrados aún.")

    def _ejecutar_simulacion_10_pasos(self):
        """Simula 10 operaciones automáticas al iniciar para cumplir con el requisito."""
        print("Iniciando simulación de 10 operaciones...")
        datos_prueba = [
            ("CLI", "Juan Perez", "juan@mail.com"),    # 1. OK
            ("CLI", "", "error_mail"),                # 2. FALLO (Validación)
            ("CLI", "Ana Gomez", "ana@mail.com"),      # 3. OK
            ("RES", 0, 0, 5),                         # 4. OK (Juan - Sala)
            ("RES", 0, 1, -2),                        # 5. FALLO (Reserva - Duración)
            ("CLI", "Luis Ruiz", "luis@mail.com"),     # 6. OK
            ("RES", 2, 2, 3),                         # 7. OK (Luis - Asesoría)
            ("RES", 2, 1, 0),                         # 8. FALLO (Reserva - Cero)
            ("RES", 1, 0, 2),                         # 9. OK (Ana - Sala)
            ("RES", 1, 2, 1)                          # 10. OK (Ana - Asesoría)
        ]

        for op in datos_prueba:
            try:
                if op[0] == "CLI":
                    self.clientes.append(Cliente(len(self.clientes), op[1], op[2]))
                else:
                    r = Reserva("SIM", self.clientes[op[1]], self.servicios[op[2]], op[3])
                    r.procesar()
            except Exception:
                pass # El sistema permanece activo a pesar de los fallos simulados

        self.actualizar_combos()
        self.actualizar_logs()

if __name__ == "__main__":
    root = tk.Tk()
    app = SoftwareFJApp(root)
    root.mainloop()