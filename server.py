from concurrent import futures #Essa classe cria um pool de threads para executar operações assíncronas em paralelo. 
import grpc
import time
import uuid
import threading
import queue
from datetime import datetime, timedelta
import jwt  # Importando o módulo jwt
import agendador_tarefas_pb2
import agendador_tarefas_pb2_grpc

# Secret key para o JWT
SECRET_KEY = "your_secret_key"

# Credenciais de exemplo para login
VALID_USERS = {
    "user1": "password1",
    "user2": "password2"
}

class TaskSchedulerServicer(agendador_tarefas_pb2_grpc.TaskSchedulerServicer):

    def __init__(self):
        # Inicialização de variáveis
        self.tasks = {}
        self.task_status = {}
        self.task_worker = {}
        self.task_queue = queue.PriorityQueue()
        self.workers = ["worker-1", "worker-2"]  # Lista de IDs de trabalhadores
        self.lock = threading.Lock()
        self.history = []

        # Inicia a thread do gerenciador de trabalhadores
        threading.Thread(target=self.worker_manager, daemon=True).start()

    # Métodos para registro e autenticação de usuários
    def register_user(self, username, password):
        # Registra um novo usuário
        if username in VALID_USERS:
            return False
        VALID_USERS[username] = password
        return True

    def authenticate_user(self, username, password):
        # Autentica um usuário
        return VALID_USERS.get(username) == password

    def generate_token(self, username):
        # Gera um token JWT para um usuário
        payload = {
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
            "sub": username
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    def authenticate(self, token):
        # Autentica um token JWT
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    # Métodos gRPC para registro, autenticação e agendamento de tarefas
    def Register(self, request, context):
        # Registro de usuário
        username = request.username
        password = request.password
        if self.register_user(username, password):
            return agendador_tarefas_pb2.RegisterResponse(message="User registered successfully")
        else:
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "User already exists")

    def Authenticate(self, request, context):
        # Autenticação de usuário
        username = request.username
        password = request.password
        if self.authenticate_user(username, password):
            token = self.generate_token(username)
            return agendador_tarefas_pb2.AuthResponse(token=token)
        else:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid credentials")

    def ScheduleTask(self, request, context):
        # Agendamento de tarefas
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        if not token or not self.authenticate(token):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing token")

        task_id = str(uuid.uuid4())
        priority = {"high": 1, "medium": 2, "low": 3}.get(request.priority, 3)
        self.tasks[task_id] = request
        self.task_status[task_id] = "Scheduled"
        self.task_queue.put((priority, task_id))

        return agendador_tarefas_pb2.TaskResponse(task_id=task_id, status="Scheduled", worker_id="")

    def GetTaskStatus(self, request, context):
        # Obtém o status de uma tarefa
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
        # Lista todas as tarefas
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
                worker_id=worker_id,
                priority=request.priority
            )
            tasks_info.append(task_info)
        return agendador_tarefas_pb2.ListTasksResponse(tasks=tasks_info)

    def ListHistory(self, request, context):
        # Lista o histórico de tarefas
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization')
        if not token or not self.authenticate(token):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid or missing token")

        return agendador_tarefas_pb2.ListHistoryResponse(history=self.history)

    def execute_task(self, task_id):
        # Executa uma tarefa
        task = self.tasks[task_id]
        worker_id = self.get_available_worker()
        self.task_worker[task_id] = worker_id
        print(f"Assigning task {task_id} to {worker_id}")
        # Aqui você enviaria a tarefa para o trabalhador real para execução
        # Simula a execução da tarefa
        time.sleep(5)
        self.task_status[task_id] = "Completa"
        completion_time = datetime.utcnow().isoformat()
        self.history.append(agendador_tarefas_pb2.HistoryEntry(
            task_id=task_id,
            name=task.name,
            description=task.description,
            worker_id=worker_id,
            completion_time=completion_time,
            priority=task.priority
        ))
        print(f"Tarefa {task_id} completa por {worker_id}")

    def get_available_worker(self):
        # Obtém um trabalhador disponível
        with self.lock:
            # Atribuição simples de round-robin
            worker = self.workers.pop(0)
            self.workers.append(worker)
            return worker

    def worker_manager(self):
        # Gerencia os trabalhadores
        while True:
            priority, task_id = self.task_queue.get()
            self.execute_task(task_id)
            self.task_queue.task_done()

def serve():
    # Inicia o servidor gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    agendador_tarefas_pb2_grpc.add_TaskSchedulerServicer_to_server(TaskSchedulerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started at [::]:50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
