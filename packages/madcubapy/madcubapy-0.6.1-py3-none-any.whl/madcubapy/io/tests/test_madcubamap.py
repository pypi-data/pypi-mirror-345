from astropy.table import Table
import astropy.units as u
from astropy.utils.diff import report_diff_values
import numpy as np
import pytest
from madcubapy.io.madcubamap import MadcubaMap

@pytest.fixture
def example_madcuba_map():
    # Create and return a Map instance to be used in tests
    return MadcubaMap.read(
        "examples/data/IRAS16293_SO_2-1_moment0_madcuba.fits"
    )

@pytest.fixture
def example_carta_map():
    # Create and return a Map instance to be used in tests
    return MadcubaMap.read(
        "examples/data/IRAS16293_SO2c_moment0_carta.fits"
    )

def test_read_madcuba_map(example_madcuba_map):
    # Test if the obligatory attributes are correctly initialized
    assert example_madcuba_map.ccddata is not None
    assert example_madcuba_map.data is not None
    assert example_madcuba_map.header is not None
    assert example_madcuba_map.filename is not None
    assert (example_madcuba_map.hist is None or
            isinstance(example_madcuba_map.hist, Table))
    assert np.array_equal(
        example_madcuba_map.data,
        example_madcuba_map.ccddata.data,
        equal_nan=True,
    )
    assert (example_madcuba_map.hist[-1]["Macro"] ==
        "//PYTHON: Open cube: 'examples/data/IRAS16293_SO_2-1_moment0_madcuba.fits'"
    )

def test_invalid_file():
    with pytest.raises(FileNotFoundError):
        MadcubaMap.read("nonexistent_file.fits")

def test_write_madcuba_map(example_madcuba_map):
    # Assert filename and hist change after writing
    assert example_madcuba_map.filename == "IRAS16293_SO_2-1_moment0_madcuba.fits"
    example_madcuba_map.write(
        "examples/data/IRAS16293_SO_2-1_moment0_madcuba_write.fits",
        overwrite=True,
    )
    assert example_madcuba_map.filename == "IRAS16293_SO_2-1_moment0_madcuba_write.fits"
    assert (example_madcuba_map.hist[-1]["Macro"] ==
        "//PYTHON: Save cube: 'examples/data/IRAS16293_SO_2-1_moment0_madcuba_write.fits'"
    )
    # Read back the written file
    example_madcuba_map_write = MadcubaMap.read(
        "examples/data/IRAS16293_SO_2-1_moment0_madcuba_write.fits"
    )
    # Assert BUNIT was written correctly
    assert example_madcuba_map_write.header["BUNIT"] == 'Jy beam-1 m s-1'
    # Assert written map is correctly read
    assert 0 == 0
    assert example_madcuba_map_write.ccddata is not None
    assert example_madcuba_map_write.data is not None
    assert example_madcuba_map_write.header is not None
    assert example_madcuba_map_write.filename is not None
    assert (example_madcuba_map_write.hist is None or
            isinstance(example_madcuba_map_write.hist, Table))
    # Assert written map is equal to original map
    assert np.array_equal(
        example_madcuba_map.data,
        example_madcuba_map_write.data,
        equal_nan=True,
    )
    assert example_madcuba_map.unit == example_madcuba_map_write.unit
    assert (example_madcuba_map.hist[0]["Macro"] ==
        example_madcuba_map_write.hist[0]["Macro"]
    )
    # Check filename and hist file
    assert example_madcuba_map_write.filename == "IRAS16293_SO_2-1_moment0_madcuba_write.fits"
    assert (example_madcuba_map_write.hist[-2]["Macro"] ==
        "//PYTHON: Save cube: 'examples/data/IRAS16293_SO_2-1_moment0_madcuba_write.fits'"
    )
    assert (example_madcuba_map_write.hist[-1]["Macro"] ==
        "//PYTHON: Open cube: 'examples/data/IRAS16293_SO_2-1_moment0_madcuba_write.fits'"
    )

def test_fix_units_correct(example_madcuba_map):
    assert example_madcuba_map.unit == u.Jy * u.m / u.beam / u.s
    example_madcuba_map.fix_units()
    assert example_madcuba_map.unit == u.Jy * u.m / u.beam / u.s

def test_fix_units_incorrect(example_carta_map):
    assert example_carta_map.unit == u.Jy / u.beam / u.km / u.s
    example_carta_map.fix_units()
    assert example_carta_map.unit == u.Jy * u.km / u.beam / u.s

def test_copy_madcuba(example_madcuba_map):
    madcuba_map_copy = example_madcuba_map.copy()
    assert np.array_equal(
        madcuba_map_copy.data, example_madcuba_map.data, equal_nan=True
    )
    assert madcuba_map_copy.header == example_madcuba_map.header
    assert madcuba_map_copy.unit == example_madcuba_map.unit
    assert report_diff_values(example_madcuba_map.hist, madcuba_map_copy.hist)
    assert madcuba_map_copy.ccddata.meta == example_madcuba_map.ccddata.meta

def test_convert_units_madcuba(example_madcuba_map):
    example_madcuba_map_mJy = example_madcuba_map.copy()
    example_madcuba_map_mJy.convert_unit_to(u.mJy * u.m / u.beam / u.s)
    assert example_madcuba_map_mJy.unit == u.mJy * u.m / u.beam / u.s
    assert example_madcuba_map_mJy.ccddata.unit == u.mJy * u.m / u.beam / u.s
    assert example_madcuba_map_mJy.hist[-1]["Macro"] == (
        "//PYTHON: Convert units to 'm mJy beam-1 s-1'"
    )

def test_convert_units_carta(example_carta_map):
    example_carta_map_mJy = example_carta_map.copy()
    example_carta_map_mJy.fix_units()
    example_carta_map_mJy.convert_unit_to(u.mJy * u.m / u.beam / u.s)
    assert example_carta_map_mJy.unit == u.mJy * u.m / u.beam / u.s
    assert example_carta_map_mJy.ccddata.unit == u.mJy * u.m / u.beam / u.s
    assert example_carta_map_mJy.hist == None
