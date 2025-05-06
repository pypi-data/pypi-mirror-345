# Notas de Compatibilidad para CapibaraGPT-v2

## Actualización de Dependencias (Marzo 2024)

Hemos actualizado las principales dependencias del proyecto para asegurar la compatibilidad y aprovechar las mejoras en seguridad y rendimiento. Estas actualizaciones resuelven varios problemas importantes.

### Cambios principales

| Biblioteca   | Versión Anterior | Versión Nueva | Cambios relevantes |
|--------------|------------------|---------------|-------------------|
| JAX          | Varias (no fija) | 0.4.20        | Mejoras de estabilidad, compatibilidad con PyTrees |
| JAXLIB       | Varias (no fija) | 0.4.20        | Compatibilidad con JAX |
| Flax         | 0.7.2            | 0.7.5         | Corrección de errores y mejoras de rendimiento |
| Optax        | 0.1.8            | 0.1.7         | Versión estable que garantiza compatibilidad |

### Problemas resueltos

1. **Error con `flax.struct.dataclass`**:
   - Problema: Esta función quedó obsoleta en versiones recientes de Flax
   - Solución: Reemplazada por el estándar `dataclasses.dataclass` de Python

2. **Incompatibilidades entre versiones**:
   - Problema: Algunas versiones de JAX, JAXLIB y Flax no son compatibles entre sí
   - Solución: Fijamos versiones específicas que funcionan correctamente juntas

3. **Problemas de tipado**:
   - Problema: Uso excesivo de `#type: ignore` debido a problemas de tipado
   - Solución: Versiones compatibles que reducen los errores de tipado

4. **Manejo de memoria mejorado**:
   - Problema: Comportamiento inconsistente en TPU y GPU
   - Solución: Versiones con mejor gestión de memoria y estabilidad

### Cómo actualizar

Hemos proporcionado scripts para facilitar la actualización:

- **Linux/Mac**: Ejecuta `bash update_dependencies.sh`
- **Windows**: Ejecuta `.\update_dependencies.ps1` en PowerShell

Estos scripts:

1. Verifican la versión de Python (se requiere 3.9+)
2. Comprueban si estás en un entorno virtual (recomendado)
3. Instalan las dependencias actualizadas
4. Verifican que la instalación sea correcta

### Cambios en el código

Las siguientes modificaciones fueron necesarias para mantener la compatibilidad:

1. Reemplazo de `from flax.struct import dataclass` por `from dataclasses import dataclass`
2. Actualización de métodos que usaban APIs obsoletas
3. Mejora en el manejo de errores y limpieza de recursos

### Compatibilidad con GPU/TPU

- **TPU**: Probado en TPU v3-8, requiere `libtpu.so` apropiado
- **GPU**: Probado en NVIDIA A100, requiere CUDA 11.8+

### Preguntas frecuentes

**P: ¿Necesito actualizar todo mi código?**  
R: No, los cambios son mayormente internos. La API pública permanece prácticamente igual.

**P: ¿Qué pasa si tengo problemas con la actualización?**  
R: Revisa los logs de errores y consulta la documentación oficial de JAX/Flax o crea un issue en nuestro repositorio.

**P: ¿Puedo seguir usando la versión anterior?**
R: Sí, pero no se garantiza soporte para problemas relacionados con versiones antiguas.
