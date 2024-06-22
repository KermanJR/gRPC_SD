import grpc
import jwt
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import agendador_tarefas_pb2
import agendador_tarefas_pb2_grpc
import sqlite3

SECRET_KEY = "bdAMR0ewbkK1e0C5NCuPwFGUkF8l2vD6"

# Função para gerar um token JWT para o usuário
def generate_token(email):
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256") 

# Função para criar um stub gRPC
def get_stub():
    channel = grpc.insecure_channel('192.168.100.45:50052')
    stub = agendador_tarefas_pb2_grpc.TaskSchedulerStub(channel)
    return stub

# Classe para a janela de login
class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Agendador de Tarefas")
        self.stub = get_stub()
        self.create_widgets()

    # Função para criar os widgets da janela de login
    def create_widgets(self):
        self.email_label = ttk.Label(self.root, text="Email:")
        self.email_label.grid(column=0, row=0, padx=10, pady=10, sticky='W')
        self.email_entry = ttk.Entry(self.root, width=40)
        self.email_entry.grid(column=1, row=0, padx=10, pady=10, sticky='W')

        self.password_label = ttk.Label(self.root, text="Senha:")
        self.password_label.grid(column=0, row=1, padx=10, pady=10, sticky='W')
        self.password_entry = ttk.Entry(self.root, width=40, show="*")
        self.password_entry.grid(column=1, row=1, padx=10, pady=10, sticky='W')

        self.login_button = ttk.Button(self.root, text="Login", command=self.login)
        self.login_button.grid(column=1, row=2, padx=10, pady=20, sticky='W')

        self.register_button = ttk.Button(self.root, text="Registrar", command=self.open_register_window)
        self.register_button.grid(column=1, row=3, padx=10, pady=10, sticky='W')

    # Função para fazer login do usuário
    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        try:
            request = agendador_tarefas_pb2.LoginRequest(email=email, password=password)
            response = self.stub.LoginUser(request)
            token = response.token
            is_admin = response.is_admin
            name = response.name
            self.root.destroy()
            main_app = tk.Tk()
            TaskSchedulerApp(main_app, email, token, is_admin, name)
            main_app.mainloop()
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                messagebox.showerror("Erro de Autenticação", "Email ou senha incorretos")
            else:
                messagebox.showerror("Erro", f"Erro ao fazer login: {e.details()}")

    # Função para abrir a janela de registro de novo usuário
    def open_register_window(self):
        self.register_window = tk.Toplevel(self.root)
        self.register_window.title("Registrar - Agendador de Tarefas")
        self.register_email_label = ttk.Label(self.register_window, text="Email:")
        self.register_email_label.grid(column=0, row=0, padx=10, pady=10, sticky='W')
        self.register_email_entry = ttk.Entry(self.register_window, width=40)
        self.register_email_entry.grid(column=1, row=0, padx=10, pady=10, sticky='W')

        self.register_name_label = ttk.Label(self.register_window, text="Nome:")
        self.register_name_label.grid(column=0, row=1, padx=10, pady=10, sticky='W')
        self.register_name_entry = ttk.Entry(self.register_window, width=40)
        self.register_name_entry.grid(column=1, row=1, padx=10, pady=10, sticky='W')

        self.register_password_label = ttk.Label(self.register_window, text="Senha:")
        self.register_password_label.grid(column=0, row=2, padx=10, pady=10, sticky='W')
        self.register_password_entry = ttk.Entry(self.register_window, width=40, show="*")
        self.register_password_entry.grid(column=1, row=2, padx=10, pady=10, sticky='W')

        self.register_button = ttk.Button(self.register_window, text="Registrar", command=self.register)
        self.register_button.grid(column=1, row=3, padx=10, pady=20, sticky='W')

    # Função para registrar novo usuário
    def register(self):
        email = self.register_email_entry.get()
        name = self.register_name_entry.get()
        password = self.register_password_entry.get()
        try:
            request = agendador_tarefas_pb2.RegisterRequest(email=email, name=name, password=password)
            response = self.stub.RegisterUser(request)
            messagebox.showinfo("Registro bem-sucedido", response.message)
            self.register_window.destroy()
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                messagebox.showerror("Erro de Registro", "Email já registrado")
            else:
                messagebox.showerror("Erro", f"Erro ao registrar: {e.details()}")

# Classe para a janela principal do agendador de tarefas
class TaskSchedulerApp:
    def __init__(self, root, email, token, is_admin, name):
        self.root = root
        self.root.title("Agendador de Tarefas gRPC")
        self.email = email
        self.token = token
        self.is_admin = is_admin
        self.name = name
        self.stub, self.metadata = self.get_stub_and_metadata()
        self.create_widgets()

    # Função para obter o stub e metadata
    def get_stub_and_metadata(self):
        stub = get_stub()
        metadata = [('authorization', self.token)]
        return stub, metadata

    # Função para criar os widgets da janela principal
    def create_widgets(self):
        self.style = ttk.Style()
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('TEntry', font=('Helvetica', 12))
        self.style.configure('TButton', font=('Helvetica', 12, 'bold'), foreground='blue')
        self.style.configure('TNotebook', font=('Helvetica', 12))
        self.style.configure('TNotebook.Tab', font=('Helvetica', 12, 'bold'))

        self.user_label = ttk.Label(self.root, text=f"{'Admin' if self.is_admin else 'Usuário'}: {self.name}")
        self.user_label.grid(column=0, row=0, padx=10, pady=10, sticky='W')

        self.tab_control = ttk.Notebook(self.root)

        self.tab_schedule = ttk.Frame(self.tab_control, padding="20")
        self.tab_status = ttk.Frame(self.tab_control, padding="20")
        self.tab_list = ttk.Frame(self.tab_control, padding="20")
        self.tab_history = ttk.Frame(self.tab_control, padding="20")

        self.tab_control.add(self.tab_schedule, text="Agendar Tarefa")
        self.tab_control.add(self.tab_status, text="Status da Tarefa")
        self.tab_control.add(self.tab_list, text="Listar Tarefas")
        self.tab_control.add(self.tab_history, text="Histórico de Tarefas")

        self.tab_control.grid(column=0, row=1, columnspan=2, padx=10, pady=10, sticky='nsew')

        self.create_schedule_tab()
        self.create_status_tab()
        self.create_list_tab()
        self.create_history_tab()

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

    # Função para criar os widgets da aba de agendamento de tarefas
    def create_schedule_tab(self):
        self.name_label = ttk.Label(self.tab_schedule, text="Nome da Tarefa:")
        self.name_label.grid(column=0, row=0, padx=10, pady=10, sticky='W')
        self.name_entry = ttk.Entry(self.tab_schedule, width=40)
        self.name_entry.grid(column=1, row=0, padx=10, pady=10, sticky='W')

        self.desc_label = ttk.Label(self.tab_schedule, text="Descrição:")
        self.desc_label.grid(column=0, row=1, padx=10, pady=10, sticky='W')
        self.desc_entry = ttk.Entry(self.tab_schedule, width=40)
        self.desc_entry.grid(column=1, row=1, padx=10, pady=10, sticky='W')

        self.date_label = ttk.Label(self.tab_schedule, text="Data de Agendamento:")
        self.date_label.grid(column=0, row=2, padx=10, pady=10, sticky='W')
        self.date_entry = DateEntry(self.tab_schedule, width=18, background='darkblue', foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.date_entry.grid(column=1, row=2, padx=10, pady=10, sticky='W')

        self.time_label = ttk.Label(self.tab_schedule, text="Hora de Agendamento (HH:MM:SS):")
        self.time_label.grid(column=0, row=3, padx=10, pady=10, sticky='W')
        self.hour_entry = ttk.Entry(self.tab_schedule, width=5)
        self.hour_entry.grid(column=1, row=3, padx=10, pady=2, sticky='W')
        self.minute_entry = ttk.Entry(self.tab_schedule, width=5)
        self.minute_entry.grid(column=1, row=3, padx=80, pady=2, sticky='W')
        self.second_entry = ttk.Entry(self.tab_schedule, width=5)
        self.second_entry.grid(column=1, row=3, padx=150, pady=2, sticky='W')

        self.schedule_button = ttk.Button(self.tab_schedule, text="Agendar Tarefa", command=self.schedule_task)
        self.schedule_button.grid(column=1, row=4, padx=10, pady=20, sticky='W')

    # Função para criar os widgets da aba de status da tarefa
    def create_status_tab(self):
        self.status_task_id_label = ttk.Label(self.tab_status, text="ID da Tarefa:")
        self.status_task_id_label.grid(column=0, row=0, padx=10, pady=10, sticky='W')
        self.status_task_id_entry = ttk.Entry(self.tab_status, width=40)
        self.status_task_id_entry.grid(column=1, row=0, padx=10, pady=10, sticky='W')

        self.status_button = ttk.Button(self.tab_status, text="Obter Status", command=self.get_task_status)
        self.status_button.grid(column=1, row=1, padx=10, pady=20, sticky='W')

        self.status_output = tk.Text(self.tab_status, height=10, width=80)
        self.status_output.grid(column=0, row=2, columnspan=2, padx=10, pady=10)

    # Função para criar os widgets da aba de listar tarefas
    def create_list_tab(self):
        self.list_button = ttk.Button(self.tab_list, text="Listar Tarefas", command=self.list_tasks)
        self.list_button.grid(column=0, row=0, padx=10, pady=10, sticky='W')

        self.tree = ttk.Treeview(self.tab_list, columns=("ID", "Nome", "Descrição", "Agendada para", "Status", "Worker", "Concluída em"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Descrição", text="Descrição")
        self.tree.heading("Agendada para", text="Agendada para")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Worker", text="Worker")
        self.tree.heading("Concluída em", text="Concluída em")

        self.tree.column("ID", width=100)
        self.tree.column("Nome", width=150)
        self.tree.column("Descrição", width=200)
        self.tree.column("Agendada para", width=150)
        self.tree.column("Status", width=100)
        self.tree.column("Worker", width=100)
        self.tree.column("Concluída em", width=150)

        self.tree.grid(column=0, row=1, columnspan=2, padx=10, pady=10, sticky='nsew')
        self.tab_list.grid_columnconfigure(0, weight=1)
        self.tab_list.grid_rowconfigure(1, weight=1)

    # Função para criar os widgets da aba de histórico de tarefas
    def create_history_tab(self):
        self.history_button = ttk.Button(self.tab_history, text="Mostrar Histórico", command=self.list_history)
        self.history_button.grid(column=0, row=0, padx=10, pady=10, sticky='W')

        self.history_output = tk.Text(self.tab_history, height=20, width=80)
        self.history_output.grid(column=0, row=1, columnspan=2, padx=10, pady=10)

    # Função para agendar uma nova tarefa
    def schedule_task(self):
        name = self.name_entry.get()
        description = self.desc_entry.get()
        schedule_date = self.date_entry.get_date()
        hour = int(self.hour_entry.get())
        minute = int(self.minute_entry.get())
        second = int(self.second_entry.get())
        schedule_time = datetime(schedule_date.year, schedule_date.month, schedule_date.day, hour, minute, second)

        request = agendador_tarefas_pb2.TaskRequest(name=name, description=description, schedule_time=schedule_time.isoformat())
        response = self.stub.ScheduleTask(request, metadata=self.metadata)
        messagebox.showinfo("Tarefa Agendada", f"ID da Tarefa: {response.task_id}\nStatus: {response.status}")

    # Função para obter o status de uma tarefa
    def get_task_status(self):
        task_id = self.status_task_id_entry.get()
        request = agendador_tarefas_pb2.TaskStatusRequest(task_id=task_id)
        response = self.stub.GetTaskStatus(request, metadata=self.metadata)
        self.status_output.delete(1.0, tk.END)
        self.status_output.insert(tk.END, f"ID da Tarefa: {response.task_id}\nStatus: {response.status}\nDetalhes: {response.details}")

    # Função para listar todas as tarefas
    def list_tasks(self):
        request = agendador_tarefas_pb2.ListTasksRequest()
        response = self.stub.ListTasks(request, metadata=self.metadata)
        
        for row in self.tree.get_children():
            self.tree.delete(row)
        for task in response.tasks:
            self.tree.insert("", "end", values=(
                task.task_id,
                task.name,
                task.description,
                task.schedule_time,
                task.status,
                task.worker_id if task.worker_id else 'N/A',
                task.completion_time if task.completion_time else 'N/A'
            ))

    # Função para listar o histórico de tarefas
    def list_history(self):
        request = agendador_tarefas_pb2.ListHistoryRequest()
        response = self.stub.ListHistory(request, metadata=self.metadata)
        self.history_output.delete(1.0, tk.END)
        for entry in response.history:
            self.history_output.insert(tk.END, f"ID da Tarefa: {entry.task_id} - Nome: {entry.name} - Descrição: {entry.description} - Data de Conclusão: {entry.completion_time}\n")

if __name__ == "__main__":
    root = tk.Tk()
    login_app = LoginApp(root)
    root.mainloop()
