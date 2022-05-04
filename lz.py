import os
import sys
import time


def saca_string(byte):
    return str(byte)[12:-2]


# def list_bytes_to_string(lista):
#     res = ""
#     for x in lista:
#         res += saca_string(x)
#     return res


def saca_t1_t2(st):
    return st // 16, st % 16


def byte_to_int(st):
    return int.from_bytes(st, "big")


def LISC(entr, i):
    e = 0
    y = i
    val = entr[y]
    while val == 255:
        e += val
        y += 1
        val = entr[y]
    e += val
    return e, y


def num_to_bytes(t):
    count = t // 255
    l = count * [bytes([255])]
    l.append(bytes([t % 255]))
    return l


def number_of_bytes(t):
    count = t // 255
    if count % 255 != 0:
        count += 1
    return count


def num_to_list_ints(t, t_vals):
    count = t // 255
    t_vals += count * [255]
    t_vals.append(t % 255)


def get_t1_offset_t2(t1, t2, offset):
    t1_vals = []
    t2_vals = []
    if offset != -1:
        t2_vals.append(offset % 256)
        t2_vals.append(offset // 256)

    if t1 >= 15:
        t1_vals.append(240)
        t1 -= 15
        num_to_list_ints(t1, t1_vals)
    else:
        t1_vals.append(t1 * 16)

    if t2 >= 15:
        t1_vals[0] += 15
        t2 -= 15
        num_to_list_ints(t2, t2_vals)
    else:
        t1_vals[0] += t2
    return bytearray(t1_vals), bytearray(t2_vals)


def is_there(entr, i, i_match, offset):
    ara = i + offset
    ant = i_match + offset
    return entr[ara:ara + 1] == entr[ant:ant + 1]


def max_match(entr, i, pos, offset):
    n = len(entr)
    while i + offset < n:
        if is_there(entr, i, pos, offset):
            offset += 1
        else:
            return offset
    return offset

# def max_match(entr, i, pos, offset):
#     n = len(entr)
#     while i + offset < n:
#         ara = i + offset
#         ant = pos + offset
#         if entr[ara:ara + 1] == entr[ant:ant + 1]:
#             # ara += 1
#             # ant += 1
#             offset += 1
#         else:
#             return offset
#     return offset


def find_best_match(entr, i, dic):
    key = saca_string(entr[i:i + 4])
    pos = dic[key]
    if i - pos < 2 ** 16:
        i_match = pos
        len_match = max_match(entr, i, pos, 4)
        dic[key] = i
        return i_match, len_match
    else:
        dic[key] = i
        return -1, 0


def normal_compressor(entr, nombre, test=False, vers = ''):
    n = len(entr)
    list_file = bytearray()
    if n <= 12:
        first_part, _ = get_t1_offset_t2(n, 0, -1)
        list_file += first_part + entr[:n]
    else:
        dic = {}
        i_lit = 0
        i = 0
        max_bytes = n / 1.11
        stop_out = False
        while i < n and not stop_out:
            key = saca_string(entr[i:i+4])
            extra = number_of_bytes(n - i) + 1
            if len(list_file) + (n - i) + extra >= max_bytes:
                if not key in dic.keys():
                    dic[key] = i
                    if i >= n - 5:
                        first_part, _ = get_t1_offset_t2(n - i_lit, 0, -1)
                        list_file += first_part + entr[i_lit:]
                        i = n
                    i += 1
                else:
                    pos, len_match = find_best_match(entr, i, dic)
                    if pos == -1:
                        i += 1
                    else:
                        if i + len_match < n - 5:
                            i_fin = i + len_match
                            i_ini = i + 1
                            while i_ini < i_fin:
                                key = saca_string(entr[i_ini:i_ini + 4])
                                dic[key] = i_ini
                                i_ini += 1
                            t1 = i - i_lit
                            t2 = len_match - 4
                            offset = i - pos
                            first_part, second_part = get_t1_offset_t2(t1, t2, offset)
                            list_file += first_part + entr[i_lit:i] + second_part
                            i = i + len_match
                            i_lit = i

                        else:
                            first_part, _ = get_t1_offset_t2(n - i_lit, 0, -1)
                            list_file += first_part + entr[i_lit:]
                            i = n
            else:
                first_part, _ = get_t1_offset_t2(n - i_lit, 0, -1)
                list_file += first_part + entr[i_lit:]
                stop_out = True

    if test:
        nombre = "comprimidos/" + vers + "_" + nombre + ".lz4"
    else:
        nombre = nombre + ".lz4"
    if os.path.isfile(nombre):
        os.remove(nombre)
    with open(nombre, "ab") as file:
        file.write(list_file)


def decompressor(entr, nombre, test=False):
    n = len(entr)
    lista_file = bytearray()
    i = 0
    while i < n:
        b = entr[i]
        # print(saca_string(lista_file))
        # treiem t1, t2 del token
        (t1, t2) = saca_t1_t2(b)
        i += 1
        # si t1 == 15, fem LISC per tenir un valor valid
        if t1 == 15:
            (e1, y) = LISC(entr, i)
            t1 += e1
            i = y + 1
        # Copiem els t1 literals
        lista_file += entr[i:i + t1]
        i += t1
        # comprovem que no estem en el ultim bloc, es a dir, que hi ha més bytes per tractar
        if i < n - 2:
            # llegim el offset
            Offset = entr[i + 1] * (2 ** 8) + entr[i]
            i += 2
            # si t1 == 15, fem LISC per tenir un valor valid
            if t2 == 15:
                (e2, y) = LISC(entr, i)
                t2 += e2
                i = y + 1
            t2 += 4
            # copiem els t2 bytes començant desde offset
            c_ini = len(lista_file) - Offset
            c_fin = min(len(lista_file), c_ini + t2)
            lista_file += lista_file[c_ini:c_fin]

            # tractem si hi ha overlap
            t2 -= Offset
            while t2 > Offset:
                lista_file += lista_file[-Offset:]
                t2 -= Offset
            if t2 > 0:
                c_ini = len(lista_file) - Offset
                c_fin = min(len(lista_file), c_ini + t2)
                lista_file += lista_file[c_ini:c_fin]
    if test:
        nombre = "descomprimidos/" + nombre[:-4]
    else:
        nombre = nombre[:-4]
    if os.path.isfile(nombre):
        os.remove(nombre)
    with open(nombre, "ab") as file:
        file.write(lista_file)


def main():
    inp = []
    for x in sys.argv:
        inp.append(str(x))
    if len(inp) > 2:
        comm = inp[1]
        name = inp[2]
        entr = []
        # ini = time.time()
        with open(name, 'rb') as reader:
            entr = bytearray(reader.read())
        if comm == "-c":
            normal_compressor(entr, name)
        elif comm == "-d":
            decompressor(entr, name)
        # end = time.time()
        # print(end-ini)
    else:
        print("no hi ha suficients arguments")


if __name__ == "__main__":
    main()
