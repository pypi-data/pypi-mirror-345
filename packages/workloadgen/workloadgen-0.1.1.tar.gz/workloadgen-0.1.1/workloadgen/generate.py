import torch

def generate_samples(model, scaler, num_samples, latent_dim, log_cols, int_cols, df_template, device):
    model.eval()
    with torch.no_grad():
        z = torch.randn(num_samples, latent_dim).to(device)
        generated = model.decode(z).cpu().numpy()

    gen_df = pd.DataFrame(scaler.inverse_transform(generated), columns=df_template.columns)

    for col in log_cols:
        if col in gen_df:
            gen_df[col] = np.expm1(np.clip(gen_df[col], a_min=None, a_max=100))

    for col in int_cols:
        if col in gen_df:
            gen_df[col] = gen_df[col].round().astype(int)

    for col in ['Submit Time', 'Wait Time', 'Run Time', 'Requested Time']:
        if col in gen_df:
            gen_df[col] = gen_df[col].clip(lower=0)

    return gen_df