from typing import Any
from collections import OrderedDict

import attrs
import numpy as np
from attrs import Attribute, define


try:
    from pyxdsm.XDSM import FUNC, XDSM
except ImportError:
    pass


def create_xdsm_from_config(config, output_file="connections_xdsm"):
    """
    Create an XDSM diagram from a given plant configuration and save it to a pdf file.

    Parameters
    ----------
    config : dict
        Configuration dictionary containing technology interconnections.
    output_file : str, optional
        The name of the output file where the XDSM diagram will be saved.
    """
    # Create an XDSM object
    x = XDSM(use_sfmath=True)

    # Use an OrderedDict to keep the order of technologies
    technologies = OrderedDict()
    if "technology_interconnections" not in config:
        return

    for conn in config["technology_interconnections"]:
        technologies[conn[0]] = None  # Source
        technologies[conn[1]] = None  # Destination

    # Add systems to the XDSM
    for tech in technologies.keys():
        tech_label = tech.replace("_", r"\_")
        x.add_system(tech, FUNC, rf"\text{{{tech_label}}}")

    # Add connections
    for conn in config["technology_interconnections"]:
        if len(conn) == 3:
            source, destination, data = conn
            connection_label = data
        else:
            source, destination, data, label = conn

        source.replace("_", r"\_")
        destination.replace("_", r"\_")
        connection_label = rf"\text{{{data} {'via'} {label}}}"

        x.connect(source, destination, connection_label)

    # Write the diagram to a file
    x.write(output_file, quiet=True)
    print(f"XDSM diagram written to {output_file}.tex")


def merge_inputs(dict1, dict2):
    """Merges two dictionaries and raises ValueError if duplicate keys exist."""
    common_keys = dict1.keys() & dict2.keys()
    if common_keys:
        raise ValueError(
            f"Duplicate parameters found: {', '.join(common_keys)}. "
            f"Please define parameters only once in the shared, performance, and cost dictionaries."
        )
    return {**dict1, **dict2}


def merge_shared_performance_inputs(config):
    """Merges two dictionaries and raises ValueError if duplicate keys exist."""
    if "performance_parameters" in config.keys() and "shared_parameters" in config.keys():
        common_keys = config["performance_parameters"].keys() & config["shared_parameters"].keys()
        if common_keys:
            raise ValueError(
                f"Duplicate parameters found: {', '.join(common_keys)}. "
                f"Please define parameters only once in the shared and performance dictionaries."
            )
        return {**config["performance_parameters"], **config["shared_parameters"]}
    elif "shared_parameters" not in config.keys():
        return config["performance_parameters"]
    else:
        return config["shared_parameters"]


def merge_shared_cost_inputs(config):
    """Merges two dictionaries and raises ValueError if duplicate keys exist."""
    if "cost_parameters" in config.keys() and "shared_parameters" in config.keys():
        common_keys = config["cost_parameters"].keys() & config["shared_parameters"].keys()
        if common_keys:
            raise ValueError(
                f"Duplicate parameters found: {', '.join(common_keys)}. "
                f"Please define parameters only once in the shared and cost dictionaries."
            )
        return {**config["cost_parameters"], **config["shared_parameters"]}
    elif "shared_parameters" not in config.keys():
        return config["cost_parameters"]
    else:
        return config["shared_parameters"]


@define
class BaseConfig:
    """
    A Mixin class to allow for kwargs overloading when a data class doesn't
    have a specific parameter defined. This allows passing of larger dictionaries
    to a data class without throwing an error.
    """

    @classmethod
    def from_dict(cls, data: dict, strict=True):
        """Maps a data dictionary to an `attr`-defined class.

        TODO: Add an error to ensure that either none or all the parameters are passed in

        Args:
            data : dict
                The data dictionary to be mapped.
            strict: bool
                A flag enabling strict parameter processing, meaning that no extra parameters
                    may be passed in or an AttributeError will be raised.
        Returns:
            cls
                The `attr`-defined class.
        """
        # Check for any inputs that aren't part of the class definition
        if strict is True:
            class_attr_names = [a.name for a in cls.__attrs_attrs__]
            extra_args = [d for d in data if d not in class_attr_names]
            if len(extra_args):
                raise AttributeError(
                    f"The initialization for {cls.__name__} \
                        was given extraneous inputs: {extra_args}"
                )

        kwargs = {a.name: data[a.name] for a in cls.__attrs_attrs__ if a.name in data and a.init}

        # Map the inputs must be provided: 1) must be initialized, 2) no default value defined
        required_inputs = [
            a.name for a in cls.__attrs_attrs__ if a.init and a.default is attrs.NOTHING
        ]
        undefined = sorted(set(required_inputs) - set(kwargs))

        if undefined:
            raise AttributeError(
                f"The class definition for {cls.__name__} is missing the following inputs: "
                f"{undefined}"
            )
        return cls(**kwargs)

    def as_dict(self) -> dict:
        """Creates a JSON and YAML friendly dictionary that can be save for future reloading.
        This dictionary will contain only `Python` types that can later be converted to their
        proper `Turbine` formats.

        Returns:
            dict: All key, value pairs required for class re-creation.
        """
        return attrs.asdict(self, filter=attr_hopp_filter, value_serializer=attr_serializer)


def attr_serializer(inst: type, field: Attribute, value: Any):
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def attr_hopp_filter(inst: Attribute, value: Any) -> bool:
    if inst.init is False:
        return False
    if value is None:
        return False
    if isinstance(value, np.ndarray):
        if value.size == 0:
            return False
    return True
