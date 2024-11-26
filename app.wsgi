import sys
import os

os.environ['DATABASE_URI'] = "mysql+pymysql://junho:335276@13.209.230.95:3306/trand_nv"
os.environ['SECRET_KEY'] = "skHo2JmYdYA"
os.environ['OPENAI_API_KEY'] = "sk-proj--7wMF4OKsCSPACwQfyOeLBHN4dB_mdgi6PgqBE7NWbvwtcM961H>

os.environ['LANGCHAIN_TRACING_V2'] = "true"
os.environ['LANGCHAIN_API_KEY'] = "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"
os.environ['LANGCHAIN_ENDPOINT'] = "https://api.smith.langchain.com"
os.environ['LANGCHAIN_PROJECT'] = "LangChainProject"

os.environ['JWT_SECRET_KEY'] = "Ji13BSrbKG"

os.environ['NAVER_CLIENT_ID'] = "IRaU3KJ02B0myg8nQbKZ"
os.environ['NAVER_CLIENT_SECRET'] = "Ji13BSrbKG"

os.environ['SERPAPI_KEY'] = "c07c4d1d280706d1ca84eaa71a271b624345023fdcddbc856a1a90454c27dd>
os.environ['IMGUR_CLIENT_ID'] = "745dde45164ef14"

os.environ['REDIS_URL'] = "redis://localhost:6379/0"


# 가상환경 경로를 명시적으로 추가
venv_path = '/home/ubuntu/.pyenv/versions/py3.11'

# 가상환경 경로를 시스템 경로에 추가
sys.path.insert(0, '/home/ubuntu/trendnv/TrandNavi_AI/')
sys.path.insert(0, os.path.join(venv_path, 'lib/python3.11/site-packages'))

# 환경 변수 설정
os.environ['PATH'] = f"{os.path.join(venv_path, 'bin')}:" + os.environ['PATH']
os.environ['PYTHONHOME'] = venv_path

# Flask 애플리케이션 로드 
from run import app as application

from dotenv import load_dotenv

# .env 파일의 절대 경로 지정
dotenv_path = "/path/to/your_project/.env"
load_dotenv(dotenv_path)