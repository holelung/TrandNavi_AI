import sys
import os

# 가상환경 활성화
activate_this = '/home/ubuntu/.pyenv/versions/py3.10/bin/activate_this.py'
exec(open(activate_this).read(), {'__file__': activate_this})

# Flask 프로젝트 경로 추가
sys.path.insert(0, '/home/ubuntu/trendnv/TrandNavi_AI')

# Flask 애플리케이션 가져오기
from run import app as application
