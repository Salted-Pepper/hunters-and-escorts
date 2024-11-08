import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from perlin_noise import PerlinNoise


def fetch_weather_markov_chain(make_plots=True, steps=1) -> dict:
    import xarray as xr
    df = xr.open_dataset("wave_data.nc", engine="netcdf4").to_dataframe()
    """
    mwd = mean wave direction
    swh = Significant Wave Height
    shww = Significant Height Wind Waves
    """

    df = df.dropna()

    df.unstack(level=-1)
    df = df.reset_index()

    if make_plots:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_title("Distribution of Sea States")
        ax.set_ylabel("Frequency")
        ax.set_xlabel("Significant Wave Height")
        plt.hist(df["swh"], bins=np.arange(int(np.floor(min(df["swh"]))),
                                           int(np.ceil(max(df["swh"]))),
                                           0.25))
        plt.show()

    df["swh_rounded"] = np.round(df["swh"])
    df["swh_rounded_lag"] = df["swh_rounded"].shift(1)
    df["swh_rounded_lag_2"] = df["swh_rounded"].shift(2)

    df["swh_rounded_lag_steps"] = df["swh_rounded"].shift(steps)

    data = df[["swh_rounded", "swh_rounded_lag", "swh_rounded_lag_2", "swh_rounded_lag_steps"]].dropna()
    data_1 = (data[["swh_rounded", "swh_rounded_lag"]].groupby(["swh_rounded", "swh_rounded_lag"])
              .size().reset_index())
    data_2 = (data[["swh_rounded", "swh_rounded_lag_2"]].groupby(["swh_rounded", "swh_rounded_lag_2"])
              .size().reset_index())
    data_steps = (data[["swh_rounded", "swh_rounded_lag_steps"]].groupby(["swh_rounded", "swh_rounded_lag_steps"])
                  .size().reset_index())
    data_1 = data_1.rename(columns={0: "count"})
    data_2 = data_2.rename(columns={0: "count"})
    data_steps = data_steps.rename(columns={0: "count"})

    states = data_1["swh_rounded"].unique()
    for state in states:
        total_value_1 = sum(data_1[data_1["swh_rounded"] == state]["count"])
        total_value_2 = sum(data_2[data_2["swh_rounded"] == state]["count"])
        total_value_steps = sum(data_steps[data_steps["swh_rounded"] == state]["count"])
        data_1.loc[data_1["swh_rounded"] == state, 'count'] = (
                data_1[data_1["swh_rounded"] == state]["count"] / total_value_1)
        data_2.loc[data_2["swh_rounded"] == state, 'count'] = (
                data_2[data_2["swh_rounded"] == state]["count"] / total_value_2)
        data_steps.loc[data_steps["swh_rounded"] == state, 'count'] = (
                data_steps[data_steps["swh_rounded"] == state]["count"] / total_value_steps)

    if make_plots:
        fig = plt.figure()
        pivot = data_1.pivot(index="swh_rounded", columns="swh_rounded_lag", values='count')
        sns.set(font_scale=0.7)
        ax = sns.heatmap(pivot, annot=True, fmt='0.3f')
        ax.set_facecolor('white')
        ax.set_title("Sea State Transitions")
        ax.set_xlabel("Next Sea State")
        ax.set_ylabel("Current Sea State")
        fig.show()

        fig_2 = plt.figure()
        pivot = data_steps.pivot(index="swh_rounded", columns="swh_rounded_lag_steps", values='count')
        sns.set(font_scale=0.7)
        ax_2 = sns.heatmap(pivot, annot=True, fmt='0.3f')
        ax_2.set_facecolor('white')
        ax_2.set_title(f"Sea State Transitions - {steps} steps")
        ax_2.set_xlabel(f"Next Sea State - {steps} steps")
        ax_2.set_ylabel("Current Sea State")
        fig_2.show()

    # Creating the DTMC matrix as dictionary:
    matrix = dict()

    for state_0 in states:
        matrix[int(state_0)] = {}
        for state_1 in states:
            if steps == 1:
                state_data = data_1[(data_1["swh_rounded"] == state_0) & (data_1["swh_rounded_lag"] == state_1)]
            else:
                state_data = data_steps[(data_steps["swh_rounded"] == state_0) &
                                        (data_steps["swh_rounded_lag_steps"] == state_1)]

            if len(state_data) == 0:
                transition_probability = 0
            else:
                transition_probability = state_data['count'].item()
            matrix[int(state_0)][int(state_1)] = transition_probability

    if make_plots:
        fig_location = px.scatter(df, x="longitude", y="latitude", animation_frame="time", color="swh")
        fig_location.show()

    return matrix

markov_dict = {0: {0: 0.8679717417139838, 1: 0.13201835468110393, 2: 9.903604912188037e-06, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0},
               1: {0: 0.01758646584138441, 1: 0.9103110115316072, 2: 0.07200003036807671, 3: 0.00010226896424985156, 4: 2.2329468176823484e-07, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0},
               2: {0: 0.0002756558192958557, 1: 0.07991486962926488, 2: 0.8487437509187451, 3: 0.0704606759018686, 4: 0.0005991057590881812, 5: 5.6836251401207355e-06, 6: 2.5834659727821525e-07, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0},
               3: {0: 0.00011851450532892008, 1: 0.008908904672011107, 2: 0.2034623166199663, 3: 0.6758416646208806, 4: 0.10751720576657722, 5: 0.004053196082249066, 6: 9.396507208221521e-05, 7: 4.232660904604288e-06, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0},
               4: {0: 6.222259094868711e-05, 1: 0.004645953457501971, 2: 0.0557988491783655, 3: 0.27422384725242815, 4: 0.4963140522314206, 5: 0.15289868384405242, 6: 0.014957125671855833, 7: 0.0010607470266490468, 8: 3.851874677775868e-05, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0},
               5: {0: 9.034811127273384e-06, 1: 0.002114145803781972, 2: 0.027673626482838377, 3: 0.1229186053865544, 4: 0.30308177407551296, 5: 0.3754235067715909, 6: 0.13974142370553744, 7: 0.02455661664392906, 8: 0.0038488295402184618, 9: 0.000542088667636403, 10: 9.034811127273385e-05, 11: 0, 12: 0, 13: 0, 14: 0},
               6: {0: 0, 1: 0.0006395906619763352, 2: 0.017995755443788702, 3: 0.07771026543012471, 4: 0.15774631508561793, 5: 0.28886240079076664, 6: 0.2849376399104573, 7: 0.13137773643050266, 8: 0.030845713288949618, 9: 0.007326220309910748, 10: 0.0019478442887461117, 11: 0.000610518359159229, 12: 0, 13: 0, 14: 0},
               7: {0: 0, 1: 0.00026845637583892615, 2: 0.01243847874720358, 3: 0.05628635346756152, 4: 0.10845637583892617, 5: 0.1887248322147651, 6: 0.25431767337807604, 7: 0.20375838926174497, 8: 0.11955257270693512, 9: 0.04384787472035794, 10: 0.008859060402684563, 11: 0.0030425055928411633, 12: 0.00044742729306487697, 13: 0, 14: 0},
               8: {0: 0, 1: 0, 2: 0.005662805662805663, 3: 0.05019305019305019, 4: 0.08571428571428572, 5: 0.11737451737451737, 6: 0.1956241956241956, 7: 0.19613899613899613, 8: 0.14465894465894466, 9: 0.1323037323037323, 10: 0.06177606177606178, 11: 0.009266409266409266, 12: 0.0010296010296010295, 13: 0.0002574002574002574, 14: 0},
               9: {0: 0, 1: 0, 2: 0.0011235955056179776, 3: 0.03651685393258427, 4: 0.0550561797752809, 5: 0.08707865168539326, 6: 0.149438202247191, 7: 0.19662921348314608, 8: 0.13089887640449438, 9: 0.1297752808988764, 10: 0.14887640449438203, 11: 0.05730337078651685, 12: 0.006179775280898876, 13: 0.0005617977528089888, 14: 0.0005617977528089888},
               10: {0: 0, 1: 0, 2: 0, 3: 0.01330603889457523, 4: 0.04196519959058342, 5: 0.04605936540429888, 6: 0.07062436028659161, 7: 0.14943705220061412, 8: 0.19344933469805528, 9: 0.13203684749232344, 10: 0.14636642784032752, 11: 0.15967246673490276, 12: 0.03991811668372569, 13: 0.007164790174002047, 14: 0},
               11: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0.018433179723502304, 5: 0.03456221198156682, 6: 0.06451612903225806, 7: 0.07834101382488479, 8: 0.12903225806451613, 9: 0.1912442396313364, 10: 0.27419354838709675, 11: 0.15207373271889402, 12: 0.055299539170506916, 13: 0, 14: 0.002304147465437788},
               12: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0.011111111111111112, 6: 0.044444444444444446, 7: 0.05555555555555555, 8: 0.08888888888888889, 9: 0.2111111111111111, 10: 0.34444444444444444, 11: 0.17777777777777778, 12: 0.06666666666666667, 13: 0, 14: 0},
               13: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0.1, 8: 0.1, 9: 0.2, 10: 0.3, 11: 0.2, 12: 0, 13: 0.1, 14: 0},
               14: {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0.5, 12: 0.5, 13: 0, 14: 0}}

# weather_transition_matrix = fetch_weather_markov_chain(make_plots=False, steps=3)
weather_transition_matrix = markov_dict


def update_sea_states(world):
    global weather_transition_matrix
    grid = world.receptor_grid
    update_u_values(grid)

    # PERLIN NOISE MODEL
    for receptor in grid.receptors:
        transition_probabilities = weather_transition_matrix[receptor.sea_state]
        prob = 0
        for key in transition_probabilities.keys():
            prob += transition_probabilities[key]
            if prob > receptor.new_uniform_value:
                receptor.sea_state = key
                break


def update_u_values(grid):
    cols = grid.max_cols
    rows = grid.max_rows

    noise = PerlinNoise(octaves=8)
    noise_data = [[noise([j/rows, i/cols]) for i in range(cols)] for j in range(rows)]
    # normalize noise
    min_value = min(x if isinstance(x, int) else min(x) for x in noise_data)
    noise_data = [[n + abs(min_value) for n in rows] for rows in noise_data]
    max_value = max(x if isinstance(x, int) else max(x) for x in noise_data)
    noise_data = [[n / max_value for n in rows] for rows in noise_data]
    min(x if isinstance(x, int) else min(x) for x in noise_data)
    max(x if isinstance(x, int) else max(x) for x in noise_data)
    new_u_matrix = noise_data

    # new_u_matrix = np.random.uniform(low=0, high=1, size=(rows, cols))
    for index, receptor in enumerate(grid.receptors):

        receptor.last_uniform_value = receptor.new_uniform_value
        receptor.new_uniform_value = new_u_matrix[index // cols][index % cols]
