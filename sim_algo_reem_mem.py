#!/usr/bin/env python

tam_pagina = 0x10  # Tamaño de la página: 16 bytes
marcos_libres = [
    0x0,
    0x1,
    0x2,
]  # 3 marcos físicos disponibles (como en el ejemplo del profe)
reqs = [0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A]
segmentos = [
    (".text", 0x00, 0x1A),
    (".data", 0x40, 0x28),
    (".heap", 0x80, 0x1F),
    (".stack", 0xC0, 0x22),
]
msg_1 = "Marco ya estaba asignado"
msg_2 = "Marco libre asignado"
msg_3 = "Marco asignado"
msg_4 = "Segmentation Fault"


def procesar(segmentos, reqs, marcos_libres):
    results = []
    tabla_paginas = {}  # página lógica -> marco físico
    pila_fifo = []
    marco_index = 0  # índice actual en marcos_libres

    for req in reqs:
        pagina_req = req // tam_pagina
        offset = req % tam_pagina       # offset dentro de la página limitado a dos bytes
        encontrado = False

        for segmento in segmentos:
            nombre_segmento, base, limite = segmento
            pag_base = base // tam_pagina
            pag_lim = (base + limite - 1) // tam_pagina

            if pag_base <= pagina_req <= pag_lim:
                encontrado = True

                if pagina_req in tabla_paginas:
                    marco = tabla_paginas[pagina_req]
                    direccion_fisica = (marco * tam_pagina) + offset    # dirección física
                    #limitamos dirección física a 2 bytes
                    
                    results.append((req, direccion_fisica, msg_1))
                else:
                    if len(tabla_paginas) < len(marcos_libres):
                        marco = marcos_libres[marco_index]
                        marco_index += 1
                        tabla_paginas[pagina_req] = marco
                        pila_fifo.append(pagina_req)
                        direccion_fisica = (marco * tam_pagina) + offset
                        results.append((req, direccion_fisica, msg_2))
                    else:
                        # Reemplazo FIFO    
                        pila_fifo, tabla_paginas, marco_out = fifo(
                            pila_fifo, pagina_req, tabla_paginas
                        )
                        direccion_fisica = (marco_out * tam_pagina) + offset
                        results.append((req, direccion_fisica, msg_3))
                break

        if not encontrado:
            results.append(
                (req, 0x1FF, msg_4)
            )  # Error: dirección fuera de los segmentos

    return results

def fifo(pila_fifo, pagina_req, tabla_paginas):
    pagina_out = pila_fifo.pop(0)   # sacamos el primer elemento
    marco_out = tabla_paginas[pagina_out]   # marco físico
    del tabla_paginas[pagina_out]   # eliminamos la página de la tabla

    tabla_paginas[pagina_req] = marco_out   # asignamos el nuevo marco
    pila_fifo.append(pagina_req)    # agregamos la nueva página
    
    return pila_fifo, tabla_paginas, marco_out


def print_results(results):
    for result in results:
        print(
            f"Req: {result[0]:#04x} Direccion Fisica: {result[1]:#04x} Acción: {result[2]}"
        )


if __name__ == "__main__":
    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)
