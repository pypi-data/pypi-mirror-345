# CUI‑GT

Valida el **Código Único de Identificación (CUI) de Guatemala** desde **Python** o **JavaScript/TypeScript** con una sola función.

Repo oficial: [https://github.com/aalonzolu/cui-gt](https://github.com/aalonzolu/cui-gt)

---

## 1 · Instalación rápida

### Python (≥3.9)

```bash
pip install cui-gt   # desde PyPI
```

### JavaScript / TypeScript (Node ≥18)

```bash
npm i cui-gt        # o  yarn add cui-gt / pnpm add cui-gt
```

> El nombre del paquete es el mismo en ambos ecosistemas: **cui-gt**.

---

## 2 · Ejemplos de uso

### Python

```python
from cui_gt import is_valid_cui

print(is_valid_cui("5486270650101"))   # True o False
```

### JavaScript / TypeScript

```js
import { isValidCui } from "cui-gt";

console.log(isValidCui("5486270650101")); // true / false
```

---

## 3 · Cómo funciona (resumen)

* Comprueba que el CUI tenga **13 dígitos**.
* Valida que el departamento (01‑22) y municipio existan.
* Calcula el dígito verificador con **módulo 11**.

Todo se hace localmente; no se llama a ningún servicio externo.

---

## 4 · Contribuir

1. Haz *fork* del repo y crea una rama.
2. Corre `pytest` (Python) y `npm test` (JS).
3. Abre un **Pull Request**.

---

## 5 · Licencia

MIT.
