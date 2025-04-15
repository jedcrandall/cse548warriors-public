import secrets

random = secrets.SystemRandom()

base16alphabet = "QWERTYUIOPLKJHGF"

total = 0
for i in range(9):
    r = random.randint(0,15)
    print(base16alphabet[r], end="")
print()
