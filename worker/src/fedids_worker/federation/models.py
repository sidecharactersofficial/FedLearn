"""Phase 2: Local Detector Backbones for FL-IDS.

1. Primary Backbone: 3-Layer MLP (66 -> 128 -> 64 -> 2 binary classification head)
   ReLU activations, batch size B=256, learning rate eta=1e-3.
2. Secondary Backbone A: 1D-CNN (Conv1d, BatchNorm, ReLU, AdaptiveAvgPool1d, Linear head)
3. Secondary Backbone B: Hybrid Autoencoder+MLP (AE+MLP: reconstruction MSE + classification CE)
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class FlowMLP(nn.Module):
    """Primary Backbone: 3-Layer MLP for binary intrusion detection."""

    def __init__(self, in_features: int = 66, hidden1: int = 128, hidden2: int = 64, num_classes: int = 2):
        super().__init__()
        self.fc1 = nn.Linear(in_features, hidden1)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(hidden1, hidden2)
        self.relu2 = nn.ReLU()
        self.classifier = nn.Linear(hidden2, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.relu1(self.fc1(x))
        out = self.relu2(self.fc2(out))
        return self.classifier(out)

    def get_penultimate_features(self, x: torch.Tensor) -> torch.Tensor:
        out = self.relu1(self.fc1(x))
        return self.relu2(self.fc2(out))


class FlowCNN1D(nn.Module):
    """Secondary Backbone: 1D Convolutional Neural Network for flow sequence features."""

    def __init__(self, in_features: int = 66, num_classes: int = 2):
        super().__init__()
        # Input shape: (B, 1, 66)
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=32, kernel_size=5, stride=1, padding=2)
        self.bn1 = nn.BatchNorm1d(32)
        self.conv2 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm1d(64)
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.classifier = nn.Linear(64, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x is (B, 66) -> reshape to (B, 1, 66)
        if x.dim() == 2:
            x = x.unsqueeze(1)
        out = F.relu(self.bn1(self.conv1(x)))
        out = F.relu(self.bn2(self.conv2(out)))
        out = self.pool(out).squeeze(-1)
        return self.classifier(out)

    def get_penultimate_features(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 2:
            x = x.unsqueeze(1)
        out = F.relu(self.bn1(self.conv1(x)))
        out = F.relu(self.bn2(self.conv2(out)))
        return self.pool(out).squeeze(-1)


class FlowAEHybrid(nn.Module):
    """Secondary Backbone: Hybrid Autoencoder + MLP Classifier.

    Jointly reconstructs unlabeled traffic via MSE and classifies labeled traffic via CE.
    Useful for zero-delay self-supervised detection in Section 5.5.
    """

    def __init__(self, in_features: int = 66, latent_dim: int = 16, num_classes: int = 2):
        super().__init__()
        # Encoder: 66 -> 32 -> 16
        self.encoder = nn.Sequential(
            nn.Linear(in_features, 32),
            nn.ReLU(),
            nn.Linear(32, latent_dim),
            nn.ReLU(),
        )
        # Decoder: 16 -> 32 -> 66
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.ReLU(),
            nn.Linear(32, in_features),
        )
        # Classification Head on latent space: 16 -> 32 -> 2
        self.classifier = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes),
        )

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        return self.encoder(x)

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        return self.decoder(z)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.encode(x)
        return self.classifier(z)

    def reconstruction_loss(self, x: torch.Tensor) -> torch.Tensor:
        z = self.encode(x)
        x_rec = self.decode(z)
        return F.mse_loss(x_rec, x)

    def get_penultimate_features(self, x: torch.Tensor) -> torch.Tensor:
        return self.encode(x)


def create_model(backbone: str = "mlp", in_features: int = 66, num_classes: int = 2) -> nn.Module:
    b = backbone.lower()
    if b in ("mlp", "3layer_mlp"):
        return FlowMLP(in_features=in_features, num_classes=num_classes)
    elif b in ("cnn", "1d_cnn", "cnn1d"):
        return FlowCNN1D(in_features=in_features, num_classes=num_classes)
    elif b in ("ae", "ae_hybrid", "hybrid"):
        return FlowAEHybrid(in_features=in_features, num_classes=num_classes)
    else:
        raise ValueError(f"Unknown backbone: {backbone}. Choose mlp, cnn1d, or ae_hybrid.")
