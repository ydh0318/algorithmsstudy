# JUNGOL 1183 동전 자판기
# 난이도: gold
# 분류: greedy
# 핵심:
#   물건을 살 때 사용하는 동전 개수를 최대화해야 한다.
#   직접 사용할 동전을 고르기보다, 전체 동전에서 물건값 W를 뺀 금액을
#   가장 적은 개수의 동전으로 남기는 문제로 바꾼다.
# 시간 복잡도: O(1)
# 공간 복잡도: O(1)


# 1. 문제 이해
# - 입력:
#   W: 자판기에서 구입하려는 물건의 가격
#   have_money: 500, 100, 50, 10, 5, 1원 동전의 개수
# - 출력:
#   첫 줄: 물건 구입에 사용할 수 있는 최대 동전 개수
#   둘째 줄: 500, 100, 50, 10, 5, 1원 동전별 사용 개수
# - 구해야 하는 것:
#   W원을 만들면서 사용하는 동전 개수를 최대화하는 동전 구성


# 2. 아이디어
# - 전체 동전 가치 합을 total_money라고 한다.
# - 물건값 W를 사용하면 남는 금액은 total_money - W이다.
# - 사용하는 동전 개수를 최대화하는 것은 남기는 동전 개수를 최소화하는 것과 같다.
# - 남길 금액 total_money - W를 큰 동전부터 최대한 남기면 남는 동전 개수가 최소가 된다.
# - 사용한 개수 = 가지고 있던 개수 - 남긴 개수


# 3. 풀이 계획
# 1) 가지고 있는 모든 동전의 총액 total_money를 구한다.
# 2) 남겨야 하는 금액 remain_money = total_money - W를 구한다.
# 3) 큰 동전부터 가능한 만큼 남긴다.
# 4) 각 동전별 사용 개수를 계산한다.
# 5) 총 사용 개수와 동전별 사용 개수를 반환한다.


def solution(W, have_money):
    coins = [500, 100, 50, 10, 5, 1]

    total_money = 0

    for i in range(6):
        total_money += have_money[i] * coins[i]

    remain_money = total_money - W

    # remain_count[i] = i번째 동전 중 사용하지 않고 남길 개수
    remain_count = [0] * 6

    for i in range(6):
        coin = coins[i]

        count = min(have_money[i], remain_money // coin)
        remain_count[i] = count
        remain_money -= coin * count

    used_count = []

    for i in range(6):
        used_count.append(have_money[i] - remain_count[i])

    return sum(used_count), used_count


if __name__ == "__main__":
    W = int(input())
    have_money = list(map(int, input().split()))

    total_count, used_count = solution(W, have_money)

    print(total_count)
    print(*used_count)
