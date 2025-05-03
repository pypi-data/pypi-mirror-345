import os
import sys
import time
import threading
from zylo.server.dev_server import app
from zylo.compiler.generate_openapi import generate_openapi

def watch_and_generate(path=".", interval=2):
    """
    파일 변경을 감지해서 openapi.yaml을 자동 재생성하는 watcher
    (간단한 시간 기반 폴링 방식)
    """
    last_mtime = 0
    while True:
        max_mtime = 0
        for dirpath, _, filenames in os.walk(path):
            for fname in filenames:
                if fname.endswith(".py"):
                    fpath = os.path.join(dirpath, fname)
                    max_mtime = max(max_mtime, os.path.getmtime(fpath))
        if max_mtime != last_mtime:
            print("🔄 Detected code change. Regenerating openapi.yaml...")
            generate_openapi()
            last_mtime = max_mtime
        time.sleep(interval)

def main():
    print("🚀 Starting Zylo Dev Server")
    print("📦 Parsing source code and generating OpenAPI spec...")
    
    try:
        generate_openapi()
    except Exception as e:
        print(f"❌ Failed to generate OpenAPI spec: {e}")
        sys.exit(1)

    print("🌐 Docs available at: http://localhost:8000/docs")
    print("📘 OpenAPI spec at:   http://localhost:8000/openapi.yaml")

    # 백그라운드에서 watcher 실행
    watcher_thread = threading.Thread(target=watch_and_generate, daemon=True)
    watcher_thread.start()

    # Flask dev server 실행
    app.run(host="0.0.0.0", port=8000, debug=True)