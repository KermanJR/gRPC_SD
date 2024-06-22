from cx_Freeze import setup, Executable
    
base = None    
    
executables = [Executable("client.py", base=base)]

packages = ["idna"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "Agendador gRPC",
    options = options,
    version = "1.0",
    description = '<any description>',
    executables = executables
)