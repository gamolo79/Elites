# Diccionario de nodos y relaciones

Este documento resume los tipos de nodos y relaciones usados en la base de datos de la élite queretana, alineados con las referencias que ya aparecen en las notas (sexenios, ayuntamientos, legislaturas, instituciones y familias).

## Tipos de nodo y atributos mínimos

| Tipo | Uso principal | Atributos mínimos recomendados |
| --- | --- | --- |
| **Persona** | Individuos con cargos, vínculos familiares o actividad pública. | `nombre` (forma canónica), `alias`/variantes, `fecha_nacimiento`, `fecha_defunción` o `vigencia` (si aplica), `lugar_origen` (opcional), `fuentes` (lista corta de referencias). |
| **Familia** | Agrupa linajes y ramas familiares ya presentes en las notas. | `nombre` (apellidos o denominación reconocible), `ramas`/`variantes` (para distinguir Alcocer-Pozo, Nava-Bolaños, etc.), `región` (municipio/estado), `notas` de contexto y `fuentes`. |
| **Institución** | Partidos, dependencias, notarías, escuelas, empresas u organizaciones civiles. | `nombre_oficial`, `ámbito` (federal/estatal/municipal/privado), `tipo` (partido, ayuntamiento, legislatura, secretaría, universidad, notaría, etc.), `sede` (ciudad/estado), `periodo_actividad` (años de inicio–fin o "activo"), `fuentes`. |
| **Administración / Periodo** | Gestión acotada en el tiempo, ligada a una institución (sexenio, ayuntamiento, legislatura, rectorado, dirigencia partidista). | `institución` (referencia a la institución matriz), `nombre_periodo` (p.ej. "Ayuntamiento de Querétaro 2021-2024"), `rango_años` (inicio–fin), `titular` (persona principal si aplica), `fuentes`. |

## Tipos de relación

Cada relación registra `origen` → `destino`, `tipo_relación`, `fecha` o `periodo` (año, rango o etiqueta de sexenio/legislatura), y `fuente`.

- **titular de**: Persona → Administración/Periodo (gobernador en sexenio, alcalde en ayuntamiento, rector en universidad, presidente de partido en dirigencia).
- **cargo en**: Persona → Institución o Administración/Periodo (secretario, regidor, diputado en legislatura específica, director de facultad, notario en notaría concreta).
- **miembro de**: Persona → Institución (militancia partidista, pertenencia a colegio, egresado/diplomado en escuela).
- **pertenece a familia**: Persona → Familia.
- **matrimonio**: Persona ↔ Persona (bidireccional; registrar fecha o rango cuando se conozca).
- **parentesco**: Persona ↔ Persona (filial, hermandad u otro vínculo consanguíneo; especificar `detalle_parentesco`).
- **alianza/participación empresarial o civil**: Persona → Institución (empresas, asociaciones civiles, patronatos).
- **continuidad de administración**: Administración/Periodo → Administración/Periodo (siguiente o anterior en la secuencia de ayuntamientos, legislaturas o sexenios).

## Convenciones de nombres y slugs

- **Nombre canónico**: mantener mayúsculas, acentos y partículas tal como aparecen en los documentos públicos (ej.: "José Eduardo Calzada Rovirosa", "LXI Legislatura del Estado de Querétaro").
- **Slug interno y URLs**: usar minúsculas, reemplazar espacios por `-`, eliminar acentos y caracteres especiales. Ejemplos:
  - `José Eduardo Calzada Rovirosa` → `jose-eduardo-calzada-rovirosa`
  - `LXI Legislatura del Estado de Querétaro` → `lxi-legislatura-del-estado-de-queretaro`
  - `Ayuntamiento de Querétaro 2021-2024` → `ayuntamiento-de-queretaro-2021-2024`
- **Caracteres especiales**:
  - Sustituir `ñ` → `n`, `ü` → `u`, y eliminar tildes (`á`→`a`, etc.).
  - Reemplazar `/` o `&` por `-`, y eliminar puntos o comas salvo que distingan siglas; si son indispensables en nombre canónico, omitirlos en el slug (`Poder Ejecutivo del Estado de Querétaro` → `poder-ejecutivo-del-estado-de-queretaro`).
- **Unicidad**: los slugs deben ser únicos; si hay homónimos, agregar un calificador breve (`-hijo`, `-padre`, `-sr`, `-jr`, año de nacimiento o rama familiar) manteniendo la forma canónica en el título.
- **Referencias cruzadas**: al enlazar notas existentes de sexenios, ayuntamientos o legislaturas, reutilizar exactamente el slug derivado de su título para que las relaciones coincidan con las páginas ya creadas.
