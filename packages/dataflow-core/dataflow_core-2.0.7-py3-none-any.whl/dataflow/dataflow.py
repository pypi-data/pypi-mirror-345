import os, requests
from .models.database import DatabaseManager
from sqlalchemy.inspection import inspect
from .utils.aws_secrets_manager import SecretsManagerClient
import json, asyncio, pkg_resources
from authenticator.package.configuration import ConfigurationManager


class Dataflow:
    def __init__(self):
        self.secrets_manager = SecretsManagerClient('us-east-1')

    def auth(self, session_id: str):
        """Retrieve user information from the auth API."""
        try:
            dataflow_config = ConfigurationManager('/dataflow/app/auth_config/dataflow_auth.cfg')
            auth_api = dataflow_config.get_config_value('auth', 'ui_auth_api')
            response = requests.get(
                auth_api,
                cookies={"dataflow_session": session_id, "jupyterhub-hub-login": ""}
            )
            
            if response.status_code != 200:
                return response.json()
            
            user_data = response.json()
            user_dict = {
                "user_name": user_data["user_name"], 
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"] if user_data.get("last_name") else "",
                "email": user_data["email"],
                "role": user_data["role"]
            }
            return user_dict
                  
        except Exception as e:
            return e
    
    def variable(self, variable_name: str):
        """Get variable value from secrets manager."""
        try:
            host_name = os.environ["HOSTNAME"]
            user_name = host_name.replace("jupyter-","")
            
            vault_path = "variables"
            variable_data =  self.secrets_manager.get_secret_by_key(vault_path, user_name, variable_name)
            return variable_data['value']
            
        except Exception as e:
            return None
        
    def connection(self, conn_id: str):
        """Get connection details from secrets manager."""
        try:
            host_name = os.environ["HOSTNAME"]
            user_name=host_name.replace("jupyter-","")
            
            vault_path = "connections"
            secret = self.secrets_manager.get_secret_by_key(vault_path, user_name, conn_id)

            conn_type = secret['conn_type'].lower()
            username = secret['login']
            password = secret.get('password', '')
            host = secret['host']
            port = secret['port']
            database = secret.get('schemas', '')

            user_info = f"{username}:{password}@" if password else f"{username}@"
            db_info = f"/{database}" if database else ""

            connection_string = f"{conn_type}://{user_info}{host}:{port}{db_info}"

            extra = secret.get('extra', '')
            if extra:
                try:
                    extra_params = json.loads(extra)
                    if extra_params:
                        extra_query = "&".join(f"{key}={value}" for key, value in extra_params.items())
                        connection_string += f"?{extra_query}"
                except json.JSONDecodeError:
                    # If 'extra' is not valid JSON, skip adding extra parameters
                    pass

            connection_instance = DatabaseManager(connection_string)
            return next(connection_instance.get_session())
        
        except Exception as e:
            return None
        
    async def create_env(self, env_name, py_version, py_requirements, status, env_version=None):
        """
        Creates a conda environment at the specified path and installs libraries in one command.
        """
        config = ConfigurationManager('/dataflow/app/config/dataflow.cfg')
        status = status.lower()
        if status == "published":
            env_base_path = config.get_config_value('paths', 'published_env_path')
            conda_env_path = os.path.join(env_base_path, env_name)
        else:
            env_base_path = config.get_config_value('paths', 'drafts_env_path')
            conda_env_path = os.path.join(env_base_path, env_name, f"{env_name}_v{env_version}")
        try:
            if not os.path.exists(conda_env_path):
                os.makedirs(conda_env_path, exist_ok=True)

            py_requirements = ",".join(py_requirements) 

            script_path = pkg_resources.resource_filename('dataflow', 'scripts/create_environment.sh')
    
            # Make the script executable
            os.chmod(script_path, 0o755)
            
            # Prepare command with arguments
            command = ["bash", script_path, py_requirements, conda_env_path, py_version]

            process = await asyncio.create_subprocess_exec(
                *command, 
                stdout=asyncio.subprocess.PIPE, 
                stderr=asyncio.subprocess.PIPE
            )
            
            return process
        except OSError as e:
            print(f"OS error while creating {conda_env_path}: {e}")
        except Exception as e:
            print(f"Unexpected error while creating {conda_env_path}: {e}")
            return {"error": str(e)}