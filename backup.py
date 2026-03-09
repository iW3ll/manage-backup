import gradio as gr
import subprocess
from rclone_utils import remote_exists, create_remote

def backup_config(source_type, source_remote, source_path,
                  local_file, local_path,
                  dest_name, dest_type, client_id, client_secret, token_json,
                  crypt_password, use_existing_remote):
    # Validações
    if source_type == "Remote":
        if not source_remote or not source_path:
            return "Erro: Preencha remote e caminho de origem remota."
        source_spec = f"{source_remote}:{source_path}"
    else:
        if local_file is not None:
            source_spec = local_file.name
        elif local_path:
            source_spec = local_path
        else:
            return "Erro: Forneça um arquivo local (upload ou caminho)."

    if not dest_name:
        return "Erro: Preencha o nome do remote de destino."

    output = ""

    # Verifica se o remote de destino já existe
    dest_exists = remote_exists(dest_name)

    if not use_existing_remote:
        # Criar novo remote com token
        if not token_json:
            return "Erro: Token OAuth é obrigatório para criar um novo remote."
        dest_config = {
            "client_id": client_id if client_id else "",
            "client_secret": client_secret if client_secret else "",
            "token": token_json,
        }
        dest_config = {k: v for k, v in dest_config.items() if v}
        if dest_exists:
            output += f"Remote '{dest_name}' já existe. Será usado.\n"
        else:
            output += "Criando remote de destino...\n"
            out, success = create_remote(dest_name, dest_type, dest_config)
            output += out + "\n"
            if not success:
                output += "ERRO: Falha ao criar remote de destino.\n"
                return output
    else:
        if not dest_exists:
            return f"Erro: Remote '{dest_name}' não existe."
        output += f"Usando remote existente: {dest_name}\n"

    # Define o destino final
    if crypt_password:
        crypt_name = f"{dest_name}-crypt"
        if remote_exists(crypt_name):
            output += f"Remote crypt '{crypt_name}' já existe. Será utilizado.\n"
        else:
            crypt_config = {
                "remote": f"{dest_name}:backup",
                "password": crypt_password,
            }
            output += "Criando remote crypt...\n"
            out, success = create_remote(crypt_name, "crypt", crypt_config)
            output += out + "\n"
            if not success:
                output += "ERRO: Falha ao criar remote crypt. Backup abortado.\n"
                return output
        dest_spec = f"{crypt_name}:"
        output += "Arquivo será criptografado antes do envio.\n"
    else:
        dest_spec = f"{dest_name}:backup"
        output += "Criptografia não utilizada. Arquivo será copiado diretamente.\n"

    # Copia
    output += f"Copiando {source_spec} para {dest_spec}...\n"
    cmd = ["rclone", "copy", source_spec, dest_spec, "--verbose"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output += result.stdout + result.stderr

    return output

def criar_aba_backup():
    with gr.Blocks() as demo_backup:
        gr.Markdown("## Backup de arquivos (com ou sem criptografia)")
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Origem")
                source_type = gr.Radio(choices=["Remote", "Local"], label="Tipo de origem", value="Remote")
                source_remote = gr.Textbox(label="Nome do remote de origem", value="drive", visible=True)
                source_path = gr.Textbox(label="Caminho do arquivo no remote", value="/rclone.conf", visible=True)
                local_file = gr.File(label="Arquivo local (upload)", visible=False)
                local_path = gr.Textbox(label="Caminho local (ex: /content/meu_arquivo.txt)", visible=False)

            with gr.Column():
                gr.Markdown("### Destino")
                dest_name = gr.Textbox(label="Nome do remote de destino", value="dbox",
                                       info="Ex: dbox (remote base, sem -crypt)")
                dest_type = gr.Dropdown(label="Tipo de remote", choices=["drive", "dropbox", "onedrive"], value="dropbox")
                use_existing_remote = gr.Checkbox(label="Usar remote já existente", value=True)
                client_id = gr.Textbox(label="Client ID (opcional)", visible=False)
                client_secret = gr.Textbox(label="Client Secret (opcional)", type="password", visible=False)
                token_json = gr.Textbox(label="Token JSON (opcional se usar remote existente)", lines=2, type="password",
                                        placeholder='{"access_token":"...", ...}')

        def toggle_remote_fields(use_existing):
            if use_existing:
                return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
            else:
                return gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)

        use_existing_remote.change(toggle_remote_fields, inputs=use_existing_remote,
                                   outputs=[client_id, client_secret, token_json])

        def toggle_source(choice):
            if choice == "Remote":
                return gr.update(visible=True), gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
            else:
                return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=True)

        source_type.change(toggle_source, inputs=source_type,
                           outputs=[source_remote, source_path, local_file, local_path])

        crypt_password = gr.Textbox(label="Senha de criptografia (opcional)", type="password",
                                    info="Se deixar em branco, o arquivo NÃO será criptografado.")

        backup_btn = gr.Button("Iniciar Backup")
        backup_output = gr.Textbox(label="Saída do Backup", lines=10)

        backup_btn.click(
            backup_config,
            inputs=[source_type, source_remote, source_path, local_file, local_path,
                    dest_name, dest_type, client_id, client_secret, token_json,
                    crypt_password, use_existing_remote],
            outputs=backup_output
        )

    return demo_backup