import grpc
import jwt
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import Calendar, DateEntry
import agendador_tarefas_pb2
import agendador_tarefas_pb2_grpc

# Configuração da chave secreta para JWT
SECRET_KEY = "your_secret_key"

def generate_token():
    payload = {
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256") 


def get_stub():
    channel = grpc.insecure_channel('localhost:50051')
    stub = agendador_tarefas_pb2_grpc.TaskSchedulerStub(channel)
    token = generate_token()
    metadata = [('authorization', token)]
    return stub, metadata

class TaskSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agendador de Tarefas gRPC")

        self.stub, self.metadata = get_stub()

        self.create_widgets()

    def create_widgets(self):
        self.tab_control = ttk.Notebook(self.root)

        self.tab_schedule = ttk.Frame(self.tab_control)
        self.tab_status = ttk.Frame(self.tab_control)
        self.tab_list = ttk.Frame(self.tab_control)
        self.tab_history = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab_schedule, text="Agendar Tarefa")
        self.tab_control.add(self.tab_status, text="Status da Tarefa")
        self.tab_control.add(self.tab_list, text="Listar Tarefas")
        self.tab_control.add(self.tab_history, text="Histórico de Tarefas")

        self.tab_control.pack(expand=1, fill="both")

        self.create_schedule_tab()
        self.create_status_tab()
        self.create_list_tab()
        self.create_history_tab()

    def create_schedule_tab(self):
        self.name_label = ttk.Label(self.tab_schedule, text="Nome da Tarefa:")
        self.name_label.grid(column=0, row=0, padx=10, pady=10)
        self.name_entry = ttk.Entry(self.tab_schedule, width=40)
        self.name_entry.grid(column=1, row=0, padx=10, pady=10)

        self.desc_label = ttk.Label(self.tab_schedule, text="Descrição:")
        self.desc_label.grid(column=0, row=1, padx=10, pady=10)
        self.desc_entry = ttk.Entry(self.tab_schedule, width=40)
        self.desc_entry.grid(column=1, row=1, padx=10, pady=10)

        self.date_label = ttk.Label(self.tab_schedule, text="Data de Agendamento:")
        self.date_label.grid(column=0, row=2, padx=10, pady=10)
        self.date_entry = DateEntry(self.tab_schedule, width=18, background='darkblue', foreground='white', borderwidth=2, date_pattern='y-mm-dd')
        self.date_entry.grid(column=1, row=2, padx=10, pady=10)

        self.schedule_button = ttk.Button(self.tab_schedule, text="Agendar Tarefa", command=self.schedule_task)
        self.schedule_button.grid(column=1, row=3, padx=10, pady=10)

    def create_status_tab(self):
        self.status_task_id_label = ttk.Label(self.tab_status, text="ID da Tarefa:")
        self.status_task_id_label.grid(column=0, row=0, padx=10, pady=10)
        self.status_task_id_entry = ttk.Entry(self.tab_status, width=40)
        self.status_task_id_entry.grid(column=1, row=0, padx=10, pady=10)

        self.status_button = ttk.Button(self.tab_status, text="Obter Status", command=self.get_task_status)
        self.status_button.grid(column=1, row=1, padx=10, pady=10)

        self.status_output = tk.Text(self.tab_status, height=10, width=80)
        self.status_output.grid(column=0, row=2, columnspan=2, padx=10, pady=10)

    def create_list_tab(self):
        self.list_button = ttk.Button(self.tab_list, text="Listar Tarefas", command=self.list_tasks)
        self.list_button.grid(column=0, row=0, padx=10, pady=10)

        self.list_output = tk.Text(self.tab_list, height=20, width=80)
        self.list_output.grid(column=0, row=1, columnspan=2, padx=10, pady=10)

    def create_history_tab(self):
        self.history_button = ttk.Button(self.tab_history, text="Mostrar Histórico", command=self.list_history)
        self.history_button.grid(column=0, row=0, padx=10, pady=10)

        self.history_output = tk.Text(self.tab_history, height=20, width=80)
        self.history_output.grid(column=0, row=1, columnspan=2, padx=10, pady=10)

    def schedule_task(self):
        name = self.name_entry.get()
        description = self.desc_entry.get()
        schedule_date = self.date_entry.get_date()
        schedule_time = datetime.combine(schedule_date, datetime.now().time()).isoformat()

        request = agendador_tarefas_pb2.TaskRequest(name=name, description=description, schedule_time=schedule_time)
        response = self.stub.ScheduleTask(request, metadata=self.metadata)
        messagebox.showinfo("Tarefa Agendada", f"ID da Tarefa: {response.task_id}\nStatus: {response.status}")

    def get_task_status(self):
        task_id = self.status_task_id_entry.get()
        request = agendador_tarefas_pb2.TaskStatusRequest(task_id=task_id)
        response = self.stub.GetTaskStatus(request, metadata=self.metadata)
        self.status_output.delete(1.0, tk.END)
        self.status_output.insert(tk.END, f"ID da Tarefa: {response.task_id}\nStatus: {response.status}\nDetalhes: {response.details}")

    def list_tasks(self):
        response = self.stub.ListTasks(agendador_tarefas_pb2.ListTasksRequest(), metadata=self.metadata)
        self.list_output.delete(1.0, tk.END)
        for task in response.tasks:
            self.list_output.insert(tk.END, f"ID da Tarefa: {task.task_id} - Nome: {task.name} - Status: {task.status}\n")

    def list_history(self):
        response = self.stub.ListHistory(agendador_tarefas_pb2.ListHistoryRequest(), metadata=self.metadata)
        self.history_output.delete(1.0, tk.END)
        for entry in response.history:
            self.history_output.insert(tk.END, f"ID da Tarefa: {entry.task_id} - Nome: {entry.name} - Descrição: {entry.description} - Data de Conclusão: {entry.completion_time}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskSchedulerApp(root)
    root.mainloop()
