from procaliper import Protein
from procaliper.site_metadata import SiteAnnotations


def test_site_annotations_without_data() -> None:
    test_description = 'DISULFID 28..87; /evidence="ECO:0000255|PROSITE-ProRule:PRU00114"; DISULFID 105; /note="Interchain (with heavy chain)"'
    sequence = "x" * 110  # does not matter for this test

    EXPECTED = [(28 <= i <= 87) or (i == 105) for i in range(1, len(sequence) + 1)]

    sa = SiteAnnotations(sequence)

    sa.extract_annotation("DISULFID", test_description)

    assert sa.disulfide_bond == EXPECTED


def test_site_annotations_with_data() -> None:
    test_description = 'ACT_SITE 88; /note="Glycyl thioester intermediate"; /evidence="ECO:0000255|PROSITE-ProRule:PRU00388, ECO:0000269|PubMed:24000165"'
    sequence = "x" * 110  # does not matter for this test

    EXPECTED_MATCH = [(i == 88) for i in range(1, len(sequence) + 1)]
    EXPECTED_DATA = [
        {} if i != 88 else {"note": '"Glycyl thioester intermediate"'}
        for i in range(1, len(sequence) + 1)
    ]

    sa = SiteAnnotations(sequence)

    sa.extract_annotation("ACT_SITE", test_description)

    assert sa.active == EXPECTED_MATCH
    assert sa.active_data == EXPECTED_DATA

    test_description2 = 'BINDING 461; /ligand="heme"; /ligand_id="ChEBI:CHEBI:30413"; /ligand_part="Fe"; /ligand_part_id="ChEBI:CHEBI:18248"; /note="axial binding residue"; /evidence="ECO:0000250|UniProtKB:P10635"'
    sequence2 = "x" * 500
    EXPECTED_MATCH2 = [(i == 461) for i in range(1, len(sequence2) + 1)]
    EXPECTED_DATA2 = [
        {} if i != 461 else {"ligand": '"heme"'} for i in range(1, len(sequence2) + 1)
    ]
    sa2 = SiteAnnotations(sequence2)

    sa2.extract_annotation("BINDING", test_description2)

    assert sa2.binding == EXPECTED_MATCH2
    assert sa2.binding_data == EXPECTED_DATA2


def test_ptm_annotation() -> None:
    PTM_SITES_ONE_INDEXED = [
        5,
        7,
        58,
        84,
        231,
        252,
        263,
        313,
        443,
        453,
        458,
        476,
        489,
        492,
        585,
        598,
        641,
    ]

    protein = Protein.from_uniprot_id("P07900")

    exctracted_ptm_sites_one_indexed = [
        i + 1 for i, x in enumerate(protein.site_annotations.ptm) if x
    ]
    assert exctracted_ptm_sites_one_indexed == PTM_SITES_ONE_INDEXED


def test_region_annotation() -> None:
    REGION_SITES_BOUNDS_ONE_INDEXED_INCLUSIVE = [
        [9, 236],
        [225, 278],
        [271, 616],
        [284, 732],
        [284, 620],
        [628, 731],
        [682, 732],
        [700, 732],
        [728, 732],
        [729, 732],
    ]
    REGION_SITES = {
        f"r_{i}": list(range(a - 1, b))
        for i, (a, b) in enumerate(REGION_SITES_BOUNDS_ONE_INDEXED_INCLUSIVE)
    }

    protein = Protein.from_uniprot_id("P07900")

    assert protein.site_annotations.regions == REGION_SITES
