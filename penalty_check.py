import os
import json
import urllib.request
import urllib.error
import ssl
from datetime import datetime, timedelta, timezone

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

# 주간 목표치 설정 (기본값: 3문제)
WEEKLY_TARGET = int(get_env_or_from_dot_env("WEEKLY_TARGET") or 3)
# 문제당 벌금 설정 (기본값: 1,000원)
FINE_PER_PROBLEM = int(get_env_or_from_dot_env("FINE_PER_PROBLEM") or 1000)

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
        "User-Agent": "DiscordBot (https://github.com/ydh0318/algorithmsstudy, 1.0.0)"
    }
    body = {
        "embeds": [embed_data]
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, context=ssl_context) as res:
            print("디스코드 벌금 알림 전송 완료!")
    except urllib.error.HTTPError as e:
        print(f"디스코드 API 에러 ({e.code}): {e.reason}")
        print(e.read().decode("utf-8"))
    except Exception as e:
        print(f"디스코드 API 연동 오류: {e}")

def get_all_members():
    """노션 DB 스키마를 조회하여 등록된 모든 스터디원 목록(해결자 옵션)을 가져옵니다."""
    res = notion_api_request(f"databases/{NOTION_DATABASE_ID}", method="GET")
    if not res:
        return []
    
    properties = res.get("properties", {})
    solver_prop = properties.get("해결자", {})
    select_info = solver_prop.get("select", {})
    options = select_info.get("options", [])
    
    return [opt["name"] for opt in options]

def get_weekly_solves():
    """지난 7일 동안의 문제 풀이 목록을 조회합니다."""
    # 7일 전 날짜 계산
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    seven_days_ago_iso = seven_days_ago.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    body = {
        "filter": {
            "timestamp": "created_time",
            "created_time": {
                "on_or_after": seven_days_ago_iso
            }
        }
    }
    
    res = notion_api_request(f"databases/{NOTION_DATABASE_ID}/query", method="POST", body=body)
    if not res:
        return []
        
    return res.get("results", [])

def main():
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        print("노션 설정값(NOTION_API_KEY, NOTION_DATABASE_ID)이 부족합니다.")
        return

    # 1. 모든 멤버 조회
    members = get_all_members()
    if not members:
        print("노션 데이터베이스에 등록된 멤버(해결자 옵션)가 아직 없습니다.")
        return
        
    print(f"조회된 스터디 멤버 목록: {members}")

    # 2. 최근 7일간 푼 문제 리스트 조회
    results = get_weekly_solves()
    
    # 3. 멤버별 푼 문제 수 카운팅
    solve_counts = {member: 0 for member in members}
    for page in results:
        properties = page.get("properties", {})
        solver_prop = properties.get("해결자", {})
        select_val = solver_prop.get("select")
        if select_val:
            solver_name = select_val.get("name")
            if solver_name in solve_counts:
                solve_counts[solver_name] += 1
            else:
                # 만약 기존 옵션에 없는 새로운 멤버가 카운트되면 추가
                solve_counts[solver_name] = 1

    print(f"주간 문제 풀이 집계: {solve_counts}")

    # 4. 달성자 및 벌금 대상자 분류
    achievers = []
    penalties = []
    
    for member, count in solve_counts.items():
        if count >= WEEKLY_TARGET:
            achievers.append(f"**{member}**: {count}문제 해결 (목표 달성! 🎉)")
        else:
            missing = WEEKLY_TARGET - count
            fine = missing * FINE_PER_PROBLEM
            penalties.append(
                f"**{member}**: {count}문제 해결 (❌ **{missing}문제 부족** / 벌금 {fine:,}원)"
            )

    # 5. 디스코드 전송 메시지 카드(Embed) 생성
    embed_color = 3066993 if not penalties else 15158332 # 전원 성공 시 초록색, 벌금자 있을 시 빨간색
    
    embed_data = {
        "title": "📊 주간 알고리즘 스터디 풀이 현황 및 벌금 정산",
        "description": f"매주 일요일 저녁 정산 시간! 지난 7일간의 풀이 현황 집계 결과입니다.\n(주간 목표치: **{WEEKLY_TARGET}문제**)",
        "color": embed_color,
        "fields": []
    }
    
    if achievers:
        embed_data["fields"].append({
            "name": "👑 이번 주 목표 달성자",
            "value": "\n".join(achievers),
            "inline": False
        })
    else:
        embed_data["fields"].append({
            "name": "👑 이번 주 목표 달성자",
            "value": "이번 주 달성자가 없습니다. 😢",
            "inline": False
        })
        
    if penalties:
        embed_data["fields"].append({
            "name": "⚠️ 벌금 적립 대상자",
            "value": "\n".join(penalties),
            "inline": False
        })
    else:
        embed_data["fields"].append({
            "name": "🎉 전원 목표 달성 완료!",
            "value": "이번 주는 모두가 목표를 달성했습니다! 다음 주도 파이팅! 🔥",
            "inline": False
        })

    send_discord_message(embed_data)

if __name__ == "__main__":
    main()
