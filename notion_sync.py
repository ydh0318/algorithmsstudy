import os
import json
import urllib.request
import urllib.error
import ssl
import re

# SSL 검증 우회 context 생성
ssl_context = ssl._create_unverified_context()

def get_env_or_from_dot_env(key):
    """GitHub Actions 환경 변수 또는 로컬 .env 파일에서 키값을 가져옵니다."""
    val = os.getenv(key)
    if val:
        return val
    
    # 로컬 .env 파일 파싱
    env_path = "/Users/yu/Desktop/무제 폴더/.env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1].strip()
    return None

NOTION_API_KEY = get_env_or_from_dot_env("NOTION_API_KEY")
NOTION_DATABASE_ID = get_env_or_from_dot_env("NOTION_DATABASE_ID")
DISCORD_BOT_TOKEN = get_env_or_from_dot_env("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = get_env_or_from_dot_env("DISCORD_CHANNEL_ID")
ALL_CHANGED_FILES = os.getenv("ALL_CHANGED_FILES", "[]")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY", "user/repo")
GITHUB_SHA = os.getenv("GITHUB_SHA", "main")

def notion_api_request(endpoint, method="POST", body=None):
    url = f"https://api.notion.com/v1/{endpoint}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ssl_context) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"Notion API 에러 ({e.code}): {e.reason}")
        print(e.read().decode("utf-8"))
        return None
    except Exception as e:
        print(f"Notion API 연동 오류: {e}")
        return None

def send_discord_message(embed_data):
    if not DISCORD_CHANNEL_ID or not DISCORD_BOT_TOKEN:
        print("디스코드 설정이 부족하여 메시지 전송을 건너뜁니다.")
        return
        
    url = f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    body = {
        "embeds": [embed_data]
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, context=ssl_context) as res:
            print("디스코드 알림 전송 완료!")
    except urllib.error.HTTPError as e:
        print(f"디스코드 API 에러 ({e.code}): {e.reason}")
        print(e.read().decode("utf-8"))
    except Exception as e:
        print(f"디스코드 API 연동 오류: {e}")

def check_duplicate_notion(solver, problem_name):
    """중복 풀이 등록 방지 검사"""
    body = {
        "filter": {
            "and": [
                {
                    "property": "문제 이름",
                    "title": {
                        "equals": problem_name
                    }
                },
                {
                    "property": "해결자",
                    "select": {
                        "equals": solver
                    }
                }
            ]
        }
    }
    res = notion_api_request(f"databases/{NOTION_DATABASE_ID}/query", method="POST", body=body)
    if res and res.get("results"):
        return True
    return False

def add_to_notion(solver, platform, difficulty, problem_name, code_url):
    """노션 데이터베이스에 데이터 등록"""
    body = {
        "parent": { "database_id": NOTION_DATABASE_ID },
        "properties": {
            "문제 이름": {
                "title": [
                    { "text": { "content": problem_name } }
                ]
            },
            "해결자": {
                "select": { "name": solver }
            },
            "난이도": {
                "select": { "name": difficulty }
            },
            "플랫폼": {
                "select": { "name": platform }
            },
            "코드 링크": {
                "url": code_url
            }
        }
    }
    res = notion_api_request("pages", method="POST", body=body)
    return res

def parse_file_path(filepath):
    """
    파일 경로 파싱
    새로운 구조: <플랫폼>/<난이도>/<문제번호. 문제이름>/<스터디원 이름>.<확장자>
    예시: 백준/Gold/1002. 터렛/홍길동.py
    """
    parts = filepath.split('/')
    if len(parts) >= 4:
        platform = parts[0]
        difficulty = parts[1]
        problem_folder = parts[2]
        filename = parts[3]
        
        # 파일 이름에서 스터디원 이름 추출 (예: 홍길동.py -> 홍길동)
        solver = filename.split('.')[0]
        
        # 난이도 매핑 보정 (예: Silver IV -> Silver)
        difficulty_clean = "Bronze"
        for diff in ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ruby"]:
            if diff.lower() in difficulty.lower():
                difficulty_clean = diff
                break
                
        # 플랫폼 매핑 보정
        platform_clean = "백준"
        if "프로그래머스" in platform:
            platform_clean = "프로그래머스"
        elif "leetcode" in platform.lower():
            platform_clean = "리트코드"
            
        return {
            "solver": solver,
            "platform": platform_clean,
            "difficulty": difficulty_clean,
            "problem_name": problem_folder,
        }
    return None

def main():
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        print("노션 설정값(NOTION_API_KEY, NOTION_DATABASE_ID)이 부족합니다.")
        return

    # 변형된 파일 목록 파싱 (GitHub Actions로부터 전달받은 JSON 파싱)
    try:
        files = json.loads(ALL_CHANGED_FILES)
    except json.JSONDecodeError:
        # 공백 구분 문자열일 경우 분할
        files = [f.strip() for f in ALL_CHANGED_FILES.split() if f.strip()]

    print(f"감지된 변경 파일 목록: {files}")

    processed_problems = []

    for filepath in files:
        # 소스코드 파일 형식만 대상 (py, java, cpp, js, ts, go, rb 등)
        if not re.search(r'\.(py|java|cpp|c|h|cs|js|ts|go|rb|swift|kt|rs|py3)$', filepath):
            continue
            
        parsed = parse_file_path(filepath)
        if parsed:
            solver = parsed["solver"]
            platform = parsed["platform"]
            difficulty = parsed["difficulty"]
            problem_name = parsed["problem_name"]
            
            # 중복 체크 키 생성
            dup_key = f"{solver} - {problem_name}"
            if dup_key in processed_problems:
                continue
            processed_problems.append(dup_key)
            
            # 깃허브 코드 URL 생성
            code_url = f"https://github.com/{GITHUB_REPOSITORY}/blob/{GITHUB_SHA}/{filepath}"
            
            # 1. 중복 체크
            if check_duplicate_notion(solver, problem_name):
                print(f"이미 등록된 내역입니다: {solver} - {problem_name}")
                continue
                
            # 2. 노션 등록
            print(f"노션에 문제 등록 시도: {solver} - {problem_name} ({difficulty})")
            notion_res = add_to_notion(solver, platform, difficulty, problem_name, code_url)
            
            if notion_res:
                print("노션 등록 성공!")
                
                # 3. 디스코드 전송
                # 난이도별 색상
                color_map = {
                    "Bronze": 14041630,   # 주황 (Bronze)
                    "Silver": 10066329,   # 은색 (Silver)
                    "Gold": 16298518,     # 노랑 (Gold)
                    "Platinum": 3899119,  # 하늘 (Platinum)
                    "Diamond": 10243572,  # 보라 (Diamond)
                    "Ruby": 14757395      # 루비 (Ruby)
                }
                embed_color = color_map.get(difficulty, 3447003) # 기본 블루
                
                embed_data = {
                    "title": f"🎉 {solver}님이 새로운 문제를 해결했습니다!",
                    "description": f"**[{platform}] {problem_name}**",
                    "color": embed_color,
                    "fields": [
                        {
                            "name": "🔥 난이도",
                            "value": difficulty,
                            "inline": True
                        },
                        {
                            "name": "💻 코드 링크",
                            "value": f"[GitHub에서 보기]({code_url})",
                            "inline": True
                        }
                    ],
                    "timestamp": None
                }
                send_discord_message(embed_data)

if __name__ == "__main__":
    main()
