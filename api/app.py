# -*- coding: utf-8 -*-

# Importações necessárias:
# Flask para criar a aplicação web (nossa API)
# os para acessar variáveis de ambiente (chaves secretas)
# requests para fazer a chamada para a API do ClickUp
from flask import Flask, request, jsonify
import os
import requests

# --- Configuração Inicial ---
# Cria a aplicação Flask
app = Flask(__name__)

# Pega a chave de API do ClickUp das variáveis de ambiente da Vercel.
# Isso é MUITO mais seguro do que colocar a chave diretamente no código.
CLICKUP_API_TOKEN = os.environ.get('CLICKUP_API_TOKEN')

# URL base da API v2 do ClickUp
CLICKUP_API_URL = "https://api.clickup.com/api/v2/task/"

# --- Endpoint Principal ---
# Este é o endpoint que os links no e-mail irão chamar.
# A Vercel irá transformar isso em uma URL como: https://seu-projeto.vercel.app/api/feedback
@app.route('/api/feedback', methods=['GET'])
def handle_feedback():
    # 1. Capturar os parâmetros da URL (o que o usuário clicou)
    task_id = request.args.get('task_id')
    resolvido = request.args.get('resolvido')
    nota = request.args.get('nota')

    # Validação básica: se não houver task_id, não há o que fazer.
    if not task_id:
        return "Erro: ID da tarefa não fornecido.", 400

    # 2. Preparar os dados para enviar à API do ClickUp
    headers = {
        'Authorization': CLICKUP_API_TOKEN,
        'Content-Type': 'application/json'
    }
    
    payload = {} # Dicionário vazio que vamos preencher

    # --- Lógica Condicional ---
    if resolvido == 'nao':
        # Se o chamado NÃO foi resolvido, reabrimos ele com prioridade alta.
        print(f"Reabrindo tarefa {task_id}...")
        payload = {
            "status": "Em Atendimento", # IMPORTANTE: Use o nome EXATO do seu status
            "priority": 1 # 1 = Urgente, 2 = Alta, 3 = Normal, 4 = Baixa
        }
    elif resolvido == 'sim':
        # Se o chamado FOI resolvido, encerramos e, se houver nota, atualizamos o campo.
        print(f"Encerrando tarefa {task_id} com nota {nota}...")
        payload = {
            "status": "Encerrado" # IMPORTANTE: Use o nome EXATO do seu status
        }
        
        # Se uma nota foi enviada, precisamos atualizar o campo personalizado.
        if nota:
            # IMPORTANTE: Você precisa pegar o ID do seu campo personalizado no ClickUp.
            # Para achar o ID: https://clickup.com/api/clickupreference/operation/GetAccessibleCustomFields/
            # Você só precisa fazer isso uma vez.
            custom_field_id = "COLOQUE_O_ID_DO_SEU_CAMPO_AVALIAR_AQUI" 
            
            # Adiciona a atualização do campo personalizado na URL da requisição
            field_update_url = f"https://api.clickup.com/api/v2/task/{task_id}/field/{custom_field_id}"
            
            field_payload = {
                "value": int(nota) # O valor precisa ser um número inteiro
            }
            
            # Faz uma requisição separada para atualizar o campo personalizado
            try:
                field_response = requests.post(field_update_url, json=field_payload, headers=headers)
                field_response.raise_for_status() # Lança um erro se a requisição falhar
                print(f"Campo personalizado da tarefa {task_id} atualizado com sucesso.")
            except requests.exceptions.RequestException as e:
                print(f"Erro ao atualizar campo personalizado: {e}")
                # Mesmo que o campo falhe, o status ainda será atualizado.
    
    else:
        return "Erro: Parâmetro 'resolvido' inválido.", 400

    # 3. Fazer a chamada PUT para a API do ClickUp para atualizar o STATUS
    try:
        update_url = f"{CLICKUP_API_URL}{task_id}"
        response = requests.put(update_url, json=payload, headers=headers)
        response.raise_for_status() # Lança um erro se a requisição falhar (ex: status 4xx ou 5xx)
        
        print(f"Tarefa {task_id} atualizada com sucesso. Resposta: {response.json()}")
        
        # 4. Retornar uma mensagem de sucesso para o usuário
        if resolvido == 'nao':
            return "Seu chamado foi reaberto e nossa equipe será notificada. Obrigado!", 200
        else:
            return "Obrigado pelo seu feedback! Seu chamado foi encerrado.", 200

    except requests.exceptions.RequestException as e:
        print(f"Erro ao atualizar a tarefa no ClickUp: {e}")
        return "Ocorreu um erro ao processar sua solicitação. Por favor, contate o suporte.", 500

# Esta parte é necessária para a Vercel encontrar e executar a aplicação.
# O nome 'app' deve ser o mesmo da sua instância Flask (app = Flask(__name__))
handler = app
