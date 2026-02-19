import hashlib
import struct
import random

# ======================================================
# BMP CORRECTO (CON PADDING)
# ======================================================

def leer_bmp(filepath):
    with open(filepath, 'rb') as f:
        header = f.read(54)

        width  = struct.unpack('<I', header[18:22])[0]
        height = struct.unpack('<I', header[22:26])[0]

        row_size = (width * 3 + 3) & ~3

        pixel_data = bytearray()

        for _ in range(height):
            row = f.read(row_size)
            pixel_data.extend(row)

    return header, pixel_data, row_size, height


def guardar_bmp(filepath, header, pixel_data):
    with open(filepath, 'wb') as f:
        f.write(header)
        f.write(pixel_data)

# ======================================================
# CIFRADO XOR
# ======================================================

def derivar_clave(password, longitud):
    clave = b''
    contador = 0
    while len(clave) < longitud:
        bloque = hashlib.sha256(password.encode() + struct.pack('<I', contador)).digest()
        clave += bloque
        contador += 1
    return clave[:longitud]


def cifrar_xor(mensaje, password):
    clave = derivar_clave(password, len(mensaje))
    return bytes(m ^ k for m, k in zip(mensaje, clave))


def descifrar_xor(cifrado, password):
    return cifrar_xor(cifrado, password)

# ======================================================
# POSICIONES
# ======================================================

def generar_posiciones(total, seed):
    rng = random.Random(seed)
    posiciones = list(range(total))
    rng.shuffle(posiciones)
    return posiciones


def semilla_de_password(password):
    hash_bytes = hashlib.sha256(password.encode()).digest()
    return int.from_bytes(hash_bytes[:8], 'big')

# ======================================================
# EMBED
# ======================================================

def embed_secure(src, dst, mensaje, password):

    header, pixel_data, row_size, height = leer_bmp(src)

    msg_bytes = mensaje.encode()
    msg_cifrado = cifrar_xor(msg_bytes, password)

    datos = struct.pack('<I', len(msg_bytes)) + msg_cifrado

    bits = []
    for byte in datos:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    seed = semilla_de_password(password)
    posiciones = generar_posiciones(len(pixel_data), seed)

    pixel_mod = bytearray(pixel_data)

    for pos, bit in zip(posiciones, bits):
        pixel_mod[pos] = (pixel_mod[pos] & 0xFE) | bit

    guardar_bmp(dst, header, pixel_mod)

    print("[OK] Mensaje incrustado correctamente")

# ======================================================
# EXTRACT
# ======================================================

def extract_secure(stego, password):

    _, pixel_data, _, _ = leer_bmp(stego)

    seed = semilla_de_password(password)
    posiciones = generar_posiciones(len(pixel_data), seed)

    # longitud
    len_bits = [pixel_data[posiciones[i]] & 1 for i in range(32)]

    msg_len = 0
    for b in len_bits:
        msg_len = (msg_len << 1) | b

    # VALIDACIÓN REAL
    if msg_len <= 0 or msg_len > len(pixel_data)//8:
        raise ValueError("Clave incorrecta o mensaje corrupto")

    # mensaje
    msg_bits = [pixel_data[posiciones[i]] & 1 for i in range(32, 32 + msg_len*8)]

    cifrado = bytearray()
    for i in range(0, len(msg_bits), 8):
        byte = 0
        for bit in msg_bits[i:i+8]:
            byte = (byte << 1) | bit
        cifrado.append(byte)

    return descifrar_xor(bytes(cifrado), password).decode()

# ======================================================
# CHI CUADRADO
# ======================================================

def chi_cuadrado_lsb(filepath):

    _, pixel_data, _, _ = leer_bmp(filepath)

    ceros = sum(1 for b in pixel_data if (b & 1) == 0)
    unos  = len(pixel_data) - ceros

    esperado = len(pixel_data)/2

    chi2 = ((ceros-esperado)**2 + (unos-esperado)**2)/esperado

    print("χ² =", chi2)
    return chi2

# ======================================================
# PRUEBA
# ======================================================

CLAVE = "Telematica@2025"
MENSAJE = "Datos confidenciales de la red 10.0.1.0/24"

IMAGEN = "Imagenes/volcan.bmp"
STEGO  = "stego_seguro.bmp"

embed_secure(IMAGEN, STEGO, MENSAJE, CLAVE)

resultado = extract_secure(STEGO, CLAVE)
print("Clave correcta:", resultado)

try:
    basura = extract_secure(STEGO, "claveWrong")
    print("Clave incorrecta:", basura[:30])
except:
    print("Clave incorrecta → no legible")

print("\nChi-cuadrado original:")
chi_cuadrado_lsb(IMAGEN)

print("Chi-cuadrado stego:")
chi_cuadrado_lsb(STEGO)

