import csv

# ========== 参数 ==========
pA = 0.007
pB = 0.007
pO = 0.016
pM = 0.97
MAX_DRAW = 500

# 正常及保底抽卡概率分配
def get_prob(c):
    if c == 99:
        # 100抽小保底：必出三星，50%概率为UP（A和B各25%），50%歪其他
        return {"A":0.25, "B":0.25, "O":0.50, "M":0.0}
    elif c == 199:
        # 200抽大保底：必出UP，A和B各50%
        return {"A":0.50, "B":0.50, "O":0.00, "M":0.0}
    else:
        return {"A":pA, "B":pB, "O":pO, "M":pM}

# 状态初始化
# S0[c] : 无任何UP，水位c
S0 = [0.0]*200
# S1A[c]: 已有A缺B；S1B[c]:已有B缺A
S1A = [0.0]*200
S1B = [0.0]*200
S0[0] = 1.0
T = 0.0  # 已经集齐双角色概率

record = [[0, 0.0]]

for step in range(1, MAX_DRAW+1):
    newS0 = [0.0]*200
    newS1A = [0.0]*200
    newS1B = [0.0]*200
    newT = T

    for c in range(200):
        prob = get_prob(c)
        pA_, pB_, pO_, pM_ = prob["A"], prob["B"], prob["O"], prob["M"]
        stay_miss = pO_ + pM_

        # ===== 状态 1：S0[c] 无任何UP =====
        s0val = S0[c]
        if s0val > 0:
            newS1A[0] += s0val * pA_  # 仅中A -> 进入S1A，水位归零
            newS1B[0] += s0val * pB_  # 仅中B -> 进入S1B，水位归零
            nc = c + 1
            if nc < 200:
                newS0[nc] += s0val * stay_miss  # 没中UP，水位+1

        # ===== 状态 2：S1A[c] 已有A缺B =====
        s1aval = S1A[c]
        if s1aval > 0:
            newT += s1aval * pB_      # 抽到B
            newS1A[0] += s1aval * pA_ # 又抽到A -> 虽重复，但触发UP重置机制，水位归零留在S1A
            nc = c + 1
            if nc < 200:
                newS1A[nc] += s1aval * stay_miss

        # ===== 状态 3：S1B[c] 已有B缺A =====
        s1bval = S1B[c]
        if s1bval > 0:
            newT += s1bval * pA_      # 抽到A
            newS1B[0] += s1bval * pB_ # 又抽到B -> 触发UP重置机制，水位归零留在S1B
            nc = c + 1
            if nc < 200:
                newS1B[nc] += s1bval * stay_miss

    # 更新状态
    S0, S1A, S1B, T = newS0, newS1A, newS1B, newT
    record.append([step, T])
    print(f"{step:3d} |  {T:.6f}")

# 写入CSV
with open("ba_gacha_exact.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["x", "P_new_exact", "P_old_analytic"])
    for x, pn in record:
        if x < 200:
            po = 1 - 2*(0.993**x) + 0.986**x
        elif x < 400:
            po = 1 - 0.986**x
        else:
            po = 1
        w.writerow([x, pn, po])

print("ba_gacha_exact.csv")
