from datetime import datetime
import socket
import requests
import os.path
import pkg_resources
import src.api.okvendas as api_okVendas

from src import utils
import src
from src.database.utils import get_database_config, final_query
from src.api import oking
from src.jobs.config_jobs import realizar_operacao, enviar_comando_operacao, enviar_criacao, send_log, get_logs
from src.jobs.config_jobs import testar_conexao
PySimpleGUI_License = 'eCyyJvMga4WENWlLbQnxNflpVXHulEwfZNSVIP65I9kZRlpscr3uRPy6ajWjJy1GdWGgl4v3bMi0IVsLIRkLxAp7Yl20VUu6cX28V0JIRYC2Ih69MKTjc5xOO5DBIqwzMPzDkyzYOnSIwni9T4GrlbjbZBWT5ezPZqUHR2luccGExuvde5Wp1KlYb3nwR8WoZvXaJ3zSaEWj9suVIsjso5iLN7SZ4QwkIMiIwYi2TzmuFftHZlUeZwp2cEn0Nc0nIUjxoCiST13VBylNbTmjsKihL4C5J7OOYjWb18lyTDGrFwzKdXCPI76fIBlERQlsYM2R5Svjb8Gl9EnuacWqEKgfZsW006g4UY2Alrz0dzG4VetoYhXsMHiFLfCcJtDMbD261KwVY8WY5Q5xIJjtoPiSTV3EB6lAbNmQs1gHVSGYVljQbQm692sWbu27dhp5YVSgBzlxbwSnBmTsa6XBNG0jZHW31khucTyPIUs4ISkiNi1CcG30RBvFbDW2VFyMStU1QIioOBi7ImyHNMTgI30TOLSbITs2IwkoRjhud0GgVNJbcc3CN11zZmW6QbiVO2iYInycMGDNIc0NLXTyAD2iLETtEMywIeiTwai8RSGrFu0NZHUmVH4XccG0lhy5ZlXfM4iPOUi8Ify9MBDJI61RLWTbA02lLOTPEeyEIHiKwXilRbWd1ahkaiWqxaBIZzGsRXyRZJXlNszEITjbocipZ5XNJiuRY8WX5VlZLImdNNyyYqX0RAvJQ6Gj9owkZcWS5drOLpmXNlvVbXST53ircRi5IGs5I7kflaQFQKWaRMkvcKmsVYzAc1ySIU63IXjuEY5qM7S64NzEMaSG48xuM9zegsukMQjuMAxgImn10K=U7659d3fd6495b1883de8a1e605e83dd7294daacee4b16bdeafebb8f2287b6c9d986f9841cc146e01104a6cc4395e433070352bc9c64b7bfde563fb19b77ed5c766abe1c3e9138d7fc1bbad27cda55395d02ea939f3fc95c8d7970cfbbbe1b7e475ae5fa1d7f8461adf29508809cff93906319ca5c276650cb735a2a50f9bc524fd78ddf97761b5615b455c8be885d9fb0e897c973fbfa1158a2121113f90ea195c1b418a19b98d24f0bf9b92d10b26c144805fea4e921d67d1eaddbd655eacd58faaf16811f4bc1c330fac3a08804d98551f835253ac58e3ee4cf943241ce0134577c92105de835e192b748743eaa5f77843549771413f70bbe79677f80b549b13312dd1793eddd09dd4bb25905b122ec24dc0892a27b7651ae0fc60b24bae049a5fc099be69f039685fc6e26b614b8a205684b36fdb03182f84dc4128923151af27b368e77ecad78e7ceb1b82d2b8bb3e21bb86d986a8e45969f2aaab314210d68e7d098b7afde85473e18f67b6262a9fdd87962d42461c73c1eb13c3bb58c65219b6787534a1f53f77527ada2e8f739a52ad4bb92c397bc6fdc639a20761a7a6ba26a3747a42e75ea6c3104ab09c2df4dd3c7fdfe66dbf25f46a62fff6787ea69fbb8c729a25b488b4ae7cbc05282ebdc171633f76c4acb0c0ea48075866ce1994ef52cf4fc146f77b6d5f5ad59067a3062115391001952ae18dcf9fe593f0'
import PySimpleGUI as sg

from src.layout import layout_shortname, layout_token, layout_conection, layout_operacao, \
    layout_erroconexao, get_config_layout, get_image, layout_change_token, layout_new_token, tabela_dashboard
from src.utils import get_config, send_photo

dashboard = []
opcoesCatalogo = []
opcoesPedido = []
opcoesAuxiliares = []
listaTarefas = []
all_jobs = utils.dict_all_jobs


def exibir_campos_config(dadosConfig, janela):
    janela['-MSG_ENTRADA-'].update(
        f"Segue abaixo os dados para a integração {dadosConfig['nome']} (loja {dadosConfig['loja_id']})")
    # janela['-IMG_LOGO-'].update(get_image(src.shortname_interface, "logo"))
    # janelaToken['-TEXTO_TOKEN-'].update(visible=False)
    # janelaToken['-LBL_TOKEN-'].update(visible=False)
    # janelaToken['-TOKEN-'].update(visible=False)
    # janelaToken['-BTN_TOKEN-'].update(visible=False)
    # janelaToken['-BTN_CANCEL-'].update(visible=False)
    # janelaToken['-FRM_CONFIG-'].update(visible=True)
    # janelaToken['-BTN_CONFIG-'].update(visible=True)
    # janelaToken['-BTN_OPERACAO-'].update(visible=True)
    # janelaToken['-BTN_CANCEL-'].update(visible=True)

    # seta valores na tela
    janela['-BANCO-'].update(dadosConfig['banco'])
    janela['-DIR_DB-'].update(dadosConfig['diretorio_db'])
    janela['-HOST-'].update(dadosConfig['host'])
    janela['-ESQUEMA-'].update(dadosConfig['esquema_db'])
    janela['-USER_DB-'].update(dadosConfig['usuario_db'])
    janela['-PASS_DB-'].update(dadosConfig['senha_db'])


# setar valores das abas
def atribuir_campos_operacao(tipo, status, comando, intervalo, obs, janelaOperacao):
    if tipo is None:
        return None
    elif status == 'S':
        janelaOperacao[f'-STATUS_{tipo}_ON-'].update(True)
        janelaOperacao[f'-STATUS_{tipo}_OFF-'].update(False)
    else:
        janelaOperacao[f'-STATUS_{tipo}_ON-'].update(False)
        janelaOperacao[f'-STATUS_{tipo}_OFF-'].update(True)

    janelaOperacao[f'-SQL_{tipo}-'].update(comando)
    if intervalo is None:
        janelaOperacao[f'-TEMPO_{tipo}-'].update(9999)
    else:
        janelaOperacao[f'-TEMPO_{tipo}-'].update(intervalo)
    janelaOperacao[f'-OBS_{tipo}-'].update(obs)
    habilita_campos(tipo, janelaOperacao, True if status == 'S' else False)


def habilita_campos(aba, janelaOperacao, desativa=False):
    janelaOperacao[f'-SQL_{aba}-'].update(disabled=not desativa, text_color=('#F5F5F5' if not desativa else '#000000'))
    janelaOperacao[f'-TEMPO_{aba}-'].update(disabled=not desativa,
                                            text_color=('#F5F5F5' if not desativa else '#000000'))
    janelaOperacao[f'-OBS_{aba}-'].update(disabled=not desativa, text_color=('#F5F5F5' if not desativa else '#000000'))


def tipo_tarefa(tipo):
    try:
        return all_jobs[tipo]['job_type']
    except:
        return None

def tarefa_formatada(tipo):
    try:
        return all_jobs[tipo]['job_description']
    except:
        return None

def tarefa_job(tipo):
    for x, y in all_jobs.items():
        if y['job_type'] == tipo:
            return x

def modifica_aba_query(janela, evento):
    job_name = tarefa_job(evento)
    query_final = final_query(get_database_config(get_config(job_name)))
    janela['-QUERY_FINAL-'].update(query_final)
    janela["-TAB_QUERY_FINAL-"].select()


def modifica_aba_log(janela, evento):
    list_log = get_logs(evento)
    janela['-TABLE_LOGS-'].update(list_log)
    janela['-TABLE_LOGS-'].table_frame.pack(expand=True, fill='both')
    janela.Element("-COMBO_LOGS-").Update(values=listaTarefas)
    janela['-COMBO_LOGS-'].update(value=tipo_tarefa(evento))
    hide_tabs(janela)
    janela["-ABA_LOGS-"].select()


def call_job(job_evento):
    return all_jobs[job_evento]['job_function']
    


# def busca_ajuda_tarefa(tipo):
#     res = requests.get(f"https://{shortname}}.oking.openk.com.br/api/consulta/ajuda/filtros?job={tipo}")
#     return res.json()
scroll_enabled = True


def exibir_janela_shortname():
    if os.path.isfile('shortname.txt'):
        shortname_file = open("shortname.txt", "r")
        src.shortname_interface = shortname_file.read()
        shortname_file.close()
    else:
        janelaEntrada = sg.Window('Conector OKing - Facilitando integrações', layout_shortname)
        while True:
            evento, valores = janelaEntrada.read()
            if evento == sg.WIN_CLOSED or evento == '-BTN_EXIT-':
                exit()
            elif evento == '-BTN_SALVAR-':
                if valores['-SHORTNAME-'] == '':
                    sg.popup("Shortname precisa ser informado!", custom_text='  Fechar  ')
                    continue
                if socket.gethostbyname(socket.gethostname()) == '127.0.0.1':
                    sg.popup_error("Verifique a conexão!")
                    continue
                try:
                    res = requests.get(f"https://{valores['-SHORTNAME-']}.oking.openk.com.br/api/consulta/ping")
                    if res.ok:
                        janelaEntrada.hide()
                        src.shortname_interface = valores['-SHORTNAME-']
                        with open('shortname.txt', 'w') as f:
                            f.write(src.shortname_interface)
                            f.close()
                        src.conexao = True
                        break
                    sg.popup_error(res.text)
                    continue
                except:
                    sg.popup_error("Shortname inválido!")
                    continue
    exibir_janela_token()


def exibir_janela_token(abre_arquivo=True):
    if os.path.isfile('token.txt') and abre_arquivo:
        token_file = open("token.txt", "r")
        src.token_total = token_file.readline()
        value = 0
        if src.token_total.__contains__('#'):
            value = src.token_total.index('#') + 1

        src.token_interface = src.token_total[value:].replace("\n", "")
        token_file.close()
        res = requests.get(
            f"https://{src.shortname_interface}.oking.openk.com.br/api/consulta/integracao/filtros?token={src.token_interface}")
        integracao = res.json()
        if not integracao["sucesso"]:
            sg.popup_error(integracao["mensagem"])
            # janelaConexao.un_hide()
            # exibir_campos_config(integracao['integracao'], janelaConexao)
            # evento, valores = janelaConexao.read()
            # if evento == sg.WIN_CLOSED or evento == '-BTN_CANCEL-':
            #     break
    else:
        janelaToken = sg.Window('Conector OKing - Facilitando integrações', layout_token)
        janelaToken.finalize()
        janelaToken.hide()
        janelaToken['-IMAGEM-'].update(get_image(src.shortname_interface, "imagem_entrada"))
        janelaToken['-MSG_TITULO-'].update(get_config_layout(src.shortname_interface, "mensagem_titulo"))
        janelaToken['-MSG_ENTRADA-'].update(get_config_layout(src.shortname_interface, "mensagem_entrada"))

        while True:
            janelaToken.un_hide()
            evento, valores = janelaToken.read()
            if evento == sg.WIN_CLOSED or evento == '-BTN_CANCEL-':
                exit()
            if socket.gethostbyname(socket.gethostname()) == '127.0.0.1':
                sg.popup_error("Verifique a conexão!")
                continue
            elif evento == '-BTN_TOKEN-':
                if valores["-TOKEN-"] == '' or valores["-NOME-"] == '':
                    sg.popup("Token e Nome precisam ser informados!", custom_text=('  Fechar  '))
                    continue

                res = requests.get(
                    f"https://{src.shortname_interface}.oking.openk.com.br/api/consulta/integracao/filtros?token={valores['-TOKEN-']}")
                integracao = res.json()
                if not integracao["sucesso"]:
                    sg.popup_error(integracao["mensagem"])
                    continue

                src.token_interface = valores['-TOKEN-']
                src.token_total = valores['-NOME-'] + "#" + valores['-TOKEN-']
                janelaToken.hide()
                with open('token.txt', 'a') as f:
                    f.write(src.token_total + "\n")
                    f.close()
                src.conexao = True
                break


def hide_tabs(janela):
    for aba in all_jobs.values():
        janela[f'-ABA_{aba["job_type"]}-'].update(visible=False)
    janela['-ABA_NOVO_BD-'].update(visible=False)
    janela['-TAB_QUERY_FINAL-'].update(visible=False)
    janela['-ABA_DASHBOARD-'].update(visible=False)
    janela['-ABA_LOGS-'].update(visible=False)
    janela['-ABA_FOTOSMASS-'].update(visible=False)


def configure(event, canvas, frame_id):
    canvas.itemconfig(frame_id, width=canvas.winfo_width())


def update_elemento_dash(janela, indice, visivel: bool):
    janela[f'-FRAME_GERAL_{indice}-'].update(visible=visivel)


def update_elemento_dados_dash(janela, indice):
    janela[f'-TEXT_EDIT_{indice}-'].update(dashboard[indice][0])
    janela[f'-INFO_TEMPO_{indice}-'].update(
        f'{dashboard[indice][1]} em {dashboard[indice][1]} {dashboard[indice][2]}')
    janela[f'-INFO_ULT_{indice}-'].update(dashboard[indice][3])


def scrollbar_set(self, lo, hi):
    if float(lo) <= 0.0 and float(hi) >= 1.0:
        self.pack_forget()
    elif self.cget("orient") != sg.tk.HORIZONTAL:
        self.pack(side=sg.tk.RIGHT, fill=sg.tk.Y)
    self.old_set(lo, hi)


sg.tk.Scrollbar.old_set = sg.tk.Scrollbar.set
sg.tk.Scrollbar.set = scrollbar_set


def exibir_interface():
    global opcoesCatalogo, opcoesPedido, opcoesAuxiliares
    tarefas_adicionadas_qtd = 0
    tarefas_extra = 0
    janelaErroconexao = sg.Window('Conexão', layout_erroconexao)
    janelaErroconexao.finalize()
    janelaErroconexao.hide()

    janelaConexao = sg.Window('Conector OKing - Facilitando integrações', layout_conection)
    janelaConexao.finalize()
    janelaConexao['-MSG_TITULO-'].update(get_config_layout(src.shortname_interface, 'mensagem_titulo'))
    janelaConexao.hide()

    janelaComboToken = sg.Window('Opções do Token', layout_change_token, size=(600, 130))
    janelaComboToken.finalize()
    janelaComboToken.hide()

    janelaOperacao = sg.Window('Conector OKing - Facilitando integrações', layout_operacao, location=(0, 0),
                               margins=(0, 0), element_padding=0, resizable=True, size=(800, 600))
    janelaOperacao.finalize()
    if opcoesCatalogo:
        janelaOperacao["-DROP_MENU_CATALOGO-"].update(visible=True)
    if opcoesPedido:
        janelaOperacao["-DROP_MENU_PEDIDO-"].update(visible=True)
    if opcoesAuxiliares:
        janelaOperacao["-DROP_MENU_AUX-"].update(visible=True)
    janelaOperacao['-TABLE_LOGS-'].expand(True, True)
    janelaOperacao.TKroot.minsize(900, 620)
    janelaOperacao['-IMG_LOGO-'].update(get_image(src.shortname_interface, 'logo'))
    janelaOperacao['-DASHBOARD-'].set_cursor('hand2')
    janelaOperacao['-FOTOSMASS-'].set_cursor('hand2')
    frame_id = janelaOperacao['-COLUMN_DASHBOARD-'].Widget.frame_id
    canvas = janelaOperacao['-COLUMN_DASHBOARD-'].Widget.canvas
    canvas.bind("<Configure>", lambda event, canvas=canvas, frame_id=frame_id: configure(event, canvas, frame_id))

    janelaOperacao.hide()

    janelaTokenInsert = sg.Window('Novo Token', layout_new_token)
    janelaTokenInsert.finalize()
    janelaTokenInsert.hide()


    while True:
        xor = False
        try:
            while True:
                res = requests.get(
                    f'https://{src.shortname_interface}.oking.openk.com.br/api/consulta/integracao/filtros?token={src.token_interface}')
                integracao = res.json()

                if src.conexao:
                    janelaConexao.un_hide()
                    exibir_campos_config(integracao['integracao'], janelaConexao)
                    janelaConexao['-IMG_ENTRADA-'].update(get_image(src.shortname_interface, 'imagem_entrada'))
                    evento, valores = janelaConexao.read()
                    if evento == sg.WIN_CLOSED or evento == '-BTN_CANCEL-':
                        return
                    if socket.gethostbyname(socket.gethostname()) == '127.0.0.1':
                        janelaErroconexao.un_hide()
                        evento, valores = janelaErroconexao.read()
                        if evento == '-BTN_TENTAR-':
                            janelaErroconexao.hide()
                            continue
                        else:
                            return
                    if evento == '-BTN_CONFIG-':
                        try:
                            dados = {'banco': valores['-BANCO-'],
                                     'diretorio_db': valores["-DIR_DB-"],
                                     'host': valores['-HOST-'],
                                     'esquema_db': valores['-ESQUEMA-'],
                                     'usuario_db': valores['-USER_DB-'],
                                     'senha_db': valores['-PASS_DB-'],
                                     'token': src.token_interface}

                            try:
                                testar_conexao(dados)
                                response = requests.post(
                                    f"https://{src.shortname_interface}.oking.openk.com.br/api/integracao",
                                    json=dados)
                                if response.json()['sucesso']:
                                    sg.popup('Configuração salva com sucesso')
                                else:
                                    sg.popup_error(response.json()['mensagem'])
                            except Exception as e:
                                sg.popup_error(f"Configuração inválida: {e}")
                        except requests.ConnectionError as error:
                            sg.popup_error(error)
                        except Exception as e:
                            sg.popup_error(f"Erro ao salvar configurações: {e}")

                else:
                    evento = '-BTN_OPERACAO-'

                if evento == '-BTN_OPERACAO-':
                    value = 0
                    if src.token_total.__contains__('#'):
                        value = src.token_total.index('#') + 1
                    src.nome_token = src.token_total[:value - 1]
                    src.token_interface = src.token_total[value:].replace('\n', '')
                    # busca dados das operações (tarefas)
                    src.conexao = False
                    res = requests.get(
                        f"https://{src.shortname_interface}.oking.openk.com.br/api/consulta/tarefas/filtros?token={src.token_interface}")
                    tarefas = res.json()
                    janelaConexao.hide()
                    for tarefa in tarefas:
                        atribuir_campos_operacao(tipo_tarefa(tarefa['tipo']), tarefa['ativo'], tarefa['comando'],
                                                 tarefa['intervalo'], tarefa['observacao'], janelaOperacao)

                    janelaOperacao['-MSG_TOKEN-'].update(f"Você está conectado com: {src.nome_token}")
                    janelaOperacao['-TOKEN_ATUAL-'].update(f' ...{src.token_interface[-5:]}')
                    version = src.version
                    janelaOperacao['-VERSAO-'].update(f"Versão {version}")
                    evento = '-BTN_ESCOLHER_TOKEN-'
                    while True:
                        if evento == '-BTN_ESCOLHER_TOKEN-':
                            src.client_data = oking.get(
                                f'https://{src.shortname_interface}.oking.openk.com.br/api/consulta/oking_hub/filtros'
                                f'?token={src.token_interface}',
                                None)
                            get_dashboard()
                            get_opcoes()

                            if tarefas_adicionadas_qtd < len(listaTarefas):
                                for x in range(tarefas_adicionadas_qtd, len(listaTarefas)):
                                    xor ^= True
                                    janelaOperacao.extend_layout(janelaOperacao['-FRAME_DASHBOARD-'],
                                                                 tabela_dashboard(str(x), '', '', '',
                                                                                  janelaOperacao.get_screen_size()[0], xor))
                                    janelaOperacao[f'-EDIT_BTN_{x}-'].set_cursor('hand2')
                                    janelaOperacao[f'-LOG_BTN_{x}-'].set_cursor('hand2')
                                    update_elemento_dados_dash(janelaOperacao, x)
                                    tarefas_adicionadas_qtd += 1
                                    tarefas_extra += 1

                            # for x in range(9):
                            #     xor ^= True
                            #     janelaOperacao.extend_layout(janelaOperacao['-FRAME_DASHBOARD-'],
                            #                                  tabela_dashboard(str(x), '', '', '',
                            #                                                   janelaOperacao.get_screen_size()[0], xor))
                            #     janelaOperacao[f'-EDIT_BTN_{x}-'].set_cursor('hand2')
                            #     janelaOperacao[f'-LOG_BTN_{x}-'].set_cursor('hand2')
                            if tarefas_adicionadas_qtd > 0:
                                for x in range(len(listaTarefas)):
                                    update_elemento_dados_dash(janelaOperacao, x)
                            if tarefas_adicionadas_qtd > len(listaTarefas):
                                for x in range(len(listaTarefas), tarefas_adicionadas_qtd):
                                    update_elemento_dash(janelaOperacao, x, False)
                                tarefas_extra = len(listaTarefas)
                            if tarefas_extra < len(listaTarefas):
                                for x in range(tarefas_extra, len(listaTarefas)):
                                    update_elemento_dash(janelaOperacao, x, True)
                            if tarefas_extra < 10:
                                janelaOperacao['-COLUMN_DASHBOARD-'].Widget.bind_all('<MouseWheel>', lambda e: "break")
                            else:
                                janelaOperacao['-COLUMN_DASHBOARD-'].Widget.unbind_all('<MouseWheel>')
                            # janelaOperacao.refresh()
                            # janelaOperacao['-COLUMN_DASHBOARD-'].contents_changed()
                            janelaOperacao["-DROP_MENU_CATALOGO-"].update(visible=False)
                            janelaOperacao["-DROP_MENU_PEDIDO-"].update(visible=False)
                            janelaOperacao["-DROP_MENU_AUX-"].update(visible=False)
                            if opcoesCatalogo:
                                janelaOperacao["-DROP_MENU_CATALOGO-"].update(visible=True)
                                janelaOperacao.Element("-DROP_MENU_CATALOGO-").Update(
                                    menu_definition=[['JOBS'], opcoesCatalogo])
                            if opcoesPedido:
                                janelaOperacao["-DROP_MENU_PEDIDO-"].update(visible=True)
                                janelaOperacao.Element("-DROP_MENU_PEDIDO-").Update(
                                    menu_definition=[['JOBS'], opcoesPedido])
                            if opcoesAuxiliares:
                                janelaOperacao["-DROP_MENU_AUX-"].update(visible=True)
                                janelaOperacao.Element("-DROP_MENU_AUX-").Update(
                                    menu_definition=[['JOBS'], opcoesAuxiliares])
                            janelaOperacao["-DROP_MENU_CONFIG-"].update(visible=True)
                        janelaOperacao.un_hide()
                        evento, valores = janelaOperacao.read()
                        if evento == '-KEY_PYSIMPLEGUI-':
                            sg.main()
                        if evento == sg.WIN_CLOSED or evento == '-BTN_FECHAR-':
                            return
                        if socket.gethostbyname(socket.gethostname()) == '127.0.0.1':
                            janelaErroconexao.un_hide()
                            evento, valores = janelaErroconexao.read()
                            if evento == '-BTN_TENTAR-':
                                janelaErroconexao.hide()
                                continue
                            else:
                                return
                        elif evento == '-DASHBOARD-':
                            hide_tabs(janelaOperacao)
                            update_dashboard(janelaOperacao)
                            janelaOperacao["-ABA_DASHBOARD-"].select()

                        elif evento == '-FOTOSMASS-':
                            hide_tabs(janelaOperacao)
                            janelaOperacao["-ABA_FOTOSMASS-"].select()
                            exists = os.path.exists('Processadas')
                            if not exists:
                                os.makedirs('Processadas')

                        elif evento == '-FOLDER-':
                            fotos = os.listdir(valores['-FILES-'])
                            janelaOperacao['-FOTOSPEND-'].update(fotos)
                            janelaOperacao['-PENDENTES-'].update(len(fotos))

                        elif evento == '-ENVIARFOTOS-':
                            exists = os.path.exists(valores['-FILES-']) and os.listdir(valores['-FILES-'])
                            if exists:
                                try:
                                    resultado = send_photo(valores['-FILES-'])
                                    janelaOperacao['-PROCESSADAS-'].update(resultado[0])

                                    fotospend = os.listdir(valores['-FILES-'])
                                    janelaOperacao['-FOTOSPEND-'].update(fotospend)
                                    janelaOperacao['-PENDENTES-'].update(len(fotospend))

                                    fotosproc = os.listdir(f'Processadas/{resultado[1]}')
                                    janelaOperacao['-FOTOSPROC-'].update(fotosproc)
                                except Exception as err:
                                    sg.popup_error('Ops!', f'Falha enviar fotos: {str(err)}')
                            else:
                                sg.popup_error("Selecione um arquivo válido!")

                        elif evento[0] == '-TABLE_LOGS-':
                            try:
                                sg.popup(janelaOperacao['-TABLE_LOGS-'].Values[evento[2][0]][evento[2][1]])
                            except:
                                continue

                        elif evento == '-DROP_MENU_CONFIG-':
                            if valores['-DROP_MENU_CONFIG-'] == 'Integração':
                                src.conexao = True
                                janelaOperacao.hide()
                                janelaConexao.un_hide()
                                break

                            elif valores["-DROP_MENU_CONFIG-"] == 'Setup (Create)':
                                hide_tabs(janelaOperacao)
                                janelaOperacao['-ABA_NOVO_BD-'].update(visible=True)
                                janelaOperacao["-ABA_NOVO_BD-"].select()

                            elif valores['-DROP_MENU_CONFIG-'] == 'Token':
                                janelaOperacao.hide()
                                janelaComboToken.un_hide()

                                with open('token.txt') as f:
                                    linhas = f.read().splitlines()
                                    janelaComboToken["-COMBO_TOKEN-"].update(lambda x: x, linhas)
                                    janelaComboToken.find_element("-COMBO_TOKEN-").update(value=linhas[0])
                                evento, valores = janelaComboToken.read()

                                if evento == sg.WIN_CLOSED:
                                    return

                                elif evento == '-BTN_VOLTAR_TOKEN-':
                                    janelaComboToken.hide()
                                    continue

                                elif evento == '-BTN_ESCOLHER_TOKEN-':
                                    src.token_total = valores['-COMBO_TOKEN-']
                                    janelaOperacao["-CREATE_DB-"].update("")
                                    janelaOperacao["-USER-"].update("")
                                    janelaOperacao["-PASSWORD-"].update("")
                                    janelaComboToken.hide()
                                    src.conexao = False
                                    break

                                elif evento == '-BTN_NOVO_TOKEN-':
                                    janelaComboToken.hide()
                                    janelaTokenInsert.un_hide()
                                    janelaTokenInsert["-NOME-"].update("")
                                    janelaTokenInsert["-TOKEN-"].update("")
                                    while True:
                                        evento, valores = janelaTokenInsert()
                                        if evento == sg.WIN_CLOSED:
                                            return

                                        elif evento == '-BTN_CANCEL-':
                                            janelaTokenInsert.hide()
                                            break

                                        elif evento == '-BTN_NOVO_TOKEN-':
                                            if valores["-TOKEN-"] == '' or valores["-NOME-"] == '':
                                                sg.popup("Token e Nome precisam ser informados!",
                                                         custom_text='  Fechar  ')
                                                continue
                                            else:
                                                res = requests.get(
                                                    f"https://{src.shortname_interface}.oking.openk.com.br/api/consulta"
                                                    f"/integracao/filtros?token={valores['-TOKEN-']}")
                                                integracao = res.json()
                                                if not integracao["sucesso"]:
                                                    sg.popup_error(integracao["mensagem"])
                                                    continue
                                                else:
                                                    src.token_interface = valores['-TOKEN-']
                                                    src.token_total = valores['-NOME-'] + "#" + valores['-TOKEN-']
                                                    janelaTokenInsert.hide()
                                                    with open('token.txt', 'a') as f:
                                                        f.write(src.token_total + "\n")
                                                        f.close()
                                                    src.conexao = True
                                                    break
                        elif evento.startswith('-DROP_'):
                            hide_tabs(janelaOperacao)
                            janelaOperacao[f'-ABA_{valores[evento]}-'].update(visible=True)
                            janelaOperacao[f'-ABA_{valores[evento]}-'].select()

                        elif evento == '-BTN_CREATE-':
                            if valores['-USER-'] != src.client_data['user'] or valores['-PASSWORD-'] != src.client_data[
                                'password']:
                                sg.popup("Senha ou usuário inválidos", custom_text='  Fechar  ')
                            else:
                                valores['-CREATE_DB-'] = replace_create(valores['-CREATE_DB-'])
                                janelaOperacao['-CREATE_DB-'].update(valores['-CREATE_DB-'])
                                src.client_data['sql'] = valores['-CREATE_DB-']
                                try:
                                    enviar_criacao(src.client_data)
                                    sg.popup('Banco criado com sucesso!')
                                except Exception as e:
                                    sg.popup_error('Ops!', f'Falha ao criar: {str(e)}')
                            continue

                        # BLOQUEIA OS CAMPOS DA TELA SE DESATIVAR A TAREFA

                        elif evento.startswith('-EDIT_BTN_'):
                            indice = int(evento[10:-1])
                            tarefa_aba = listaTarefas[indice]
                            hide_tabs(janelaOperacao)
                            janelaOperacao[f'-ABA_{tarefa_aba}-'].update(visible=True)
                            janelaOperacao[f"-ABA_{tarefa_aba}-"].select()

                        elif evento == "-COMBO_LOGS-":
                            janelaOperacao["-ABA_LOGS-"].update(visible=True)
                            modifica_aba_log(janelaOperacao, tarefa_job(valores["-COMBO_LOGS-"]))

                        elif evento.startswith('-STATUS_'):
                            evento_temp = evento[8:]
                            evento_final = evento_temp[:evento_temp.index('_')]
                            habilita_campos(evento_final, janelaOperacao, valores[f'-STATUS_{evento_final}_ON-'])

                        #   salvam configuração da QUERY

                        elif evento.startswith('-BTN_SAVE_'):
                            evento_temp = evento[10:-1]
                            enviar_comando_operacao(src.shortname_interface,
                                                    tarefa_job(evento_temp),
                                                    valores[f'-STATUS_{evento_temp}_ON-'],
                                                    valores[f'-SQL_{evento_temp}-'],
                                                    valores[f'-TEMPO_{evento_temp}-'],
                                                    valores[f'-OBS_{evento_temp}-'], src.token_interface)
                            src.client_data = oking.get(
                                f'https://{src.shortname_interface}.oking.openk.com.br/api/consulta/oking_hub/filtros'
                                f'?token={src.token_interface}',
                                None)
                        #

                        elif evento.startswith('-VALIDAR_'):
                            try:
                                evento_temp = evento[9:-1]
                                job_evento = tarefa_job(evento_temp)

                                config = get_config(job_evento)
                                config['sql'] = replace_select(valores[f'-SQL_{evento_temp}-'])
                                qdelinhas = (realizar_operacao(config, job_evento), job_evento)
                                janelaOperacao[f'-RES_{evento_temp}-'].update(qdelinhas[0])
                                sg.popup('Query executada! Verifique a quantidade de linhas!')

                            except Exception as e:
                                sg.popup_error('Ops!', f'Falha ao validar query: {str(e)}')

                        elif evento.startswith('-EXECJOB_'):
                            evento_temp = evento[9:-1]
                            job_evento = tarefa_job(evento_temp)
                            try:
                                executa_job = call_job(job_evento)
                                executa_job(get_config(job_evento))
                                sg.popup('Job Executada')
                            except Exception as e:
                                # if e.name is None:
                                send_log(job_evento, src.client_data.get('enviar_logs'), True,
                                         f'Erro ao Executar JOB {evento_temp}: {e}', 'error', job_evento.upper(),
                                         f'JOB_{evento_temp}')
                                sg.popup_error('Ops!', f'Falha ao executar job: {str(e)}')
                        elif evento.startswith('-QUERY_FINAL_'):
                            evento_temp = evento[13:-1]
                            janelaOperacao["-QUERY_FINAL-"].update(visible=True)
                            try:
                                modifica_aba_query(janelaOperacao, evento_temp)
                            except Exception as e:
                                send_log(evento_temp, src.client_data.get('enviar_logs'), True,
                                         f'Erro ao exibir query final', 'error', evento_temp,
                                         f'{evento_temp}')
                                sg.popup_error('Ops!', f'Falha ao exibir query final: {str(e)}')

                        elif evento.startswith('-LOG_BTN_'):
                            indice_log = int(evento[9:-1])
                            tarefa_log = listaTarefas[indice_log]
                            evento_temp = tarefa_job(tarefa_log)
                            janelaOperacao["-ABA_LOGS-"].update(visible=True)
                            modifica_aba_log(janelaOperacao, evento_temp)
        except Exception as e:
            if socket.gethostbyname(socket.gethostname()) == '127.0.0.1':
                janelaErroconexao.un_hide()
                evento, valores = janelaErroconexao.read()
                if evento == '-BTN_TENTAR-':
                    janelaErroconexao.hide()
                    continue
                else:
                    return
            else:
                sg.popup_error(f'Erro inesperado ocorrido: {e}')
                break


def get_opcoes():
    modules: list = [oking.Module(**m) for m in src.client_data.get('modulos')]
    global opcoesCatalogo, opcoesPedido, opcoesAuxiliares, listaTarefas
    # catalogos = ['ESTOQUE', 'FOTO', 'PRECO', 'PRODUTO']
    # pedidos = ['ENCAMINHA', 'NOTAFISCAL', 'PEDIDO', 'PEDIDOPAGO', 'NOTAFISCALSEMFILA', 'VENDASUGERIDA']
    # auxiliares = ['ENTREGUE', 'IMPOSTOPRODUTO', 'IMPOSTOLOTE', 'LISTAPRECO', 'PRODUTOLISTAPRECO', 'PAGAMENTO',
    #               'REPRESENTANTE', 'CLIENTEAPROVADO', 'COLETACLIENTE', 'COLETAVENDA', 'CLIENTE', 'CLIENTEPLANOPGT',
    #               'PRODUTORELACIONADO', 'PRODUTOCROSSELLING', 'PRODUTOLANCAMENTO', 'PRODUTOVITRINE']
    listaTarefas = []
    opcoesCatalogo = []
    opcoesPedido = []
    opcoesAuxiliares = []
    for module in modules:
        if module.ativo != 'S':
            continue
        if module.job_name not in all_jobs:
            continue
        # opcao = tipo_tarefa(module.job_name)
        elif all_jobs[module.job_name]['job_category'] == "catalogo":
            listaTarefas.append(all_jobs[module.job_name]['job_type'])
            opcoesCatalogo.append(all_jobs[module.job_name]['job_type'])
        elif all_jobs[module.job_name]['job_category'] == "pedido":
            listaTarefas.append(all_jobs[module.job_name]['job_type'])
            opcoesPedido.append(all_jobs[module.job_name]['job_type'])
        elif all_jobs[module.job_name]['job_category'] == "auxiliar":
            listaTarefas.append(all_jobs[module.job_name]['job_type'])
            opcoesAuxiliares.append(all_jobs[module.job_name]['job_type'])


def get_dashboard():
    global dashboard
    dashboard = []
    modules: list = [oking.Module(**m) for m in src.client_data.get('modulos')]
    for module in modules:
        tarefa = tarefa_formatada(module.job_name)
        if tarefa is not None and module.ativo == 'S':
            tempo = 9999 if module.time is None else module.time
            ultima_execucao = '' if module.ultima_execucao is None else datetime.strptime(module.ultima_execucao,
                                                                                          '%Y-%m-%d %H:%M:%S.%f')
            dado_dash = [tarefa, tempo, module.time_unit, ultima_execucao]
            dashboard.append(dado_dash)


def update_dashboard(janela):
    modules: list = [oking.Module(**m) for m in src.client_data.get('modulos')]
    indice = 0
    for module in modules:
        tarefa = tipo_tarefa(module.job_name)
        if tarefa is not None and module.ativo == 'S':
            tempo = 9999 if module.time is None else module.time
            janela[f'-INFO_TEMPO_{indice}-'].update(f'{tempo} em {tempo} {module.time_unit}')
            janela[f'-INFO_ULT_{indice}-'].update(module.ultima_execucao)
            indice += 1







def replace_select(sql):
    return sql.replace("DELETE", "SELECT").replace("CREATE", "SELECT").replace("delete",
                                                                               "SELECT").replace(
        "create", "SELECT")


def replace_create(sql):
    return sql.replace("DELETE", "CREATE").replace("SELECT", "CREATE").replace("delete",
                                                                               "CREATE").replace(
        "select", "CREATE")
