#!/usr/bin/python3.6

import sys
import re
import os
from asterisk import agi
from unidecode import unidecode


try:
    action = 'validaNumero'
except Exception as e:
    dd(str(action) + "() ARGUMENTO 1(AÇÃO) NÃO INFORMADO "+str(e), log, uniqueid)
    agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,CUSTOM')
    exit()

action_list = ['validaNumero',
               'consultarClienteTipo']

if action not in action_list:
    dd(str(action) + ' AÇÃO NÃO IDENTIFICADA ' + action, log, uniqueid)
    agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,CUSTOM')
    exit()



if action == 'validaNumero':

# Número de exemplo
numero = '85'

# Regex para validar o número (XX9XXXXXXXX)
regex = r"^[0-9]{2}9[0-9]{8}$"

# Verifica se o número corresponde à regex
if re.match(regex, numero):
    agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '1,CUSTOM')
else:
    agi.set_variable('ARRAY(__RETORNO1,__INTEGRACAO)', '0,CUSTOM')
