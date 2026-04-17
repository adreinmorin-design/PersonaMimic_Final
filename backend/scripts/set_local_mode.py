import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config.models import SystemSetting
from app.database.database import SessionLocal

db = SessionLocal()
try:
    s = db.query(SystemSetting).filter(SystemSetting.key == "use_cloud").first()
    if s:
        s.value = "False"
    else:
        s = SystemSetting(key="use_cloud", value="False")
        db.add(s)
    db.commit()
    print("Successfully set use_cloud to False")
finally:
    db.close()
