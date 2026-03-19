import subprocess

def run(cmd):
    """Executa um comando e retorna a saída (stdout + stderr)."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout + result.stderr

def install_rclone():
    """Verifica se rclone está instalado; se não, instala via apt."""
    try:
        subprocess.run(["rclone", "version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        subprocess.run(["apt", "update"], check=True)
        subprocess.run(["apt", "install", "-y", "rclone", "fuse"], check=True)

def remote_exists(name):
    """Verifica se um remote já está configurado no rclone."""
    result = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True)
    return f"{name}:" in result.stdout

def create_remote(name, rtype, token):
    """Cria um remote do tipo especificado com o token fornecido."""
    if remote_exists(name):
        return f"Remote '{name}' já existe\n"
    if not token:
        return "Erro: Token obrigatório\n"
    cmd = [
        "rclone", "config", "create",
        name, rtype,
        "token", token
    ]
    return run(cmd)

def create_crypt(name, base_remote, password):
    """Cria um remote crypt sobre um remote base existente."""
    if remote_exists(name):
        return f"Crypt '{name}' já existe\n"
    if not password:
        return "Erro: senha do crypt obrigatória\n"
    cmd = [
        "rclone", "config", "create",
        name, "crypt",
        "remote", f"{base_remote}:",
        "password", password
    ]
    return run(cmd)

def show_config(name):
    """Exibe a configuração de um remote."""
    return run(["rclone", "config", "show", name])