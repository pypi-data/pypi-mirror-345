import astropy
from astropy.io import fits
from astropy.nddata import CCDData
from astropy.table import Table
import astropy.units as u
from copy import deepcopy
import numpy as np
import os
from pathlib import Path

from .madcubafits import MadcubaFits

__all__ = [
    'MadcubaMap',
]

class MadcubaMap(MadcubaFits):
    """
    A container for MADCUBA FITS maps, using the `~madcubapy.io.MadcubaFits`
    interface.

    This class is basically a wrapper to read MADCUBA exported FITS maps and
    their history files with astropy.

    Parameters
    ----------
    data : `~numpy.ndarray`
        The data array contained in the FITS file.
    header : `~astropy.io.fits.Header`
        The header object associated with the FITS file.
    wcs : `~astropy.wcs.WCS`
        Object with the world coordinate system for the data in the FITS file.
    unit : `~astropy.units.Unit`
        The unit of the data in the FITS file.
    hist : `~astropy.table.Table`
        Table containing the history information of the FITS file, which is
        stored in a separate *_hist.csv* file.
    ccddata : `~astropy.nddata.CCDData`
        An astropy CCDData object loaded with astropy as a failsafe.
    filename : `~str`
        Name of the FITS file.

    Methods
    -------
    add_hist(*args)
        Load the history table from a csv file.

    """
    
    def __init__(
        self,
        data=None,
        header=None,
        wcs=None,
        unit=None,
        hist=None,
        ccddata=None,
        filename=None,
    ):
        # inherit hist
        super().__init__(hist)  # Initialize the parent class with hist

        if data is not None and not isinstance(data, np.ndarray):
            raise TypeError("The data must be a numpy array.")
        self._data = data

        if header is not None and not isinstance(header, astropy.io.fits.Header):
            raise TypeError("The header must be an astropy.io.fits.Header.")
        self._header = header

        if wcs is not None and not isinstance(wcs, astropy.wcs.WCS):
            raise TypeError("The WCS must be an astropy.wcs.WCS.")
        self._wcs = wcs

        if unit is not None and not isinstance(unit, astropy.units.UnitBase):
            raise TypeError("The unit must be an astropy unit.")
        self._unit = unit

        if ccddata is not None and not isinstance(ccddata, astropy.nddata.CCDData):
            raise TypeError("The ccddata must be a CCDData instance.")
        self._ccddata = ccddata

        if filename is not None and not isinstance(filename, str):
            raise TypeError("The filename must be a string.")
        self._filename = filename

    @property
    def ccddata(self):
        """
        `~astropy.nddata.CCDData` : An astropy CCDData object loaded with
        astropy as a failsafe.
        """
        return self._ccddata

    @ccddata.setter
    def ccddata(self, value):
        if value is not None and not isinstance(value, CCDData):
            raise TypeError("The ccddata must be a CCDData instance.")
        self._ccddata = value

    @property
    def filename(self):
        """
        `~str` : Name of the FITS file.
        """
        return self._filename

    @filename.setter
    def filename(self, value):
        if value is not None and not isinstance(value, str):
            raise TypeError("The filename must be a string.")
        self._filename = value

    @property
    def data(self):
        """
        `~numpy.ndarray` : The data array contained in the FITS file.
        """
        return self._data

    @data.setter
    def data(self, value):
        if value is not None and not isinstance(value, np.ndarray):
            raise TypeError("The data must be a numpy array.")
        self._data = value

    @property
    def header(self):
        """
        `~astropy.io.fits.Header` : The header object associated with the FITS
        file.
        """
        return self._header

    @header.setter
    def header(self, value):
        if value is not None and not isinstance(value, astropy.io.fits.Header):
            raise TypeError("The header must be an astropy.io.fits.Header.")
        self._header = value

    @property
    def wcs(self):
        """
        `~astropy.wcs.WCS` : Object with the world coordinate system for the data in the FITS file.
        """
        return self._wcs

    @wcs.setter
    def wcs(self, value):
        if value is not None and not isinstance(value, astropy.wcs.WCS):
            raise TypeError("The WCS must be an astropy.wcs.WCS.")
        self._wcs = value

    @property
    def unit(self):
        """
        `~astropy.units.Unit` : The unit of the data in the FITS file.
        """
        return self._unit

    @unit.setter
    def unit(self, value):
        if value is not None and not isinstance(value, astropy.units.UnitBase):
            raise TypeError("The unit must be an astropy unit.")
        self._unit = value

    @classmethod
    def read(cls, filepath, **kwargs):
        """
        ``Classmethod`` to generate a `~madcubapy.io.MadcubaMap` object from a
        FITS file. This method creates an `~astropy.nddata.CCDData` from the
        FITS file.

        Parameters
        ----------
        filepath : `~str`
            Name of FITS file.

        Other Parameters
        ----------------
        **kwargs
            Additional keyword parameters passed through to the Astropy
            :func:`~astropy.nddata.fits_ccddata_reader` function.

        """
        fits_filepath = filepath
        filename_terms = str(filepath).split('/')
        filename = filename_terms[-1]
        # Check if the fits file exists
        if not os.path.isfile(fits_filepath):
            raise FileNotFoundError(f"File {fits_filepath} not found.")
        # Load the CCDData from the .fits file
        ccddata = CCDData.read(fits_filepath, **kwargs)
        # Load the Table from the .csv file if present
        hist_filepath = os.path.splitext(fits_filepath)[0] + "_hist.csv"
        if not os.path.isfile(hist_filepath):
            print("WARNING: Default history file not found.")
            hist = None
        else:
            hist = Table.read(hist_filepath, format='csv')
            # Set default column types in history table to avoid errors
            hist["Macro"] = np.array(hist["Macro"], dtype='U500')
            hist["Type"] = np.array(hist["User"], dtype='U5')
            hist["User"] = np.array(hist["User"], dtype='U50')
            hist["Date"] = np.array(hist["Date"], dtype='U23')
        # Store the attributes
        data = ccddata.data
        header = ccddata.header
        # header = fits.getheader(fits_filepath)
        wcs = ccddata.wcs
        unit = ccddata.unit
        # Return an instance of MadcubaFits
        madcuba_map = cls(
            data=data,
            header=header,
            wcs=wcs,
            unit=unit,
            hist=hist,
            ccddata=ccddata,
            filename=filename,
        )
        if madcuba_map.hist:
            update_action = f"Open cube: '{str(filepath)}'"
            madcuba_map._update_hist(update_action)
        return madcuba_map

    def write(self, filepath, **kwargs):
        """
        Write a `~madcubapy.io.MadcubaMap` into a FITS file alongside its
        history file.

        Parameters
        ----------
        filepath : `~str`
            Name of output FITS file.
        
        Other Parameters
        ----------------
        **kwargs
            Additional keyword parameters passed through to the Astropy
            :func:`~astropy.nddata.fits_ccddata_writer` function.

        """
        if not self._ccddata:
            raise TypeError("Cannot export manually created MadcubaMaps (yet)")
        else:
            # Get save directory and file name
            filepath_terms = str(filepath).split('/')
            save_dir = Path("/".join(filepath_terms[:-1]))
            filename = filepath_terms[-1]
            filename_terms = filename.split('.')
            csv_filename = ".".join(filename_terms[:-1]) + "_hist.csv"
            # Write fits
            self._ccddata.write(filepath, **kwargs)
            # Correct units not recognized by madcuba
            with fits.open(filepath, mode="update") as hdul:
                parsed_bunit = _parse_madcuba_friendly_bunit(self.unit)
                hdul[0].header['BUNIT'] = parsed_bunit
                hdul.flush()  # Save changes
            # write hist
            if self.hist:
                update_action = f"Save cube: '{str(filepath)}'"
                self._update_hist(update_action)
                if 'overwrite' in kwargs:
                    overwrite_csv = kwargs['overwrite']
                else:
                    overwrite_csv = False
                self.hist.write(
                    save_dir/csv_filename,
                    format='csv',
                    overwrite=overwrite_csv,
                ) 
            else:
                print("Empty history file has not been saved")
            # Update filename
            self.filename = filename

    def copy(self):
        """
        Create a copy of the `~madcubapy.io.MadcubaMap`.
        """
        if self._hist:
            new_hist = self._hist.copy()
        else:
            new_hist = None
        return MadcubaMap(
            data=deepcopy(self._data),
            header=deepcopy(self._header),
            wcs=deepcopy(self._wcs),
            unit=deepcopy(self._unit),
            hist=new_hist,
            ccddata=deepcopy(self._ccddata),
        )

    def show(self, **kwargs):
        """
        Show the map in a pop-up window.

        Other Parameters
        ----------------
        **kwargs
            Additional parameters passed to
            :func:`~madcubapy.visualization.add_wcs_axes`.
            
        """
        from madcubapy.visualization.quick_plotters import quick_show
        quick_show(self, **kwargs)

    def get_input(self, **kwargs):
        """
        Return mouse click coordinates from this map.

        Other Parameters
        ----------------
        **kwargs
            Additional parameters passed to
            :func:`~madcubapy.visualization.add_wcs_axes`.
        """
        from madcubapy.visualization.interaction import _get_input_from_map
        return _get_input_from_map(self, **kwargs)

    def update_sigma(self, statistic='std', **kwargs):
        """
        Measure the noise (sigma) of the map by calculating the standard
        deviation (std) or root mean square (rms) inside several polygons
        selected by mouse clicks, and store it in the SIGMA header card.

        - Left clicks create polygon vertices.
        - Right click closes the current polygon, and a subsequent left click
          starts a new polygon.

        Parameters
        ----------
        statistic : {'std', 'rms'}, optional
            Statistic to be used as sigma. Defaults to 'std' and can be changed
            at runtime via GUI buttons.

        Other Parameters
        ----------------
        **kwargs
            Additional parameters passed to
            :func:`~madcubapy.visualization.add_wcs_axes`.
        
        """
        from madcubapy.operations.maps.noise import measure_noise
        sigma = measure_noise(self, statistic, **kwargs)
        # Update sigma header card
        if np.isnan(sigma):
            raise Exception("Function aborted.")
        self.header["SIGMA"] = (sigma, 'madcubapy update sigma')
        self.ccddata.header["SIGMA"] = (sigma, 'madcubapy update sigma')
        # Update hist file
        if self._hist:
            self._update_hist((f"Update sigma to '{sigma}'."))

    def fix_units(self):
        """
        Tries to fix problems when the units are incorrectly parsed. The user
        should confirm that the new units are correct.
        """
        unit_str = self.header["BUNIT"]
        # Fix CARTA strings
        new_unit_str = _fix_unit_string_multiple_slashes(unit_str)
        # Overwrite units
        self._unit = u.Unit(new_unit_str)
        self._ccddata.unit = u.Unit(new_unit_str)
        if self._hist:
            self._update_hist((f"Fixed BUNIT card from '{unit_str}' "
                             + f"to '{new_unit_str}"))

    def convert_unit_to(self, unit):
        """
        Convert the units of the map to other units.
        """
        previous_unit = self.unit
        # Change unit in CCDDdata and copy it into MadcubaMap
        converted_ccddata = self._ccddata.convert_unit_to(unit)
        self._ccddata = converted_ccddata
        self._data = converted_ccddata.data
        self._unit = converted_ccddata.unit
        # Convert sigma header card
        if "SIGMA" in self.header:
            sigma = self.header["SIGMA"] * previous_unit
            converted_sigma = sigma.to(unit).value
            self.header["SIGMA"] = (converted_sigma, 'madcubapy convert unit')
            self.ccddata.header["SIGMA"] = (converted_sigma,
                                            'madcubapy convert unit')
        if self._hist:
            self._update_hist((f"Convert units to "
                             + f"'{unit.to_string(format='fits')}'"))

    def __repr__(self):
        # If hist is None, display that it's missing
        if self._hist is None:
            hist_r = "hist=None"
        # If hist is present, display a summary of the table
        else: hist_r = (
            f"hist=<Table length={len(self._hist)} rows, " +
            f"{len(self._hist.columns)} columns>"
        )
        if self._data is None:
            data_r = "data=None"
        else:
            data_r = f"data=<numpy.ndarray shape={self._data.shape}>"
        if self._unit is None:
            unit_r = "unit=None"
        else:
            unit_r = f"unit={self._unit}"

        return f"<MadcubaMap({data_r}, {unit_r}, {hist_r})>"



def _fix_unit_string_multiple_slashes(unit_str):
    """
    This function converts dots to spaces and slashes to '-1' exponents if the
    BUNIT card contains more than one slash.
    """
    result = []
    # Split by slashes
    terms = unit_str.split('/')
    # The entire first term is in the numerator, no correction for a slash must
    # be applied. Split the units and append to a list.
    first_sub_terms = terms[0].split('.')
    result.extend(first_sub_terms)
    # Process terms after slashes
    for term in terms[1:]:
        # Split units and append a -1 to the first one because now it is a unit
        # after a slash and append the rest without changes because they are
        # preceeded by dots.
        sub_terms = term.split('.')
        result.append(f"{sub_terms[0]}-1")
        result.extend(sub_terms[1:])
    # Join all terms with a space
    return ' '.join(result)



def _parse_madcuba_friendly_bunit(unit):
    """
    This function returns a BUNIT card string that MADCUBA can recognize.
    """
    if not isinstance(unit, u.UnitBase):
        raise TypeError("Input value is not an Astropy unit")
    else:
        if unit == u.Jy * u.m / u.beam / u.s:
            return 'Jy beam-1 m s-1'
        elif unit == u.Jy * u.km / u.beam / u.s:
            return 'Jy beam-1 km s-1'
        elif unit == u.mJy * u.m / u.beam / u.s:
            return 'mJy beam-1 m s-1'
        elif unit == u.mJy * u.km / u.beam / u.s:
            return 'mJy beam-1 km s-1'
        elif unit == u.Jy / u.beam:
            return 'Jy beam-1'
        elif unit == u.mJy / u.beam:
            return 'mJy beam-1'
        else:
            return unit.to_string(fraction=False)
