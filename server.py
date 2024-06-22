from concurrent import futures
import grpc
import time
import uuid
import threading
import queue
from datetime import datetime, timezone, timedelta
import jwt
import sqlite3
import agendador_tarefas_pb2
import agendador_tarefas_pb2_grpc
import pytz
import hashlib

SECRET_KEY = "bdAMR0ewbkK1e0C5NCuPwFGUkF8l2vD6"

# Dados fixos para o usuário admin
ADMIN_EMAIL = "administrador@.com"
ADMIN_PASSWORD = "administrador123"

# Inicializa o banco de dados SQLite e cria as tabelas de tasks e usuários
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
            completion_time TEXT,
            user_id TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            task_id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            worker_id TEXT,
            completion_time TEXT,
            user_id TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            is_admin INTEGER
        )
    ''')

    # Adiciona o usuário admin fixo por padrão
    c.execute('''
        INSERT OR IGNORE INTO users (user_id, name, email, password, is_admin) VALUES (?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), 'Admin', ADMIN_EMAIL, hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest(), 1))
    conn.commit()
    conn.close()

class TaskSchedulerServicer(agendador_tarefas_pb2_grpc.TaskSchedulerServicer):
    def __init__(self):
        self.tasks = {}
        self.task_status = {}
        self.task_worker = {}
        self.task_queue = queue.Queue()
        self.workers = ["worker-1", "worker-2"]
        self.lock = threading.Lock()
        self.history = []
        threading.Thread(target=self.worker_manager, daemon=True).start()
        init_db()

    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    # Autenticação com o jwt
    def authenticate(self, token):
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return decoded['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    # Verificar se o usuário é comum ou administrador (puxa do banco de dados)
    def is_admin(self, user_id):
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] == 1 if result else False
    
    # Função para registrar usuário no banco de dados
    def RegisterUser(self, request, context):
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        user_id = str(uuid.uuid4())
        try:
            c.execute("INSERT INTO users (user_id, name, email, password, is_admin) VALUES (?, ?, ?, ?, ?)",
                      (user_id, request.name, request.email, self.hash_password(request.password), 0))
            conn.commit()
        except sqlite3.IntegrityError:
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "E-mail já registrado!")
        finally:
            conn.close()
        return agendador_tarefas_pb2.UserResponse(user_id=user_id, message="Usuário registrado com sucesso!")

    #Função para logar usuário
    def LoginUser(self, request, context):
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("SELECT user_id, password, is_admin, name FROM users WHERE email = ?", (request.email,))
        user = c.fetchone()
        conn.close()
        if user and user[1] == self.hash_password(request.password):
            token = jwt.encode({'user_id': user[0], 'exp': datetime.utcnow() + timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")
            return agendador_tarefas_pb2.LoginResponse(token=token, is_admin=user[2] == 1, name=user[3])
        else:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "E-mail ou senha inválido")


    # Função para o agendamento de tarefas
    def ScheduleTask(self, request, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        user_id = self.authenticate(token)
        if not user_id:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing token")

        task_id = str(uuid.uuid4())
        self.tasks[task_id] = request
        self.task_status[task_id] = "Agendada"
        self.task_queue.put(task_id)
        self.save_task_to_db(task_id, request, user_id)
        
        return agendador_tarefas_pb2.TaskResponse(task_id=task_id, status="Agendada", worker_id="")

    # Função que retorna o status da tarefa pelo ID da tarefa
    def GetTaskStatus(self, request, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        user_id = self.authenticate(token)
        if not user_id:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing token")

        task_id = request.task_id
        status = self.task_status.get(task_id, "Not Found")
        worker_id = self.task_worker.get(task_id, "Not Assigned")
        details = "Task details here" if status != "Not Found" else "Task not found"
        return agendador_tarefas_pb2.TaskStatusResponse(task_id=task_id, status=status, details=details, worker_id=worker_id)


    # Função que retorna a lista de tarefa do usuário
    def ListTasks(self, request, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        user_id = self.authenticate(token)
        if not user_id:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing token")

        tasks_info = []
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()

        if self.is_admin(user_id):
            c.execute("SELECT task_id, name, description, schedule_time, status, worker_id, completion_time FROM tasks")
        else:
            c.execute("SELECT task_id, name, description, schedule_time, status, worker_id, completion_time FROM tasks WHERE user_id = ?", (user_id,))

        rows = c.fetchall()
        conn.close()
        for row in rows:
            task_info = agendador_tarefas_pb2.TaskInfo(
                task_id=row[0],
                name=row[1],
                description=row[2],
                schedule_time=row[3],
                status=row[4],
                worker_id=row[5] if row[5] else "N/A",
                completion_time=row[6] if row[6] else "N/A"
            )
            tasks_info.append(task_info)
        return agendador_tarefas_pb2.ListTasksResponse(tasks=tasks_info)

    def ListHistory(self, request, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        user_id = self.authenticate(token)
        if not user_id:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing token")

        history = []
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()

        if self.is_admin(user_id):
            c.execute("SELECT * FROM history")
        else:
            c.execute("SELECT * FROM history WHERE user_id = ?", (user_id,))

        rows = c.fetchall()
        conn.close()
        for row in rows:
            history.append(agendador_tarefas_pb2.HistoryEntry(
                task_id=row[0],
                name=row[1],
                description=row[2],
                worker_id=row[3],
                completion_time=row[4]
            ))
        return agendador_tarefas_pb2.ListHistoryResponse(history=history)


    # Função para salvar a tarefa no sqlite3
    def save_task_to_db(self, task_id, task, user_id):
        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("INSERT INTO tasks (task_id, name, description, schedule_time, status, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                  (task_id, task.name, task.description, task.schedule_time, 'Agendada', user_id))
        conn.commit()
        conn.close()

    # Função para executar a tarefa agendada na data e hora especificada
    def execute_task(self, task_id):
        task = self.tasks[task_id]
        scheduled_time = datetime.fromisoformat(task.schedule_time).astimezone(pytz.timezone('America/Campo_Grande'))

        while datetime.now(pytz.timezone('America/Campo_Grande')) < scheduled_time:
            time.sleep(10)  # Checa a condição a cada 10 segundos

        worker_id = self.get_available_worker()
        self.task_worker[task_id] = worker_id
        start_time = datetime.now(pytz.timezone('America/Campo_Grande'))
        print(f"Atribuindo tarefa {task_id} ao {worker_id}.")

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

        self.history.append({
            'task_id': task_id,
            'name': task.name,
            'description': task.description,
            'worker_id': worker_id,
            'completion_time': end_time.isoformat(),
            'execution_time': execution_time  # Tempo de execução em segundos
        })

        print(f"Tarefa {task_id} concluída por {worker_id} em {execution_time} segundos.")

    # Esta função verifica se há algum trabalhador/nó disponível para executar alguma tarefa
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

# Função que iniciaiza o servidor
# Não esquecer de definir a porta corretamente de acordo como IP
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    agendador_tarefas_pb2_grpc.add_TaskSchedulerServicer_to_server(TaskSchedulerServicer(), server)
    server.add_insecure_port('192.168.100.45:50052')

    server.start()
    print("Server started at 192.168.100.45:50052")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
