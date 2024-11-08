import tkinter as tk
from tkinter import ttk

import numpy as np

import zones
from zones import Zone
import constants
import constants as cs


class Interface(tk.Tk):

    def __init__(self, game):
        super().__init__()
        self.game = game
        constants.interface = self

        self.frame = tk.Frame(self)
        self.title("Hunters and Escorts Simulation")
        self.geometry("1200x800")

        self.world_started = False

        # ---- CREATE TABS -----
        self.tab_control = ttk.Notebook(self)

        self.main_tab = ttk.Frame(self.tab_control)
        self.initiate_world_tab = ttk.Frame(self.tab_control)
        self.r_o_e_tab = ttk.Frame(self.tab_control)
        self.assignment_tab = ttk.Frame(self.tab_control)
        self.targeting_tab = ttk.Frame(self.tab_control)
        self.order_of_battle_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.main_tab, text="Simulation")
        self.tab_control.add(self.initiate_world_tab, text="World Settings")
        self.tab_control.add(self.r_o_e_tab, text="RoE")
        self.tab_control.add(self.assignment_tab, text="Agent Assignment")
        self.tab_control.add(self.targeting_tab, text="Targeting Rules")
        self.tab_control.add(self.order_of_battle_tab, text="OOB")
        self.tab_control.pack(expand=1, fill="both")

        # Data warehousing for the tabs
        self.log_canvas = None
        self.simulation_logs = []
        self.simulation_logs_labels = []

        self.r_o_e_current_levels = zones.coalition_maxima.copy()

        self.zone_assignment_hunter = zones.zone_assignment_hunter.copy()
        self.zone_assignment_coalition = zones.zone_assignment_coalition.copy()

        self.targeting_hunter_target_rules = {hunter: {agent: False for agent in constants.COALITION_ALL_TYPES}
                                              for hunter in constants.HUNTER_TYPES}
        self.targeting_checkbox_vars = {hunter: {} for hunter in constants.HUNTER_TYPES}

        self.merchant_oob_entries = {country: {} for country in [constants.TAIWAN, constants.USA, constants.JAPAN]}

        # Populate all the tabs
        self.create_main_tab()
        self.create_world_settings_tab()
        self.create_r_o_e_tab()
        self.create_assignment_tab()
        self.create_target_rules_tab()
        self.create_order_of_battle_tab()

    def continue_simulation(self) -> None:
        """
        Continues the simulation (or starts it if it wasn't started yet)
        :return:
        """

        # Check if start or continuation
        if not self.world_started:
            # Set the parameters as in settings
            self.add_to_logs("Processing Warm-up Period...")
            self.update()
            # Start the world
            self.start_simulation_button['text'] = "Continue Simulation"
            self.game.time_delta = float(self.time_delta_value.get())
            constants.sub_time_delta = float(self.sub_time_delta_value.get())
            self.game.create_world()

            # do warm up
            constants.PLOTTING_MODE = False
            constants.world.world_time = -self.time_between_input.get()

        # Update Rules & Parameters
        print(f"Plotting mode is {self.do_plot_label.state()} - debug mode {self.debug_mode_checkbox.state()}")
        constants.DEBUG_MODE = self.debug_mode_checkbox.cget('text')
        constants.coalition_rules = self.r_o_e_current_levels
        self.normalize_zone_assignments()
        zones.zone_assignment_hunter = self.zone_assignment_hunter
        zones.zone_assignment_coalition = self.zone_assignment_coalition
        constants.targeting_rules = self.targeting_hunter_target_rules
        constants.CHINA_SELECTED_LEVEL = int(self.china_escalation_entry.get())
        constants.COALITION_SELECTED_LEVEL = int(self.coalition_escalation_entry.get())
        self.set_o_o_b()

        print(f"{constants.CHINA_SELECTED_LEVEL=}")
        print(f"{constants.COALITION_SELECTED_LEVEL=}")

        # Continue simulation
        num_time_steps = int(np.ceil(self.time_between_input.get()) / float(self.time_delta_entry.get()))
        if not self.world_started:
            # Do warm-up without plotting the world
            self.world_started = True
            for step in range(num_time_steps):
                self.game.world.time_step()

            # Do the actual run post-warm up
            constants.PLOTTING_MODE = self.do_plot_label.cget('text')
            for step in range(num_time_steps):
                self.game.world.time_step()

        else:
            constants.PLOTTING_MODE = self.do_plot_label.cget('text')

            for step in range(num_time_steps):
                self.game.world.time_step()

    def normalize_zone_assignments(self):
        """
        Changes the selection values for the zone assignments per agent
        to ensure that they sum up to a 100%.
        :return:
        """
        # Hunter Normalisation
        for hunter in self.zone_assignment_hunter.keys():
            sum_hunter_zones = 0
            for zone in self.zone_assignment_hunter[hunter].keys():
                sum_hunter_zones += self.zone_assignment_hunter[hunter][zone]

            if sum_hunter_zones == 0:
                self.zone_assignment_hunter[hunter][zones.ZONE_A] = 1
            else:
                for zone in self.zone_assignment_hunter[hunter].keys():
                    self.zone_assignment_hunter[hunter][zone] = (self.zone_assignment_hunter[hunter][zone]
                                                                 / sum_hunter_zones)

        # Coalition Normalisation
        for agent in self.zone_assignment_coalition.keys():
            sum_agent_zones = 0
            for zone in self.zone_assignment_coalition[agent].keys():
                sum_agent_zones += self.zone_assignment_coalition[agent][zone]

            if sum_agent_zones == 0:
                self.zone_assignment_coalition[agent][zones.ZONE_A] = 1
            else:
                for zone in self.zone_assignment_coalition[agent].keys():
                    self.zone_assignment_coalition[agent][zone] = (self.zone_assignment_coalition[agent][zone]
                                                                   / sum_agent_zones)

    def set_o_o_b(self):
        # Merchants
        for country in self.merchant_oob_entries.keys():
            for merchant in self.merchant_oob_entries[country].keys():
                value = self.merchant_oob_entries[country][merchant].get()
                if value == "":
                    agent_oob = 0
                else:
                    agent_oob = int(value)
                print(f"Setting OOB for {country} {merchant} to: {agent_oob}")
                constants.merchant_quantities[country][merchant] = agent_oob

        # Hunters

        # Coalition

    def create_main_tab(self) -> None:
        tab = self.main_tab

        self.start_simulation_button = ttk.Button(tab, text="Start Simulation", command=self.continue_simulation)
        self.start_simulation_button.place(x=30, y=10)

        simulation_log_label = tk.Label(tab, text="Simulation Logs", font=('Helvetica', 12, 'bold'))
        simulation_log_label.place(x=30, y=40)

        logging_frame = tk.Frame(tab)
        logging_frame.place(x=30, y=90)

        self.log_canvas = tk.Canvas(logging_frame, width=500, height=500)
        self.log_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=0)

        y_scrollbar = tk.Scrollbar(logging_frame, orient=tk.VERTICAL, command=self.log_canvas.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_canvas.configure(yscrollcommand=y_scrollbar.set)
        self.log_canvas.bind('<Configure>',
                             lambda _: self.log_canvas.configure(scrollregion=self.log_canvas.bbox('all')))

        self.log_sub_frame = tk.Frame(self.log_canvas, width=500, height=500)

        self.add_to_logs("Start of Simulation...")

        self.log_canvas.create_window((0, 0), window=self.log_sub_frame, anchor="nw")

        # ---- Summary Statistics -----
        summary_column_start = 600

        row_start = 40
        row_height = 40

        summary_label = tk.Label(tab, text="Summary", font=('Helvetica', 12, 'bold'))
        summary_label.place(x=summary_column_start, y=40)

        merchant_header_label = ttk.Label(tab, text="Merchants", font=('Segoe UI', 9, 'bold'))
        merchant_seized_label = ttk.Label(tab, text="Seized")
        merchant_sunk_label = ttk.Label(tab, text="Sunk")
        merchant_damaged_label = ttk.Label(tab, text="Damaged")
        merchant_arrived_label = ttk.Label(tab, text="Arrived")
        merchant_labels = [merchant_header_label, merchant_seized_label, merchant_sunk_label,
                           merchant_damaged_label, merchant_arrived_label]

        self.merchant_seized_val = tk.IntVar()
        merchant_seized_val_label = ttk.Label(tab, text=0, textvariable=self.merchant_seized_val)
        self.merchant_sunk_val = tk.IntVar()
        merchant_sunk_val_label = ttk.Label(tab, text=0, textvariable=self.merchant_sunk_val)
        self.merchant_damaged_val = tk.IntVar()
        merchant_damaged_val_label = ttk.Label(tab, text=0, textvariable=self.merchant_damaged_val)
        self.merchant_arrived_val = tk.IntVar()
        merchant_arrived_val_label = ttk.Label(tab, text=0, textvariable=self.merchant_arrived_val)

        hunter_header_label = ttk.Label(tab, text="Hunters", font=('Segoe UI', 9, 'bold'))
        hunter_sunk_label = ttk.Label(tab, text="Sunk")
        hunter_damaged_label = ttk.Label(tab, text="Damaged")
        hunter_labels = [hunter_header_label, hunter_sunk_label, hunter_damaged_label]

        self.hunter_sunk_val = tk.IntVar()
        hunter_sunk_val_label = ttk.Label(tab, text=0, textvariable=self.hunter_sunk_val)
        self.hunter_damaged_val = tk.IntVar()
        hunter_damaged_val_label = ttk.Label(tab, text=0, textvariable=self.hunter_damaged_val)

        escort_header_label = ttk.Label(tab, text="Escorts", font=('Segoe UI', 9, 'bold'))
        escort_sunk_label = ttk.Label(tab, text="Sunk")
        escort_damaged_label = ttk.Label(tab, text="Damaged")

        self.escort_sunk_val = tk.IntVar()
        escort_sunk_val_label = ttk.Label(tab, text=0, textvariable=self.escort_sunk_val)
        self.escort_damaged_val = tk.IntVar()
        escort_damaged_val_label = ttk.Label(tab, text=0, textvariable=self.escort_damaged_val)

        interactions_label = ttk.Label(tab, text="Hunters deterred")
        self.deterred_val = tk.IntVar()
        interaction_val_label = tk.Label(tab, text=0, textvariable=self.deterred_val)

        escort_labels = [escort_header_label, escort_sunk_label, escort_damaged_label, interactions_label]

        value_label_link = {merchant_seized_label: merchant_seized_val_label,
                            merchant_sunk_label: merchant_sunk_val_label,
                            merchant_damaged_label: merchant_damaged_val_label,
                            merchant_arrived_label: merchant_arrived_val_label,
                            hunter_sunk_label: hunter_sunk_val_label,
                            hunter_damaged_label: hunter_damaged_val_label,
                            escort_sunk_label: escort_sunk_val_label,
                            escort_damaged_label: escort_damaged_val_label,
                            interactions_label: interaction_val_label,
                            }

        current_row_height = row_start + 20
        for label in merchant_labels:
            current_row_height = current_row_height + row_height
            label.place(x=summary_column_start, y=current_row_height)

        current_row_height += 20
        for label in hunter_labels:
            current_row_height = current_row_height + row_height
            label.place(x=summary_column_start, y=current_row_height)

        current_row_height += 20
        for label in escort_labels:
            current_row_height = current_row_height + row_height
            label.place(x=summary_column_start, y=current_row_height)

        # Match the values up with the correct vars
        x_value = 750

        for label_type in value_label_link.keys():
            value_label_to_place = value_label_link[label_type]
            y_value = label_type.place_info().get('y')
            value_label_to_place.place(x=x_value, y=y_value)

    def create_world_settings_tab(self) -> None:
        tab = self.initiate_world_tab

        self.world_settings_label = ttk.Label(tab, text="World Settings", font=('Helvetica', 16, 'bold'))

        self.time_between_input_label = ttk.Label(tab, text="Iteration time (hrs)")
        self.time_between_input = tk.IntVar()
        self.time_between_input_entry = ttk.Entry(tab, validate='all', textvariable=self.time_between_input,
                                                  validatecommand=(self.register(self.check_is_float), '%P'), width=5)
        self.time_between_input.set(24 * 7)  # Set to recommended week default

        self.time_delta_label = ttk.Label(tab, text="Time Delta (hrs)")
        self.time_delta_value = tk.StringVar()
        self.time_delta_entry = ttk.Entry(tab, validate='all', textvariable=self.time_delta_value,
                                          validatecommand=(self.register(self.check_is_float), '%P'), width=5)
        self.time_delta_value.set("0.25")

        self.sub_time_delta_label = ttk.Label(tab, text="Sub Time Delta (hrs)")
        self.sub_time_delta_value = tk.StringVar()
        self.sub_time_delta_entry = ttk.Entry(tab, validate='all', textvariable=self.sub_time_delta_value,
                                              validatecommand=(self.register(self.check_is_float), '%P'), width=5)
        self.sub_time_delta_value.set("0.05")

        self.world_settings_label.place(x=10, y=10)

        self.time_between_input_label.place(x=10, y=40)
        self.time_between_input_entry.place(x=120, y=40)
        self.time_delta_label.place(x=10, y=80)
        self.time_delta_entry.place(x=120, y=80)
        self.sub_time_delta_label.place(x=10, y=120)
        self.sub_time_delta_entry.place(x=120, y=120)

        escalation_height = 160
        self.escalation_level_label = ttk.Label(tab, text="Escalation Levels", font=('Helvetica', 14, 'bold'))

        self.china_level_var = tk.IntVar()
        self.china_escalation_label = ttk.Label(tab, text="China")
        self.china_escalation_entry = ttk.Combobox(tab, values=cs.CHINA_ESCALATION_LEVELS, width=5,
                                                   textvariable=self.china_level_var)
        self.china_level_var.set(1)

        self.coalition_level_var = tk.IntVar()
        self.coalition_escalation_label = ttk.Label(tab, text="Coalition")
        self.coalition_escalation_entry = ttk.Combobox(tab, values=cs.COALITION_ESCALATION_LEVELS, width=5,
                                                       textvariable=self.coalition_level_var)
        self.coalition_level_var.set(1)
        self.coalition_escalation_entry.bind("<<ComboboxSelected>>", self.update_r_o_e_tab)

        self.escalation_level_label.place(x=10, y=escalation_height + 20)
        self.china_escalation_label.place(x=10, y=escalation_height + 60)
        self.china_escalation_entry.place(x=80, y=escalation_height + 60)
        self.coalition_escalation_label.place(x=10, y=escalation_height + 100)
        self.coalition_escalation_entry.place(x=80, y=escalation_height + 100)

        plot_setting_x = 300
        self.plot_setting_label = ttk.Label(tab, text="Plot Settings", font=('Helvetica', 14, 'bold'))
        self.do_plot_label = ttk.Label(tab, text="Show Simulation")
        self.do_plot_checkbox = ttk.Checkbutton(tab)
        self.do_plot_checkbox.state(['selected'])

        self.debug_mode_label = ttk.Label(tab, text="Debug Mode")
        self.debug_mode_checkbox = ttk.Checkbutton(tab)
        self.debug_mode_checkbox.state(['selected'])

        self.receptor_label = ttk.Label(tab, text="Show Receptors")
        self.receptor_option = ttk.Combobox(tab, values=['Sea State', 'Coalition Pheromones',
                                                         'China Pheromones', 'None'])
        self.receptor_option.bind("<<ComboboxSelected>>", self.set_receptor_option)

        self.plot_setting_label.place(x=plot_setting_x, y=10)
        self.do_plot_label.place(x=plot_setting_x, y=50)
        self.do_plot_checkbox.place(x=plot_setting_x + 120, y=50)

        self.debug_mode_label.place(x=plot_setting_x, y=80)
        self.debug_mode_checkbox.place(x=plot_setting_x + 120, y=80)

        self.receptor_label.place(x=plot_setting_x, y=150)
        self.receptor_option.place(x=plot_setting_x + 120, y=150)

    def set_receptor_option(self, event):
        constants.RECEPTOR_PLOT_PARAMETER = self.receptor_option.get()

    def create_r_o_e_tab(self) -> None:
        tab = self.r_o_e_tab
        r_o_e_header = ttk.Label(tab, text="Rules of Engagement", font=('Helvetica', 16, 'bold'))
        escort_header = ttk.Label(tab, text="Escort Rules of Engagement", font=('Helvetica', 12, 'bold'))

        self.selected_esc_level_var = tk.StringVar()
        self.selected_escalation_label = ttk.Label(tab, textvariable=self.selected_esc_level_var)
        self.selected_esc_level_var.set("A coalition escalation level has to be set.")

        r_o_e_header.place(x=20, y=20)
        escort_header.place(x=20, y=80)
        self.selected_escalation_label.place(x=20, y=110)
        self.level_selectors = []

        row_start = 140
        row_height = 40

        column_start = 20
        column_width = 120

        # Create basic labels
        for index, zone in enumerate(zones.ZONES):
            label = ttk.Label(tab, text=zone.name)
            label.place(x=column_start, y=row_start + row_height * (index + 1))

        for index, country in enumerate([constants.TAIWAN, constants.USA, constants.JAPAN]):
            label = ttk.Label(tab, text=country)
            label.place(x=column_start + column_width * (index + 1.2), y=row_start)

    def update_r_o_e_tab(self, event: None):
        row_start = 140
        row_height = 40

        column_start = 20
        column_width = 120
        level = self.coalition_escalation_entry.get()
        if level == "":
            for selector in self.level_selectors:
                selector.place_forget()
            self.level_selectors = []

            self.selected_esc_level_var.set("A coalition escalation level has to be set.")
            return
        else:
            level = int(level)

        self.selected_esc_level_var.set(f"Escalation Level: {level}")
        escalation_rule_set = zones.coalition_maxima

        for j, escort_type in enumerate([constants.COALITION_TW_ESCORT,
                                         constants.COALITION_JP_ESCORT,
                                         constants.COALITION_US_ESCORT]):
            for i, zone in enumerate(zones.ZONES):
                min_value = escalation_rule_set[level][escort_type][zone.name]
                current_value = self.r_o_e_current_levels[level][escort_type][zone.name]
                valid_values = [value for value in [1, 2, 3, 4] if value >= min_value]
                combobox = ttk.Combobox(self.r_o_e_tab, values=valid_values, width=2)
                combobox.place(x=column_start + (j + 1.2) * column_width, y=row_start + (i + 1) * row_height)

                combobox.set(current_value)
                combobox.bind("<<ComboboxSelected>>",
                              lambda x, lvl=level, esc_type=escort_type, zn=zone.name, val=combobox.get():
                              self.set_r_o_e(x, lvl, esc_type, zn, val))
                self.level_selectors.append(combobox)

    def set_r_o_e(self, event, level, escort_type, zone, value):
        print(f"Set {level}-{escort_type}-{zone} to {value}")
        self.r_o_e_current_levels[level][escort_type][zone.name] = value

    def create_assignment_tab(self) -> None:
        tab = self.assignment_tab
        tab_main_frame = tk.Frame(tab)
        tab_main_frame.pack(fill=tk.BOTH, expand=1)

        tab_canvas = tk.Canvas(tab_main_frame)
        tab_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        y_scrollbar = tk.Scrollbar(tab_main_frame, orient=tk.VERTICAL, command=tab_canvas.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tab_canvas.configure(yscrollcommand=y_scrollbar.set)
        tab_canvas.bind('<Configure>', lambda x: tab_canvas.configure(scrollregion=tab_canvas.bbox("all")))

        tab_frame = tk.Frame(tab_canvas, width=1000, height=1000)

        target_header = ttk.Label(tab_frame, text="Assignment Tab", font=('Helvetica', 16, 'bold'))

        hunter_header = ttk.Label(tab_frame, text="Hunter Assignments", font=('Helvetica', 12, 'bold'))
        instructions = ttk.Label(tab_frame, text="Drag the Slider to assign a larger "
                                                 "fraction of the corresponding agent to the zone.")

        target_header.place(x=20, y=20)
        hunter_header.place(x=20, y=70)
        instructions.place(x=20, y=90)

        row_start = 120
        row_height = 40

        column_start = 20
        column_width = 120

        # Creating labeling
        for index, zone in enumerate(zones.ZONES):
            zone_label = ttk.Label(tab_frame, text=zone.name)
            zone_label.place(x=column_start, y=row_start + (index + 1) * row_height)
        end_of_zone_height = row_start + (len(zones.ZONES) + 1) * row_height

        for index, hunter in enumerate(constants.HUNTER_TYPES):
            hunter_label = ttk.Label(tab_frame, text=hunter, width=column_width)
            hunter_label.place(x=column_start + (index + 1) * column_width, y=row_start)

        # Creating selection tool
        for i, zone in enumerate(zones.ZONES):
            for j, hunter in enumerate(constants.HUNTER_TYPES):
                scaler = ttk.Scale(tab_frame, from_=0, to=100, value=0, length=40,
                                   command=lambda x, z=zone, h=hunter:
                                   self.set_assignment(x, z, h, 'hunter'))
                scaler.place(x=column_start + (j + 1) * column_width, y=row_start + (i + 1) * row_height)
                if zone.polygon in zones.HUNTER_ILLEGAL_ZONES:
                    scaler.state(['disabled'])

        # Coalition zone
        coalition_header = ttk.Label(tab_frame, text="Coalition Assignments", font=('Helvetica', 12, 'bold'))
        coalition_header.place(x=column_start, y=end_of_zone_height + row_height)
        row_start = end_of_zone_height + 2 * row_height

        for index, zone in enumerate(zones.ZONES):
            zone_label = ttk.Label(tab_frame, text=zone.name)
            zone_label.place(x=column_start, y=row_start + (index + 1) * row_height)

        for index, agent in enumerate(constants.COALITION_ACTIVE_TYPES):
            agent_label = ttk.Label(tab_frame, text=agent)
            agent_label.place(x=column_start + (index + 1) * column_width, y=row_start)

        for i, zone in enumerate(zones.ZONES):
            for j, agent in enumerate(constants.COALITION_ACTIVE_TYPES):
                scaler = ttk.Scale(tab_frame, from_=0, to=100, value=0, length=40,
                                   command=lambda x, z=zone, a=agent:
                                   self.set_assignment(x, z, a, 'coalition'))
                scaler.place(x=column_start + (j + 1) * column_width, y=row_start + (i + 1) * row_height)
                if zone.polygon in zones.COALITION_ILLEGAL_ZONES:
                    scaler.state(['disabled'])

        tab_canvas.create_window((0, 0), window=tab_frame, anchor="nw")

    def set_assignment(self, val, zone: Zone, agent: str, agent_type: str):
        """
        Sets zone assignment
        :param val:
        :param zone:
        :param agent:
        :param agent_type: "hunter" or "coalition"
        :return:
        """
        print(f"Setting {agent}, {zone.name} to {val}")
        if agent_type == 'hunter':
            self.zone_assignment_hunter[agent][zone] = float(val)
        elif agent_type == 'coalition':
            self.zone_assignment_coalition[agent][zone] = float(val)
        else:
            raise NotImplementedError(f"Invalid agent type {agent_type}.")

    def create_target_rules_tab(self) -> None:
        # Title Labels
        tab = self.targeting_tab
        target_header = ttk.Label(tab, text="Targeting Rules", font=('Helvetica', 16, 'bold'))
        hunter_header = ttk.Label(tab, text="Hunter Target Rules", font=('Helvetica', 12, 'bold'))

        target_header.place(x=20, y=20)
        hunter_header.place(x=20, y=70)

        row_start = 120
        row_height = 40

        column_start = 20
        column_width = 100
        # Creating matrix description labels
        for index, hunter in enumerate(constants.HUNTER_TYPES):
            hunter_label = ttk.Label(tab, text=hunter)
            hunter_label.place(x=column_start, y=row_start + (1 + index) * row_height)

        for index, target in enumerate(constants.COALITION_ALL_TYPES):
            target_label = ttk.Label(tab, text=target)
            target_label.place(x=column_start + (2 + index) * column_width, y=row_start)

        # Creating toggle matrix checkboxes
        for i, hunter in enumerate(constants.HUNTER_TYPES):
            for j, target in enumerate(constants.COALITION_ALL_TYPES):
                checkbox_var = tk.StringVar()
                checkbox = ttk.Checkbutton(tab, variable=checkbox_var,
                                           command=(lambda h=hunter, t=target:
                                                    self.update_r_o_e_rule(hunter=h, target=t)))
                self.targeting_checkbox_vars[hunter][target] = checkbox_var
                checkbox.place(x=column_start + (j + 2.3) * column_width, y=row_start + (i + 1) * row_height)

    def create_order_of_battle_tab(self) -> None:
        # Title Labels
        tab = self.order_of_battle_tab

        tab_main_frame = tk.Frame(tab)
        tab_main_frame.pack(fill=tk.BOTH, expand=1)

        tab_canvas = tk.Canvas(tab_main_frame)
        tab_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        y_scrollbar = tk.Scrollbar(tab_main_frame, orient=tk.VERTICAL, command=tab_canvas.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tab_canvas.configure(yscrollcommand=y_scrollbar.set)
        tab_canvas.bind('<Configure>', lambda x: tab_canvas.configure(scrollregion=tab_canvas.bbox("all")))

        tab_frame = tk.Frame(tab_canvas, width=1000, height=1000)

        oob_header = ttk.Label(tab_frame, text="Orders of Battle", font=('Helvetica', 16, 'bold'))
        merchants_header = ttk.Label(tab_frame, text="Weekly Merchant Arrivals", font=('Helvetica', 12, 'bold'))

        oob_header.place(x=20, y=20)
        merchants_header.place(x=20, y=70)

        row_height = 40
        row_start = 120

        column_width = 80
        merchant_col_start = 20

        country_label = ttk.Label(tab_frame, text="Country", font=('Helvetica', 10, 'bold'))
        type_label = ttk.Label(tab_frame, text="Type", font=('Helvetica', 10, 'bold'))
        number_label = ttk.Label(tab_frame, text="# Arrivals/Week", font=('Helvetica', 10, 'bold'))

        country_label.place(x=merchant_col_start + column_width, y=row_start)
        type_label.place(x=merchant_col_start + 2 * column_width, y=row_start)
        number_label.place(x=merchant_col_start + 3 * column_width, y=row_start)

        for i, country in enumerate([constants.TAIWAN, constants.USA, constants.JAPAN]):
            for j, merchant_type in enumerate(constants.MERCHANT_TYPES):

                height = row_start + i * len(constants.MERCHANT_TYPES) * row_height + row_height

                if j == 0:
                    country_section_label = ttk.Label(tab_frame, text=country)
                    country_section_label.place(x=merchant_col_start + column_width, y=height)

                unit_type_label = ttk.Label(tab_frame, text=merchant_type)
                unit_type_label.place(x=merchant_col_start + 2 * column_width, y=height + j * row_height)

                number_entry_value = tk.StringVar()
                number_entry = ttk.Entry(tab_frame, width=10, validate='all',
                                         validatecommand=(self.register(self.check_is_int), '%P'),
                                         textvariable=number_entry_value)
                number_entry.place(x=merchant_col_start + 3 * column_width, y=height + j * row_height)

                self.merchant_oob_entries[country][merchant_type] = number_entry_value

        tab_canvas.create_window((0, 0), window=tab_frame, anchor="nw")

    @staticmethod
    def check_is_float(text):
        if (all(char in "0123456789." for char in text) and  # all characters are valid
                text.count(".") <= 1):  # only 0 or 1 periods
            return True
        else:
            return False

    @staticmethod
    def check_is_int(text):
        if all(char in "0123456789" for char in text):
            return True
        else:
            return False

    def update_r_o_e_rule(self, hunter, target):
        button = self.targeting_checkbox_vars[hunter][target]
        self.targeting_hunter_target_rules[hunter][target] = button.get()
        print(f"Updated {hunter}, {target} to {button.get()}")

    def update_statistics_and_logs(self, event_code: str, log: str, other=None) -> None:
        # Don't log during warm up period
        if constants.world.world_time < 0:
            return

        self.add_to_logs(log)
        if event_code == "merchant_seized":
            self.merchant_seized_val.set(self.merchant_seized_val.get() + 1)
        elif event_code == "merchant_sunk":
            self.merchant_sunk_val.set(self.merchant_sunk_val.get() + 1)
        elif event_code == "merchant_damaged":
            self.merchant_damaged_val.set(self.merchant_damaged_val.get() + 1)
        elif event_code == "merchant_arrived":
            self.merchant_arrived_val.set(self.merchant_arrived_val.get() + 1)
        elif event_code == "boarded_merchant_arrived":
            self.merchant_seized_val.set(self.merchant_seized_val.get() + 1)
        elif event_code == "hunter_sunk":
            self.hunter_sunk_val.set(self.hunter_sunk_val.get() + 1)
        elif event_code == "hunter_damaged":
            self.hunter_damaged_val.set(self.hunter_damaged_val.get() + 1)
        elif event_code == "escort_sunk":
            self.escort_sunk_val.set(self.escort_sunk_val.get() + 1)
        elif event_code == "escort_damaged":
            self.escort_damaged_val.set(self.escort_damaged_val.get() + 1)
        elif event_code == "deterred":
            self.deterred_val.set(self.deterred_val.get() + 1)
        elif event_code is None:
            pass
        else:
            raise ValueError(f"No label for {event_code}")

    def add_to_logs(self, log_text: str) -> None:
        """
        Adds most recent activity to log and updates the log display
        :param log_text:
        :return:
        """
        self.simulation_logs.append(log_text)
        self.simulation_logs_labels.append(ttk.Label(self.log_sub_frame, text=log_text, font=('Segoe UI', 8)))

        start_y = 10
        row_height = 20

        for index, label in enumerate(reversed(self.simulation_logs_labels)):
            # label.forget()
            label.place(x=20, y=start_y + index * row_height)

        self.log_canvas.configure(scrollregion=self.log_canvas.bbox('all'))
