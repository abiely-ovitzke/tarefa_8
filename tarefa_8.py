import pandas as pd
import matplotlib.pyplot as plt
import os

configurations = pd.read_json("flowda_data/MF_C3b_60/configurations.json")
instruments = pd.read_json("flowda_data/MF_C3b_60/instruments.json")
measurements = pd.read_json("flowda_data/MF_C3b_60/measurements.json")

exp_ids = measurements["exp_id"].drop_duplicates()

multiflow_dict = {
    "exp_id": [],       # Id do experimento
    "WC": [],           # Water Cut
    "USG": [],          # Velocidade superficial do gás
    "USL": [],          # Velocidade superficial do líquido
    "DP_DX_FRIC": [],   # Perda de carga friccional
}

for exp_id in exp_ids:
    multiflow_dict["exp_id"].append(exp_id)

    for var, key in zip(["wc", "usg", "usl", "dp_dx_fric"], ["WC", "USG", "USL", "DP_DX_FRIC"]):
        idx = measurements.index[(measurements["exp_id"] == exp_id) & (measurements["instr_id"] == var)]
        if len(idx) > 0:
            value = measurements.loc[idx, "value"].values[0]
        else:
            value = None
        multiflow_dict[key].append(value)

multiflow_df = pd.DataFrame(multiflow_dict)

# Verifica se WC está entre 0 e 1, ou entre 0 e 100
wc_max = multiflow_df["WC"].max()
if wc_max <= 1.5:
    multiflow_df["WC_percent"] = multiflow_df["WC"] * 100
else:
    multiflow_df["WC_percent"] = multiflow_df["WC"]  # já em %

multiflow_df["USG_group"] = multiflow_df["USG"].round(1) # Arredondar USG

os.makedirs("graficos_usg", exist_ok=True) # Diretório para salvar os gráficos

for usg_value in sorted(multiflow_df["USG_group"].dropna().unique()): # Gera gráfico para cada USG
    df_group = multiflow_df[multiflow_df["USG_group"] == usg_value]

    if df_group.empty:
        continue

    plt.figure(figsize=(7, 6))
    scatter = plt.scatter(
        df_group["WC_percent"],
        df_group["DP_DX_FRIC"],
        c=df_group["USL"],
        cmap='jet',
        s=70,
        edgecolor='k'
    )

    plt.xlabel("Water Cut [%]")
    plt.ylabel(r"$\dfrac{dP}{dX}_{\mathrm{fric}}$ [Pa/m]")
    plt.title(rf"$j_g = {usg_value:.2f}$ m/s", fontsize=14, style='italic')

    cbar = plt.colorbar(scatter)
    cbar.set_label(r"$j_l$ [m/s]")

    plt.grid(True)
    plt.tight_layout()

    filename = f"graficos_usg/FlowDa_MF_C3b_60_USG_{usg_value:.2f}.png"
    plt.savefig(filename, dpi=300)
    plt.close()
