import string
import random


def extended_euc(a, b):
    if a == 0:
        return (b, 0, 1)
    gcd, y, x = extended_euc(b % a, a)
    return (gcd, x - (b // a) * y, y)

def mod_inverse(a, mod):
    a = a % mod
    ret = extended_euc(mod, abs(a))[2]
    return (mod + ret) % mod

def secure_randint(min, max, sys_random=None):
        if not sys_random:
            sys_random = random.SystemRandom()
        return sys_random.randint(min, max)

def random_polynomial(degree, intercept, upper_bound):
    coefficients = [secure_randint(0, upper_bound-1) for x in range(degree)]
    coefficients.insert(0, intercept)
    return coefficients

def get_polynomial_points(coefficients, num_points, prime):
    points = []
    for x_coeff in range(1, num_points+1):
        y_coeff = coefficients[0]
        for i in range(1, len(coefficients)):
            exponentiation = (x_coeff**i) % prime
            term = (coefficients[i] * exponentiation) % prime
            y_coeff = (y_coeff + term) % prime
        points.append((x_coeff, y_coeff))
    return points

def modular_lagrange_interpolation(x_coor, points, prime):
    x_values, y_values = zip(*points)
    f_x = 0
    for i in range(len(points)):
        numerator, denominator = 1, 1
        for j in range(len(points)):
            if i == j:
                continue
            numerator = (numerator * (x_coor - x_values[j])) % prime
            denominator = (denominator * (x_values[i] - x_values[j])) % prime
        lagrange_polynomial = numerator * mod_inverse(denominator, prime)
        f_x = (prime + f_x + (y_values[i] * lagrange_polynomial)) % prime
    return f_x

def get_large_enough_prime(batch):
    standard_primes = [
        5, 13, 127, 617, 997, 8191, 131071, 524287, 2147483647, 2305843009213693951,
        618970019642690137449562111, 162259276829213363391578010288127,
        170141183460469231731687303715884105727,
        115792089237316195423570985008687907853269984665640564039457584007913129640233,
        2135987035920910082395021706169552114602704522356652769947041607822219725780640550022962086936603,
        39402006196394479212279040100143613805079739270465446667948293404245721771497210611414266254884915640806627990307047,
        6864797660130609714981900799081393217269435300143305409394463459185543183397656052122559640661454554977296311391480858037121987999716643812574028291115057151,
        531137992816767098689588206552468627329593117727031923199444138200403559860852242739162502265229285668889329486246501015346579337652707239409519978766587351943831270835393219031728127,
        10407932194664399081925240327364085538615262247266704805319112350403608059673360298012239441732324184842421613954281007791383566248323464908139906605677320762924129509389220345773183349661583550472959420547689811211693677147548478866962501384438260291732348885311160828538416585028255604666224831890918801847068222203140521026698435488732958028878050869736186900714720710555703168729087
    ]
    for prime in standard_primes:
        if not [i for i in batch if i >= prime]:
            return prime
    return None

def charset_to_int(s, charset):
    output = 0
    for char in s:
        output = output * len(charset) + charset.index(char)

    return output

def int_to_charset(val, charset):
    #將剛剛charset_to_int的charset.index取出
    if val == 0:
        return charset[0]
    output = ""
    while val > 0:
        val, digit = divmod(val, len(charset))
        output += charset[digit]
    return output[::-1]

def secret_int_to_points(secret_int, point_threshold, num_points, prime=None):
    prime = get_large_enough_prime([secret_int, num_points])
    coefficients = random_polynomial(point_threshold-1, secret_int, prime)
    return get_polynomial_points(coefficients, num_points, prime)

def points_to_secret_int(points, prime=None):
    _, y_values = zip(*points)
    if not prime:
        prime = get_large_enough_prime(y_values)
    return modular_lagrange_interpolation(0, points, prime)

def point_to_share_string(point, charset):
    x_val, y_val = point
    x_string = int_to_charset(x_val, charset)
    y_string = int_to_charset(y_val, charset)
    return "%s-%s" % (x_string, y_string)

def share_string_to_point(share_string, charset):
    x_string, y_string = share_string.split('-')
    x_val = charset_to_int(x_string, charset)
    y_val = charset_to_int(y_string, charset)
    return (x_val, y_val)

class SecretSharer():
    secret_charset = string.hexdigits[0:17][::-1]
    share_charset = string.hexdigits[0:17][::-1]

    def __init__(self):
        pass

    @classmethod
    def split_secret(cls, secret_string, share_threshold, num_shares):
        secret_int = charset_to_int(secret_string, cls.secret_charset)
        points = secret_int_to_points(secret_int, share_threshold, num_shares)
        shares = []
        for point in points:
            shares.append(point_to_share_string(point, cls.share_charset))
        return shares

    @classmethod
    def recover_secret(cls, shares):
        points = []
        for share in shares:
            points.append(share_string_to_point(share, cls.share_charset))
        secret_int = points_to_secret_int(points)
        return int_to_charset(secret_int, cls.secret_charset)

class HexToHexSecretSharer(SecretSharer):
    secret_charset = string.hexdigits[0:17][::-1]
    share_charset = string.hexdigits[0:17][::-1]

class PlaintextToHexSecretSharer(SecretSharer):
    secret_charset = string.printable[::-1]
    share_charset = string.hexdigits[0:17][::-1]