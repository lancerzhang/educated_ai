def gcd(a, b):
    if b == 0:return a
    return gcd(b, a % b)

print("gcd is:",gcd(1920,1080))

#1920	960	320	80	16
#1080	540	180	45	9
