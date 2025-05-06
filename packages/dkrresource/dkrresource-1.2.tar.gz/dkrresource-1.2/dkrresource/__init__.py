import multiprocessing, subprocess, threading, time, requests
from datetime import datetime as dt
from sqlalchemy import create_engine
from contextlib import contextmanager
from sqlalchemy import Column, Integer, String, DATE
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ControlResource(Base):
    __tablename__ = 'resources' 
    __table_args__ = {'schema': 'CONTROL'}

    id = Column(Integer, primary_key=True)
    app_name = Column(String)
    execution_id = Column(String)
    dt_execution = Column(DATE)
    max_cpu = Column(String)
    avg_cpu = Column(String)
    max_ram = Column(String)
    avg_ram = Column(String)


class ResourceManager:
    ''' Classe que gerencia a coleta de recursos '''

    def __init__(self, routine_name: str, start_date: dt, routine_path: str, db_str: str, t_channel: str, t_url: str):
        self.routine_name = routine_name
        self.dt_start = start_date
        self.routine_path = routine_path
        self.cpu_max = -1
        self.mamory_max = -1
        self.cpu_avg = -1
        self.memory_avg = -1
        self.core_count = multiprocessing.cpu_count()
        self.machine_memory = self.get_machine_memory()
        self.running = False
        self.db_str = db_str
        self.t_channel = t_channel
        self.t_url = t_url

    
    def set_id(self, id):
        ''' Define o id da execução atualizado '''

        self.id_exec = id
    

    def start_log(self):
        ''' Inicia no banco de dados o log de coleta de recursos '''
        
        self.start_resource({
            'app_name': self.routine_name,
            'execution_id': self.id_exec ,
            'dt_execution': self.dt_start,
            'max_cpu': f'{self.cpu_max} GB',
            'avg_cpu': f'{self.cpu_avg} %',
            'max_ram': f'{self.mamory_max} GB',
            'avg_ram': f'{self.memory_avg} %'
        })


    def get_machine_memory(self):
        ''' Obtém a quantidade de RAM do servdor que a rotina está sendo executada '''

        check_command = "grep MemTotal /proc/meminfo"
        output = subprocess.check_output(check_command, shell=True).decode('utf-8-sig')
        
        while "  " in output:
            output = output.replace("  ", " ")
        
        output = output.split(" ")[1]
        output = int(output)
        
        return round(output / 1024 / 1024, 2) # Converte de KB to GB


    def collect_ram_cpu(self):
        ''' Faz a captura de recursos de RAM e CPU '''
        
        count = 0
        while self.running:

            self.collect_ram()
            self.collect_cpu()

            count += 1

            # Gera log a cada minuto, aproximadamente
            if count % 12 == 0:
                self.update_resources()

            time.sleep(5)
            

    def collect_cpu(self):
        ''' Coleta a quantidade de CPU utilizada pela rotina naquele instante '''

        cpu_usage = 0
        check_command = f'ps aux | head -1; ps aux | sort -rnk 3 | grep "python -m.*{self.routine_path}" | head -1'

        output = subprocess.check_output(check_command, shell=True).decode('utf-8-sig')
        output = output.split('\n')
        output = output[1]

        while "  " in output:
            output = output.replace("  ", " ")

        output = output.split(" ")
        cpu_usage = float(output[2])

        cpu_usage = round(float(cpu_usage)/(self.core_count*100), 2)

        if self.cpu_max == -1: # Primeira vez que é executado
            self.cpu_max = cpu_usage
        
        elif cpu_usage > self.cpu_max:
            self.cpu_max = cpu_usage

        if self.cpu_avg == -1: # Primeira vez que é executado
            self.cpu_avg = cpu_usage
        
        else:
            self.cpu_avg = round((self.cpu_avg + cpu_usage) / 2, 2)


    def collect_ram(self):
        ''' Obtém a quantidade de RAM utilizada pela rotina naquele instante '''
        
        ram_usage = 0
        check_command = f'ps aux | head -1; ps aux | sort -rnk 4 | grep "python -m.*{self.routine_path}" | head -1'

        output = subprocess.check_output(check_command, shell=True).decode('utf-8-sig')
        output = output.split('\n')
        output = output[1]
        
        while "  " in output:
            output = output.replace("  ", " ")
        
        output = output.split(" ")
        ram_usage = float(output[3])

        ram_usage = round(self.machine_memory * (ram_usage / 100), 2) 

        if self.mamory_max == -1: # Primeira vez que é executado
            self.mamory_max = ram_usage
        
        elif ram_usage > self.mamory_max:
            self.mamory_max = ram_usage

        if self.memory_avg == -1: # Primeira vez que é executado
            self.memory_avg = ram_usage
        
        else:
            self.memory_avg = round((self.memory_avg + ram_usage) / 2, 2)


    def start_collection(self):
        ''' Inicia a coleta de recursos '''

        # Cria uma thread para coletar os recursos
        collection_thread = threading.Thread(target=self.collect_ram_cpu)

        # Altera o status da execucao
        self.running = True

        # Inicia a thread
        collection_thread.start()


    def finish_collection(self):
        ''' Finaliza a coleta de recursos '''

        self.running = False

        time.sleep(10) # Aguarda 10 segundos para que a thread termine
        self.update_resources()


    def update_resources(self):
        ''' Atualiza os dados de recursos no banco de dados '''

        self.update_resource({
            'max_cpu': f'{self.cpu_max} GB',
            'avg_cpu': f'{self.cpu_avg} %',
            'max_ram': f'{self.mamory_max} GB',
            'avg_ram': f'{self.memory_avg} %'
        })


    def send_error(self, step: str, desc: str):
        ''' Envia o card de erro para o teams de suporte interno na DKR. Os parametros são: 
            - step: Etapa do fluxo da rotina
            - desc: Descrição do erro 
            Além disso, no payload é informado o canal que o card deve ser enviado, pois a distribuição entre os clientes é feita pelo Power Automate '''

        try:
            payload = {
                'channel': self.t_channel, 
                'step': step, 
                'desc': desc
            }
            
            req = requests.post(self.t_url, json=payload)

            print(f"| TEAMS |--> Card status code: {req.status_code} | Content: {req.content}")

            return True
        
        except Exception as e:
            print("| TEAMS | Falha ao enviar card para o suporte", e)
            return
    

    def start_resource(self, res_data: dict):
        ''' Inicia o log de coleta de recursos da rotina '''

        with self.open_conn('Iniciando log Recursos') as db:    
            try:
                new_record = ControlResource(
                    app_name = res_data['app_name'],
                    execution_id = res_data['execution_id'],
                    dt_execution = res_data['dt_execution'],
                    max_cpu = res_data['max_cpu'],
                    avg_cpu = res_data['avg_cpu'],
                    max_ram = res_data['max_ram'],
                    avg_ram = res_data['avg_ram']
                )
                db.add(new_record)        
                db.commit()

                self.c_id_resource = new_record.id
        
            except Exception as e:
                print(f'| RESOURCE | Criando registro de coleta de recursos. Erro: {e}')
                self.send_error(f'Iniciando log de Recursos', f'Durante o envio das primeiras informações sobre uso de recursos da execução para o banco de dados')


    def update_resource(self, res_data: dict):
        ''' Atualiza o log de coleta de recursos da rotina '''

        with self.open_conn('Atualizando log Recursos') as db:    
            try:
                record = db.query(ControlResource).filter(ControlResource.id == self.c_id_resource, ControlResource.execution_id == self.id_exec).first()

                for key, value in res_data.items():
                    if hasattr(record, key):
                        setattr(record, key, value)
        
                db.commit()
        
            except Exception as e:
                print(f'| RESOURCE | Atualizando registro de coleta de recursos. Erro: {e}')
                self.send_error(f'Atualizando log de Recursos', f'Atualizando as informações sobre uso de recursos da execução no banco de dados')


    @contextmanager
    def open_conn(self, step: str):
        ''' Função que abre, aguarda a utilização e fecha a conexão com o banco de dados.
        A exceção é capturada por quem chama a função, e não internamente '''

        try:
            conn = None
            engine = create_engine(self.db_str)    
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

            conn = SessionLocal()  
            yield conn  

        except Exception as e:
            self.send_error(f'Conexão com o banco', f'IMPORTANTE!! Erro na conexão com o banco de dados para a etapa: {step}. Erro: {str(e)[:500]}')
        
        finally:        
            if conn is not None:
                conn.close()
        