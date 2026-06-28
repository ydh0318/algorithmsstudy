"""
내가 가지고 있는 총액에서 물건 값을 뺀 나머지 R을 최소 개수의 동전으로 만들어야 함.
"""
W = int(input())
coins = list(map(int, input().split()))
values = [500, 100, 50, 10, 5, 1]
total = sum(v * c for v, c in zip(values, coins))
R = total - W

ans = 0
ans_list = [0, 0, 0, 0, 0, 0]

for i in range(6):
    # 큰 숫자부터 고려함.
    # 최대로 제외할 수 있는 동전 수 -> 가진 동전개수, 남은 금액 나누기 가치의 min
    exclude = min(coins[i], R // values[i])
    ans_list[i] = coins[i] - exclude
    R -= exclude * values[i]

print(sum(ans_list))
print(*ans_list)
