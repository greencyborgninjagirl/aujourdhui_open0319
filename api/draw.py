"""
Vercel Python Serverless：与 POST /api/draw 对应。
将仓库根目录加入 path，以便导入 backend_api、app、draw_logic 等。
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from backend_api import app
