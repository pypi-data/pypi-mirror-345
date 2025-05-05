import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader


def loss_function(recon_x, x, mu, logvar, beta):
    recon_loss = F.mse_loss(recon_x, x, reduction='sum')
    kl_div = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    return recon_loss + beta * kl_div

def train_model(model, train_tensor, val_tensor, epochs, lr, beta_schedule, device):
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    train_loader = DataLoader(train_tensor, batch_size=128, shuffle=True)
    val_loader = DataLoader(val_tensor, batch_size=128)
    train_losses, val_losses = [], []

    for epoch in range(1, epochs + 1):
        beta = beta_schedule(epoch)
        model.train()
        epoch_loss = 0
        for batch in train_loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            recon, mu, logvar = model(batch)
            loss = loss_function(recon, batch, mu, logvar, beta)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        train_losses.append(epoch_loss / len(train_loader.dataset))

        model.eval()
        val_loss = 0
        with torch.no_grad():
            for batch in val_loader:
                batch = batch.to(device)
                recon, mu, logvar = model(batch)
                val_loss += loss_function(recon, batch, mu, logvar, 1.0).item()
        val_losses.append(val_loss / len(val_loader.dataset))

        print(f"Epoch {epoch} | Train Loss: {train_losses[-1]:.4f} | Val Loss: {val_losses[-1]:.4f}")
    return train_losses, val_losses
