# Versão Final - Com Página de Confirmação em HTML Personalizada
import os
from flask import Flask, request
import requests
import traceback # Importe traceback para obter o stack trace completo

# --- Início da sua Ficha de Informações ---
# Token da API do ClickUp, obtido das variáveis de ambiente da Vercel.
API_TOKEN = os.environ.get("CLICKUP_API_TOKEN")
# Status para reabrir o chamado no ClickUp.
STATUS_EM_ABERTO = "EM ATENDIMENTO"
# Status para encerrar o chamado no ClickUp.
STATUS_ENCERRADO = "ENCERRADO"
# Prioridade para o chamado reaberto.
PRIORIDADE_URGENTE = 1
# ID do campo personalizado de avaliação no ClickUp.
ID_CAMPO_AVALIACAO = "41c52161-d702-4c71-9ad8-c0ece9e85e34"
# --- Fim da sua Ficha de Informações ---

# Cabeçalhos padrão para todas as requisições à API do ClickUp.
headers = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

# Inicializa a aplicação Flask.
app = Flask(__name__)

# --- FUNÇÃO ATUALIZADA PARA GERAR A PÁGINA DE RESPOSTA ---
def gerar_pagina_resposta(titulo, mensagem):
    """
    Gera uma página HTML de resposta bonita e personalizada com logo.

    Args:
        titulo (str): O título a ser exibido na página.
        mensagem (str): A mensagem principal a ser exibida.

    Returns:
        str: O conteúdo HTML completo da página.
    """
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{titulo}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #f0f2f5;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                color: #333;
            }}
            .container {{
                text-align: center;
                background-color: #ffffff;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            .logo {{
                max-width: 250px;
                margin-bottom: 25px;
            }}
            h1 {{
                font-size: 24px;
                color: #A738FF; /* Cor roxa da Faculdade Belavista */
            }}
            p {{
                font-size: 16px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <img src="https://inside.faculdadebelavista.edu.br/logo_01_escuro.png" alt="Logo Faculdade Belavista" class="logo">
            <h1>{titulo}</h1>
            <p>{mensagem}</p>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/avaliacao_tec', methods=['GET'])
def handle_evaluation():
    """
    Endpoint principal para lidar com as ações de avaliação e reabertura de chamados.
    Recebe 'id_tarefa' e 'acao' (e 'nota' se a ação for 'avaliar') via parâmetros de URL.
    """
    try: # Início do bloco try para capturar exceções
        task_id = request.args.get('id_tarefa')
        action = request.args.get('acao')

        # Validação inicial dos parâmetros.
        if not task_id or not action:
            print("Erro: Parâmetros id_tarefa ou acao não encontrados na URL.")
            return gerar_pagina_resposta("Erro na Solicitação", "Os parâmetros necessários não foram encontrados na URL."), 400

        print(f"Recebido: id_tarefa={task_id}, acao={action}")

        # URL base para a tarefa no ClickUp.
        task_url = f"https://api.clickup.com/api/v2/task/{task_id}"

        # Lógica para REABRIR o chamado.
        if action == 'reabrir':
            # Payload para atualizar o status e a prioridade da tarefa.
            payload = {
                "status": STATUS_EM_ABERTO,
                "priority": PRIORIDADE_URGENTE
            }
            print(f"Tentando atualizar status da tarefa {task_id} para '{STATUS_EM_ABERTO}' com prioridade {PRIORIDADE_URGENTE}.")
            # Envia a requisição PUT para atualizar a tarefa.
            response_update = requests.put(task_url, json=payload, headers=headers)
            print(f"Resposta da atualização de status: {response_update.status_code} - {response_update.text}")

            if response_update.status_code != 200:
                print(f"Erro ao reabrir tarefa no ClickUp: {response_update.status_code} - {response_update.text}")
                return gerar_pagina_resposta("Erro", f"Não foi possível reabrir o chamado no ClickUp. Código: {response_update.status_code}"), 500

            # Payload para adicionar um comentário na tarefa.
            comment_payload = {"comment_text": "Chamado reaberto pelo cliente via link no e-mail."}
            print(f"Tentando adicionar comentário à tarefa {task_id}.")
            # Envia a requisição POST para adicionar o comentário.
            response_comment = requests.post(f"{task_url}/comment", json=comment_payload, headers=headers)
            print(f"Resposta do comentário: {response_comment.status_code} - {response_comment.text}")

            if response_comment.status_code != 200:
                print(f"Aviso: Erro ao adicionar comentário à tarefa {task_id}: {response_comment.status_code} - {response_comment.text}")
                # Não retorna erro aqui, pois a reabertura já foi feita e o comentário é secundário.

            # Retorna a página de confirmação para o cliente.
            print("Gerando página de resposta para reabertura bem-sucedida.")
            # CORREÇÃO: Adicionando o argumento 'mensagem' que estava faltando.
            return gerar_pagina_resposta("Seu chamado foi reaberto!", "Nossa equipe já foi notificada e dará andamento à sua solicitação.")

        # Lógica para AVALIAR o chamado.
        elif action == 'avaliar':
            nota = request.args.get('nota')
            # Valida se a nota foi fornecida.
            if not nota:
                print("Erro: Nota não fornecida na ação 'avaliar'.")
                return gerar_pagina_resposta("Erro", "Nota inválida ou não fornecida."), 400

            try:
                nota_int = int(nota)
            except ValueError:
                print(f"Erro: Nota '{nota}' não é um número inteiro válido.")
                return gerar_pagina_resposta("Erro", "A nota deve ser um número inteiro."), 400

            # Ação 1: Preencher o campo de avaliação personalizado.
            field_update_url = f"https://api.clickup.com/api/v2/task/{task_id}/field/{ID_CAMPO_AVALIACAO}"
            field_payload = { "value": nota_int }
            print(f"Tentando atualizar campo de avaliação {ID_CAMPO_AVALIACAO} da tarefa {task_id} com nota {nota_int}.")
            # Envia a requisição POST para atualizar o campo personalizado.
            response_field = requests.post(field_update_url, json=field_payload, headers=headers)
            print(f"Resposta da atualização do campo: {response_field.status_code} - {response_field.text}")

            if response_field.status_code != 200:
                print(f"Erro ao atualizar campo de avaliação no ClickUp: {response_field.status_code} - {response_field.text}")
                return gerar_pagina_resposta("Erro", f"Não foi possível registrar sua avaliação no ClickUp. Código: {response_field.status_code}"), 500

            # Ação 2: Mudar o status da tarefa para "ENCERRADO".
            status_payload = { "status": STATUS_ENCERRADO }
            print(f"Tentando mudar status da tarefa {task_id} para '{STATUS_ENCERRADO}'.")
            # Envia a requisição PUT para atualizar o status da tarefa.
            response_status = requests.put(task_url, json=status_payload, headers=headers)
            print(f"Resposta da atualização de status para encerrado: {response_status.status_code} - {response_status.text}")

            if response_status.status_code != 200:
                print(f"Aviso: Erro ao encerrar tarefa no ClickUp: {response_status.status_code} - {response_status.text}")
                # Se a avaliação foi registrada, mas o status não mudou, ainda assim é um sucesso parcial.
                return gerar_pagina_resposta("Avaliação Recebida!", "Obrigado pelo seu feedback. Houve um pequeno problema ao encerrar o chamado, mas sua avaliação foi registrada.")

            # Retorna a página de confirmação para o cliente.
            print("Gerando página de resposta para avaliação bem-sucedida.")
            # CORREÇÃO: Adicionando o argumento 'mensagem' que estava faltando.
            return gerar_pagina_resposta("Avaliação Recebida!", "Obrigado pelo seu feedback! Seu chamado foi encerrado com sucesso.")

        # Caso a ação não seja reconhecida.
        print(f"Erro: Ação desconhecida ou inválida: {action}")
        return gerar_pagina_resposta("Erro", "Ação desconhecida ou inválida."), 400

    except Exception as e:
        # Captura qualquer exceção não tratada e retorna uma página de erro genérica.
        print(f"ERRO CRÍTICO INESPERADO NA handle_evaluation: {e}")
        print(traceback.format_exc()) # Imprime o stack trace completo para depuração.
        return gerar_pagina_resposta("Erro Inesperado", f"Ocorreu um erro interno: {e}. Por favor, tente novamente mais tarde."), 500

# Esta parte faz o servidor rodar localmente.
# Na Vercel, o gunicorn ou similar será usado para rodar o app.
if __name__ == '__main__':
    # 'host='0.0.0.0'' permite que o servidor seja acessível de qualquer IP.
    # 'port=5000' é a porta padrão para aplicações Flask.
    # 'debug=True' habilita o modo de depuração (não usar em produção).
    app.run(host='0.0.0.0', port=5000, debug=True)
