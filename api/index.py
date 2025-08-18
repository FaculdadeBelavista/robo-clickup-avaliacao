# -*- coding: utf-8 -*-

# Importações necessárias
from flask import Flask, request, jsonify
import os
import requests

# --- Configuração Inicial ---
app = Flask(__name__)

# Pega a chave de API do ClickUp das variáveis de ambiente da Vercel.
CLICKUP_API_TOKEN = os.environ.get('CLICKUP_API_TOKEN')

# URL base da API v2 do ClickUp
CLICKUP_API_URL = "https://api.clickup.com/api/v2/task/"

# --- Endpoint Principal ---
@app.route('/api/feedback', methods=['GET'])
def handle_feedback():
    print("--- Nova Requisição de Feedback Recebida ---")

    # Verificação crítica: Checa se a chave de API foi carregada.
    if not CLICKUP_API_TOKEN:
        print("ERRO CRÍTICO: A variável de ambiente CLICKUP_API_TOKEN não está configurada na Vercel.")
        return "Erro de configuração no servidor.", 500

    # 1. Capturar os parâmetros da URL
    task_id = request.args.get('task_id')
    resolvido = request.args.get('resolvido')
    nota = request.args.get('nota')
    print(f"Parâmetros recebidos: task_id={task_id}, resolvido={resolvido}, nota={nota}")

    if not task_id:
        print("Erro: task_id não foi fornecido na URL.")
        return "Erro: ID da tarefa não fornecido.", 400

    # 2. Preparar os dados para a API do ClickUp
    headers = {
        'Authorization': CLICKUP_API_TOKEN,
        'Content-Type': 'application/json'
    }
    
    payload = {}

    # --- Lógica Condicional ---
    if resolvido == 'nao':
        print(f"Ação: Reabrir tarefa {task_id}.")
        payload = {
            "status": "Em Atendimento", # IMPORTANTE: Verifique se este nome é EXATO.
            "priority": 1 
        }
    elif resolvido == 'sim':
        print(f"Ação: Encerrar tarefa {task_id}.")
        payload = {
            "status": "Encerrado" # IMPORTANTE: Verifique se este nome é EXATO.
        }
        
        if nota:
            print(f"Ação adicional: Atualizar nota para {nota}.")
            custom_field_id = "COLOQUE_O_ID_DO_SEU_CAMPO_AVALIAR_AQUI"
            
            if "COLOQUE_O_ID" in custom_field_id:
                 print("AVISO: O ID do campo personalizado 'Avaliar' ainda não foi configurado no código.")
            else:
                field_update_url = f"https://api.clickup.com/api/v2/task/{task_id}/field/{custom_field_id}"
                field_payload = {"value": int(nota)}
                try:
                    field_response = requests.post(field_update_url, json=field_payload, headers=headers)
                    field_response.raise_for_status()
                    print("Campo personalizado atualizado com sucesso.")
                except requests.exceptions.RequestException as e:
                    print(f"ERRO ao atualizar campo personalizado: {e}")
                    print(f"Resposta da API do ClickUp (Campo): {field_response.text}")
    else:
        print(f"Erro: Parâmetro 'resolvido' inválido: {resolvido}")
        return "Erro: Parâmetro 'resolvido' inválido.", 400

    # 3. Fazer a chamada PUT para a API do ClickUp para atualizar o STATUS
    try:
        update_url = f"{CLICKUP_API_URL}{task_id}"
        print(f"Enviando requisição PUT para: {update_url}")
        print(f"Payload: {payload}")
        response = requests.put(update_url, json=payload, headers=headers)
        response.raise_for_status()
        
        print(f"Tarefa {task_id} atualizada com sucesso.")
        
        if resolvido == 'nao':
            return "Seu chamado foi reaberto e nossa equipe será notificada. Obrigado!", 200
        else:
            return "Obrigado pelo seu feedback! Seu chamado foi encerrado.", 200

    except requests.exceptions.RequestException as e:
        print(f"ERRO CRÍTICO ao atualizar a tarefa no ClickUp: {e}")
        print(f"Resposta da API do ClickUp (Status): {response.text}") # Imprime a mensagem de erro do ClickUp
        return "Ocorreu um erro ao processar sua solicitação. A equipe de TI foi notificada.", 500

handler = app
