import sys
import os

# Flask 프로젝트 경로 추가
sys.path.insert(0, '/home/ubuntu/trendnv/TrandNavi_AI')
os.environ['PYTHONHOME'] = '/home/ubuntu/.pyenv/versions/3.11.10'
os.environ['PYTHONPATH'] = ''

# Flask 애플리케이션 가져오기
from run import app as application
