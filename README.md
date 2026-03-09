Este projeto fornece uma interface web simples usando Gradio para fazer backup e restauração de arquivos utilizando o rclone, com suporte a criptografia opcional via remote `crypt`.

## Estrutura do Projeto

- `main.py`: Ponto de entrada, executa a interface Gradio com abas.
- `rclone_utils.py`: Funções auxiliares para instalar o rclone, verificar e criar remotes.
- `backup.py`: Função de backup e sua interface (incorporada no `main.py`).
- `restore.py`: Função de restauração e sua interface (incorporada no `main.py`).

## Requisitos

- Python 3.7+
- Bibliotecas: `gradio` (instalada automaticamente no Colab, mas pode ser necessário `pip install gradio`)

## Como usar no Google Colab

1. Faça upload dos arquivos `.py` para o ambiente Colab ou copie o conteúdo.
2. Execute o arquivo `main.py` em uma célula:

```python
!python main.py