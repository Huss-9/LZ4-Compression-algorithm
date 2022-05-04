import os
import sys
import time


def saca_string(byte):
    return str(byte)[12:-2]


def list_bytes_to_string(lista):
    res = ""
    for x in lista:
        res += saca_string(x)
    return res

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


def num_to_correct_bytes(num):
    b = hex(num % 256)[2:]
    a = hex(num // 256)[2:]
    b = (2 - len(b)) * "0" + b
    a = (2 - len(a)) * "0" + a
    bajo = bytes.fromhex(b)
    alto = bytes.fromhex(a)
    return [bajo, alto]


def convert_to_block(t1, t2, literals, offset):
    byte_1 = 0
    lisp1 = []
    lisp2 = []
    if t1 >= 15:
        byte_1 = 240
        t1 -= 15
        lisp1 = num_to_bytes(t1)
    else:
        byte_1 = t1 * 16
    if t2 >= 15:
        byte_1 += 15
        t2 -= 15
        lisp2 = num_to_bytes(t2)
    else:
        byte_1 += t2
    block = []
    if offset != -1:
        block += num_to_correct_bytes(offset)
    return [bytes([byte_1])] + lisp1 + literals + block + lisp2


def is_there(entr, i, i_match, offset):
    return entr[i + offset] == entr[i_match + offset]


def filter_far_pos(dic, key, i):
    limit = 2 ** 16
    lista = dic[key][:]
    dic[key] = list(filter(lambda pos: i - pos < limit, lista))  # miralo


def max_match(entr, i, pos, offset):
    n = len(entr)
    while i + offset < n:
        if is_there(entr, i, pos, offset):
            offset += 1
        else:
            return offset
    return offset


def find_best_match(entr, i, dic):
    # ini = entr[i:i + 4]
    key = saca_string(entr[i:i + 4])
    filter_far_pos(dic, key, i)
    new_poses = dic[key]
    if new_poses:
        if new_poses[0] < i:
            i_match = new_poses[0]
            max_length = 4
            for pos in new_poses:
                if pos < i:
                    aux_match = max_match(entr, i, pos, 4)
                    if aux_match > max_length:
                        max_length = aux_match
                        i_match = pos
            # b_match = entr[i_match:i_match + max_length]
            dic[key].append(i)
            if len(dic[key]) >= 1000:
                dic[key].pop(0)
            return i_match, max_length
        else:
            dic[key] = [i]
            return -1, 0
    else:
        dic[key] = [i]
        return -1, 0


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

def high_compressor(entr, nombre, test=False, vers=''):
    n = len(entr)
    literals = []
    list_file = bytearray()
    i = 0
    if n <= 12:
        first_part, _ = get_t1_offset_t2(n, 0, -1)
        list_file += first_part + entr[:n]
    else:
        dic = {}
        i_lit = 0
        while i < n:
            key = saca_string(entr[i:i + 4])
            if not key in dic:
                dic[key] = [i]
                # literals += [entr[i]]
                if i >= n - 5:
                    first_part, _ = get_t1_offset_t2(n - i_lit, 0, -1)
                    list_file += first_part + entr[i_lit:]
                    i = n
                i += 1
            else:
                (pos, len_match) = find_best_match(entr, i, dic)
                if pos == -1:
                    i += 1
                else:
                    # i_safe = i
                    i_lim = i
                    literals_aux = literals[:]
                    best_k = 0
                    i_aux = i
                    for k in range(1, 2):
                        y = i + k
                        # ini = 
                        key_aux = saca_string(entr[y:y + 4])
                        if key_aux in dic:
                            (pos_aux, len_match_aux) = find_best_match(entr, y, dic)
                            if len_match_aux != 0 and pos_aux != -1:
                                if len_match < len_match_aux - k:
                                    best_k = k
                                    # b_match = len_match_aux[:]
                                    len_match = len_match_aux
                                    pos = pos_aux

                    if best_k == 1:
                        i_lim = i_aux + 1
                        # literals.append(entr[i_aux])
                    elif best_k > 1:
                        i_lim = i_aux + best_k
                        # literals += entr[i_aux:i_aux + best_k]
                    if i_aux + len_match < n - 5:
                        hasta = i_aux + len_match
                        i_ini = i_aux + 1
                        while i_ini < hasta:
                            key_aux_2 = saca_string(entr[i_ini:i_ini + 4])
                            if key_aux_2 not in dic:
                                dic[key_aux_2] = [i_ini]
                            else:
                                dic[key_aux_2].append(i_ini)
                                if len(dic[key_aux_2]) >= 1000:
                                    dic[key_aux_2].pop(0)
                            i_ini += 1
                        # t1 = len(literals)
                        t1 = i_lim - i_lit
                        t2 = len_match - 4
                        offset = -1
                        y = i_aux + best_k
                        if y < n:
                            offset = y - pos
                        first_part, second_part = get_t1_offset_t2(t1, t2, offset)
                        list_file += first_part + entr[i_lit:i_lim] + second_part
                        i = y + len_match
                        i_lit = i
                        # literals = []

                    else:
                        # literals = literals_aux + entr[i_aux:]
                        # offset = -1
                        # t1 = len(literals)
                        # t2 = 0
                        # list_file += convert_to_block(t1, t2, literals, offset)
                        # i = n
                        # literals = []
                        first_part, _ = get_t1_offset_t2(n - i_lit, 0, -1)
                        list_file += first_part + entr[i_lit:]
                        i = n
    if test:
        nombre = f'comprimidos/{vers}_{nombre}.lz4'
    else:
        nombre = nombre + ".lz4"
    # print("ratio:", len(entr) / len(list_file))
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
        ini = time.time()
        # with open(name, 'rb') as reader:
        #     byte = reader.read(1)
        #     while byte:
        #         entr.append(byte)
        #         byte = reader.read(1)
        with open(name, 'rb') as reader:
            entr = bytearray(reader.read())
        if comm == "-c":
            high_compressor(entr, name)
        elif comm == "-d":
            decompressor(entr, name)
        end = time.time()
        print(end - ini)
    else:
        print("no hi ha suficients arguments")


if __name__ == "__main__":
    main()
