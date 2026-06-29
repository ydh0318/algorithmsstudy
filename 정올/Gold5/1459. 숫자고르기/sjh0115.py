# JUNGOL 1459 숫자고르기
# 티어: gold
# 분류: dfs, graph, cycle
# 핵심:
#   각 숫자 i에서 numbers[i]로 가는 함수형 그래프로 보고,
#   사이클에 포함되는 정점들을 정답으로 고른다.
# 시간 복잡도: O(N)
# 공간 복잡도: O(N)


# 1. 문제 이해
# - 입력:
#   N: 숫자의 개수
#   numbers[i]: i번 위칸 숫자 아래에 적힌 숫자
# - 출력:
#   첫 줄: 고른 숫자의 개수
#   이후 줄: 고른 숫자를 오름차순으로 한 줄에 하나씩 출력
# - 구해야 하는 것:
#   선택한 위칸 숫자 집합과 그 아래칸 숫자 집합이 같아지는 최대 집합


# 2. 아이디어
# - TODO: 어떤 규칙이 있는가?
# - TODO: 어떤 값을 상태로 둘 것인가?
# - TODO: 완전 탐색 / DFS / 그래프 / 자료구조 중 어떤 방식이 어울리는가?


# 3. 구현 계획
# 1)
# 2)
# 3)


def solution(N, numbers):
    # TODO: 문제 해결 로직 작성
    # return answer
    pass


if __name__ == "__main__":
    N = int(input())
    numbers = [0]

    for _ in range(N):
        numbers.append(int(input()))

    answer = solution(N, numbers)

    # TODO: 정답 출력 형식에 맞게 수정
    # print(len(answer))
    # for number in answer:
    #     print(number)
