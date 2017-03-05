#nie mam jak sprawdzić czy działa

import quick2wire.i2c as i2c

i2c_bus=i2c.I2CMaster(0)
address=0x68 # adres, nie jestem pewien

def switch (n):
    return {
        'forward' : ox00,
        'turn'    : ox10,
        'rotate'  : ox11,
    }[n]

def send (command, arg):
    instruction = switch(command) * (2 ** 10) + arg #złożenie instrukcji, 2 najstarsze bity to rozkaz, a kolejne to argument
    i2c_bus.transaction(i2c.writing_bytes(address, instruction)) # wysłanie przez I2C
