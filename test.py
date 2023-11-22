def test(value,repeat):
    wd = (value-1)%7
    print(wd)
    print([d - wd for d in range(wd, wd+8) if (2**(d%7)) & repeat])

test(1, 1)