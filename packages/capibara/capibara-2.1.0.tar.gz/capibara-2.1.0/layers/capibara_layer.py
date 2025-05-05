"""Capa *todo‑en‑uno* con atención, esparsidad y procesamiento cuántico.

Integra en orden secuencial:
1. **Multi‑Head Attention** con meta‑aprendizaje.
2. **Esparsidad dinámica** que fuerza un objetivo de densidad :math:`\rho`.
3. **Bloque cuántico** opcional, delegando en :class:`QuantumWrapper`.

-----
Complejidad
===========
* **Atención** :math:`\mathcal{O}(B\,S^2\,H)`  
* **Esparsidad** :math:`\mathcal{O}(B\,S\,D)`  
* **Cuántico** depende del backend; típicamente lineal en el número de disparos
  (``shots``).

-----
Métricas expuestas
==================
output_norm, attention_norm, sparsity_level, quantum_latency_ms, ...

-----
Notas
=====
* Si ``training=True`` se requiere un ``rng`` distinto por sub‑componente para
  reproducibilidad.
* El wrapper cuántico se omite con gracia cuando no hay backend disponible.
"""