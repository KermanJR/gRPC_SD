import grpc  # Importa a biblioteca gRPC para comunicação remota
import jwt  # Importa a biblioteca JWT para manipulação de tokens de autenticação
import agendador_tarefas_pb2  # Importa os módulos gerados pelo compilador protobuf para as mensagens
import agendador_tarefas_pb2_grpc  # Importa os módulos gerados pelo compilador protobuf para os serviços gRPC
import tkinter as tk  # Importa a biblioteca tkinter para criar interfaces gráficas
from tkinter import messagebox, ttk  # Importa módulos específicos do tkinter para componentes e mensagens
from tkcalendar import DateEntry  # Importa o DateEntry do tkcalendar para selecionar datas
from datetime import datetime, timedelta  # Importa módulos de data e hora
from rich.console import Console  # Importa Console do rich para saída formatada
from rich.tree import Tree  # Importa Tree do rich para exibição hierárquica
from io import StringIO  # Importa StringIO para manipulação de strings em memória

console = Console()  # Cria uma instância do Console do rich
SECRET_KEY = "your_secret_key"  # Chave secreta para a geração de tokens JWT

class TaskSchedulerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Agendador de Tarefas Distribuído")
        self.stub = None
        self.metadata = None
        self.create_login_widgets()

    # Cria os widgets da tela de login com o tkinter
    def create_login_widgets(self):
        self.login_frame = ttk.Frame(self.root)
        self.login_frame.pack(padx=10, pady=10)

        self.username_label = ttk.Label(self.login_frame, text="Nome:")
        self.username_label.grid(column=0, row=0, padx=10, pady=10)
        self.username_entry = ttk.Entry(self.login_frame, width=40)
        self.username_entry.grid(column=1, row=0, padx=10, pady=10)

        self.password_label = ttk.Label(self.login_frame, text="Senha:")
        self.password_label.grid(column=0, row=1, padx=10, pady=10)
        self.password_entry = ttk.Entry(self.login_frame, show="*", width=40)
        self.password_entry.grid(column=1, row=1, padx=10, pady=10)

        self.login_button = ttk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(column=1, row=2, padx=10, pady=10)

    # Cria os widgets da tela principal após login
    def create_main_widgets(self):
        self.tab_control = ttk.Notebook(self.root)

        self.tab_schedule = ttk.Frame(self.tab_control)
        self.tab_status = ttk.Frame(self.tab_control)
        self.tab_list = ttk.Frame(self.tab_control)
        self.tab_history = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab_schedule, text="Agendar Tarefa")
        self.tab_control.add(self.tab_status, text="Consultar Status da Tarefa")
        self.tab_control.add(self.tab_list, text="Listar Tarefas")
        self.tab_control.add(self.tab_history, text="Histórico de Tarefas")

        self.tab_control.pack(expand=1, fill="both")

        self.create_schedule_tab()
        self.create_status_tab()
        self.create_list_tab()
        self.create_history_tab()

    # Função de login, envia credenciais ao servidor gRPC e recebe token JWT
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        channel = grpc.insecure_channel('localhost:50051')
        stub = agendador_tarefas_pb2_grpc.TaskSchedulerStub(channel)

        request = agendador_tarefas_pb2.AuthRequest(username=username, password=password)
        try:
            response = stub.Authenticate(request)
            token = response.token
            self.metadata = [('authorization', token)]
            self.stub = stub

            self.login_frame.pack_forget()

            self.create_main_widgets()

            messagebox.showinfo("Login Successful", "You have been successfully logged in.")
        except grpc.RpcError as e:
            messagebox.showerror("Login Failed", f"Login failed: {e.details()}")

    # Cria a aba de agendamento de tarefas
    def create_schedule_tab(self):
        self.name_label = ttk.Label(self.tab_schedule, text="Nome da Tarefa:")
        self.name_label.grid(column=0, row=0, padx=10, pady=10)
        self.name_entry = ttk.Entry(self.tab_schedule, width=40)
        self.name_entry.grid(column=1, row=0, padx=10, pady=10)

        self.desc_label = ttk.Label(self.tab_schedule, text="Descrição da Tarefa:")
        self.desc_label.grid(column=0, row=1, padx=10, pady=10)
        self.desc_entry = ttk.Entry(self.tab_schedule, width=40)
        self.desc_entry.grid(column=1, row=1, padx=10, pady=10)

        self.date_label = ttk.Label(self.tab_schedule, text="Data de agendamento")
        self.date_label.grid(column=0, row=2, padx=10, pady=10)
        self.date_entry = DateEntry(self.tab_schedule, width=18, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.date_entry.grid(column=1, row=2, padx=10, pady=10)

        self.time_label = ttk.Label(self.tab_schedule, text="Hora Agendamento (HH:MM:SS):")
        self.time_label.grid(column=0, row=3, padx=10, pady=10)
        self.time_entry = ttk.Entry(self.tab_schedule, width=40)
        self.time_entry.grid(column=1, row=3, padx=10, pady=10)

        self.schedule_button = ttk.Button(self.tab_schedule, text="Agenda Tarefa", command=self.schedule_task)
        self.schedule_button.grid(column=1, row=5, padx=10, pady=10)

    # Cria a aba de consulta de status de tarefas
    def create_status_tab(self):
        self.status_task_id_label = ttk.Label(self.tab_status, text="ID da Tarefa:")
        self.status_task_id_label.grid(column=0, row=0, padx=10, pady=10)
        self.status_task_id_entry = ttk.Entry(self.tab_status, width=40)
        self.status_task_id_entry.grid(column=1, row=0, padx=10, pady=10)

        self.status_button = ttk.Button(self.tab_status, text="Consultar Status da Tarefa", command=self.get_task_status)
        self.status_button.grid(column=1, row=1, padx=10, pady=10)

        self.status_output = tk.Text(self.tab_status, height=10, width=80)
        self.status_output.grid(column=0, row=2, columnspan=2, padx=10, pady=10)

    # Cria a aba de listagem de tarefas
    def create_list_tab(self):
        self.list_button = ttk.Button(self.tab_list, text="Listar Tarefas", command=self.list_tasks)
        self.list_button.grid(column=0, row=0, padx=10, pady=10)

        self.list_output = tk.Text(self.tab_list, height=20, width=80)
        self.list_output.grid(column=0, row=1, padx=10, pady=10)

    # Cria a aba de histórico de tarefas
    def create_history_tab(self):
        self.history_button = ttk.Button(self.tab_history, text="Mostrar Histórico", command=self.list_history)
        self.history_button.grid(column=0, row=0, padx=10, pady=10)

        self.history_output = tk.Text(self.tab_history, height=20, width=80)
        self.history_output.grid(column=0, row=1, padx=10, pady=10)

    # Função para agendar uma tarefa
    def schedule_task(self):
        name = self.name_entry.get()
        description = self.desc_entry.get()
        schedule_date = self.date_entry.get_date()
        schedule_time = self.time_entry.get()

        schedule_datetime = datetime.combine(schedule_date, datetime.strptime(schedule_time, '%H:%M:%S').time())
        schedule_time_iso = schedule_datetime.isoformat()

        request = agendador_tarefas_pb2.TaskRequest(
            name=name,
            description=description,
            schedule_time=schedule_time_iso,
        )
        response = self.stub.ScheduleTask(request, metadata=self.metadata)
        messagebox.showinfo("Tarefa Agendada", f"ID Tarefa: {response.task_id}\nStatus: {response.status}")

    # Função para consultar o status de uma tarefa
    def get_task_status(self):
        task_id = self.status_task_id_entry.get()
        request = agendador_tarefas_pb2.TaskStatusRequest(task_id=task_id)
        response = self.stub.GetTaskStatus(request, metadata=self.metadata)
        self.status_output.delete(1.0, tk.END)
        self.status_output.insert(tk.END, f"Task ID: {response.task_id}\nStatus: {response.status}\nWorker ID: {response.worker_id}\nDetails: {response.details}")

    # Função para listar todas as tarefas
    def list_tasks(self):
        request = agendador_tarefas_pb2.ListTasksRequest()
        response = self.stub.ListTasks(request, metadata=self.metadata)

        self.list_output.delete(1.0, tk.END)
        tree = Tree("Tasks")
        for task in response.tasks:
            status = task.status
            worker = task.worker_id
            branch = tree.add(f"Task ID: {task.task_id} - {task.name} - Status: {status} - Worker: {worker}")

        string_output = StringIO()
        console = Console(file=string_output, force_terminal=True)
        console.print(tree)
        self.list_output.insert(tk.END, string_output.getvalue())

    # Função para listar o histórico de tarefas
    def list_history(self):
        request = agendador_tarefas_pb2.ListHistoryRequest()
        response = self.stub.ListHistory(request, metadata=self.metadata)

        self.history_output.delete(1.0, tk.END)
        tree = Tree("Task History")
        for entry in response.history:
            branch = tree.add(f"ID Tarefa: [bold]{entry.task_id}[/bold] - [i]{entry.name}[/i] - Descrição: {entry.description} - Worker: {entry.worker_id} - Completion Time: {entry.completion_time}")

        string_output = StringIO()
        console = Console(file=string_output, force_terminal=True)
        console.print(tree)
        self.history_output.insert(tk.END, string_output.getvalue())

# Main
if __name__ == "__main__":

    #Carrega o tkinter na variável root
    root = tk.Tk()

    #Cria aplicação gráfica com base no tkinter
    app = TaskSchedulerApp(root)

    #Mantém a janela da aplicação aberta enquanto o usuário não fechar
    root.mainloop()
