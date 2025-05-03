import numpy as np
import openmdao.api as om
from attrs import field, define

from h2integrate.core.utilities import BaseConfig, merge_shared_performance_inputs


# TODO: fix import structure in future refactor


from h2integrate.simulation.technologies.hydrogen.h2_storage.storage_sizing import hydrogen_storage_capacity  # noqa: E501  # fmt: skip  # isort:skip
from h2integrate.simulation.technologies.hydrogen.h2_storage.salt_cavern.salt_cavern import SaltCavernStorage  # noqa: E501  # fmt: skip  # isort:skip
from h2integrate.simulation.technologies.hydrogen.h2_storage.lined_rock_cavern.lined_rock_cavern import LinedRockCavernStorage  # noqa: E501  # fmt: skip  # isort:skip


@define
class H2StorageModelConfig(BaseConfig):
    rating: float = field(default=640)
    size_capacity_from_demand: dict = field(default={"flag": True})
    capacity_from_max_on_turbine_storage: bool = field(default=False)
    type: str = field(default="salt_cavern")
    days: int = field(default=0)


class H2Storage(om.ExplicitComponent):
    def initialize(self):
        self.options.declare("tech_config", types=dict)
        self.options.declare("plant_config", types=dict)
        self.options.declare("verbose", types=bool, default=True)

    def setup(self):
        self.config = H2StorageModelConfig.from_dict(
            merge_shared_performance_inputs(self.options["tech_config"]["model_inputs"])
        )
        self.add_input(
            "hydrogen_input",
            val=0.0,
            shape_by_conn=True,
            copy_shape="hydrogen_output",
            units="kg/h",
        )
        self.add_input("efficiency", val=0.0, desc="Average efficiency of the electrolyzer")

        self.add_output(
            "hydrogen_output",
            val=0.0,
            shape_by_conn=True,
            copy_shape="hydrogen_input",
            units="kg/h",
        )
        self.add_output("CapEx", val=0.0, units="USD", desc="Capital expenditure")
        self.add_output("OpEx", val=0.0, units="USD/year", desc="Operational expenditure")

    def compute(self, inputs, outputs):
        self.options["tech_config"]
        ########### initialize output dictionary ###########
        h2_storage_results = {}

        storage_max_fill_rate = np.max(inputs["hydrogen_input"])

        ########### get hydrogen storage size in kilograms ###########
        ##################### no hydrogen storage
        if self.config.type == "none":
            h2_storage_capacity_kg = 0.0
            storage_max_fill_rate = 0.0

        ##################### get storage capacity from hydrogen storage demand
        elif self.config.size_capacity_from_demand["flag"]:
            hydrogen_storage_demand = np.mean(
                inputs["hydrogen_input"]
            )  # TODO: update demand based on end-use needs
            results_dict = {
                "Hydrogen Hourly Production [kg/hr]": inputs["hydrogen_input"],
                "Sim: Average Efficiency [%-HHV]": inputs["efficiency"],
            }
            (
                hydrogen_demand_kgphr,
                hydrogen_storage_capacity_kg,
                hydrogen_storage_duration_hr,
                hydrogen_storage_soc,
            ) = hydrogen_storage_capacity(
                results_dict,
                self.config.rating,
                hydrogen_storage_demand,
            )
            h2_storage_capacity_kg = hydrogen_storage_capacity_kg
            h2_storage_results["hydrogen_storage_duration_hr"] = hydrogen_storage_duration_hr
            h2_storage_results["hydrogen_storage_soc"] = hydrogen_storage_soc

        ##################### get storage capacity based on storage days in config
        else:
            storage_hours = self.config.days * 24
            h2_storage_capacity_kg = round(storage_hours * storage_max_fill_rate)

        h2_storage_results["h2_storage_capacity_kg"] = h2_storage_capacity_kg
        h2_storage_results["h2_storage_max_fill_rate_kg_hr"] = storage_max_fill_rate

        ########### run specific hydrogen storage models for costs and energy use ###########
        if self.config.type == "none":
            h2_storage_results["storage_capex"] = 0.0
            h2_storage_results["storage_opex"] = 0.0
            h2_storage_results["storage_energy"] = 0.0

            h2_storage = None

        elif self.config.type == "salt_cavern":
            # initialize dictionary for salt cavern storage parameters
            storage_input = {}

            # pull parameters from plant_config file
            storage_input["h2_storage_kg"] = h2_storage_capacity_kg
            storage_input["system_flow_rate"] = storage_max_fill_rate
            storage_input["model"] = "papadias"

            # run salt cavern storage model
            h2_storage = SaltCavernStorage(storage_input)

            h2_storage.salt_cavern_capex()
            h2_storage.salt_cavern_opex()

            h2_storage_results["storage_capex"] = h2_storage.output_dict[
                "salt_cavern_storage_capex"
            ]
            h2_storage_results["storage_opex"] = h2_storage.output_dict["salt_cavern_storage_opex"]
            h2_storage_results["storage_energy"] = 0.0

        elif self.config.type == "lined_rock_cavern":
            # initialize dictionary for salt cavern storage parameters
            storage_input = {}

            # pull parameters from plat_config file
            storage_input["h2_storage_kg"] = h2_storage_capacity_kg
            storage_input["system_flow_rate"] = storage_max_fill_rate
            storage_input["model"] = "papadias"

            # run salt cavern storage model
            h2_storage = LinedRockCavernStorage(storage_input)

            h2_storage.lined_rock_cavern_capex()
            h2_storage.lined_rock_cavern_opex()

            h2_storage_results["storage_capex"] = h2_storage.output_dict[
                "lined_rock_cavern_storage_capex"
            ]
            h2_storage_results["storage_opex"] = h2_storage.output_dict[
                "lined_rock_cavern_storage_opex"
            ]
            h2_storage_results["storage_energy"] = 0.0
        else:
            msg = (
                "H2 storage type %s was given, but must be one of ['none', 'turbine', 'pipe',"
                " 'pressure_vessel', 'salt_cavern', 'lined_rock_cavern']"
            )
            raise ValueError(msg)

        if self.options["verbose"]:
            print("\nH2 Storage Results:")
            print("H2 storage capex: ${:,.0f}".format(h2_storage_results["storage_capex"]))
            print("H2 storage annual opex: ${:,.0f}/yr".format(h2_storage_results["storage_opex"]))
            print(
                "H2 storage capacity (metric tons): ",
                h2_storage_results["h2_storage_capacity_kg"] / 1000,
            )
            if h2_storage_results["h2_storage_capacity_kg"] > 0:
                print(
                    "H2 storage cost $/kg of H2: ",
                    h2_storage_results["storage_capex"]
                    / h2_storage_results["h2_storage_capacity_kg"],
                )

        outputs["CapEx"] = h2_storage_results["storage_capex"]
        outputs["OpEx"] = h2_storage_results["storage_opex"]

        # For now, pass through hydrogen
        outputs["hydrogen_output"] = inputs["hydrogen_input"]
