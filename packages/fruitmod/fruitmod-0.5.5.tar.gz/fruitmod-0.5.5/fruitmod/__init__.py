def sib(n):
    x=1
    for i in range(1,n+1):
        x=x*i
    return x

def golabi(a,b):
    m=0
    for i in range(a,b+1):
        m+=i
    return m

def tameshk(a,b):
    x=a
    if b>a:
        x=b
    return x

def porteghal(n):
    while n**0.5%1!=0:
        n-=1
    return n

def talebi(n):
    t=0
    while n!=0:
        t+=1
        n//=10
    return t

def havij(n):
    m=0
    while n!=0:
        m=m*10+n%10
        n//=10
    return m

def kivi(n):
    m=0
    for i in range(1,n):
        if n%i==0:
            m+=1
    if m==n:
        j='yes'
    else:
        j='no'
    return j

def khiar(n):
    j="yes"
    for i in range(2,n):
        if n%i==0:
            j="no"
    return j

def holoo(a,b):
    i=a
    while a%i!=0 or b%i!=0:
        i-=1
    return i

def ananas(n):
    a=0
    b=1
    for i in range(n):
        t=a+b
        a=b
        b=t
    return a

def aloo(n,a):
    t=0
    while n!=0:
        if n%10==a:
            t=+t
        n//= 10
    return t

def moz(n):
    t=0
    for i in range(1,n+1):
            if n%i == 0:
                t+=1
    return t

def anar(n):
    if n <0:
        n = -n
    return n

def angoor(n):
    while n!=0:
        print(n%10)
        n//=10
    return

def albaloo(a,b):
    for i in range(a,b+1):
        print(i)
    return

factorail = sib
sum = golabi
compair = tameshk
Perfect_Square = porteghal
sum_digits = talebi
reverse = havij
perfect = kivi
is_prime = khiar
gcd = holoo
fibonacci = ananas
count_digit = aloo
count_divisor = moz
absolute = anar
print_reverse = angoor
print_atob = albaloo
