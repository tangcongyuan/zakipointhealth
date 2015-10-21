#!/usr/bin/python
# Ref: http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python/23728630

import string, random
def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

print id_generator(size=9, chars=string.ascii_uppercase + '23456789')
