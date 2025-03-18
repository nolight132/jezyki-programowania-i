def sum_of_proper_divisors(n):
    divisors_sum = 1
    sqrt_n = int(n**0.5)
    for i in range(2, sqrt_n + 1):
        if n % i == 0:
            divisors_sum += i
            if i != n // i:
                divisors_sum += n // i
    return divisors_sum

def find_amicable_numbers_in_range(start, end):
    amicable_numbers = []
    for a in range(start, end + 1):
        b = sum_of_proper_divisors(a)
        if b > a and b <= end:
            if sum_of_proper_divisors(b) == a:
                amicable_numbers.append((a, b))
    return amicable_numbers

start = int(input("Podaj początek zakresu: "))
end = int(input("Podaj koniec zakresu: "))
amicable_numbers = find_amicable_numbers_in_range(start, end)

print("Liczby zaprzyjaźnione w zakresie od", start, "do", end, ":")
for pair in amicable_numbers:
    print(pair)
