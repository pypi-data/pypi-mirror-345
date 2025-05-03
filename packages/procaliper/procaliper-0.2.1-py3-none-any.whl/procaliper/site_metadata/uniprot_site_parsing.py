from __future__ import annotations

from typing import Any

"""
Module for parsing UniProt site annotations.
"""


class SiteAnnotations:
    """Class for parsing and storing UniProt site annotations.

    An example of a UniProt site annotation:

    `DISULFID 28..87; /evidence="ECO:0000255|PROSITE-ProRule:PRU00114"; DISULFID 105; /note="Interchain (with heavy chain)"`

    Attributes:
        residue_letter (list[str]): A list of amino acid letters.
        residue_number (list[int]): A list of residue numbers.
        binding (list[bool]): A list of booleans indicating whether a residue
            is a binding site.
        active (list[bool]): A list of booleans indicating whether a residue
            is an active site.
        ptm (list[bool]): A list of booleans indicating whether a residue
            is reported to be post-translationally modified.
        dna_binding (list[bool]): A list of booleans indicating whether a residue
            is a DNA binding site.
        disulfide_bond (list[bool]): A list of booleans indicating whether a residue
            is a disulfide bond.
        helix (list[bool]): A list of booleans indicating whether a residue
            is in a helix.
        turn (list[bool]): A list of booleans indicating whether a residue
            is in a turn.
        beta_strand (list[bool]): A list of booleans indicating whether a residue
            is in a beta strand.
        binding_data (list[dict[str, str]]): A list of dictionaries containing
            binding site metadata.
        active_data (list[dict[str, str]]): A list of dictionaries containing
            active site metadata.
        ptm_data (list[dict[str, str]]): A list of dictionaries containing
            post-translationally modified site metadata.
        regions (dict[str,list[int]]): A dictionary mapping region names to lists
            of (zero-indexed) residue numbers.
        region_data (dict[str,str]): A dictionary mapping region names to annotation data.
        domains (dict[str,list[int]]): A dictionary mapping domain names to lists
            of (zero-indexed) residue numbers.
        domain_data (dict[str,str]): A dictionary mapping domain names to annotation data.
    """

    fields_by_description_type: dict[str, list[str]] = {
        "BINDING": ["ligand"],
        "ACT_SITE": ["note"],
        "MOD_RES": ["note"],
        "REGION": ["note"],
        "DOMAIN": ["note"],
        "DNA_BIND": [],
        "DISULFID": [],
        "HELIX": [],
        "TURN": [],
        "STRAND": [],
    }

    def __init__(self, sequence: str) -> None:
        """Instantiates a SiteAnnotations object from a string of amino acid letters.

        It is recommended to call `SiteAnnotations.extract_annotation` after instantiating.
        Before that, the `SiteAnnotations` object contains only default values.

        Args:
            sequence (str): A string of amino acid letters. See
                `type_aliases.AminoAcidLetter` for valid letters.
        """
        self.residue_letter: list[str] = list(sequence)
        self.residue_number: list[int] = list(range(1, len(sequence) + 1))
        self.binding: list[bool] = [False] * len(sequence)
        self.active: list[bool] = [False] * len(sequence)
        self.ptm: list[bool] = [False] * len(sequence)
        self.dna_binding: list[bool] = [False] * len(sequence)
        self.disulfide_bond: list[bool] = [False] * len(sequence)
        self.helix: list[bool] = [False] * len(sequence)
        self.turn: list[bool] = [False] * len(sequence)
        self.beta_strand: list[bool] = [False] * len(sequence)

        self.binding_data: list[dict[str, str]] = [{} for _ in range(len(sequence))]
        self.active_data: list[dict[str, str]] = [{} for _ in range(len(sequence))]
        self.ptm_data: list[dict[str, str]] = [{} for _ in range(len(sequence))]

        self.regions: dict[str, list[int]] = {}
        self.region_data: dict[str, dict[str, str]] = {}

        self.domains: dict[str, list[int]] = {}
        self.domain_data: dict[str, dict[str, str]] = {}

    def table(self) -> dict[str, list[Any]]:
        """Return a dictionary of the data in the SiteAnnotations object.

        Returns:
            dict[str, list[Any]]: Each key is a site annotation feature name.
                Each value is a list of the values for that feature.
        """
        tbl: dict[str, list[Any]] = {}

        tbl["residue_letter"] = self.residue_letter
        tbl["residue_number"] = self.residue_number
        tbl["binding"] = self.binding
        tbl["active"] = self.active
        tbl["ptm"] = self.ptm
        tbl["dna_binding"] = self.dna_binding
        tbl["disulfide_bond"] = self.disulfide_bond
        tbl["helix"] = self.helix
        tbl["turn"] = self.turn
        tbl["beta_strand"] = self.beta_strand
        tbl["binding_data"] = self.binding_data
        tbl["active_data"] = self.active_data
        tbl["ptm_data"] = self.ptm_data

        return tbl

    def __len__(self) -> int:
        return len(self.residue_letter)

    def _parse_description(
        self,
        description_type: str,
        description: str,
        extract_metadata: bool | None = None,
    ) -> tuple[list[bool], list[dict[str, str]] | None]:
        # example of descrition:
        # DISULFID 28..87; /evidence="ECO:0000255|PROSITE-ProRule:PRU00114"; DISULFID 105; /note="Interchain (with heavy chain)"

        site_matches = [False] * len(self)

        site_data: list[dict[str, str]] | None = None

        if extract_metadata is None:
            extract_metadata = bool(self.fields_by_description_type[description_type])
        if extract_metadata:
            site_data = [{} for _ in range(len(self))]

        if description_type not in self.fields_by_description_type:
            raise NotImplementedError(f"Unknown description type: {description_type}")
        if (
            not description or description != description
        ):  # not-equal check is for pandas nans
            return site_matches, site_data
        if description_type not in description:
            raise ValueError(
                f"{description_type} does not appear in the description: {description}"
            )

        stretches = description.split(description_type)

        # first stretch is always empty
        for stretch in stretches[1:]:
            fields = stretch.split(";")
            # first field is always site numbers
            se = fields[0].strip().split("..")
            start, end = len(self), len(self)
            if len(se) not in (1, 2):
                raise ValueError(
                    f"Unable to parse site numbers {se} in {stretch} from {description}"
                )
            se_start = se[0].split(":")[-1]

            if len(se) == 1:
                start, end = (
                    int(se_start) - 1,
                    int(se_start) - 1,
                )  # uniprot 1-indexes sites
            else:
                start, end = int(se_start) - 1, int(se[1]) - 1

            if start >= len(self) or end >= len(self) or start > end:
                raise ValueError(
                    f"Improperly formatted descritpion; site numbers not recognized: {stretch} in {description}"
                )

            field_sites = list(range(start, end + 1))
            for s in field_sites:
                site_matches[s] = True
                if se[0] != se_start and extract_metadata:
                    # site_data is populated if extract_metadata is True
                    # mypy does not catch this
                    site_data[s]["isoform"] = se[0].split(":")[0]  # type: ignore

            if len(fields) == 1 or site_data is None:
                continue

            for field in fields[1:]:
                field = field.strip()
                for field_id in self.fields_by_description_type[description_type]:
                    if not field.startswith(f"/{field_id}="):
                        continue
                    field_data = field.removeprefix(f"/{field_id}=")
                    for s in field_sites:
                        if field_id not in site_data[s]:
                            site_data[s][field_id] = field_data
                        else:
                            site_data[s][field_id] += "," + field_data

        return site_matches, site_data

    def _region_parsing(self, description: str) -> None:
        region_annotations = description.split("REGION ")[1:]
        self.regions = {}
        self.region_data = {}
        for region_index, x in enumerate(region_annotations):
            r = f"r_{region_index}"
            fields = x.split(";")
            self.regions[r] = list(
                range(
                    int(fields[0].split("..")[0]) - 1,
                    int(fields[0].split("..")[1]),
                )
            )
            self.region_data[r] = {}
            for field in fields[1:]:
                field = field.strip()
                for field_id in self.fields_by_description_type["REGION"]:
                    if not field.startswith(f"/{field_id}="):
                        continue
                    field_data = field.removeprefix(f"/{field_id}=")
                    if field_id not in self.region_data[r]:
                        self.region_data[r][field_id] = field_data
                    else:
                        self.region_data[r][field_id] += "," + field_data

    def _domain_parsing(self, description: str) -> None:
        domain_annotations = description.split("DOMAIN ")[1:]
        self.domains = {}
        self.domain_data = {}
        for domain_index, x in enumerate(domain_annotations):
            r = f"d_{domain_index}"
            fields = x.split(";")
            self.domains[r] = list(
                range(
                    int(fields[0].split("..")[0]) - 1,
                    int(fields[0].split("..")[1]),
                )
            )
            self.domain_data[r] = {}
            for field in fields[1:]:
                field = field.strip()
                for field_id in self.fields_by_description_type["DOMAIN"]:
                    if not field.startswith(f"/{field_id}="):
                        continue
                    field_data = field.removeprefix(f"/{field_id}=")
                    if field_id not in self.domain_data[r]:
                        self.domain_data[r][field_id] = field_data
                    else:
                        self.domain_data[r][field_id] += "," + field_data

    def extract_annotation(
        self,
        description_type: str,
        description: str,
        extract_metadata: bool | None = None,
    ) -> None:
        """Extracts the site annotations from the description.

        Args:
            description_type (str): The type of site annotation to extract. Must be
                one of the keys in `self.fields_by_description_type`.
            description (str): The UniProt site description string.
            extract_metadata (bool | None, optional): Whether to extract metadata.
                By default, this is inferred from the `description_type` parameter.

        Raises:
            NotImplementedError: From `_parse_description`. If an unknown `description_type` is provided.
            ValueError: From `_parse_description`. If the `description_type` is not found in `description`.
            AssertionError: If a `description_type` is provided that is known to `_parse_description` but
                not `extract_annotation`. This indicates an internal bug and should be reported.
        """
        # regions are a special case because they can overlap
        if description_type == "REGION":
            self._region_parsing(description)
            return
        if description_type == "DOMAIN":
            self._domain_parsing(description)
            return

        matches, data = self._parse_description(
            description_type, description, extract_metadata
        )
        if description_type == "ACT_SITE":
            self.active = matches
            if data:
                self.active_data = data
        elif description_type == "BINDING":
            self.binding = matches
            if data:
                self.binding_data = data
        elif description_type == "MOD_RES":
            self.ptm = matches
            if data:
                self.ptm_data = data
        elif description_type == "DNA_BIND":
            self.dna_binding = matches
        elif description_type == "DISULFID":
            self.disulfide_bond = matches
        elif description_type == "STRAND":
            self.beta_strand = matches
        elif description_type == "HELIX":
            self.helix = matches
        elif description_type == "TURN":
            self.turn = matches
        else:
            raise AssertionError(
                f"If this is raised, the description type {description_type} is only partially handled. Please file an issue."
            )
