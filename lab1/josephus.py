def josephus_simulation(n, k):
    soldiers = list(range(1, n + 1))
    index = 0
    while len(soldiers) > 1:
        index = (index + k - 1) % len(soldiers)
        soldiers.pop(index)
    return soldiers[0]

n = int(input("Podaj liczbę żołnierzy: "))
k = 2
safe_position = josephus_simulation(n, k)
print("Bezpieczna pozycja:", safe_position)
