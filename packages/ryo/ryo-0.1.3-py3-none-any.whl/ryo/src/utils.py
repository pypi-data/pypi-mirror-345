import os
import yaml
import yamale
from yamale.validators import Validator, DefaultValidators


class StepValidator(Validator):
    tag = 'step'

    def _is_valid(self, value):
        action_fields = {
            'commit_file': {
                'required': [],
                'optional': ['auto_commit', 'commit_msg', 'repository']
            },
            'workflow_monitor': {
                'required': ['workflow_name'],
                'optional': ['show_workflow']
            },
            'approve_pull_request': {
                'required': ['source_branch', 'target_branch'],
                'optional': []
            }
        }

        action = value.get('action')
        if not action:
            self._errors.append("O campo 'action' é obrigatório.")
            return False

        if action not in action_fields:
            self._errors.append(f"A ação '{action}' não é reconhecida.")
            return False

        required_fields = action_fields[action]['required']
        optional_fields = action_fields[action]['optional']
        allowed_fields = set(required_fields + optional_fields + ['action'])

        missing_fields = [field for field in required_fields if field not in value]
        if missing_fields:
            self._errors.append(f"Campos obrigatórios ausentes para a ação '{action}': {', '.join(missing_fields)}.")
            return False

        unexpected_fields = [field for field in value if field not in allowed_fields]
        if unexpected_fields:
            self._errors.append(f"Campos inesperados para a ação '{action}': {', '.join(unexpected_fields)}.")
            return False

        return True

    def fail(self, value):
        return " ".join(self._errors)

def config_validator(base_dir: str) -> bool:
    """
    Valida um arquivo YAML contra um esquema definido.

    Args:
        base_dir (str): Base dir.

    Returns:
        bool: True se o arquivo for válido, False caso contrário.
    """
    config_path = os.path.join(base_dir, '.config.yml')
    utils_base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(utils_base_dir, 'schema.yml')

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        data = yamale.make_data(content=content)
        validators = DefaultValidators.copy()
        validators[StepValidator.tag] = StepValidator
        schema = yamale.make_schema(schema_path, validators=validators)
        yamale.validate(schema, data)
        return True
    except FileNotFoundError:
        print(f"Erro: Arquivo de configuração não encontrado em: {config_path}")
        return False
    except yamale.YamaleError as exc:
        print(".config.yml não é válido:")
        for result in exc.results:
            for error in result.errors:
                print(f"  - {error}")
        return False
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante a validação: {e}")
        return False


def check_config_name():
    config_files = ['config.yml', 'config.yaml']
    config_file = None
    
    for file in config_files:
        if os.path.exists(os.path.join(os.getcwd(), file)):
            config_file = file
            break

    if config_file is None:
        raise FileNotFoundError("Config file not founded (.config.yml ou .config.yaml).")

    return config_file


def load_config():
    """
        Load the configuration from the YAML file.

        Returns:
            dict: The loaded configuration.
    """
    #print("Getting config file...")
    
    config_path = os.path.join(os.getcwd(), "config.yml")

    with open(config_path, 'r', encoding='utf-8') as f:
        try:
            config = yaml.safe_load(f)
            #print(f"Load configuration with success!")
            return config
        except FileNotFoundError:
            print(f"Aviso: arquivo config.yml não encontrado em: {os.getcwd()}. Usando configurações padrão (se houver).")
            return {}
        except yaml.YAMLError as e:
            print(f"Erro ao ler o arquivo config.yml: {e}")
            return {}


def get_task(task_name: str) -> dict:
    """
    Load the configuration from the YAML file and return the task details.
    
    Args:
        task_name (str): The name of the task to retrieve.
    
    Returns:
        dict: The task details.
    """
    #print("Getting task parameters...")
    try:
        config = load_config()
        task = config["tasks"].get(task_name)
        if task != None:
            return task
        else:
            raise KeyError(f"Task '{task_name}' not founded.")
    except KeyError as exc:  #Verificar: esta é a mensagem de erro correta?
        print(f"Error getting desired task: {exc}")
        raise

