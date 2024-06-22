from concurrent import futures
import grpc
import time
import uuid
import threading
import queue
from datetime import datetime
import jwt
import sqlite3
import agendador_tarefas_pb2
import agendador_tarefas_pb2_grpc
from datetime import datetime, timezone, timedelta
import pytz

# Chave secreta para codificação e decodificação JWT
SECRET_KEY = "your_secret_key"

# Inicializa o banco de dados SQLite
def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            schedule_time TEXT,
            status TEXT,
            worker_id TEXT,
            completion_time TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            task_id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            worker_id TEXT,
            completion_time TEXT
        )
    ''')
    conn.commit()
    conn.close()

class TaskSchedulerServicer(agendador_tarefas_pb2_grpc.TaskSchedulerServicer):
    def __init__(self):
        self.tasks = {}
        self.task_status = {}
        self.task_worker = {}
        self.task_queue = queue.Queue()
        self.workers = ["worker-1", "worker-2", "worker-3", "worker-4", "worker-5", "worker-6", "worker-7", "worker-8", "worker-9"]
        self.lock = threading.Lock()
        self.history = []
        threading.Thread(target=self.worker_manager, daemon=True).start()
        init_db()

    def authenticate(self, token):
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    def ScheduleTask(self, request, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        if not token or not self.authenticate(token):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing token")

        task_id = str(uuid.uuid4())
        self.tasks[task_id] = request
        self.task_status[task_id] = "Scheduled"
        self.task_queue.put(task_id)
        self.save_task_to_db(task_id, request)
        
        return agendador_tarefas_pb2.TaskResponse(task_id=task_id, status="Agendada", worker_id="")

    def GetTaskStatus(self, request, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        if not token or not self.authenticate(token):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing token")

        task_id = request.task_id
        status = self.task_status.get(task_id, "Not Found")
        worker_id = self.task_worker.get(task_id, "Not Assigned")
        details = "Task details here" if status != "Not Found" else "Task not found"
        return agendador_tarefas_pb2.TaskStatusResponse(task_id=task_id, status=status, details=details, worker_id=worker_id)

    def ListTasks(self, request, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        if not token or not self.authenticate(token):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing token")

        tasks_info = []
        for task_id, request in self.tasks.items():
            status = self.task_status[task_id]
            worker_id = self.task_worker.get(task_id, "Not Assigned")
            task_info = agendador_tarefas_pb2.TaskInfo(
                task_id=task_id,
                name=request.name,
                status=status,
                worker_id=worker_id
            )
            tasks_info.append(task_info)
        return agendador_tarefas_pb2.ListTasksResponse(tasks=tasks_info)

    def ListHistory(self, request, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        if not token or not self.authenticate(token):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing token")

        history = []
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("SELECT * FROM history")
        rows = c.fetchall()
        for row in rows:
            history.append(agendador_tarefas_pb2.HistoryEntry(
                task_id=row[0],
                name=row[1],
                description=row[2],
                worker_id=row[3],
                completion_time=row[4]
            ))
        conn.close()
        return agendador_tarefas_pb2.ListHistoryResponse(history=history)

    def save_task_to_db(self, task_id, task):
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("INSERT INTO tasks (task_id, name, description, schedule_time, status) VALUES (?, ?, ?, ?, ?)",
                  (task_id, task.name, task.description, task.schedule_time, 'Agendada'))
        conn.commit()
        conn.close()

    def execute_task(self, task_id):
        task = self.tasks[task_id]
        scheduled_time = datetime.fromisoformat(task.schedule_time).astimezone(pytz.timezone('America/Campo_Grande'))

        print(datetime.now(pytz.timezone('America/Campo_Grande')).strftime('%Y-%m-%d %H:%M:%S'))
        print(scheduled_time.strftime('%Y-%m-%d %H:%S:%M'))
        # Aguardar até que seja a hora de executar a tarefa
        while datetime.now(pytz.timezone('America/Campo_Grande')).strftime('%Y-%m-%d %H:%M:%S')< scheduled_time.strftime('%Y-%m-%d %H:%S:%M'):
            time.sleep(10)  # Checa a condição a cada 10 segundos

        # Executar a tarefa
        worker_id = self.get_available_worker()
        self.task_worker[task_id] = worker_id
        start_time = datetime.now(pytz.timezone('America/Campo_Grande'))
        print(f"Atribuindo tarefa {task_id} ao {worker_id}.")

        # Simular execução da tarefa
        time.sleep(5)  # Simulação de tempo de execução da tarefa

        end_time = datetime.now(pytz.timezone('America/Campo_Grande'))
        execution_time = (end_time - start_time).total_seconds()
        self.task_status[task_id] = "Completa"

        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("""
            UPDATE tasks
            SET name = ?, description = ?, schedule_time = ?, status = 'Completa', worker_id = ?, completion_time = ?
            WHERE task_id = ?""",
            (task.name, task.description, task.schedule_time, worker_id, end_time.isoformat(), task_id))
        conn.commit()
        conn.close()

        # Registrar no histórico
        self.history.append({
            'task_id': task_id,
            'name': task.name,
            'description': task.description,
            'worker_id': worker_id,
            'completion_time': end_time.isoformat(),
            'execution_time': execution_time  # Tempo de execução em segundos
        })

        print(f"Tarefa {task_id} concluída por {worker_id} em {execution_time} segundos.")



    def get_available_worker(self):
        with self.lock:
            worker = self.workers.pop(0)
            self.workers.append(worker)
            return worker

    def worker_manager(self):
        while True:
            task_id = self.task_queue.get()
            self.execute_task(task_id)
            self.task_queue.task_done()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    agendador_tarefas_pb2_grpc.add_TaskSchedulerServicer_to_server(TaskSchedulerServicer(), server)
    server.add_insecure_port('192.168.100.45:50051')

    server.start()
    print("Server started at 192.168.100.45:50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()