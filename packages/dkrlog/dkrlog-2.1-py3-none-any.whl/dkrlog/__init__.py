import traceback, inspect, traceback, logzero as lz, os, requests, logging, pytz, requests
from typing import Optional
from datetime import datetime as dt
from sqlalchemy import create_engine
from contextlib import contextmanager
from sqlalchemy import Column, Integer, String, DATE, Identity
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_STR = os.getenv("DB_LOG_E_STR", "")
Base = declarative_base()

class CustomFormatter(logging.Formatter):
    ''' Classe que formata como as mensagens de log vão ser inseridas no sistema '''
    
    def format(self, record):
        ''' Formata o atributo levelname da mensagem de log trazendo apenas a primeira letra'''
        
        record.levelname = record.levelname[0] # Transforma o levelname em uma letra        
        return super().format(record)

class ControlLogException(Base):
    __tablename__ = 'log_exception'
    __table_args__ = {'schema': 'CONTROL'}

    id = Column(Integer, Identity(start=1, increment=1), primary_key=True)
    dt_error = Column(DATE)
    exception_e = Column(String)
    custom_msg = Column(String)
    func_name = Column(String)
    filename = Column(String)
    line_no = Column(String)
    params = Column(String)
    detailed_exp = Column(String)
    app_name = Column(String)

class Errors():
    ''' Classe que armazena os erros gerados pela aplicação '''
    error_list = []

    def error_len(self):
        ''' Retorna o número de erros gerados '''

        return len(self.error_list)
    

def set_vars(exec_id: str, app_name: str, t_channel: str, t_url: str):
    ''' Define o ID da execução '''
    global EXEC_ID, APPLICATION_NAMESPACE, T_CHANNEL, T_URL

    EXEC_ID = exec_id
    APPLICATION_NAMESPACE = app_name
    T_CHANNEL = t_channel
    T_URL = t_url


def set_logfile(name: str):
    ''' Determina o logfile da execução do script '''

    # Criando pasta se ela não existe
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Personalizando a formatação do logfile
    formatter = CustomFormatter('[%(levelname)s] %(message)s')
    lz.formatter(formatter)    
    lz.logfile(f'logs/{name}.logs')


def log_exception(msg: str, e: Exception):
    ''' Faz o tratamento da exception e registra no log '''

    # Pega o frame da exception, ou seja, a função onde a exception foi gerada
    frame = inspect.currentframe().f_back

    func_name = frame.f_code.co_name    # Nome da função
    filename = frame.f_code.co_filename # Nome do arquivo
    line_no = frame.f_lineno            # Número da linha

    # Pega os nomes e valores dos argumentos da função chamadora
    arg_info = inspect.getargvalues(frame)
    ''' 
    Aqui ele retorna um tuple com os seguintes valores:
        args: argumentos da função
        varargs: argumentos variáveis da função
        keywords: argumentos com nome da função
        locals: valores locais da função
    Mas vamos apenas capturar os argumentos explicitos (args)
    '''
    params = {arg: arg_info.locals.get(arg) for arg in arg_info.args}
    detailed_exp = traceback.format_exc()

    full_msg = f"{filename}: {msg}\n|===> Função: {func_name}() | Linha: {line_no} | Argumentos: {str(params)[:5000]} | Exception: {e}\n\n{detailed_exp}\n"
    log(full_msg, type='e')
    
    try:
        register_log(
            timestamp = get_date(get_string=False),
            error = str(e),
            func_name = func_name,
            filename = filename,
            line_no = str(line_no), 
            detailed_exp = str(detailed_exp),
            custom_msg = msg,
            params = str(params)[:5000]
        )
    
    except Exception:
        log(str(traceback.print_exc()), 'e')
    
    return full_msg


def log(msg: str, type: Optional[str] = 'i'):
    ''' Adiciona log no arquivo de log. O tipo de log pode ser "i" para informações, "e" para erros e "w" para avisos '''

    if type == 'i':
        lz.logger.info(f'{get_date()} | {EXEC_ID} |{msg}')
        
    elif type == 'e':
        ERROR_LIST.error_list.append(msg)
        lz.logger.error(f'{get_date()} | {EXEC_ID} | {msg}')
        
    elif type == 'w':
        lz.logger.warning(f'{get_date()} | {EXEC_ID} |{msg}')


def register_log(timestamp: dt, error: str, func_name: str, filename: str, line_no: str, detailed_exp: str, custom_msg: Optional[str] = None, params: Optional[str] = None):
    ''' Registra o log no banco de dados '''

    with open_conn_log('Salvando exception no banco') as db:    
        try:
            new_record = ControlLogException(
                dt_error = timestamp,
                exception_e = error,
                custom_msg = custom_msg,
                func_name = func_name,
                filename = filename,
                line_no = line_no,
                params = params,
                detailed_exp = detailed_exp,
                app_name = APPLICATION_NAMESPACE
            )
            db.add(new_record)        
            db.commit()
    
        except Exception as e:
            log(f'LOG DB | Criando registro de log. Erro: {e}', 'e')


def get_date(get_string: Optional[bool] = True):
    ''' Retorna o horario com o fuso horário de Brasilia no formato "dd/mm/yyyy hh:mm:ss" '''
 
    now = dt.now(pytz.timezone('America/Sao_Paulo'))

    return now.strftime("%d/%m/%Y %H:%M:%S") if get_string else now


@contextmanager
def open_conn_log(step: str):
    ''' Função que abre, aguarda a utilização e fecha a conexão com o banco de dados.
    A exceção é capturada por quem chama a função, e não internamente '''

    try:
        conn = None
        engine = create_engine(DB_STR)    
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        conn = SessionLocal()  
        yield conn  

    except Exception as e:
        log(f'DB CONN | Erro na conexão com o banco de dados para a etapa: {step}. Erro: {str(e)[:500]}', 'e')
        send_error(f'Conexão com o banco | Log Exception', f'IMPORTANTE!! Erro na conexão com o banco de dados para a etapa: {step}. Erro: {str(e)[:500]}')
    
    finally:        
        if conn is not None:
            conn.close()


def send_error(step: str, desc: str):
    ''' Envia o card de erro para o teams de suporte interno na DKR. Os parametros são: 
        - step: Etapa do fluxo da rotina
        - desc: Descrição do erro 
        Além disso, no payload é informado o canal que o card deve ser enviado, pois a distribuição entre os clientes é feita pelo Power Automate '''

    try:
        payload = {
            'channel': T_CHANNEL, 
            'step': step, 
            'desc': desc
        }
        
        req = requests.post(T_URL, json={payload})

        log(f" TEAMS |--> Card status code: {req.status_code} | Content: {req.content}")

        return True
    
    except Exception as e:
        log(f"TEAMS | Falha ao enviar card para o suporte. Erro: {e}", 'e')
        return

    
ERROR_LIST = Errors()