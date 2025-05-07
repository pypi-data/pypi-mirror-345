from datetime import datetime
import logging
import src.api.okinghub as api_okinghub
from src.entities.log import Log
import src.api.slack as slack
import src
from threading import Lock
logger = logging.getLogger()
lock = Lock()

class OnlineLogger:

    @staticmethod
    def send_log(job_name: str, send_slack: bool, send_api: bool, message: str, log_type: str, job_method: str = 'LOG_ONLINE', api_log_identifier: str = ''):
        if send_slack:
            if not message.lower().__contains__('produto nao encontrado'):
                slack.post_message(f'{job_name} | {message} | Integracao {src.client_data.get("integracao_id")} | API {src.client_data.get("url_api")}')

        tipo_log = 'I'
        if log_type == 'info':
            logger.info(f'{job_name} | {message}')
            tipo_log = 'I'  # INFORMAÇÃO
        elif log_type == 'warning':
            logger.warning(f'{job_name} | {message}')
            tipo_log = 'V'  # VALIDAÇÃO
        elif log_type == 'error':
            logger.error(f'{job_name} | {message}')
            tipo_log = 'E'  # ERRO
        elif log_type == 'exec':
            logger.info(f'{job_name} | {message}')
            tipo_log = 'X'  # EXECUÇÃO - Monitora a execução de JOB mesmo quando não tem registros

        if send_api:
            api_okinghub.post_log(Log(f'{message}'
                                      , api_log_identifier
                                      , job_name
                                      , src.client_data.get("integracao_id")
                                      , tipo_log
                                      , src.client_data.get("seller_id")
                                      )
                                  )
                                # Log(f'Oking inicializando', '', 'INICIALIZACAO',f'{client_data.get("integracao_id")}', 'I', F'{client_data.get("seller_id")}')


def send_execution_notification(job_config: dict) -> None:
    with lock:
        # Exibe mensagem monstrando que a Thread foi Iniciada
        logger.info(f'==== THREAD INICIADA -job: ' + job_config.get('job_name'))
        # Formata a data para Melhorar a Visualização
        data_desativacao_formatada = job_config.get("execution_start_time").replace('T', ' ')
        data_objeto = datetime.strptime(data_desativacao_formatada, '%d//%m/%Y %H:%M:%S')

        mensagem = f'Oking em execucao desde {data_objeto} com {job_config.get("job_qty")}' \
                   f' jobs para o cliente {src.client_data.get("integracao_nome")} - Versão {src.version}'
        api_okinghub.post_log(Log(mensagem
                                  , 'OKING_EXECUCAO'
                                  , 'OKING_EXECUCAO'
                                  , src.client_data.get("integracao_id")
                                  , 'X'
                                  , src.client_data.get("seller_id")
                                  )
                              )
# online_logger = OnlineLogger.send_log
# online_logger(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'', 'warning', '')
# online_logger(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'', 'info', '')
# online_logger(job_config.get('job_name'), job_config.get('enviar_logs'), False, f'', 'error', '')
#
#
