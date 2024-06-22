# Utilização da biblioteca cx_Freeze pra gerar o executável
from cx_Freeze import setup, Executable

base = None

# Executável para ser criado
executables = [Executable("client.py", base=base)]

# Lista de pacotes necessários para a aplicação. Neste caso, apenas o pacote 'idna' é especificado.
packages = ["idna"]

# Opções para a criação do executável. 'build_exe' é uma chave que contém as opções específicas para a construção do executável.
options = {
    'build_exe': {    
        'packages': packages,  # Pacotes a serem incluídos no executável
    },    
}

# Configuração do script de instalação usando cx_Freeze.
setup(
    name = "Agendador gRPC",  # Nome da aplicação
    options = options,  # Opções especificadas acima
    version = "1.0",  # Versão da aplicação
    description = '<any description>',  # Descrição da aplicação
    executables = executables  # Executáveis a serem criados, especificados anteriormente
)
