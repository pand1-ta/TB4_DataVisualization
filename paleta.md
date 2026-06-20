# Paleta de color — TB4

## Paleta cualitativa (regiones y países)

Tipo: Cualitativo  
Fuente: ColorBrewer — `Set2` (8 colores)  
Validación: colorblind safe confirmado en colorbrewer2.org  

| Hex       | Variable / Categoría que codifica                          |
|-----------|------------------------------------------------------------|
| `#66c2a5` | América Latina                                             |
| `#fc8d62` | Europa                                                     |
| `#8da0cb` | Asia-Pacífico                                              |
| `#e78ac3` | América del Norte                                          |
| `#a6d854` | Asia del Sur                                               |
| `#ffd92f` | Medio Oriente y N. África                                  |
| `#e5c494` | África Subsahariana                                        |
| `#b3b3b3` | Asia Central / Otras regiones                              |

Simulación deuteranopia: todos los colores permanecen distinguibles entre sí.  
Los tonos azul-verdoso (`#66c2a5`, `#8da0cb`) y naranja-rosado (`#fc8d62`, `#e78ac3`)  
mantienen contraste suficiente bajo deuteranopia y protanopia según Viz Palette  
(projects.susielu.com/viz-palette).

---

## Paleta divergente (cambio entre períodos: mejora / empeora)

Tipo: Divergente  
Fuente: ColorBrewer — `RdBu` (5 niveles)  
Validación: colorblind safe confirmado en colorbrewer2.org  

| Hex       | Variable / Categoría que codifica                          |
|-----------|------------------------------------------------------------|
| `#2166ac` | Mejora fuerte (gran reducción de carbono / aumento renovables) |
| `#92c5de` | Mejora leve                                                |
| `#f7f7f7` | Sin cambio significativo (centro neutro)                   |
| `#f4a582` | Empeoramiento leve                                         |
| `#d6604d` | Empeoramiento fuerte                                       |

Simulación deuteranopia: la escala azul–gris–rojo es distinguible bajo todos los  
tipos de daltonismo simulados; el rojo no se confunde con el azul en ninguna variante.

---

## Paleta secuencial (intensidad de una variable continua)

Tipo: Secuencial  
Fuente: ColorBrewer — `YlOrRd` (5 niveles)  
Validación: colorblind safe confirmado en colorbrewer2.org  

| Hex       | Variable / Categoría que codifica                          |
|-----------|------------------------------------------------------------|
| `#ffffb2` | Valor bajo (ej. consumo energético mínimo)                 |
| `#fecc5c` | Valor medio-bajo                                           |
| `#fd8d3c` | Valor medio                                                |
| `#f03b20` | Valor medio-alto                                           |
| `#bd0026` | Valor alto (ej. consumo energético máximo)                 |

Simulación deuteranopia: la progresión amarillo → rojo mantiene luminosidad  
creciente distinguible incluso sin percepción del rojo.

---

## Colores de acento fijo

| Hex       | Uso específico                                             |
|-----------|------------------------------------------------------------|
| `#1a1a2e` | Fondo principal del dashboard (dark mode)                  |
| `#e63946` | Perú destacado en gráficos comparativos (P8, P9)           |
| `#ffffff` | Texto principal sobre fondo oscuro                         |

**Restricciones absolutas aplicadas:**  
- Sin gráficos de torta ni donut en ninguna sección.  
- Sin gráficos 3D en ninguna forma.  
- Ninguna paleta usada en el dashboard queda fuera de las validadas en este archivo.
