################ IMPORTS ################
import requests
import json
import base64
import jsonpickle
from datetime import datetime
##########################################

def Queue_Item_Change_Exception_Error(path, queueItemID, exception):
    try:
        # Status:
        # 0 = New
        # 1 = In Progress
        # 2 = Success
        # 3 = Error
        # Capturar dados do arquivo de configuração do bot
        Dados_Json = getBotID(path)
        ClientToken = Dados_Json['ClientToken']

        # EndPoint API
        UrlAPI = 'https://api-app.hypercoe.com/api/item-queue/exception'
        #UrlAPIStatus = 'https://api-app.hypercoe.com​/api​/item-queue/get-all'
        
        dados = {
            "id": queueItemID,
            "exception": exception
            }

        # Headers da requisição (caso necessário)
        headers = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        # Realize a requisição
        response = requests.put(UrlAPI, json=dados, headers=headers)

        # Verifique o status da resposta
        if response.status_code == 200:  # 200 indica sucesso
            print("Change Exception Error")
        else:
            print("Error Change Exception Error: ", response.status_code)
            
    except Exception as erro:
        print(f"Error Change Exception Error: ", erro)
        return erro

def Queue_Item_Change_Status(path, queueItemID, status):
    try:
        # Status:
        # 0 = New
        # 1 = In Progress
        # 2 = Success
        # 3 = Error
        # Capturar dados do arquivo de configuração do bot
        Dados_Json = getBotID(path)
        ClientToken = Dados_Json['ClientToken']

        # EndPoint API
        UrlAPI = 'https://api-app.hypercoe.com/api/item-queue/status'
        #UrlAPIStatus = 'https://api-app.hypercoe.com​/api​/item-queue/get-all'
        
        dados = {
            "id": queueItemID,
            "status": status
            }

        # Headers da requisição (caso necessário)
        headers = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        # Realize a requisição
        response = requests.put(UrlAPI, json=dados, headers=headers)

        # Verifique o status da resposta
        if response.status_code == 200:  # 200 indica sucesso
            print("Change Status Queue Item sucessful")
        else:
            print("Error Change Status Queue Item: ", response.status_code)
            
    except Exception as erro:
        print(f"Error Change Status Item: ", erro)
        return erro

def Queue_Item_Get(path):
    try:
        # Capturar dados do arquivo de configuração do bot
        Dados_Json = getBotID(path)
        ClientToken = Dados_Json['ClientToken']
        QueueID = Dados_Json['QueueId']

        # EndPoint API
        UrlAPIStatus = 'https://api-app.hypercoe.com/api/item-queue/get-all'

        # priority (0=Low / 1=Medium / 2=High)
        priorities = [2, 1, 0]  # Lista de prioridades em ordem de preferência

        # Headers da requisição
        headers = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        for priority in priorities:
            dados = {
                "queueId": QueueID,
                "pageIndex": 0,
                "pageSize": 1,
                "priority": priority,
                "status": 0
            }

            # Realize a requisição
            response = requests.post(UrlAPIStatus, json=dados, headers=headers)

            # Verifique o status da resposta
            if response.status_code == 200:  # 200 indica sucesso
                data = jsonpickle.decode(response.text)
                documents = data['dados']
                if documents and documents.get('data'):  # Checa se há dados
                    print("Get Queue Item successful")
                    Queue_Item_Change_Status(path, documents['data'][0]['id'], 1)
                    return documents['data'][0]

        print("No items found in any priority level.")
        return None

    except Exception as error:
        print(f"Error Get Queue Item: ", error)
        return error

def Clear_Queue_Items(path):
    try:
        Dados_Json = getBotID(path)
        ClientToken = Dados_Json['ClientToken']
        QueueID = Dados_Json['QueueId']
        
        UrlAPIStatus = 'https://api-app.hypercoe.com/api/item-queue/clear-queue-itens'

        headers = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        dados = {"queueId": QueueID}
        response = requests.put(UrlAPIStatus, json=dados, headers=headers)

        if response.status_code == 200:
            print("Queue Cleared")

    except Exception as error:
            print(f"Error Clear Queue Item: ", error)
            return error


def Queue_Item_Abandoned(path):
    try:
        # Capturar dados do arquivo de configuração do bot
        Dados_Json = getBotID(path)
        ClientToken = Dados_Json['ClientToken']
        QueueID = Dados_Json['QueueId']

        # EndPoint API
        UrlAPIStatus = 'https://api-app.hypercoe.com/api/item-queue/get-all'

        # priority (0=Low / 1=Medium / 2=High)
        priorities = [2, 1, 0]  # Lista de prioridades em ordem de preferência

        # Headers da requisição
        headers = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        for priority in priorities:
            dados = {
                "queueId": QueueID,
                "pageIndex": 0,
                "pageSize": 500,
                "priority": priority,
                "status": 0
            }

            # Realize a requisição
            response = requests.post(UrlAPIStatus, json=dados, headers=headers)

            # Verifique o status da resposta
            if response.status_code == 200:  # 200 indica sucesso
                data = jsonpickle.decode(response.text)
                documents = data['dados']
                if documents and documents.get('data'):  # Checa se há dados
                    for QueueItem in documents['data']:
                        queueItemID = QueueItem['id']
                        status = 4
                        Queue_Item_Change_Status(path, queueItemID, status)

        print("No items found in any priority level.")
        return None

    except Exception as error:
        print(f"Error Get Queue Item: ", error)
        return error

def Populate_Queue(path, Reference, DadosJson):
    try:
        # Capturar dados do arquivo de configuração do bot
        Dados_Json = getBotID(path)
        ClientToken = Dados_Json['ClientToken']
        QueueId = Dados_Json['QueueId']

        # EndPoint API
        UrlAPIStatus = 'https://api-app.hypercoe.com/api/item-queue'
        #UrlAPIStatus = 'https://api-app.hypercoe.com​/api​/item-queue'
        
        dados = {
            "queueId": QueueId,
            "reference": Reference,
            "exception": "",
            "json": f"{DadosJson}"
            }

        ID_Execution = Dados_Json['ExecutionID']
       
        if(ID_Execution != ""):
            dados['executionId'] = ID_Execution

        # Headers da requisição (caso necessário)
        headers = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        # Realize a requisição
        response = requests.post(UrlAPIStatus, json=dados, headers=headers)

        # Verifique o status da resposta
        if response.status_code == 200:  # 200 indica sucesso
            print("Add Queue Item sucessful")
        else:
            print("Error Add Queue Item: ", response.status_code)
            
    except Exception as erro:
        print(f"Error Queue Item: ", erro)
        return erro

def Start_Status(path):
    try:
        # Capturar dados do arquivo de configuração do bot
        Dados_Json = getBotID(path)
        BotId = Dados_Json['BotId']
        ClientToken = Dados_Json['ClientToken']

        # EndPoint API
        UrlAPIStatus = 'https://api-app.hypercoe.com/api/bot/change-status-by-bot'
        #UrlAPIStatus = 'https://api-app.hypercoe.com/api/bot/change-status-by-bot'
        

        # ID - Active=0, Running=1, Paused=2, Error=3
        BOT_Status = 1
        dados = {'id': BotId, 'status': BOT_Status}

        # Headers da requisição (caso necessário)
        headers = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        # Realize a requisição
        response = requests.post(UrlAPIStatus, json=dados, headers=headers)

        # Verifique o status da resposta
        if response.status_code == 200:  # 200 indica sucesso
            print("Bot Status Changed Successfully")
        else:
            print("Error in the request. Status code:", response.status_code)
            
    except Exception as erro:
        print(f"Erro API Status: ", erro)
        return erro

def End_Status(path):
    try:

        # Capturar dados do arquivo de configuração do bot
        Dados_Json = getBotID(path)
        BotId = Dados_Json['BotId']
        ClientToken = Dados_Json['ClientToken']

        # EndPoint API
        UrlAPIStatus = 'https://api-app.hypercoe.com/api/bot/change-status-by-bot'
        #UrlAPIStatus = 'https://api-app.hypercoe.com/api/bot/change-status-by-bot'

        # ID - Active=0, Running=1, Paused=2, Error=3
        BOT_Status = 0
        dados = {'id': BotId, 'status': BOT_Status}

        # Headers da requisição (caso necessário)
        headers = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        # Realize a requisição
        response = requests.post(UrlAPIStatus, json=dados, headers=headers)

        # Verifique o status da resposta
        if response.status_code == 200:  # 200 indica sucesso
            print("Status do Bot Alterado com sucesso")
        else:
            print("Error in the request. Status code:", response.status_code)

    except Exception as erro:
        print(f"Erro API Status: ", erro)
        return erro

def Error_Status(path):
    try:

        # Capturar dados do arquivo de configuração do bot
        Dados_Json = getBotID(path)
        BotId = Dados_Json['BotId']
        ClientToken = Dados_Json['ClientToken']

        # EndPoint API
        UrlAPIStatus = 'https://api-app.hypercoe.com/api/bot/change-status-by-bot'
        #UrlAPIStatus = 'https://api-app.hypercoe.com/api/bot/change-status-by-bot'

        # ID - Active=0, Running=1, Paused=2, Error=3
        BOT_Status = 3
        dados = {'id': BotId, 'status': BOT_Status}

        # Headers da requisição (caso necessário)
        headers = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        # Realize a requisição
        response = requests.post(UrlAPIStatus, json=dados, headers=headers)

        # Verifique o status da resposta
        if response.status_code == 200:  # 200 indica sucesso
            print("Status do Bot Alterado com sucesso")
        else:
            print("Error in the request. Status code:", response.status_code)

    except Exception as erro:
        print(f"Erro API Status: ", erro)
        return erro

def Log (message,path):
    try:

        # Capturar dados do arquivo de configuração do bot
        Dados_Json = getBotID(path)
        ID_Iteration = Dados_Json['IteracaoID']
        ClientToken = Dados_Json['ClientToken']

        # True / False
        finalLog = False
        # Level - info=0, warn=1, error=2
        level = 0
        typeError = ''
        fileBase64 = ''
        UrlAPILog = 'https://api-app.hypercoe.com/api/execution/add-log-by-bot'
        #UrlAPILog = 'https://api-app.hypercoe.com/api/execution/add-log-by-bot'
        dataatual = datetime.now()
        date = dataatual.strftime("%Y-%m-%dT%H:%M:%S")


        # Setar variaveis
        dados = {'date': date, 'level': level, 'typeError': typeError, 'message': message, 'fileBase64': fileBase64 ,'iterationId': ID_Iteration, 'finalLog':finalLog}

        # Headers da requisição (caso necessário)
        headers = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        # Realize a requisição
        response = requests.post(UrlAPILog, json=dados, headers=headers)

        # Verifique o status da resposta
        if response.status_code == 200:  # 200 indica sucesso
            print("Log:", message)
        else:
            print("Error in the request. Status code:", response.status_code)

    except Exception as erro:
        print(f"Erro API Log: ", erro)
        return erro

def Log_Error (message,path):
    try:

        # Capturar dados do arquivo de configuração do bot
        Dados_Json = getBotID(path)
        ID_Iteration = Dados_Json['IteracaoID']
        ClientToken = Dados_Json['ClientToken']


        finalLog = False
        # Level - info=0, warn=1, error=2
        level = 1
        typeError = ''
        fileBase64 = ''
        UrlAPILog = 'https://api-app.hypercoe.com/api/execution/add-log-by-bot'
        #UrlAPILog = 'https://api-app.hypercoe.com/api/execution/add-log-by-bot'
        dataatual = datetime.now()
        date = dataatual.strftime("%Y-%m-%dT%H:%M:%S")

        
        # Setar variaveis
        dados = {'date': date, 'level': level, 'typeError': typeError, 'message': message, 'fileBase64': fileBase64 ,'iterationId': ID_Iteration, 'finalLog':finalLog}

        # Headers da requisição (caso necessário)
        headers = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        # Realize a requisição
        response = requests.post(UrlAPILog, json=dados, headers=headers)

        # Verifique o status da resposta
        if response.status_code == 200:  # 200 indica sucesso
            print("Log:", message)
        else:
            print("Error in the request. Status code:", response.status_code)

    except Exception as erro:
        print(f"Erro API Log: ", erro)
        return erro

def Log_Attaching_File (message,pathfile,path):
    try:

        # Capturar dados do arquivo de configuração do bot
        Dados_Json = getBotID(path)
        ID_Iteration = Dados_Json['IteracaoID']
        ClientToken = Dados_Json['ClientToken']


        finalLog = False
        # Level - info=0, warn=1, error=2
        level = 0
        typeError = ''
        UrlAPILog = 'https://api-app.hypercoe.com/api/execution/add-log-by-bot'
        #UrlAPILog = 'https://api-app.hypercoe.com/api/execution/add-log-by-bot'
        dataatual = datetime.now()
        date = dataatual.strftime("%Y-%m-%dT%H:%M:%S")

        #Converter arquivo em Base64 caso tenha dados na variavel
        if len(pathfile) > 4:
            try:
                with open(pathfile, 'rb') as file:
                    arquivo_bytes = file.read()
                # Converter o arquivo para base64
                arquivo_base64 = base64.b64encode(arquivo_bytes).decode('utf-8')
                fileBase64 = arquivo_base64
            except Exception as erro:
                print(f"Erro na tentativa de converter o arquivo em Base64: ", erro)
                fileBase64 = ""
        else:
            fileBase64 = ""

        # Setar variaveis
        dados = {'date': date, 'level': level, 'typeError': typeError, 'message': message, 'fileBase64': fileBase64 ,'iterationId': ID_Iteration, 'finalLog':finalLog}

        # Headers da requisição (caso necessário)
        headers = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        # Realize a requisição
        response = requests.post(UrlAPILog, json=dados, headers=headers)

        # Verifique o status da resposta
        if response.status_code == 200:  # 200 indica sucesso
            print("Log:", message)
        else:
            print("Error in the request. Status code:", response.status_code)

    except Exception as erro:
        print(f"Erro API Log: ", erro)
        return erro

def End_Log (message,path):
    try:

        # Capturar dados do arquivo de configuração do bot
        Dados_Json = getBotID(path)
        ID_Iteration = Dados_Json['IteracaoID']
        ClientToken = Dados_Json['ClientToken']


        finalLog = True
        # Level - info=0, warn=1, error=2
        level = 0
        typeError = ''
        fileBase64 = ''
        UrlAPILog = 'https://api-app.hypercoe.com/api/execution/add-log-by-bot'
        #UrlAPILog = 'https://api-app.hypercoe.com/api/execution/add-log-by-bot'
        dataatual = datetime.now()
        date = dataatual.strftime("%Y-%m-%dT%H:%M:%S")

        # Setar variaveis
        dados = {'date': date, 'level': level, 'typeError': typeError, 'message': message, 'fileBase64': fileBase64 ,'iterationId': ID_Iteration, 'finalLog':finalLog}

        # Headers da requisição (caso necessário)
        headers = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        # Realize a requisição
        response = requests.post(UrlAPILog, json=dados, headers=headers)

        # Verifique o status da resposta
        if response.status_code == 200:  # 200 indica sucesso
            print("Log:", message)
        else:
            print("Error in the request. Status code:", response.status_code)

    except Exception as erro:
        print(f"Erro API Log: ", erro)
        return erro

def Iteration(path):
    try:

        # Capturar dados do arquivo de configuração do bot
        Dados_Json = getBotID(path)
        BotId = Dados_Json['BotId']
        ClientToken = Dados_Json['ClientToken']

        UrlAPIExecution = 'https://api-app.hypercoe.com/api/execution/add-execution-by-bot'
        #UrlAPIExecution = 'https://api-app.hypercoe.com/api/execution/add-execution-by-bot'
        
        UrlAPIIteracao = 'https://api-app.hypercoe.com/api/execution/add-iteration-by-bot'
        #UrlAPIIteracao = 'https://api-app.hypercoe.com/api/execution/add-iteration-by-bot'
        
        # ID - Active=0, Running=1, Paused=2, Error=3
        dados = {'botId': BotId}

        # Headers da requisição (caso necessário)
        headers = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        # Realize a requisição
        response = requests.post(UrlAPIExecution, json=dados, headers=headers)

        # Verifique o status da resposta
        if response.status_code == 200:  # 200 indica sucesso
            result = response.json()
            ExecutionID = result['dados']['id']
        else:
            print("Erro na requisição. Execution code:", response.status_code)

        # Dados que você quer enviar no corpo da requisição (em formato JSON, por exemplo)
        dadosIteracao = {'executionId': ExecutionID}
        
        # Headers da requisição (caso necessário)
        headersIteracao = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        # Realize a requisição
        responseIteracao = requests.post(UrlAPIIteracao, json=dadosIteracao, headers=headersIteracao)

        # Verifique o status da resposta
        if responseIteracao.status_code == 200:  # 200 indica sucesso
            resultIteracao = responseIteracao.json()
            IteracaoID = resultIteracao['dados']['id']
            print("Iteration ID:", IteracaoID)  # Retorna os dados da resposta em formato JSON
            #return IteracaoID

            # Chamar Função para escrever o IteracaoID no arquivo config.txt para serem utilizadas em outros processos
            write_IteracaoID(IteracaoID,path)
            write_ExecutionID(ExecutionID,path)
        else:
            print("Erro na requisição. Iteration code:", responseIteracao.status_code)
                
    except Exception as erro:
            print(f"Erro API Execution: ", erro)
            return erro

def Get_Asset(Name_Asset,path):
    try:
        # Capturar dados do arquivo de configuração do bot
        Dados_Json = getBotID(path)
        ClientToken = Dados_Json['ClientToken']

        UrlAPILog = f'https://api-app.hypercoe.com/api/assets/get-by-name/{Name_Asset}'
        #UrlAPILog = f'https://api-app.hypercoe.com/api/assets/get-by-name/{Name_Asset}'
    
        # Headers da requisição (caso necessário)
        headers = {'Content-Type': 'application/json', 'ClientToken': ClientToken}

        # Realize a requisição
        response = requests.get(UrlAPILog, headers=headers)

        # Verifique o status da resposta
        if response.status_code == 200:  # 200 indica sucesso
            data = jsonpickle.decode(response.text)
            documents = data['dados']
            value = documents['value']
            if documents['type'] == 3:
                pwd = documents['secondValue']
                return value, pwd
            else:
                return value
        else:
            return "Error in the request. Status code:", response.status_code

    except Exception as erro:
        return "Erro API Log: ", erro

def getBotID(path):
    #Obtenha o diretório do arquivo
    try:
        dados_em_memoria = {}
        with open(path, 'r') as arquivo:
            Dados = arquivo.read()
            Dados_Json = json.loads(Dados)
            chaves = Dados_Json.keys()
            for chave in chaves:
                 # Cria um novo dicionário com a chave e o valor
                novo_dado = {chave: Dados_Json[f'{chave}']}
                dados_em_memoria.update(novo_dado)
                
            Valores = dados_em_memoria
            return Valores
    except Exception as erro:
        print('Erro na etapa de leitura do config.txt')
        raise Exception('Erro na etapa de leitura do config.txt')

def write_IteracaoID(IteracaoID,Path):

    # Abre o arquivo e lê o conteúdo
    try:
        with open(Path, 'r') as arquivo:
            conteudo = arquivo.read()
        # Converte o conteúdo em um dicionário Python
        config_dict = json.loads(conteudo)
    except FileNotFoundError:
        # Se o arquivo não existir, cria um dicionário vazio
        config_dict = {}

    # Verifica se a chave "IteracaoID" já existe no dicionário
    if "IteracaoID" in config_dict:
        # Se a chave já existir, atualiza apenas o valor
        config_dict["IteracaoID"] = f"{IteracaoID}"
    else:
        # Se a chave não existir, adiciona a chave e o valor
        config_dict["IteracaoID"] = f"{IteracaoID}"

    # Escreve o dicionário atualizado de volta para o arquivo config.txt
    with open(Path, 'w') as arquivo:
        json.dump(config_dict, arquivo, indent=4)

def write_ExecutionID(ExecutionID,Path):

    # Abre o arquivo e lê o conteúdo
    try:
        with open(Path, 'r') as arquivo:
            conteudo = arquivo.read()
        # Converte o conteúdo em um dicionário Python
        config_dict = json.loads(conteudo)
    except FileNotFoundError:
        # Se o arquivo não existir, cria um dicionário vazio
        config_dict = {}

    # Verifica se a chave "ExecutionID" já existe no dicionário
    if "ExecutionID" in config_dict:
        # Se a chave já existir, atualiza apenas o valor
        config_dict["ExecutionID"] = f"{ExecutionID}"
    else:
        # Se a chave não existir, adiciona a chave e o valor
        config_dict["ExecutionID"] = f"{ExecutionID}"

    # Escreve o dicionário atualizado de volta para o arquivo config.txt
    with open(Path, 'w') as arquivo:
        json.dump(config_dict, arquivo, indent=4)
