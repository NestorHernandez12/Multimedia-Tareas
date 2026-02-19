import struct
import math

def leer_bmp(filepath):
    """Retorna (header_bytes, pixels, width, height, row_size)"""
    with open(filepath, 'rb') as f:
        data = f.read()
        offset = struct.unpack_from('<I', data, 10)[0]
        width  = struct.unpack_from('<i', data, 18)[0]
        height = struct.unpack_from('<i', data, 22)[0]
        row_size = (width * 3 + 3) & ~3
        header = bytearray(data[:offset])
        pixels = bytearray(data[offset:])
        return header, pixels, width, height, row_size


def guardar_bmp(filepath, header, pixels):
    with open(filepath, 'wb') as f:
        f.write(header)
        f.write(pixels)


def embed_lsb(src_path, dst_path, mensaje):
    header, pixels, width, height, row_size = leer_bmp(src_path)

    msg_bytes = mensaje.encode('utf-8')
    msg_len   = len(msg_bytes)

    datos = struct.pack('>I', msg_len) + msg_bytes
    bits  = []

    for byte in datos:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    if len(bits) > len(pixels):
        raise ValueError('Mensaje demasiado largo para esta imagen')

    pixels_mod = bytearray(pixels)

    for idx, bit in enumerate(bits):
        pixels_mod[idx] = (pixels_mod[idx] & 0xFE) | bit

    guardar_bmp(dst_path, header, pixels_mod)
    print(f'[OK] Mensaje de {msg_len} bytes incrustado en {dst_path}')


def extract_lsb(stego_path):
    _, pixels, _, _, _ = leer_bmp(stego_path)

    len_bits = [pixels[i] & 1 for i in range(32)]
    msg_len  = 0

    for b in len_bits:
        msg_len = (msg_len << 1) | b

    total_bits = 32 + msg_len * 8
    msg_bits   = [pixels[i] & 1 for i in range(32, total_bits)]

    msg_bytes = bytearray()

    for i in range(0, len(msg_bits), 8):
        byte = 0
        for bit in msg_bits[i:i+8]:
            byte = (byte << 1) | bit
        msg_bytes.append(byte)

    return msg_bytes.decode('utf-8')


def calcular_psnr(original_path, stego_path):
    _, pix_orig, w, h, _ = leer_bmp(original_path)
    _, pix_steg, _, _, _ = leer_bmp(stego_path)

    mse = sum((a - b)**2 for a, b in zip(pix_orig, pix_steg)) / (w * h * 3)

    if mse == 0:
        return float('inf')

    psnr = 10 * math.log10(255**2 / mse)

    print(f'MSE:  {mse:.6f}')
    print(f'PSNR: {psnr:.2f} dB  (>40 dB: cambio imperceptible)')

    return psnr


# --- PRUEBA ---
embed_lsb('imagen.bmp', 'stego.bmp', 'TELEMÁTICA SECRETA 2025')

recuperado = extract_lsb('stego.bmp')
print(f'Mensaje recuperado: {recuperado}')

assert recuperado == 'TELEMÁTICA SECRETA 2025', '¡Error en la extracción!'
print('Prueba exitosa.')

calcular_psnr('imagen.bmp', 'stego.bmp')