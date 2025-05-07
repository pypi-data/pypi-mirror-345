# Compatibilidad

Este documento detalla la compatibilidad de CapibaraGPT con diferentes sistemas, hardware y software.

## Versiones de Python

| Versión | Estado | Notas |
|---------|--------|-------|
| 3.9     | ✅     | Totalmente compatible |
| 3.10    | ✅     | Totalmente compatible |
| 3.11    | ✅     | Totalmente compatible |
| 3.12    | ⚠️     | Compatible con limitaciones |

## Sistemas Operativos

| Sistema | Estado | Notas |
|---------|--------|-------|
| Linux   | ✅     | Totalmente compatible |
| Windows | ✅     | Totalmente compatible |
| macOS   | ✅     | Totalmente compatible |

## Hardware

### GPUs

| Fabricante | Modelo | Estado | Notas |
|------------|--------|--------|-------|
| NVIDIA    | A100   | ✅     | Optimizado |
| NVIDIA    | V100   | ✅     | Optimizado |
| NVIDIA    | T4     | ✅     | Compatible |
| NVIDIA    | RTX    | ✅     | Compatible |
| AMD       | MI200  | ⚠️     | Compatible con limitaciones |
| AMD       | MI100  | ⚠️     | Compatible con limitaciones |

### TPUs

| Versión | Estado | Notas |
|---------|--------|-------|
| v4      | ✅     | Optimizado |
| v3      | ✅     | Compatible |
| v2      | ⚠️     | Compatible con limitaciones |

## Backends

| Backend | Versión | Estado | Notas |
|---------|---------|--------|-------|
| JAX     | ≥0.4.23 | ✅     | Principal |
| TensorFlow | ≥2.16.1 | ✅     | Compatible |
| PyTorch | ≥2.2.2  | ⚠️     | Compatible con limitaciones |

## Dependencias Principales

| Paquete | Versión | Estado | Notas |
|---------|---------|--------|-------|
| jax     | ≥0.4.23 | ✅     | Requerido |
| jaxlib  | ≥0.4.23 | ✅     | Requerido |
| flax    | ≥0.8.2  | ✅     | Requerido |
| tensorflow | ≥2.16.1 | ✅     | Opcional |
| torch   | ≥2.2.2  | ⚠️     | Opcional |

## Notas de Compatibilidad

### CUDA

- Se requiere CUDA 11.8 o superior para soporte GPU
- Se recomienda usar los controladores más recientes
- Algunas funcionalidades avanzadas pueden requerir CUDA 12.0+

### TPU

- Se requiere acceso a Google Cloud TPU
- Algunas optimizaciones específicas están disponibles solo para TPU v4
- El entrenamiento distribuido está optimizado para TPU v4

### Windows

- Se recomienda usar WSL2 para mejor rendimiento
- Algunas optimizaciones específicas pueden no estar disponibles
- El soporte para TPU está limitado

### macOS

- El soporte para GPU está limitado a Macs con GPU NVIDIA
- Se recomienda usar CPU o TPU para mejor rendimiento
- Algunas optimizaciones específicas pueden no estar disponibles

## Solución de Problemas

Si encuentras problemas de compatibilidad:

1. Verifica que tienes las versiones correctas de las dependencias
2. Consulta los logs de error para más detalles
3. Abre un issue en GitHub con la información relevante
4. Proporciona detalles sobre tu configuración de hardware y software

## Actualizaciones

Este documento se actualizará periódicamente para reflejar cambios en la compatibilidad. La última actualización fue el 2024-03-20.
