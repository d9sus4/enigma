## Enigma 密码破译（图灵已知明文的攻击方法）

### 代码说明

Python3 下开发，使用状态机模式实现了一个 Enigma 的仿真类 `Enigma` 并实现了破译的相关算法。运行 `main.py` 即可顺序执行后文内容并输出破译结果。更多细节详见代码。

### 找到循环圈

已知明文 (x) - 密文 (y) 对：

| i    | 0    | 1    | 2    | 3    | 4    | 5    | 6    | 7    | 8    | 9    | 10   | 11   | 12   | 13   | 14   | 15   | 16   |
| ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| x    | B    | H    | U    | I    | L    | O    | P    | A    | L    | O    | P    | B    | J    | X    | F    | C    | E    |
| y    | P    | B    | D    | P    | P    | X    | J    | O    | M    | E    | X    | L    | F    | O    | L    | G    | A    |

圈的定义：定义变换 $A_i(x) = y$，自然地 $A_i^{-1}(y) = x$。比如，依次使用变换 i = 0、4、11，有 B-P-L-B，那么 $A_{11}A_4^{-1}A_0$ 就是从 B 出发、回到 B 的一个圈 (cycle)。

编写程序找出所有的圈：

#### 算法原理

简单的递归遍历，找出所有圈。注意为了避免死循环，规定同一个 i 不能在同一个圈中出现两次。由于 $P_i$ 一定自反，$P_i$ 和 $P_i^{-1}$ 其实没有区别，二者都可以用角标 i 简单表示。

```python
def find_next(x: str, y: str, current: str, target: str, history: set):
    all = []
    for i in range(len(x)):
        if x[i] == current and i not in history:
            if y[i] == target:
                all.append([i])
            else:
                new_history = history.copy()
                new_history.add(i)
                res = find_next(x, y, y[i], target, new_history)
                for item in res:
                    new_item = [i]
                    new_item.extend(item.copy())
                    all.append(new_item)
        elif y[i] == current and i not in history:
            if x[i] == target:
                all.append([i])
            else:
                new_history = history.copy()
                new_history.add(i)
                res = find_next(x, y, x[i], target, new_history)
                for item in res:
                    new_item = [i]
                    new_item.extend(item.copy())
                    all.append(new_item)
    return all
 

def find_cycles(x: str, y: str):
    all = {}
    for i in range(len(x)):
        res = find_next(x, y, y[i], x[i], set([i]))
        for item in res:
            cycle = [i]
            cycle.extend(item.copy())
            if x[i] not in all.keys():
                all[x[i]] = [cycle]
            else:
                all[x[i]].append(cycle)
        res = find_next(x, y, x[i], y[i], set([i]))
        for item in res:
            cycle = [i]
            cycle.extend(item.copy())
            if y[i] not in all.keys():
                all[y[i]] = [cycle]
            else:
                all[y[i]].append(cycle)
    return all
```

#### 运行结果

调用 ```find_cycles('bhuilopalopbjxfce', 'pbdppxjomexlfolga')``` 可得：

```
all found cycles are: {'b': [[0, 4, 11], [0, 6, 12, 14, 11], [11, 4, 0], [11, 14, 12, 6, 0]], 'p': [[0, 11, 4], [0, 11, 14, 12, 6], [4, 11, 0], [4, 14, 12, 6], [6, 12, 14, 4], [6, 12, 14, 11, 0]], 'l': [[4, 0, 11], [4, 6, 12, 14], [11, 0, 4], [11, 0, 6, 12, 14], [14, 12, 6, 0, 11], [14, 12, 6, 4]], 'o': [[5, 13], [7, 16, 9], [9, 16, 7], [13, 5]], 'x': [[5, 7, 16, 9, 13], [5, 9, 16, 7, 13], [5, 13], [13, 5], [13, 7, 16, 9, 5], [13, 9, 16, 7, 5]], 'j': [[6, 0, 11, 14, 12], [6, 4, 14, 12], [12, 14, 4, 6], [12, 14, 11, 0, 6]], 'a': [[7, 5, 13, 9, 16], [7, 9, 16], [7, 13, 5, 9, 16], [16, 9, 5, 13, 7], [16, 9, 7], [16, 9, 13, 5, 7]], 'e': [[9, 5, 13, 7, 16], [9, 7, 16], [9, 13, 5, 7, 16], [16, 7, 5, 13, 9], [16, 7, 9], [16, 7, 13, 5, 9]], 'f': [[12, 6, 0, 11, 14], [12, 6, 4, 14], [14, 4, 6, 12], [14, 11, 0, 6, 12]]}
```

### 破译

图灵方法的核心思想：Enigma 的每次点击事件的加密过程可以描述为 $y = Ax=S^{-1}PSx$，其中 S 是 plugboard 引起的变换，P是 rotor 和 reflector 引起的变换。

对于某个环 $x = A_{i_n}\dots A_{i_2}A_{i_1}x = S^{-1}P_{i_n}S\dots S^{-1}P_{i_2}S\cdot S^{-1}P_{i_1}Sx=S^{-1}P_{i_n}\dots P_{i_2}P_{i_1}Sx$，由于 S 的未知性，将上式变形为：
$$
Sx=P_{i_n}\dots P_{i_2}P_{i_1}Sx
$$
接下来只需要穷举 $P_0$，各 $P_i$ 便已知，再猜测 $Sx$ 的值即可。可能的密钥空间里的密钥满足：对于所有字母的环，存在一组 S 乘上各字母的猜测值，让上式总成立。

#### 算法原理

由于 init position 已知为 AAA，只需要枚举 rotor 选择（共 6 种排列）和 ring setting（共 $26^3$ 种）。

```python
for p in itertools.permutations([0, 1, 2], 3):
    rotors = [rotor[p[0]], rotor[p[1]], rotor[p[2]]]
    notches = [notch[p[0]], notch[p[1]], notch[p[2]]]

    for ring_settings in itertools.product(alphabet, alphabet, alphabet):
        enigma = Enigma(reflector, rotors, notches, ring_settings, known_init_settings)
        subs_list = test(enigma, cycles.copy(), {})
        if len(subs_list) > 0:
            possible_keys.append((p, ring_settings, subs_list))
```

`test` 方法就是依序猜测各成环字母经过 plugboard 后的值，如果能猜到底，各自不冲突，且让所有的环都成立，则认为该密钥是可能的，同时这些猜测值一定是实际 plugboard 的子集。

#### 运行结果

```
start cracking...
5000 combinations tested, found 0 possible keys. rate of progress: 4.74%
10000 combinations tested, found 0 possible keys. rate of progress: 9.48%
15000 combinations tested, found 0 possible keys. rate of progress: 14.22%
20000 combinations tested, found 0 possible keys. rate of progress: 18.97%
25000 combinations tested, found 2 possible keys. rate of progress: 23.71%
30000 combinations tested, found 2 possible keys. rate of progress: 28.45%
35000 combinations tested, found 2 possible keys. rate of progress: 33.19%
40000 combinations tested, found 2 possible keys. rate of progress: 37.93%
45000 combinations tested, found 2 possible keys. rate of progress: 42.67%
50000 combinations tested, found 2 possible keys. rate of progress: 47.41%
55000 combinations tested, found 2 possible keys. rate of progress: 52.15%
60000 combinations tested, found 2 possible keys. rate of progress: 56.90%
65000 combinations tested, found 2 possible keys. rate of progress: 61.64%
70000 combinations tested, found 2 possible keys. rate of progress: 66.38%
75000 combinations tested, found 2 possible keys. rate of progress: 71.12%
80000 combinations tested, found 2 possible keys. rate of progress: 75.86%
85000 combinations tested, found 2 possible keys. rate of progress: 80.60%
90000 combinations tested, found 2 possible keys. rate of progress: 85.34%
95000 combinations tested, found 2 possible keys. rate of progress: 90.08%
100000 combinations tested, found 2 possible keys. rate of progress: 94.83%
105000 combinations tested, found 2 possible keys. rate of progress: 99.57%
all possible keys are: [((0, 2, 1), ('g', 'y', 'e'), [{'f': 'i', 'i': 'f', 'e': 'e', 'a': 'a', 'j': 'j', 'x': 'x', 'o': 'k', 'k': 'o', 'l': 'l', 'p': 'y', 'y': 'p', 'b': 'w', 'w': 'b'}]), ((0, 2, 1), ('h', 'l', 'l'), [{'f': 'd', 'd': 'f', 'e': 'k', 'k': 'e', 'a': 'r', 'r': 'a', 'j': 'n', 'n': 'j', 'x': 'c', 'c': 'x', 'o': 'o', 'l': 'q', 'q': 'l', 'p': 'w', 'w': 'p', 'b': 'y', 'y': 'b'}])]
```

可以看到成功找出了 GYE 和另一个可能的密钥 HLL。接下来尝试选出最可能的那个解。

### 选择最优解及尝试还原 plugboard

最简单的思想是：用求得的各密钥（以及 plugboard 的子集），尝试破译密文，拿得到的译文与原文计算相似度，选择最相似的那个。

| 原文        | BHUIL OPALO PBJXF CE | 相同位数 |
| ----------- | -------------------- | -------- |
| 译文1 (GYE) | BHQIL OPALO OBJXF CE | 16       |
| 译文2 (HLL) | BOMML OPADO PBJXF JE | 12       |

故 GYE 是最可能的密钥。同时得到了 plugboard 至少连接了：F/I，O/K，P/Y，B/W。

观察可以发现，在上述 plugboard 解密后的第三位 Q，原文中实际上是 U，怀疑 Q/U 也是一对连接。由此还原出 plugboard：Q/U，F/I，O/K，P/Y，B/W。

事实上，这是运气比较好的情况，信息刚好足够还原出正确的密钥和 plugboard。实际应用中，也许需要更多已知的明文 - 密文对才能还原全部的 plugboard 信息。
