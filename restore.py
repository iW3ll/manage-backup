import gradio as gr
import subprocess
import os
from rclone_utils import remote_exists

def restore_files(crypt_name, crypt_password,
                  restore_dest_type, restore_local_path, restore_remote_name, restore_remote_path):
    # Validações
    if not crypt_name:
        return "Erro: Preencha o nome do remote crypt."
    if not crypt_password:
        return "Erro: A senha de criptografia é necessária para descriptografar."

    output = ""

    # Verifica se o remote crypt existe
    if not remote_exists(crypt_name):
        return f"Erro: Remote crypt '{crypt_name}' não existe. Verifique o nome."

    # Testa a senha (tentando listar)
    test_cmd = ["rclone", "ls", f"{crypt_name}:"]
    test_result = subprocess.run(test_cmd, capture_output=True, text=True)
    if test_result.returncode != 0:
        output += "AVISO: Não foi possível listar o remote crypt. A senha pode estar incorreta ou não há arquivos.\n"
        output += test_result.stderr + "\n"
        # Continua, pode ser que a pasta esteja vazia

    # Define o destino da restauração
    if restore_dest_type == "Local":
        if not restore_local_path:
            return "Erro: Forneça um caminho local para restaurar os arquivos."
        os.makedirs(restore_local_path, exist_ok=True)
        dest_spec = restore_local_path
    else:  # Remoto
        if not restore_remote_name:
            return "Erro: Forneça o nome do remote de destino para restauração."
        if not restore_remote_path:
            restore_remote_path = ""
        if not remote_exists(restore_remote_name):
            return f"Erro: Remote '{restore_remote_name}' não existe. Crie-o manualmente."
        dest_spec = f"{restore_remote_name}:{restore_remote_path}"

    # Copia os arquivos do crypt para o destino
    output += f"Copiando de {crypt_name}: para {dest_spec}...\n"
    cmd = ["rclone", "copy", f"{crypt_name}:", dest_spec, "--verbose"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output += result.stdout + result.stderr

    return output

def criar_aba_restore():
    with gr.Blocks() as demo_restore:
        gr.Markdown("## Restauração de arquivos criptografados")
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Remote crypt (já configurado)")
                crypt_name_rest = gr.Textbox(label="Nome do remote crypt", value="dbox-crypt",
                                             info="Ex: dbox-crypt (o remote que você usa para acessar os arquivos criptografados)")
                crypt_password_rest = gr.Textbox(label="Senha de criptografia", type="password")

            with gr.Column():
                gr.Markdown("### Destino da restauração")
                restore_dest_type = gr.Radio(choices=["Local", "Remoto"], label="Tipo de destino", value="Local")
                restore_local_path = gr.Textbox(label="Caminho local (ex: /content/restaurado)", value="/content/restaurado", visible=True)
                restore_remote_name = gr.Textbox(label="Nome do remote de destino (para restauração remota)", visible=False)
                restore_remote_path = gr.Textbox(label="Caminho no remote (opcional)", value="", visible=False)

        # Mostrar/esconder campos de destino local/remoto
        def toggle_restore_dest(choice):
            if choice == "Local":
                return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
            else:
                return gr.update(visible=False), gr.update(visible=True), gr.update(visible=True)

        restore_dest_type.change(toggle_restore_dest, inputs=restore_dest_type,
                                 outputs=[restore_local_path, restore_remote_name, restore_remote_path])

        restore_btn = gr.Button("Restaurar Arquivos")
        restore_output = gr.Textbox(label="Saída da Restauração", lines=10)

        restore_btn.click(
            restore_files,
            inputs=[crypt_name_rest, crypt_password_rest,
                    restore_dest_type, restore_local_path, restore_remote_name, restore_remote_path],
            outputs=restore_output
        )

    return demo_restore