from pathlib import Path

import yaml
import numpy as np
import openmdao.api as om

from h2integrate.core.finances import ProFastComp, AdjustedCapexOpexComp
from h2integrate.core.utilities import create_xdsm_from_config
from h2integrate.core.feedstocks import FeedstockComponent
from h2integrate.core.resource_summer import ElectricitySumComp
from h2integrate.core.supported_models import supported_models, electricity_producing_techs
from h2integrate.core.inputs.validation import load_tech_yaml, load_plant_yaml, load_driver_yaml
from h2integrate.core.pose_optimization import PoseOptimization


try:
    import pyxdsm
except ImportError:
    pyxdsm = None


class H2IntegrateModel:
    def __init__(self, config_file):
        # read in config file; it's a yaml dict that looks like this:
        self.load_config(config_file)

        # create site-level model
        # this is an OpenMDAO group that contains all the site information
        self.create_site_model()

        # create plant-level model
        # this is an OpenMDAO group that contains all the technologies
        # it will need plant_config but not driver or tech config
        self.create_plant_model()

        # create technology models
        # these are OpenMDAO groups that contain all the components for each technology
        # they will need tech_config but not driver or plant config
        self.create_technology_models()

        self.create_financial_model()

        # connect technologies
        # technologies are connected within the `technology_interconnections` section of the
        # plant config
        self.connect_technologies()

        # create driver model
        # might be an analysis or optimization
        self.create_driver_model()

    def load_config(self, config_file):
        config_path = Path(config_file)
        with config_path.open() as file:
            config = yaml.safe_load(file)

        self.name = config.get("name")
        self.system_summary = config.get("system_summary")

        # Load each config file as yaml and save as dict on this object
        self.driver_config = load_driver_yaml(config_path.parent / config.get("driver_config"))
        self.technology_config = load_tech_yaml(
            config_path.parent / config.get("technology_config")
        )
        self.plant_config = load_plant_yaml(config_path.parent / config.get("plant_config"))

    def create_site_model(self):
        # Create a site-level component
        site_config = self.plant_config.get("site", {})
        site_component = om.IndepVarComp()
        site_component.add_output("latitude", val=site_config.get("latitude", 0.0))
        site_component.add_output("longitude", val=site_config.get("longitude", 0.0))
        site_component.add_output("elevation_m", val=site_config.get("elevation_m", 0.0))
        site_component.add_output("time_zone", val=site_config.get("time_zone", 0))

        # Add boundaries if they exist
        site_config = self.plant_config.get("site", {})
        boundaries = site_config.get("boundaries", [])
        for i, boundary in enumerate(boundaries):
            site_component.add_output(f"boundary_{i}_x", val=np.array(boundary.get("x", [])))
            site_component.add_output(f"boundary_{i}_y", val=np.array(boundary.get("y", [])))

        self.prob = om.Problem()
        self.model = self.prob.model
        self.model.add_subsystem("site", site_component, promotes=["*"])

    def create_plant_model(self):
        """
        Create the plant-level model.

        This method creates an OpenMDAO group that contains all the technologies.
        It uses the plant configuration but not the driver or technology configuration.

        Information at this level might be used by any technology and info stored here is
        the same for each technology. This includes site information, project parameters,
        control strategy, and finance parameters.
        """
        # Create a plant-level component
        plant_component = om.IndepVarComp()
        plant_component.add_output("plant_component_example_value", val=1.0)
        project_parameters = self.plant_config.get("project_parameters", {})
        for key, value in project_parameters.items():
            plant_component.add_output(key, val=value)

        # Add control strategy parameters
        control_strategy = self.plant_config.get("control_strategy", {})
        for key, value in control_strategy.items():
            plant_component.add_output(key, val=value)

        # Add finance parameters
        # Not using financial parameters through OpenMDAO right now; instead
        # using the config dicts directly.
        # finance_parameters = self.plant_config.get('finance_parameters', {})
        # for key, value in finance_parameters.items():
        #     plant_component.add_output(key, val=value)

        plant_group = om.Group()
        plant_group.add_subsystem("plant_info", plant_component, promotes=["*"])

        # Create the plant model group and add components
        self.plant = self.model.add_subsystem("plant", plant_group, promotes=["*"])

    def create_technology_models(self):
        # Loop through each technology and instantiate an OpenMDAO object (assume it exists)
        # for each technology

        self.tech_names = []
        self.performance_models = []
        self.cost_models = []
        self.financial_models = []

        combined_performance_and_cost_model_technologies = ["hopp", "h2_storage"]

        # Create a technology group for each technology
        for tech_name, individual_tech_config in self.technology_config["technologies"].items():
            if "feedstocks" in tech_name:
                feedstock_component = FeedstockComponent(feedstocks_config=individual_tech_config)
                self.plant.add_subsystem(tech_name, feedstock_component)
            else:
                tech_group = self.plant.add_subsystem(tech_name, om.Group())
                self.tech_names.append(tech_name)

                # Special HOPP handling for short-term
                if tech_name in combined_performance_and_cost_model_technologies:
                    hopp_comp = supported_models[tech_name](
                        plant_config=self.plant_config, tech_config=individual_tech_config
                    )
                    tech_group.add_subsystem(tech_name, hopp_comp, promotes=["*"])
                    self.performance_models.append(hopp_comp)
                    self.cost_models.append(hopp_comp)
                    self.financial_models.append(hopp_comp)
                    continue

                # Process the technology models
                performance_name = individual_tech_config["performance_model"]["model"]
                performance_object = supported_models[performance_name]
                tech_group.add_subsystem(
                    performance_name,
                    performance_object(
                        plant_config=self.plant_config, tech_config=individual_tech_config
                    ),
                    promotes=["*"],
                )
                self.performance_models.append(performance_object)

                # Process the cost models
                if "cost_model" in individual_tech_config:
                    cost_name = individual_tech_config["cost_model"]["model"]
                    cost_object = supported_models[cost_name]
                    tech_group.add_subsystem(
                        cost_name,
                        cost_object(
                            plant_config=self.plant_config, tech_config=individual_tech_config
                        ),
                        promotes=["*"],
                    )
                    self.cost_models.append(cost_object)

                # Process the financial models
                if "financial_model" in individual_tech_config:
                    financial_name = cost_name  # TODO: Should this be a separate name?
                    if "model" in individual_tech_config["financial_model"]:
                        financial_name = individual_tech_config["financial_model"]["model"]

                    try:  # TODO: migrate to explicit model naming once financial side is figured out
                        financial_object = supported_models[f"{financial_name}_financial"]
                        tech_group.add_subsystem(
                            f"{tech_name}_financial",
                            financial_object(
                                plant_config=self.plant_config, tech_config=individual_tech_config
                            ),
                            promotes=["*"],
                        )
                        self.financial_models.append(financial_object)
                    except KeyError:
                        # TODO: Is this currently a bypass until the financial portion is more concrete?
                        pass

    def create_financial_model(self):
        """
        Creates and configures the financial model for the plant.

        Creates financial groups based on the technology configurations
        and adds the appropriate financial components to each group.
        """

        if "finance_parameters" not in self.plant_config:
            return

        # Create a dictionary to hold financial groups
        financial_groups = {}

        # Loop through each technology and add it to the appropriate financial group
        for tech_name, individual_tech_config in self.technology_config["technologies"].items():
            financial_group_id = individual_tech_config.get("financial_model", {}).get("group")
            if financial_group_id is not None:
                if financial_group_id not in financial_groups:
                    financial_groups[financial_group_id] = {}
                financial_groups[financial_group_id][tech_name] = individual_tech_config

        # If no financial groups are defined, add all technologies to a single group
        if not financial_groups:
            financial_groups["1"] = self.technology_config["technologies"]

        # Add each financial group to the plant
        for group_id, tech_configs in financial_groups.items():
            commodity_types = ["electricity"]
            if "electrolyzer" in tech_configs:
                commodity_types.append("hydrogen")
            if "ammonia" in tech_configs:
                commodity_types.append("ammonia")

            # Steel provides its own financials
            if "steel" in tech_configs:
                continue

            financial_group = om.Group()

            # Add the ExecComp to the plant model
            financial_group.add_subsystem(
                "electricity_sum", ElectricitySumComp(tech_configs=tech_configs)
            )

            # Add adjusted capex component
            adjusted_capex_opex_comp = AdjustedCapexOpexComp(
                tech_config=tech_configs, plant_config=self.plant_config
            )
            financial_group.add_subsystem(
                "adjusted_capex_opex_comp", adjusted_capex_opex_comp, promotes=["*"]
            )

            # Add profast components
            for idx, commodity_type in enumerate(commodity_types):
                profast_comp = ProFastComp(
                    tech_config=tech_configs,
                    plant_config=self.plant_config,
                    commodity_type=commodity_type,
                )
                financial_group.add_subsystem(f"profast_comp_{idx}", profast_comp, promotes=["*"])

            self.plant.add_subsystem(f"financials_group_{group_id}", financial_group)

        self.financial_groups = financial_groups

    def connect_technologies(self):
        technology_interconnections = self.plant_config.get("technology_interconnections", [])

        combiner_counts = {}

        # loop through each linkage and instantiate an OpenMDAO object (assume it exists) for
        # the connection type (e.g. cable, pipeline, etc)
        for connection in technology_interconnections:
            if len(connection) == 4:
                source_tech, dest_tech, transport_item, transport_type = connection

                # make the connection_name based on source, dest, item, type
                connection_name = f"{source_tech}_to_{dest_tech}_{transport_type}"

                # Create the transport object
                connection_component = supported_models[transport_type]()

                # Add the connection component to the model
                self.plant.add_subsystem(connection_name, connection_component)

                if "storage" in source_tech:
                    # Connect the source technology to the connection component
                    self.plant.connect(
                        f"{source_tech}.{transport_item}_output",
                        f"{connection_name}.{transport_item}_input",
                    )
                else:
                    # Connect the source technology to the connection component
                    self.plant.connect(
                        f"{source_tech}.{transport_item}",
                        f"{connection_name}.{transport_item}_input",
                    )

                # Check if the transport type is a combiner
                if "combiner" in dest_tech:
                    # Connect the source technology to the connection component
                    # with specific input names
                    if dest_tech not in combiner_counts:
                        combiner_counts[dest_tech] = 1
                    else:
                        combiner_counts[dest_tech] += 1

                    # Connect the connection component to the destination technology
                    self.plant.connect(
                        f"{connection_name}.{transport_item}_output",
                        f"{dest_tech}.electricity_input{combiner_counts[dest_tech]}",
                    )

                elif "storage" in dest_tech:
                    # Connect the connection component to the destination technology
                    self.plant.connect(
                        f"{connection_name}.{transport_item}_output",
                        f"{dest_tech}.{transport_item}_input",
                    )

                else:
                    # Connect the connection component to the destination technology
                    self.plant.connect(
                        f"{connection_name}.{transport_item}_output",
                        f"{dest_tech}.{transport_item}",
                    )

            elif len(connection) == 3:
                # connect directly from source to dest
                source_tech, dest_tech, connected_parameter = connection

                self.plant.connect(
                    f"{source_tech}.{connected_parameter}", f"{dest_tech}.{connected_parameter}"
                )

            else:
                err_msg = f"Invalid connection: {connection}"
                raise ValueError(err_msg)

        # TODO: connect outputs of the technology models to the cost and financial models of the
        # same name if the cost and financial models are not None
        if "finance_parameters" in self.plant_config:
            # Connect the outputs of the technology models to the appropriate financial groups
            for group_id, tech_configs in self.financial_groups.items():
                # Skip steel financials; it provides its own financials
                if "steel" in tech_configs:
                    continue

                # Loop through technologies and connect electricity outputs to the ExecComp
                for tech_name in self.tech_names:
                    if tech_name in electricity_producing_techs:
                        self.plant.connect(
                            f"{tech_name}.electricity",
                            f"financials_group_{group_id}.electricity_sum.electricity_{tech_name}",
                        )

                # Connect total electricity produced to the financial group
                self.plant.connect(
                    f"financials_group_{group_id}.electricity_sum.total_electricity_produced",
                    f"financials_group_{group_id}.total_electricity_produced",
                )

                for tech_name in tech_configs.keys():
                    self.plant.connect(
                        f"{tech_name}.CapEx", f"financials_group_{group_id}.capex_{tech_name}"
                    )
                    self.plant.connect(
                        f"{tech_name}.OpEx", f"financials_group_{group_id}.opex_{tech_name}"
                    )

                    if "electrolyzer" in tech_name:
                        self.plant.connect(
                            f"{tech_name}.total_hydrogen_produced",
                            f"financials_group_{group_id}.total_hydrogen_produced",
                        )
                        self.plant.connect(
                            f"{tech_name}.time_until_replacement",
                            f"financials_group_{group_id}.time_until_replacement",
                        )

                    if "ammonia" in tech_name:
                        self.plant.connect(
                            f"{tech_name}.total_ammonia_produced",
                            f"financials_group_{group_id}.total_ammonia_produced",
                        )

        self.plant.options["auto_order"] = True

        # Check if there are any connections FROM a financial group to ammonia
        # This handles the case where LCOH is computed in the financial group and passed to ammonia
        for connection in technology_interconnections:
            if connection[0].startswith("financials_group_") and connection[1] == "ammonia":
                # If the connection is from a financial group, set solvers for the
                # plant to resolve the coupling
                self.plant.nonlinear_solver = om.NonlinearBlockGS()
                self.plant.linear_solver = om.DirectSolver()
                break

        if pyxdsm is not None:
            create_xdsm_from_config(self.plant_config)

    def create_driver_model(self):
        """
        Add the driver to the OpenMDAO model.
        """
        if "driver" in self.driver_config:
            myopt = PoseOptimization(self.driver_config)
            myopt.set_driver(self.prob)
            myopt.set_objective(self.prob)
            myopt.set_design_variables(self.prob)
            myopt.set_constraints(self.prob)

    def run(self):
        # do model setup based on the driver config
        # might add a recorder, driver, set solver tolerances, etc

        # Add a recorder if specified in the driver config
        if "recorder" in self.driver_config:
            recorder_config = self.driver_config["recorder"]
            recorder = om.SqliteRecorder(recorder_config["file"])
            self.model.add_recorder(recorder)

        self.prob.setup()

        self.prob.run_driver()

    def post_process(self):
        self.prob.model.list_inputs(units=True)
        self.prob.model.list_outputs(units=True)
