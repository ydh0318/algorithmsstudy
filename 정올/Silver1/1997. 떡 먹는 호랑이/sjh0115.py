# JUNGOL 1997 떡 먹는 호랑이
# 분류: dp, brute_force, fibonacci
# 핵심:
#   첫째 날 떡 개수를 A, 둘째 날 떡 개수를 B라고 두면
#   D일째 떡 개수는 x*A + y*B 형태로 표현할 수 있다.
#   x, y는 피보나치처럼 계수만 따로 구한다.
# 시간 복잡도: O(D + K)
# 공간 복잡도: O(D)


# 1. 문제 이해
# - 입력:
#   D: 할머니가 호랑이를 만난 날, 3 <= D <= 30
#   K: D일째에 호랑이에게 준 떡의 개수, 10 <= K <= 100000
# - 출력:
#   첫째 날 준 떡의 개수 A
#   둘째 날 준 떡의 개수 B
# - 조건:
#   A와 B는 자연수이고, 보통 A <= B인 답을 찾는다.


# 2. 아이디어
# - 1일째: A = 1*A + 0*B
# - 2일째: B = 0*A + 1*B
# - 3일째부터는 전날 + 전전날이다.
# - 따라서 A의 계수와 B의 계수도 피보나치처럼 더해진다.
# - D일째 계수를 x, y라고 하면 x*A + y*B = K이다.
# - A를 1부터 확인하면서 B가 자연수로 나오는 값을 찾는다.


# 3. 풀이 계획
# 1) D일째의 A 계수 x, B 계수 y를 구한다.
# 2) A를 1부터 하나씩 넣어본다.
# 3) K - x*A가 y로 나누어떨어지면 B를 구한다.
# 4) A, B를 반환한다.


def solution(D, K):
    a_coef = [0] * (D + 1)
    b_coef = [0] * (D + 1)

    a_coef[1] = 1
    b_coef[1] = 0
    a_coef[2] = 0
    b_coef[2] = 1

    for day in range(3, D + 1):
        a_coef[day] = a_coef[day - 1] + a_coef[day - 2]
        b_coef[day] = b_coef[day - 1] + b_coef[day - 2]

    x = a_coef[D]
    y = b_coef[D]

    for A in range(1, K + 1):
        remain = K - x * A

        if remain <= 0:
            break

        if remain % y == 0:
            B = remain // y

            if A <= B:
                return A, B

    return None


# 정올 제출용 실행부
if __name__ == "__main__":
    D, K = map(int, input().split())
    A, B = solution(D, K)

    print(A)
    print(B)
