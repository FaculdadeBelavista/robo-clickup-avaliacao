import os
from flask import Flask, request, jsonify
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
ID_CAMPO_AVALIACAO = "ae76c408-912b-4954-acf4-aa8d0e61e5" # ID atualizado conforme sua última mensagem
# Base URL da sua aplicação Vercel. Você vai configurá-la nas variáveis de ambiente da Vercel.
VERCEL_APP_BASE_URL = os.environ.get("VERCEL_APP_BASE_URL")
# --- Fim da sua Ficha de Informações ---

# Cabeçalhos padrão para todas as requisições à API do ClickUp.
headers = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

# Inicializa a aplicação Flask.
app = Flask(__name__)

# --- FUNÇÃO PARA GERAR A PÁGINA DE RESPOSTA (SEM ALTERAÇÕES) ---
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

# --- NOVA ROTA: GERAR HTML DO E-MAIL ---
@app.route('/generate_email_html', methods=['POST'])
def generate_email_html_endpoint():
    """
    Recebe task_id, client_email e client_name do Make.com e retorna o HTML do e-mail.
    """
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        client_name = data.get('client_name', 'Prezado(a) Cliente') # Valor padrão se não vier

        if not all([task_id, VERCEL_APP_BASE_URL]):
            print(f"Erro: Dados incompletos para gerar HTML. task_id: {task_id}, VERCEL_APP_BASE_URL: {VERCEL_APP_BASE_URL}")
            return jsonify({"error": "Missing task_id or VERCEL_APP_BASE_URL environment variable."}), 400

        # O HTML base (fornecido por você) com os links dinâmicos
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Avaliação de Chamado</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5;">
            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin: 0 auto; max-width: 600px;">
                <tr>
                    <td style="padding: 20px;">
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; padding: 40px;">
                            <tr>
                                <td>
                                    <img src="https://inside.faculdadebelavista.edu.br/logo_01_escuro.png" alt="Logo Faculdade Belavista" width="200" style="max-width: 250px; margin-bottom: 25px;">
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <h1 style="font-size: 24px; color: #A738FF; margin: 0 0 20px 0;">Olá {client_name}, seu chamado foi encerrado?</h1>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding-bottom: 25px;">
                                    <p style="font-size: 16px; color: #333; margin: 0 0 15px 0;"><b>Sim?</b> Por favor, avalie o atendimento recebido clicando em uma das estrelas abaixo:</p>
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" style="margin: 0 auto;">
                                        <tr>
                                            <td style="padding: 0 5px;"><a href="{VERCEL_APP_BASE_URL}/avaliacao_tec?id_tarefa={task_id}&acao=avaliar&nota=1" target="_blank" style="font-size: 32px; text-decoration: none;">⭐</a></td>
                                            <td style="padding: 0 5px;"><a href="{VERCEL_APP_BASE_URL}/avaliacao_tec?id_tarefa={task_id}&acao=avaliar&nota=2" target="_blank" style="font-size: 32px; text-decoration: none;">⭐</a></td>
                                            <td style="padding: 0 5px;"><a href="{VERCEL_APP_BASE_URL}/avaliacao_tec?id_tarefa={task_id}&acao=avaliar&nota=3" target="_blank" style="font-size: 32px; text-decoration: none;">⭐</a></td>
                                            <td style="padding: 0 5px;"><a href="{VERCEL_APP_BASE_URL}/avaliacao_tec?id_tarefa={task_id}&acao=avaliar&nota=4" target="_blank" style="font-size: 32px; text-decoration: none;">⭐</a></td>
                                            <td style="padding: 0 5px;"><a href="{VERCEL_APP_BASE_URL}/avaliacao_tec?id_tarefa={task_id}&acao=avaliar&nota=5" target="_blank" style="font-size: 32px; text-decoration: none;">⭐</a></td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td style="border-top: 1px solid #eeeeee; padding-top: 20px;">
                                    <p style="font-size: 14px; color: #666; margin: 0;">
                                        <b>Não?</b> 
                                        <a href="{VERCEL_APP_BASE_URL}/avaliacao_tec?id_tarefa={task_id}&acao=reabrir" target="_blank" style="color: #007bff; text-decoration: underline;">Clique aqui para reabrir o chamado.</a>
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        return html_content, 200, {'Content-Type': 'text/html'} # Retorna HTML

    except Exception as e:
        print(f"ERRO CRÍTICO INESPERADO NA generate_email_html_endpoint: {e}")
        print(traceback.format_exc())
        return jsonify({"error": f"Internal server error generating HTML: {e}"}), 500


# --- ROTA EXISTENTE: LIDAR COM AVALIAÇÃO/REABERTURA (SEM ALTERAÇÕES SIGNIFICATIVAS) ---
@app.route('/avaliacao_tec', methods=['GET'])
def handle_evaluation():
    """
    Endpoint principal para lidar com as ações de avaliação e reabertura de chamados.
    Recebe 'id_tarefa' e 'acao' (e 'nota' se a ação for 'avaliar') via parâmetros de URL.
    """
    try:
        task_id = request.args.get('id_tarefa')
        action = request.args.get('acao')

        if not task_id or not action:
            print("Erro: Parâmetros id_tarefa ou acao não encontrados na URL.")
            return gerar_pagina_resposta("Erro na Solicitação", "Os parâmetros necessários não foram encontrados na URL."), 400

        if not API_TOKEN:
            print("Erro: CLICKUP_API_TOKEN não configurado nas variáveis de ambiente.")
            return gerar_pagina_resposta("Erro de Configuração", "O token da API do ClickUp não foi configurado corretamente. Por favor, verifique as variáveis de ambiente na Vercel."), 500

        print(f"Recebido: id_tarefa={task_id}, acao={action}")

        task_url = f"https://api.clickup.com/api/v2/task/{task_id}"

        if action == 'reabrir':
            payload = {
                "status": STATUS_EM_ABERTO,
                "priority": PRIORIDADE_URGENTE
            }
            print(f"Tentando atualizar status da tarefa {task_id} para '{STATUS_EM_ABERTO}' com prioridade {PRIORIDADE_URGENTE}.")
            response_update = requests.put(task_url, json=payload, headers=headers)
            print(f"Resposta da atualização de status: {response_update.status_code} - {response_update.text}")

            if response_update.status_code != 200:
                print(f"Erro ao reabrir tarefa no ClickUp: {response_update.status_code} - {response_update.text}")
                error_message = f"Não foi possível reabrir o chamado no ClickUp. Código: {response_update.status_code}"
                if response_update.status_code == 401:
                    error_message += " (Não autorizado - Verifique seu CLICKUP_API_TOKEN e permissões)."
                return gerar_pagina_resposta("Erro", error_message), 500

            comment_payload = {"comment_text": "Chamado reaberto pelo cliente via link no e-mail."}
            print(f"Tentando adicionar comentário à tarefa {task_id}.")
            response_comment = requests.post(f"{task_url}/comment", json=comment_payload, headers=headers)
            print(f"Resposta do comentário: {response_comment.status_code} - {response_comment.text}")

            if response_comment.status_code != 200:
                print(f"Aviso: Erro ao adicionar comentário à tarefa {task_id}: {response_comment.status_code} - {response_comment.text}")

            print("Gerando página de resposta para reabertura bem-sucedida.")
            return gerar_pagina_resposta("Seu chamado foi reaberto!", "Nossa equipe já foi notificada e dará andamento à sua solicitação.")

        elif action == 'avaliar':
            nota = request.args.get('nota')
            if not nota:
                print("Erro: Nota não fornecida na ação 'avaliar'.")
                return gerar_pagina_resposta("Erro", "Nota inválida ou não fornecida."), 400

            try:
                nota_int = int(nota)
            except ValueError:
                print(f"Erro: Nota '{nota}' não é um número inteiro válido.")
                return gerar_pagina_resposta("Erro", "A nota deve ser um número inteiro."), 400

            field_update_url = f"https://api.clickup.com/api/v2/task/{task_id}/field/{ID_CAMPO_AVALIACAO}"
            field_payload = { "value": nota_int }
            print(f"Tentando atualizar campo de avaliação {ID_CAMPO_AVALIACAO} da tarefa {task_id} com nota {nota_int}.")
            response_field = requests.post(field_update_url, json=field_payload, headers=headers)
            print(f"Resposta da atualização do campo: {response_field.status_code} - {response_field.text}")

            if response_field.status_code != 200:
                print(f"Erro ao atualizar campo de avaliação no ClickUp: {response_field.status_code} - {response_field.text}")
                error_message = f"Não foi possível registrar sua avaliação no ClickUp. Código: {response_field.status_code}"
                if response_field.status_code == 401:
                    error_message += " (Não autorizado - Verifique seu CLICKUP_API_TOKEN e permissões)."
                if response_field.text:
                    error_message += f" Detalhes: {response_field.text}"
                return gerar_pagina_resposta("Erro", error_message), 500

            status_payload = { "status": STATUS_ENCERRADO }
            print(f"Tentando mudar status da tarefa {task_id} para '{STATUS_ENCERRADO}'.")
            response_status = requests.put(task_url, json=status_payload, headers=headers)
            print(f"Resposta da atualização de status para encerrado: {response_status.status_code} - {response_status.text}")

            if response_status.status_code != 200:
                print(f"Aviso: Erro ao encerrar tarefa no ClickUp: {response_status.status_code} - {response_status.text}")
                warning_message = "Obrigado pelo seu feedback. Houve um pequeno problema ao encerrar o chamado, mas sua avaliação foi registrada."
                if response_status.status_code == 401:
                    warning_message = "Obrigado pelo seu feedback. Sua avaliação foi registrada, mas não foi possível encerrar o chamado devido a um erro de autenticação (401 - Verifique seu CLICKUP_API_TOKEN e permissões)."
                if response_status.text:
                    warning_message += f" Detalhes: {response_status.text}"
                return gerar_pagina_resposta("Avaliação Recebida!", warning_message)

            print("Gerando página de resposta para avaliação bem-sucedida.")
            return gerar_pagina_resposta("Avaliação Recebida!", "Obrigado pelo seu feedback! Seu chamado foi encerrado com sucesso.")

        print(f"Erro: Ação desconhecida ou inválida: {action}")
        return gerar_pagina_resposta("Erro", "Ação desconhecida ou inválida."), 400

    except Exception as e:
        print(f"ERRO CRÍTICO INESPERADO NA handle_evaluation: {e}")
        print(traceback.format_exc())
        return gerar_pagina_resposta("Erro Inesperado", f"Ocorreu um erro interno: {e}. Por favor, tente novamente mais tarde."), 500

# Esta parte faz o servidor rodar localmente.
# Na Vercel, o gunicorn ou similar será usado para rodar o app.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
