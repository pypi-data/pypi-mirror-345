import pandas as pd

from procaliper import Protein

TEST_DATA_PATH = (
    "tests/test_data/uniprotkb_Human_AND_model_organism_9606_2024_08_07.tsv"
)


def test_read_uniprot_row() -> None:
    COMPARISON_ENTRY_1 = "A0A0B4J2F0"
    COMPARISON_SEQUENCE_1 = "MFRRLTFAQLLFATVLGIAGGVYIFQPVFEQYAKDQKELKEKMQLVQESEEKKS"

    COMPARISON_ENTRY_2 = "A0A0K2S4Q6"
    COMPARISON_DISULFIDE_2 = list(range(43, 111 + 1))  # 43..111, expand = True
    # STRAND 79..81; /evidence="ECO:0007829|PDB:7EMF"	HELIX 83..86; /evidence="ECO:0007829|PDB:7EMF"; HELIX 90..96; /evidence="ECO:0007829|PDB:7EMF"; HELIX 112..116; /evidence="ECO:0007829|PDB:7EMF"; HELIX 128..138; /evidence="ECO:0007829|PDB:7EMF"; HELIX 147..152; /evidence="ECO:0007829|PDB:7EMF"
    COMPARISON_ENTRY_3 = "A0JLT2"
    COMPARISON_STRAND = [79, 80, 81]
    COMPARISON_HELIX = (
        [83, 84, 85, 86]
        + [90, 91, 92, 93, 94, 95, 96]
        + [112, 113, 114, 115, 116]
        + [128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138]
        + [147, 148, 149, 150, 151, 152]
    )
    COMPARISON_TURN = [117, 118, 119]

    df = pd.read_csv(
        TEST_DATA_PATH,
        sep="\t",
        nrows=20,
    )

    assert df is not None

    for _, row in df.iterrows():
        protein = Protein.from_uniprot_row(row)  # type: ignore

        assert protein is not None

        if protein.data["entry"] == COMPARISON_ENTRY_1:
            assert protein.data["sequence"] == COMPARISON_SEQUENCE_1

        if protein.data["entry"] == COMPARISON_ENTRY_2:
            assert protein.site_annotations is not None
            dbonds = protein.site_annotations.disulfide_bond
            assert dbonds is not None
            left = [i + 1 for i, v in enumerate(dbonds) if v]
            assert left == COMPARISON_DISULFIDE_2

        if protein.data["entry"] == COMPARISON_ENTRY_3:
            assert protein.site_annotations is not None
            strand = protein.site_annotations.beta_strand
            assert strand is not None
            left = [i + 1 for i, v in enumerate(strand) if v]
            assert left == COMPARISON_STRAND

            helix = protein.site_annotations.helix
            assert helix is not None
            left = [i + 1 for i, v in enumerate(helix) if v]
            assert left == COMPARISON_HELIX

            turn = protein.site_annotations.turn
            assert turn is not None
            left = [i + 1 for i, v in enumerate(turn) if v]
            assert left == COMPARISON_TURN


def test_unravel() -> None:
    TEST_HEADER = "Entry	Reviewed	Entry Name	Protein names	Gene Names	Organism	Length	Sequence	Active site	Binding site	DNA binding	Disulfide bond	Beta strand	Helix	Turn"
    TEST_ROW = "A0A0B4J2F0	reviewed	PIOS1_HUMAN	Protein PIGBOS1 (PIGB opposite strand protein 1)	PIGBOS1	Homo sapiens (Human)	54	MFRRLTFAQLLFATVLGIAGGVYIFQPVFEQYAKDQKELKEKMQLVQESEEKKS							"

    row_dict = {k: v for k, v in zip(TEST_HEADER.split("\t"), TEST_ROW.split("\t"))}
    protein = Protein.from_uniprot_row(row_dict)
    print(protein.data.keys())
    unravelled = protein.unravel_sites(
        selected_aas={"M"},
        selected_keys={"entry", "turn", "residue_letter", "residue_number"},
    )

    expected = {
        "entry": ["A0A0B4J2F0", "A0A0B4J2F0"],
        "turn": [False, False],
        "residue_letter": ["M", "M"],
        "residue_number": [1, 43],
    }

    assert unravelled == expected


def test_unravel_with_custom_sites() -> None:
    TEST_HEADER = "Entry	Reviewed	Entry Name	Protein names	Gene Names	Organism	Length	Sequence	Active site	Binding site	DNA binding	Disulfide bond	Beta strand	Helix	Turn"
    TEST_ROW = "A0A0B4J2F0	reviewed	PIOS1_HUMAN	Protein PIGBOS1 (PIGB opposite strand protein 1)	PIGBOS1	Homo sapiens (Human)	54	MFRRLTFAQLLFATVLGIAGGVYIFQPVFEQYAKDQKELKEKMQLVQESEEKKS							"

    row_dict = {k: v for k, v in zip(TEST_HEADER.split("\t"), TEST_ROW.split("\t"))}
    protein = Protein.from_uniprot_row(row_dict)
    print(protein.data.keys())

    seq = "MFRRLTFAQLLFATVLGIAGGVYIFQPVFEQYAKDQKELKEKMQLVQESEEKKS"
    fake_data = [ord(s) + 1 for s in seq]
    protein.add_custom_site_data_column("nonsense", fake_data)

    unravelled = protein.unravel_sites(
        selected_aas={"M"},
        selected_keys={"entry", "turn", "residue_letter", "residue_number", "nonsense"},
    )

    expected = {
        "entry": ["A0A0B4J2F0", "A0A0B4J2F0"],
        "turn": [False, False],
        "residue_letter": ["M", "M"],
        "residue_number": [1, 43],
        "nonsense": [fake_data[0], fake_data[42]],
    }

    assert unravelled == expected


def test_read_row_with_site_data() -> None:
    TEST_HEADER = "Entry	Reviewed	Entry Name	Protein names	Gene Names	Organism	Length	Sequence	Active site	Binding site	DNA binding	Disulfide bond	Beta strand	Helix	Turn"
    TEST_ROW = 'A0A0K2S4Q6	reviewed	CD3CH_HUMAN	Protein CD300H (CD300 antigen-like family member H)	CD300H	Homo sapiens (Human)	201	MTQRAGAAMLPSALLLLCVPGCLTVSGPSTVMGAVGESLSVQCRYEEKYKTFNKYWCRQPCLPIWHEMVETGGSEGVVRSDQVIITDHPGDLTFTVTLENLTADDAGKYRCGIATILQEDGLSGFLPDPFFQVQVLVSSASSTENSVKTPASPTRPSQCQGSLPSSTCFLLLPLLKVPLLLSILGAILWVNRPWRTPWTES				DISULFID 43..111; /evidence="ECO:0000255|PROSITE-ProRule:PRU00114"			'

    row_dict = {k: v for k, v in zip(TEST_HEADER.split("\t"), TEST_ROW.split("\t"))}
    protein = Protein.from_uniprot_row(row_dict)

    assert protein.site_annotations is not None

    dbonds = protein.site_annotations.disulfide_bond
    assert dbonds is not None
    assert all(dbonds[42:111])  # 43..111, one-indexed
    assert not any(dbonds[:42]) and not any(dbonds[111:])


def test_read_row_with_binding_site_data() -> None:
    TEST_HEADER = "Entry	Reviewed	Entry Name	Protein names	Gene Names	Organism	Length	Sequence	Active site	Binding site	DNA binding	Disulfide bond	Beta strand	Helix	Turn"
    TEST_ROW = 'A0A087X1C5	reviewed	CP2D7_HUMAN	Putative cytochrome P450 2D7 (EC 1.14.14.1)	CYP2D7	Homo sapiens (Human)	515	MGLEALVPLAMIVAIFLLLVDLMHRHQRWAARYPPGPLPLPGLGNLLHVDFQNTPYCFDQLRRRFGDVFSLQLAWTPVVVLNGLAAVREAMVTRGEDTADRPPAPIYQVLGFGPRSQGVILSRYGPAWREQRRFSVSTLRNLGLGKKSLEQWVTEEAACLCAAFADQAGRPFRPNGLLDKAVSNVIASLTCGRRFEYDDPRFLRLLDLAQEGLKEESGFLREVLNAVPVLPHIPALAGKVLRFQKAFLTQLDELLTEHRMTWDPAQPPRDLTEAFLAKKEKAKGSPESSFNDENLRIVVGNLFLAGMVTTSTTLAWGLLLMILHLDVQRGRRVSPGCPIVGTHVCPVRVQQEIDDVIGQVRRPEMGDQAHMPCTTAVIHEVQHFGDIVPLGVTHMTSRDIEVQGFRIPKGTTLITNLSSVLKDEAVWKKPFRFHPEHFLDAQGHFVKPEAFLPFSAGRRACLGEPLARMELFLFFTSLLQHFSFSVAAGQPRPSHSRVVSFLVTPSPYELCAVPR		BINDING 461; /ligand="heme"; /ligand_id="ChEBI:CHEBI:30413"; /ligand_part="Fe"; /ligand_part_id="ChEBI:CHEBI:18248"; /note="axial binding residue"; /evidence="ECO:0000250|UniProtKB:P10635"					'

    row_dict = {k: v for k, v in zip(TEST_HEADER.split("\t"), TEST_ROW.split("\t"))}
    protein = Protein.from_uniprot_row(row_dict)

    assert protein.site_annotations is not None

    bsite = protein.site_annotations.binding
    assert bsite is not None
    assert bsite[460]


def test_fetch_pdb() -> None:
    TEST_HEADER = "Entry	Reviewed	Entry Name	Protein names	Gene Names	Organism	Length	Sequence	Active site	Binding site	DNA binding	Disulfide bond	Beta strand	Helix	Turn"
    TEST_ROW = "A0A0B4J2F0	reviewed	PIOS1_HUMAN	Protein PIGBOS1 (PIGB opposite strand protein 1)	PIGBOS1	Homo sapiens (Human)	54	MFRRLTFAQLLFATVLGIAGGVYIFQPVFEQYAKDQKELKEKMQLVQESEEKKS							"

    row_dict = {k: v for k, v in zip(TEST_HEADER.split("\t"), TEST_ROW.split("\t"))}
    protein = Protein.from_uniprot_row(row_dict)
    protein.fetch_pdb(save_path="tests/test_data/outputs/test_pdb.pdb")


def test_structure_run_only() -> None:
    TEST_HEADER = "Entry	Reviewed	Entry Name	Protein names	Gene Names	Organism	Length	Sequence	Active site	Binding site	DNA binding	Disulfide bond	Beta strand	Helix	Turn"
    TEST_ROW = "A0A0B4J2F0	reviewed	PIOS1_HUMAN	Protein PIGBOS1 (PIGB opposite strand protein 1)	PIGBOS1	Homo sapiens (Human)	54	MFRRLTFAQLLFATVLGIAGGVYIFQPVFEQYAKDQKELKEKMQLVQESEEKKS							"

    row_dict = {k: v for k, v in zip(TEST_HEADER.split("\t"), TEST_ROW.split("\t"))}
    protein = Protein.from_uniprot_row(row_dict)
    protein.fetch_pdb(save_path="tests/test_data/outputs/test_pdb.pdb")

    protein.get_confidence()

    protein.get_charge()
    protein.get_sasa()
    protein.get_cysteine_data()

    protein.get_titration()
    protein.get_titration_from_propka()

    try:
        protein.get_titration_from_pypka()  # optional dependency
    except ImportError:
        pass
    try:
        protein.get_titration_from_pkai()  # optional dependency
    except ImportError:
        pass


def test_residue_data_frame_run_only() -> None:
    TEST_HEADER = "Entry	Reviewed	Entry Name	Protein names	Gene Names	Organism	Length	Sequence	Active site	Binding site	DNA binding	Disulfide bond	Beta strand	Helix	Turn"
    TEST_ROW = "A0A0B4J2F0	reviewed	PIOS1_HUMAN	Protein PIGBOS1 (PIGB opposite strand protein 1)	PIGBOS1	Homo sapiens (Human)	54	MFRRLTFAQLLFATVLGIAGGVYIFQPVFEQYAKDQKELKEKMQLVQESEEKKS							"

    row_dict = {k: v for k, v in zip(TEST_HEADER.split("\t"), TEST_ROW.split("\t"))}
    protein = Protein.from_uniprot_row(row_dict)
    protein.fetch_pdb(save_path="tests/test_data/outputs/test_pdb.pdb")

    protein.residue_data_frame()


def test_uniprot_api() -> None:
    df = pd.read_csv(
        TEST_DATA_PATH,
        sep="\t",
        nrows=2,
    )
    # NOTE: the UniProt entry "A0A0B4J2F2" from our test data (row 3) has been removed from UniProt!
    # Trying to fetch this from UniProt throws an error (as it should).

    ids: list[str] = df["Entry"].to_list()

    print(Protein.from_uniprot_id(ids[0]).data)
    print(Protein.from_uniprot_row(df.iloc[0].to_dict()).data)

    fields_in_table = [
        x
        for x in Protein.UNIPROT_API_DEFAULT_FIELDS
        if x not in ["ft_mod_res", "ft_region", "ft_domain"]
    ]

    assert Protein.from_uniprot_id(
        ids[0], fields=fields_in_table
    ) == Protein.from_uniprot_row(df.iloc[0].to_dict())

    assert Protein.list_from_uniprot_ids(ids, fields=fields_in_table) == [
        Protein.from_uniprot_row(row.to_dict()) for _, row in df.iterrows()
    ]
