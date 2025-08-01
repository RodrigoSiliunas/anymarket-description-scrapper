import os
from pathlib import Path
from dotenv import load_dotenv

"""
==========================================================================
 ➠ Environments Configuration File
 ➠ Section By: Siliunas
 ➠ Related system: Environments
==========================================================================
"""

# Carrega as variáveis de ambiente do arquivo.env no código
load_dotenv()

# Obtém o caminho absoluto do diretório atual do script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Caminha para trás até o diretório raiz do projeto
project_root = os.path.abspath(os.path.join(current_dir, os.pardir))

# Define que a variável de ambiente ROOT_PATH recebe o valor do caminho da pasta raiz do projeto
os.environ['ROOT_PATH'] = str(Path(project_root).parent)

"""
==========================================================================
 ➠ Environments Configuration File
 ➠ Section By: Siliunas
 ➠ Related system: Environments
==========================================================================
"""

# Define que a variável de ambiente ROOT_PATH recebe o valor do caminho da pasta raiz do projeto
ROOT_PATH = os.environ.get('ROOT_PATH', None)
AI_STUDIO_API_KEY = os.environ.get('AI_STUDIO_API_KEY', None)
