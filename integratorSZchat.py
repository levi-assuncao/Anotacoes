#!/usr/bin/python3.6
import sys
import urllib3
from integratorSZchat_functions import *
from asterisk import agi


# NAO exibe erro de certificado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Inicializa o AGI
agi = agi.AGI()

# Arquivo de log PADRAO
log = '/var/log/asterisk/integrator.py.log'

# Identificador de atividade
try:
    uniqueid = agi.get_full_variable('${CHANNEL(linkedid)}')

except Exception as e:
    uniqueid = 'DEBUG MANUAL'

# Verifica se variável action foi enviada
try:
    action = sys.argv[1]
except Exception as e:
    dd("ARGUMENTO 1(ACAO) NAO INFORMADO " + str(e), log, uniqueid)
    agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,Fortics_SZ_chat')
    exit()

# Lista de ações
action_list = [
    'solicitaNumMsg',
    'consultarContato',
    'enviaMsg'
    ]

# Verifica se a ação é valida
if action not in action_list:
    dd('ACAO NAO IDENTIFICADA ' + action, log, uniqueid)
    agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,Fortics_SZ_chat')
    exit()

#Busca dados do CRM no banco de dados do Fortics PBX
retorno_creds   = getcreds('Fortics_SZ_chat', log, uniqueid)
api_key         = retorno_creds['api_key']
channel_key     = retorno_creds['channel_key']
host            = retorno_creds['url']
login           = retorno_creds['login']
senha           = retorno_creds['senha']

#Busca dados do CRM no banco de dados do Fortics PBX
retorno_gupshup = getcreds('Gupshup', log, uniqueid)
gup_key         = retorno_gupshup['gupkey']
gup_name        = retorno_gupshup['gupname']
gup_host        = retorno_gupshup['host']

if not gup_key or not gup_name or not gup_host:
    gupshup = 0
else:
    gupshup = 1      

# Verifica se api_key foi identificado
if not api_key:
    dd(str(action) + "()  API KEY NAO CONSTA NO CADASTRO DA INTEGRACAO", log, uniqueid)
    agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,Fortics_SZ_chat')
    exit()
# Verifica se channel_key foi identificada
if not channel_key:
    dd(str(action) + "()  CHANNEL KEY NAO CONSTA NO CADASTRO DA INTEGRACAO", log, uniqueid)
    agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,Fortics_SZ_chat')
    exit()
# Verifica se host foi identificado
if not host:
    dd(str(action) + "()  HOST NAO CONSTA NO CADASTRO DA INTEGRACAO", log, uniqueid)
    agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,Fortics_SZ_chat')
    exit()

red = redisdb('0', log, uniqueid)
token = red.get('auth-szchat-' + login)

if not token:    
    retorno_auth_agente = auth_login(host, login, senha, log, uniqueid)
    dd(str(action) + "() NÃO FOI POSSÍVEL IDENTIFICAR TOKEN NO REDIS. GERANDO NOVO TOKEN NO SZ.CHAT...", log, uniqueid)
    try:
        token = retorno_auth_agente['token']
        red.set('auth-szchat-' + login, token, 25200)
        dd(str(action) + "() TOKEN GERADO COM SUCESSO.", log, uniqueid)
        red.close()
    except:
        dd(str(action) + "() ERROR AO GERAR TOKEN PELO SZ.CHAT.", log, uniqueid)
        agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,Fortics_SZ_chat')
        red.close()
        exit()
else:
    token = token.decode()


if action == 'solicitaNumMsg':

    numero = sys.argv[2]

    if numero:
        dd(str(action) + "() NUMERO IDENTIFICADO POR MEIO DE DIGITAÇÃO." ,log, uniqueid)
        agi.set_variable('ARRAY(__RETORNO1,__NUM_SOLICITE,__INTEGRACAO)', '1,' + str(numero) + ',Fortics_SZ_chat')
        exit()  

    else:    
        dd(str(action) + "() NUMERO NÃO IDENTIFICADO ", log, uniqueid)
        agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,Fortics_SZ_chat')
        exit()

if action == 'consultarContato':

    try:
        numero = agi.get_full_variable('${CALLERID(num)}')
    except Exception as e:
        dd(str(action) + "() NUMERO NAO IDENTIFICADO " + str(e), log, uniqueid)
        agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,Fortics_SZ_chat')
        exit()

    telefone = format_number(numero)

    retorno_buscarContato = contacts_search(host, token, telefone, log, uniqueid)    
    try:
        retorno_grupo = retorno_buscarContato['data'][0]['group'][0]
    except Exception as e:
        dd(str(action) + "() GRUPO NAO IDENTIFICADO " + str(e) , log, uniqueid)
        agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,Fortics_SZ_chat')
        exit()

    if retorno_grupo:
        dd(str(action) + "() GRUPO IDENTIFICADO " + str(retorno_grupo) , log, uniqueid)
        agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', str(retorno_grupo) + ',Fortics_SZ_chat')
        exit()
    

if action == 'enviaMsg':

    try:
        numero = agi.get_full_variable('${NUM_SOLICITE}')
    except Exception as e:
        dd(str(action) + "() NUMERO NAO IDENTIFICADO " + str(e), log, uniqueid)

    if not numero:
        try:
            numero = agi.get_full_variable('${CALLERID(num)}')
        except Exception as e:
            dd(str(action) + "() NUMERO NAO IDENTIFICADO " + str(e), log, uniqueid)
            agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,Fortics_SZ_chat')
            exit()
    else:
        dd(str(action) + "() NUMERO IDENTIFICADO POR MEIO DE DIGITACAO " + str(numero), log, uniqueid)
        
   
    telefone = format_number(numero)
    dd(str(action) + "() FORMAT NUMBER " + str(type(numero)), log, uniqueid)

    if(gupshup != 0):
        retorno_gupshup = reg_gupshup(gup_host, telefone, gup_name, gup_key, log, uniqueid)
        if retorno_gupshup == True:
            dd(str(action) + "() REGISTRO EFETUADO COM SUCESSO NO GUPSHUP", log, uniqueid)
        else:
            dd(str(action) + "() REGISTRO NO GUPSHUP FALHOU", log, uniqueid)
            agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,Fortics_SZ_chat')
            exit()
    try:
        template_name = sys.argv[2]
    except Exception as e:
        dd(str(action) + "() ARGUMENTO 2(TEMPLATE) NÃO INFORMADO" + str(e), log, uniqueid)
        agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,Fortics_SZ_chat')
        exit()

    try:
        placeholders = sys.argv[3:]
    except:
        dd(str(action) + "() NÃO FOI FORNECIDO PARAMETROS PARA O TEMPLATE. => " + str(template_name), log, uniqueid)


    vars = ["@@NOME@@","@@NUMERO@@"]

    if any(marcador in placeholders for marcador in vars):           
        retorno_consulta_contato = contacts_search(host, token, telefone, log, uniqueid)

        if 'error' in retorno_consulta_contato:
            dd(str(action) + "() ERRO: " + retorno_consulta_contato['error'], log, uniqueid)
            agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,Fortics_SZ_chat')
            exit()

        else:
            try:
                name = retorno_consulta_contato['data'][0]['name']
            except:
                name = telefone
                dd(str(action) + "() NÃO FOI POSSÍVEL IDENTIFICAR O NOME DO CLIENTE.", log, uniqueid)

        for i, item in enumerate(placeholders):
            if item == "@@NOME@@":
                placeholders[i] = name
            elif item == "@@NUMERO@@":
                placeholders[i] = telefone    
                            
    retorno_send_msg_hsm = send_msg_hsm(host, token, channel_key, telefone, template_name, placeholders, log, uniqueid)

    if 'messages' in retorno_send_msg_hsm:
        dd(str(action) + "() MENSAGEM ENVIADA COM SUCESSO. NÚMERO => " + str(telefone), log, uniqueid)
        agi.set_variable('ARRAY(__RETORNO1,__TELEFONE,__INTEGRACAO)', '1,' + str(telefone) +',Fortics_SZ_chat')
        exit()
    else:
        dd(str(action) + "() NAO FOI POSSIVEL ENVIAR A MENSAGEM. " + str(telefone), log, uniqueid)
        agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,Fortics_SZ_chat')
        exit()
