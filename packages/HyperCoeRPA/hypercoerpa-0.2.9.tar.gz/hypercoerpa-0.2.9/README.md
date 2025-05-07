<!-- coding: utf-8 -->
# HyperCoe RPA: 

## Kit de componentes para Governança de Bots na plataforma HyperCoe.

### Intalação
    >>> pip install hypercoerpa

### Como usar a biblioteca:
    >>> from hypercoerpa.function import *

###  Exemplo de como usar a função de registro de log
- write_IteracaoID(IteracaoID,Path):
- getBotID(path):
- Get_Asset(Name_Asset,path):
- Iteration(path):
- End_Log (message,path):
- Log_Attaching_File (message,pathfile,path):
- Log_Error (message,path):
- Log (message,path):
- Error_Status(path):
- End_Status(path):
- Start_Status(path):
- Populate_Queue(path, Reference, DadosJson):
- Queue_Item_Abandoned(path):
- Queue_Item_Get(path):
- Queue_Item_Change_Status(path, queueItemID, status):
- Queue_Item_Change_Exception_Error(path, queueItemID, exception):


### -inição dos parâmetros:
- **rpa-hypercoe-log**
    - **bot_status** - Valor inteiro correspondente ao status do bot sendo # Active=0, Running=1, Paused=2, Error=3 (Campo obrigatório)
    - **bot_id** - Valor inteiro referente ao ID do bot que será gerado no momento de criação do robô pelo agente do HyperCoe (Campo obrigatório)
    - **clienttoken** - Valor string do Token que será disponibilizado pelo Portal HyperCoe (Campo obrigatório)
    - **level** - Valor inteiro correspondente ao tipo de informação que será regsitrado no log, sendo # Info=0, Warn=1, Error=2 (Campo obrigatório)
    - **typeError** - Valor string com a mensagem em caso de erro. (Campo não obrigatório)
    - **message** - Valor string com a mensagem de log (Campo obrigatório)
    - **pathfile** - Valor string com o caminho absoluto para envio de evidência (Campo não obrigatório)
    - **ID_Iteration** - Valor inteiro capturado pela api "Iteration" (Campo obrigatório)
    - **finalLog** - Valor boleano (False/True) que deverá ser padrão False e somente utilizar o parametro True no último registro de log do robô (Campo não obrigatório)