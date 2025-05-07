#!/usr/bin/env python3

"""Module containing the Pdbmerge class and the command line interface."""

import argparse
import os
import zipfile
from pathlib import Path
from typing import Optional

from biobb_common.configuration import settings
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger


class Pdbmerge(BiobbObject):
    """
    | biobb_pdb_tools Pdbmerge
    | Merges several PDB files into one.
    | This tool merges several PDB files into one. It can be used to merge several PDB files into one.

    Args:
        input_file_path (str): ZIP file of selected protein. File type: input. `Sample file <https://raw.githubusercontent.com/bioexcel/biobb_pdb_tools/master/biobb_pdb_tools/test/data/pdb_tools/input_pdb_merge.pdb>`_. Accepted formats: zip (edam:format_3987).
        output_file_path (str): PDB file with input PDBs merged. File type: output. `Sample file <https://raw.githubusercontent.com/bioexcel/biobb_pdb_tools/master/biobb_pdb_tools/test/reference/pdb_tools/ref_pdb_merge.pdb>`_. Accepted formats: pdb (edam:format_1476).
        properties (dic):
            * **binary_path** (*str*) - ("pdb_merge") Path to the pdb_merge executable binary.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.

    Examples:
        This is a use example of how to use the building block from Python::

            from biobb_pdb_tools.pdb_tools.biobb_pdb_merge import biobb_pdb_merge

            biobb_pdb_merge(input_file_path='/path/to/input1.zip',
                    output_file_path='/path/to/output.pdb')

    Info:
        * wrapped_software:
            * name: pdb_tools
            * version: >=2.5.0
            * license: Apache-2.0
        * ontology:
            * name: EDAM
            * schema: http://edamontology.org/EDAM.owl

    """

    def __init__(
        self, input_file_path, output_file_path, properties=None, **kwargs
    ) -> None:
        properties = properties or {}

        super().__init__(properties)
        self.locals_var_dict = locals().copy()

        self.io_dict = {
            "in": {"input_file_path": input_file_path},
            "out": {"output_file_path": output_file_path},
        }

        self.binary_path = properties.get("binary_path", "pdb_merge")
        self.properties = properties

        self.check_properties(properties)
        self.check_arguments()

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`Pdbmerge <biobb_pdb_tools.pdb_tools.pdb_merge>` object."""

        if self.check_restart():
            return 0
        self.stage_files()

        input_file_path = self.stage_io_dict["in"]["input_file_path"]
        folder_path = os.path.dirname(input_file_path)

        if zipfile.is_zipfile(input_file_path):
            with zipfile.ZipFile(input_file_path, "r") as zip_ref:
                zip_ref.extractall(folder_path)

            pdb_files = [
                file
                for file in os.listdir(folder_path)
                if file.lower().endswith(".pdb")
            ]

            input_file_list = [os.path.join(folder_path, file) for file in pdb_files]

            input_file_list = [Path(i) for i in input_file_list]
            input_file_list = sorted(input_file_list, key=lambda i: i.stem.upper())
            input_file_list = [str(i) for i in input_file_list]

            self.cmd = [
                self.binary_path,
                *input_file_list,
                ">",
                self.io_dict["out"]["output_file_path"],
            ]

        else:
            fu.log(
                f"The archive {input_file_path} is not a ZIP!",
                self.out_log,
                self.global_log,
            )

        fu.log(" ".join(self.cmd), self.out_log, self.global_log)

        fu.log(
            "Creating command line with instructions and required arguments",
            self.out_log,
            self.global_log,
        )

        self.run_biobb()
        self.copy_to_host()

        self.tmp_files.extend([self.stage_io_dict.get("unique_dir", "")])
        self.remove_tmp_files()
        self.check_arguments(output_files_created=True, raise_exception=False)

        return self.return_code


def biobb_pdb_merge(
    input_file_path: str,
    output_file_path: str,
    properties: Optional[dict] = None,
    **kwargs,
) -> int:
    """Create :class:`Pdbmerge <biobb_pdb_tools.pdb_tools.pdb_merge>` class and
    execute the :meth:`launch() <biobb_pdb_tools.pdb_tools.pdb_merge.launch>` method."""
    return Pdbmerge(
        input_file_path=input_file_path,
        output_file_path=output_file_path,
        properties=properties,
        **kwargs,
    ).launch()

biobb_pdb_merge.__doc__ = Pdbmerge.__doc__


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(
        description="Merges several PDB files into one.",
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
    )
    parser.add_argument("--config", required=True, help="Configuration file")

    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument(
        "--input_file_path",
        required=True,
        help="Description for the first input file path. Accepted formats: pdb.",
    )
    required_args.add_argument(
        "--output_file_path",
        required=True,
        help="Description for the output file path. Accepted formats: zip.",
    )

    args = parser.parse_args()
    args.config = args.config or "{}"
    properties = settings.ConfReader(config=args.config).get_prop_dic()
    biobb_pdb_merge(
        input_file_path=args.input_file_path,
        output_file_path=args.output_file_path,
        properties=properties,
    )


if __name__ == "__main__":
    main()
