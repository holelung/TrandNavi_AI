import sys
import os
from dotenv import load_dotenv

# 가상환경 경로를 명시적으로 추가
venv_path = '/home/ubuntu/.pyenv/versions/py3.11'

# 가상환경 경로를 시스템 경로에 추가
sys.path.insert(0, '/home/ubuntu/trendnv/TrandNavi_AI/')
sys.path.insert(0, os.path.join(venv_path, 'lib/python3.11/site-packages'))

# 환경 변수 설정
os.environ['PATH'] = f"{os.path.join(venv_path, 'bin')}:" + os.environ['PATH']
os.environ['PYTHONHOME'] = venv_path

# .env 파일의 절대 경로 지정
dotenv_path = "/path/to/your_project/.env"
load_dotenv(dotenv_path)

# Flask 애플리케이션 로드 
from run import app as application

with open('/tmp/python_path.log', 'w') as f:
    import sys
    f.write(f"Python Executable: {sys.executable}\n")
    f.write(f"Python Path: {sys.path}\n")
