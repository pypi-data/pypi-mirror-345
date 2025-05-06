"""Módulo para codificación de video usando patches espaciales y proyección temporal."""

import jax.numpy as jnp # type: ignore
from flax import linen as nn # type: ignore
import logging

class VideoEncoderModule(nn.Module):
    """Módulo para codificación de video usando patches espaciales y proyección temporal."""
    
    def setup(self):
        # --- Configuración de Dimensiones ---
        self.max_h = getattr(self.config.model, "max_image_height", 256)
        self.max_w = getattr(self.config.model, "max_image_width", 256)
        self.patch_size = getattr(self.config.model, "patch_size", 16)
        
        # Validación de dimensiones
        if self.max_h % self.patch_size != 0 or self.max_w % self.patch_size != 0:
            # Ajuste automático de dimensiones al múltiplo más cercano
            self.max_h = (self.max_h // self.patch_size + 1) * self.patch_size
            self.max_w = (self.max_w // self.patch_size + 1) * self.patch_size
            logging.warning(
                f"Ajustando dimensiones a {self.max_h}x{self.max_w} "
                f"para ser divisibles por patch_size={self.patch_size}"
            )
        
        # Cálculo de número máximo de patches
        self.max_hp = self.max_h // self.patch_size
        self.max_wp = self.max_w // self.patch_size
        self.max_num_patches = self.max_hp * self.max_wp
        
        # --- Capas de Proyección ---
        self.frame_proj = nn.Conv(
            features=self.config.hidden_size,
            kernel_size=(self.patch_size, self.patch_size),
            strides=(self.patch_size, self.patch_size),
            padding='VALID',
            dtype=self.dtype,
            name="frame_patch_proj"
        )
        
        self.temporal_proj = nn.Dense(
            self.config.hidden_size,
            dtype=self.dtype,
            name="temporal_proj"
        )
        
        # --- Embeddings Posicionales ---
        self.spatial_pos_embed = nn.Embed(
            num_embeddings=self.max_num_patches,
            features=self.config.hidden_size,
            embedding_init=nn.initializers.normal(stddev=0.02),
            dtype=self.dtype,
            name="spatial_pos_embed"
        )
        
        self.temporal_pos_embed = FramePositionalEncoding(
            dim=self.config.hidden_size,
            name="temporal_pos_enc"
        )
        
        # --- Normalización y Dropout ---
        self.dropout = nn.Dropout(rate=self.config.dropout_rate)
        self.norm = nn.LayerNorm(dtype=self.dtype)
        
    def __call__(self, video_tensor: jnp.ndarray, training: bool = False) -> jnp.ndarray:
        """Procesa tensor de video (B, T, H, W, C) -> (B, T, N, hidden)."""
        assert video_tensor.ndim == 5, "Se espera tensor de video de 5 dimensiones (B, T, H, W, C)"
        B, T, H_orig, W_orig, C = video_tensor.shape

        # --- Padding (si es necesario) ---
        H_padded, W_padded = H_orig, W_orig
        pad_h_after = (self.patch_size - (H_orig % self.patch_size)) % self.patch_size
        pad_w_after = (self.patch_size - (W_orig % self.patch_size)) % self.patch_size

        if pad_h_after > 0 or pad_w_after > 0:
            # Padding solo al final (derecha, abajo)
            padding_config = ((0, 0), (0, 0), (0, pad_h_after), (0, pad_w_after), (0, 0))
            video_tensor = jnp.pad(video_tensor, padding_config, mode='constant', constant_values=0)
            H_padded = H_orig + pad_h_after
            W_padded = W_orig + pad_w_after

        video_tensor = video_tensor.astype(self.dtype)
        # Reshape para Conv (B*T, H, W, C - asumiendo channels-last para Flax Conv)
        video_tensor_reshaped = video_tensor.reshape(B * T, H_padded, W_padded, C)

        # --- Proyección de Patches ---
        patch_embs = self.frame_proj(video_tensor_reshaped) # (B*T, H', W', D)
        _BT, Hp, Wp, D = patch_embs.shape
        N = Hp * Wp # Número de patches actual

        # Validar contra max_num_patches
        if N > self.max_num_patches:
            raise ValueError(f"El número de patches ({N}) excede el máximo precalculado ({self.max_num_patches}). Ajusta max_height/max_width en config.")

        # Reshape a (B, T, N, D)
        patch_embs = patch_embs.reshape(B, T, N, D)

        # --- Proyección Temporal Adicional ---
        patch_embs = self.temporal_proj(patch_embs)

        # --- Añadir Embeddings Posicionales ---
        # 1. Espacial (Aprendible)
        patch_indices = jnp.arange(N)
        s_pos_emb = self.spatial_pos_embed(patch_indices)
        s_pos_emb = s_pos_emb[None, None, :, :]
        patch_embs = patch_embs + s_pos_emb

        # 2. Temporal (Sinusoidal)
        patch_embs = self.temporal_pos_embed(patch_embs)

        # --- Dropout y Normalización Final ---
        patch_embs = self.dropout(patch_embs, deterministic=not training)
        patch_embs = self.norm(patch_embs)

        return patch_embs # Salida final: (B, T, N, hidden_size) 