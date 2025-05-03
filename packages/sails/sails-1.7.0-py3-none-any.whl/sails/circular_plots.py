#!/usr/bin/python3

# vim: set expandtab ts=4 sw=4;

from csv import DictReader
from os import makedirs, symlink
from os.path import join
from shutil import copyfile
import warnings

import tempfile

import numpy as np

import matplotlib.colors as mc
import matplotlib.pyplot as plt

# Note that we currently assume the use of 1000 for band widths to make life
# easier
BAND_WIDTH = 1000

CIRCOS_CONF_TEMPLATE = """
karyotype = {karyotype:s}
chromosomes_units = 1

<ideogram>
<spacing>
default = 0.005r
</spacing>
radius           = {circle_radius:f}r
thickness        = 50p
fill             = yes
stroke_color     = dgrey
stroke_thickness = 2p
show_label       = no
show_bands            = yes
fill_bands            = yes
band_stroke_thickness = 2
band_stroke_color     = white
band_transparency     = 4
</ideogram>

{colors:s}

{ticks:s}

<image>
angle_orientation* = counterclockwise
radius* = {radius:d}p
<<include {circospath:s}/image.conf>>
</image>
<<include {circospath:s}/colors_fonts_patterns.conf>>
<<include {circospath:s}/housekeeping.conf>>
<links>
<link>
file          = {linksname:s}
radius        = 0.95r
color         = black_a4
bezier_radius = 0.1r
thickness     = 1
</link>
</links>

<image>
file = {outputimage:s}
</image>
"""


class CircosException(BaseException):
    def __init__(self, retcode, stdout, stderr):
        self.retcode = retcode
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return '<CircosException: Return code: {}>'.format(self.retcode)


class CircosGroup(object):
    def __init__(self, name, c_idx=0, n_idx=0, circoscolour='unknown',
                 rgbcolour=None, netmatreverse=False):

        self.name = name
        self.c_idx = c_idx
        self.n_idx = n_idx
        self.circoscolour = circoscolour
        if rgbcolour is None:
            self.rgbcolour = [0, 0, 0]
        else:
            # Make sure to take a copy
            self.rgbcolour = rgbcolour[:]
        self.netmatreverse = netmatreverse

        # Dictionary of regions
        self.regions = {}

    def __str__(self):
        return '<CircosGroup {}>'.format(self.name)

    def __repr__(self):
        return '<CircosGroup {}>'.format(self.name)

    def __len__(self):
        return len(self.regions)

    def add_region(self, name, offset, shortname, analysisid):
        """
        Adds a new region to the group.

        Parameters
        ----------
        name: str
            Region name

        offset: int
            Region offset value

        shortname: str
            Region short name (used in plotting)

        analysisid: int
            Data index to use when accessing region data
        """
        self.regions[name] = {}
        self.regions[name]['offset'] = offset
        self.regions[name]['shortname'] = shortname
        self.regions[name]['analysisid'] = analysisid

    def find_region_idx(self, region):
        """
        Find a region index from an name.

        Parameters
        ----------
        region: str
            Region name

        Returns
        -------
        int or None
            Region index or None if not found
        """
        if region in self.regions:
            return self.regions[region]['analysisid']
        return None

    def find_region_from_idx(self, idx):
        """
        Find a region name from an index.

        Parameters
        ----------
        idx: int
            Region index

        Returns
        -------
        str or None
            Region name or None if not found
        """
        for region in self.regions.keys():
            if self.regions[region]['analysisid'] == idx:
                return region

        return None

    def has_region(self, region):
        return region in self.regions.keys()

    @property
    def circular_indices(self):
        """
        Get a list of all region analysis indices in circular plotting order.

        Returns
        -------
        list
            List of indices to use when accessing data in order to access
            data in the correct order for circular plotting.
        """
        return [x[1]['analysisid'] for x in sorted(self.regions.items(),
                                                   key=lambda x: x[1]['offset'])]

    @property
    def circular_regions(self):
        """
        Get a list of the regions in circular plotting order

        Returns
        -------
        list
            List of region names to use in the correct order for circular
            plotting.
        """
        return [x[0] for x in sorted(self.regions.items(),
                                     key=lambda x: x[1]['offset'])]

    @property
    def circular_shortnames(self):
        """
        Get a list of the region short names in circular plotting order

        Returns
        -------
        list
            List of region short names names in the correct order for circular
            plotting.
        """
        return [x[1]['shortname'] for x in sorted(self.regions.items(),
                                                  key=lambda x: x[1]['offset'])]

    def circular_link_cache(self, groupname):
        """Return a dictionary of the regions and their information"""
        ret = {}
        for region in self.regions:
            ret[region] = (groupname,
                           self.regions[region]['offset'],
                           self.regions[region]['offset'] + BAND_WIDTH)

        return ret

    @property
    def netmat_indices(self):
        """
        Get a list of all analysis indices in netmat plotting order.

        Returns
        -------
        list
            List of indices to use when accessing data in order to access
            data in the correct order for netmat plotting.
        """

        tmp = self.circular_indices

        if self.netmatreverse:
            tmp = tmp[::-1]

        return tmp

    @property
    def netmat_regions(self):
        """
        Get a list of all region names in netmat plotting order.

        Returns
        -------
        list
            List of names to use when accessing data in order to access
            data in the correct order for netmat plotting.
        """
        tmp = self.circular_regions

        if self.netmatreverse:
            tmp = tmp[::-1]

        return tmp

    @property
    def netmat_shortnames(self):
        """
        Get a list of the region short names in netmat plotting order

        Returns
        -------
        list
            List of region short names names in the correct order for netmat
            plotting.
        """
        tmp = self.circular_shortnames

        if self.netmatreverse:
            tmp = tmp[::-1]

        return tmp


class CircosHandler(object):
    """
    Handler for producing plots using the Circos tool.

    Note that if you are creating plots for publication using Circos, you should
    cite the relevant publication: [Krzywinski2009]_.
    """

    def __init__(self):
        self.groups = {}

    def has_region(self, region):
        """Check whether a region exists in any currently defined group"""
        for region in self.groups.keys():
            if self.groups[region].has_region(region):
                return True

        return False

    def find_region_idx(self, region):
        """Find a region index"""
        for group in self.groups.keys():
            idx = self.groups[group].find_region_idx(region)
            if idx is not None:
                return idx

        return None

    def find_region_from_idx(self, idx):
        """Find a region name from an index"""
        for group in self.groups.keys():
            name = self.groups[group].find_region_from_idx(idx)
            if name is not None:
                return name

        return None

    @property
    def num_regions(self):
        return len(self.circular_regions)

    def colour_mapping(self, normalise=True):
        """
        Return a dictionary of colour name to 3-tuples.

        Parameters
        ----------
        normalise: bool, optional
            If True, colour names will be scaled from the standard 0-255
            range to 0-1; this is primarily useful for matplotlib

        Returns
        -------
        dict
            Maps colour names to 3-tuples of colour information.
        """
        colours = {}
        for group in self.groups.keys():
            colourname = self.groups[group].circoscolour
            rgbcolour = self.groups[group].rgbcolour

            if normalise:
                rgbcolour = [(x / 255.0) for x in rgbcolour]

            colours[colourname] = rgbcolour

        return colours

    @property
    def data_regions(self):
        """Return a list of region names in data order"""
        ret = []
        for k in range(self.num_regions):
            ret.append(self.find_region_from_idx(k))
        return ret

    @property
    def circular_indices(self):
        """Return a list of all region analysis indices in circular plotting order"""
        ret = []
        for group in self.circular_groups:
            ret.extend(self.groups[group].circular_indices)

        return ret

    @property
    def circular_regions(self):
        """Return a list of the groups in ascending order"""
        ret = []
        for group in self.circular_groups:
            ret.extend(self.groups[group].circular_regions)

        return ret

    @property
    def circular_shortnames(self):
        """Return a list of all shortnames in circular plotting order"""
        ret = []
        for group in self.circular_groups:
            ret.extend(self.groups[group].circular_shortnames)

        return ret

    @property
    def circular_link_cache(self):
        """Returns a dictionary which caches the circular position information for links"""
        ret = {}
        for group in self.circular_groups:
            ret.update(self.groups[group].circular_link_cache(group))

        return ret

    @property
    def netmat_indices(self):
        """Return a list of all region analysis indices in netmat plotting order"""
        ret = []
        for group in self.netmat_groups:
            ret.extend(self.groups[group].netmat_indices)

        return ret

    @property
    def netmat_regions(self):
        """Return a list of all regions in netmat plotting order"""
        ret = []
        for group in self.netmat_groups:
            ret.extend(self.groups[group].netmat_regions)

        return ret

    @property
    def netmat_shortnames(self):
        """Return a list of all shortnames in netmat plotting order"""
        ret = []
        for group in self.netmat_groups:
            ret.extend(self.groups[group].netmat_shortnames)

        return ret

    @property
    def circular_groups(self):
        """Return a list of the groups in circular order"""
        return [x[0] for x in sorted(self.groups.items(),
                                     key=lambda x: x[1].c_idx)]

    @property
    def netmat_groups(self):
        """Return a list of the groups in netmat order"""
        return [x[0] for x in sorted(self.groups.items(),
                                     key=lambda x: x[1].n_idx)]

    @classmethod
    def from_csv_files(cls, group_filename, region_filename, analysis_column='AnalysisID'):
        """
        This routine sets up a CircosHandler from two CSV files.

        The group file must contain a list of groups; in Circos terms these are
        known as the 'chromosomes'.  This file must contain the columns:
          * Group: The name of the group: must be unique
          * CircularIdx: The ordering of the group (from 1..N) in the circular plot order

        The following columns are optional:
          * NetmatIdx: The ordering of the group (from 1..N) in the netmat plot order.
                       If not provided, the CircularIdx will be used
          * CircosColour: The colour to use for the chromosome in circos format
          * RGBColour: A 3-tuple of the RGB (0-255) colour to use in non-circos (e.g. for netmats)
                       If no colour is set, mid-grey will be used.
          * NetmatReverseOrder: If True, when sorting out netmat indices,
                                the ordering within the group will be reversed.  This is
                                commonly used when going from circular to netmat order
                                on the left hand side of the plot.  If not set, False
                                will be assumed.

        The region file must contain a list of regions; in Circos
        terms these are known as the 'bands' within each chromosome.
        This file must contain the columns:
          * Region: The name of the region
          * Group: The name of the group which the region should be placed in
          * GroupOffset: The integer location at which the region should be
                         placed within the group.  Note that by default, this
                         should be a multiple of 1000.  The first value within
                         a region should be 0
          * AnalysisID: The position of the data for the region in the analysis
                        data.  I.e. an index from 0-(N-1).  This is used to
                        extract information from, e.g. netmats in the correct
                        order.
                        Note that the name of this column can be varied using
                        the optional 'analysis_column' argument to the function.
                        This allows having CSV files with multiple data orderings
                        in different columns.

        The following columns are optional:
          * ShortName: The short name to use on the outer labels.  If this is
                       not present, the Region name will be used.

        Parameters
        ----------
        group_filename: str
            Filename of group CSV file to load (see above)

        region_filename: str
            Filename of the region CSV file to load (see above)

        analysis_column: str, optional
            Column name to use for loading analysis ordering (see above).
            Defaults to 'AnalysisID'

        Returns
        -------
        CircosHandler
            CircosHandler object ready to be used for plotting.
        """
        ret = cls()

        # Read the groups
        with open(group_filename, 'r') as f:
            reader = DictReader(f)
            for row in reader:
                name = row['Group']

                if name in ret.groups:
                    raise Exception("Group name {} defined more than once".format(name))

                c_idx = int(row['CircularIdx'])
                n_idx = int(row.get('NetmatIdx', c_idx))
                circoscolour = row.get('CircosColour', 'grey')
                rgbcolour = [int(x.strip()) for x in row.get('RGBColour', '128,128,128').split(',')]
                tmp = row.get('NetmatReverseOrder', 'False')
                if tmp.lower() in ['true', '1', 't', 'y', 'yes']:
                    netmatreverse = True
                else:
                    netmatreverse = False

                group = CircosGroup(name, c_idx, n_idx, circoscolour, rgbcolour, netmatreverse)

                ret.groups[name] = group

        # Now read each region
        with open(region_filename, 'r') as f:
            reader = DictReader(f)
            for row in reader:
                name = row['Region']
                group = row['Group']
                offset = int(row['GroupOffset'])
                shortname = row.get('ShortName', name)
                analysispos = int(row.get(analysis_column))

                if group not in ret.groups:
                    raise Exception("Group {} for ROI {} not defined".format(group, name))

                ret.groups[group].add_region(name, offset, shortname, analysispos)

        return ret

    def karyotype(self):
        """Return a string containing the contents of a karyotype file"""
        s = []

        # First of all the group definitions
        for group in self.circular_groups:
            g = self.groups[group]
            num_entries = len(g.regions)
            s.append('chr - {} {} 0 {} {}'.format(group, g.c_idx,
                                                  num_entries * BAND_WIDTH,
                                                  g.circoscolour))

        # Now the region definitions
        for group in self.circular_groups:
            g = self.groups[group]
            for region in g.circular_regions:
                start = g.regions[region]['offset']
                end = start + BAND_WIDTH

                s.append('band {} {} {} {} {} grey'.format(group, region, region,
                                                           start, end))

        return '\n'.join(s)

    def ticks(self, **kwargs):
        """
        Return a string containing the contents of a ticks.conf file
        All parameters must be passed as kwargs.

        Parameters
        ----------
        ticks: bool
            Show ticks around circle

        tick_labels: bool
            Show tick labels around circle

        Returns
        -------
        str
            String containing ticks.conf content needed for the relevant
            plot configuration
        """
        s = []

        # A header
        s.append('show_ticks          = {}'.format('yes' if kwargs.get('ticks', True) else 'no'))
        s.append('show_tick_labels    = {}'.format('yes' if kwargs.get('tick_labels', True) else 'no'))
        s.append('')
        s.append('<ticks>')
        s.append('chromosomes_display_default = no')
        s.append('skip_first_label = no')
        s.append('skip_last_label  = no')
        s.append('radius           = dims(ideogram,radius_outer)')
        s.append('tick_separation  = 2p')
        s.append('label_separation = 5p')
        s.append('multiplier       = 1')
        s.append('color            = black')
        s.append('thickness        = 4p')
        s.append('size             = 20p')
        s.append('show_label     = yes')
        s.append('label_size     = 40p')
        s.append('label_offset   = 10p')

        # Now the region definitions
        for group in self.circular_groups:
            g = self.groups[group]
            for region in g.circular_regions:
                shortname = g.regions[region]['shortname']
                start = int(g.regions[region]['offset'])
                s.append('<tick>')
                s.append('chromosomes = {}'.format(group))
                s.append('position = {}u'.format(start + (BAND_WIDTH // 2)))
                s.append('format = {}'.format(shortname))
                s.append('</tick>')

        s.append('</ticks>')

        return '\n'.join(s)

    def links(self, data, linkcolors=None, defaultlinkcolor='black'):
        """
        Parameters
        ----------
        data: ndarray
            an (N x N) matrix containing thickness (and np.nan where no connection is desired)

        linkcolors: tuple, None or numpy array, optional
            One of 1) a tuple of three strings (zerocolor, negcolor, poscolor);
            e.g. ('black', 'blue', 'red), 2) None (in which case ('black', 'blue', 'red')
            will be assumed) or 3) a numpy array of dtype object (N, N)
            with a specific color string in each entry

            In the tuple case, all data values which are identically 0 will be coloured as
            zerocolor, all negative values as negcolor and all positive values as poscolor.

            In the numpy array case each connection will be set to the colour as specified in
            the same position in the array.  If the entry is None then defaultcolor will be used

        defaultlinkcolor: str, optionals
            defaults to 'black'.  Only used if linkcolors is a numpy array
            and None entries are found

        Returns
        -------
        str
            String containing links.conf content needed for the relevant
            plot configuration
        """

        s = []

        if linkcolors is None:
            # zero, neg, pos
            linkcolors = ('black', 'blue', 'red')

        num_regions = self.num_regions

        if data.shape != (num_regions, num_regions):
            raise Exception("Data must be {} x {}".format(num_regions, num_regions))

        # Generate a cache of map lookups and region IDs to names
        cache = self.circular_link_cache
        region_names = self.data_regions

        linefmt = "{} {} {} {} {} {} thickness={}p,color={}"

        for row in range(num_regions):
            for col in range(num_regions):
                val = data[row, col]

                # Skip any entries which are NaN
                if np.isnan(val):
                    continue

                if isinstance(linkcolors, (tuple, list)):
                    if val == 0:
                        color = linkcolors[0]
                    elif val < 0:
                        color = linkcolors[1]
                    else:
                        color = linkcolors[2]
                else:
                    # Assume a numpy array of strings
                    color = linkcolors[row, col]

                if color is None:
                    color = defaultlinkcolor

                reg_from = region_names[row]
                reg_to = region_names[col]

                # Note that thickness must be positive
                s.append(linefmt.format(cache[reg_from][0], cache[reg_from][1], cache[reg_from][2],
                                        cache[reg_to][0], cache[reg_to][1], cache[reg_to][2],
                                        np.abs(val), color))

        return '\n'.join(s)

    def parse_colors(self, linkcolors, defaultlinkcolor):
        """
        Parse hex colours into something usable by circos
        """

        # Map (r, g, b) tuples to colour names
        colour_dict = {}
        colidx = 0

        if isinstance(linkcolors, (tuple, list)):
            lc = []
            for colour in linkcolors:
                if colour.startswith('#'):
                    # Parse as #RGB and add to colour_dict
                    r, g, b = mc.hex2color(colour)
                    r = int(r * 255)
                    g = int(g * 255)
                    b = int(b * 255)

                    if (r, g, b) not in colour_dict.keys():
                        colour_dict[(r, g, b)] = 'customcolor{}'.format(colidx)
                        colidx += 1

                    lc.append(colour_dict[(r, g, b)])
                else:
                    # Leave as it is
                    lc.append(colour)

            lc = tuple(lc)
        elif isinstance(linkcolors, np.ndarray):
            lc = linkcolors.copy()

            for row in range(lc.shape[0]):
                for col in range(lc.shape[1]):
                    colour = lc[row, col]
                    if colour is not None and colour.startswith('#'):
                        # Parse as #RGB and add to colour_dict
                        r, g, b = mc.hex2color(colour)
                        r = int(r * 255)
                        g = int(g * 255)
                        b = int(b * 255)

                        if (r, g, b) not in colour_dict.keys():
                            colour_dict[(r, g, b)] = 'customcolor{}'.format(colidx)
                            colidx += 1

                        lc[row, col] = colour_dict[(r, g, b)]

        elif linkcolors is None:
            lc = None
        else:
            raise Exception("Cannot parse link colors {}".format(linkcolors))

        if defaultlinkcolor is None:
            dlc = None
        elif defaultlinkcolor.startswith("#"):
            # Parse as #RGB and add to colour_dict
            r, g, b = mc.hex2color(defaultlinkcolor)
            r = int(r * 255)
            g = int(g * 255)
            b = int(b * 255)

            if (r, g, b) not in colour_dict.keys():
                colour_dict[(r, g, b)] = 'customcolor{}'.format(colidx)
                colidx += 1

            dlc = colour_dict[(r, g, b)]
        else:
            dlc = defaultlinkcolor

        # Work out what to put in the colors section (if anything)
        colour_text = ""

        if len(colour_dict) > 0:
            colour_text = """<colors>\n"""

            for k, v in colour_dict.items():
                colour_text += "{} = {},{},{}\n".format(v, k[0], k[1], k[2])

            colour_text += """</colors>\n"""

        return lc, dlc, colour_text

    def gen_circos_files(self, data, karyotype_name, output_name,
                         radius=1500,
                         circos_path='/etc/circos',
                         output_dir=None, **kwargs):
        """
        Create a Circos plot.

        Note that additional kwargs parameters can be passed to this routine.
        They will be passed to the ticks() and links() routines.  See those
        routines for details of the additional parameters available.

        Parameters
        ----------
        data : ndarray
            a (N x N) matrix containing thickness (and np.nan where no connection is desired)

        karyotype_name: str
            the filename of your karyotype file on disk

        output_name: str
            output basename of configuration files (with no extension)

        radius: int, optional
            in pixels (defaults to 1500)

        circos_path: str, optional
            where to find the circos configuration files (defaults to /etc/circos)

        output_name: str, optional
            Directory in which to store output

        circle_prop: float, optional
            proportion of image to fill circle with (defaults to 0.85).  Must
            be in range 0-1.


        Note that if you are creating plots for publication using Circos, you should
        cite the relevant publication: [Krzywinski2009]_.
        """

        linksname = output_name + '.txt'

        linkspath = linksname
        if output_dir is not None:
            linkspath = join(output_dir, linksname)

        imagename = output_name + '.png'

        confpath = output_name + '.conf'
        if output_dir is not None:
            confpath = join(output_dir, confpath)

        linkcolors = kwargs.get('linkcolors', None)
        defaultlinkcolor = kwargs.get('defaultlinkcolor', 'black')

        lc, dlc, colors = self.parse_colors(linkcolors, defaultlinkcolor)

        circle_radius = kwargs.get('circle_prop', 0.85)

        # First of all, create the .txt links file
        f = open(linkspath, 'w')
        f.write(self.links(data, lc, dlc))
        f.close()

        # Now the config file - pass all keyword arguments down
        ticks = self.ticks(**kwargs)

        f = open(confpath, 'w')
        f.write(CIRCOS_CONF_TEMPLATE.format(karyotype=karyotype_name,
                                            ticks=ticks,
                                            radius=radius,
                                            colors=colors,
                                            circospath=circos_path,
                                            linksname=linksname,
                                            outputimage=imagename,
                                            circle_radius=circle_radius))
        f.close()

    def gen_circos_plot(self, data, output_name,
                        radius=1500, circos_path='/etc/circos', **kwargs):
        """
        Generate a circos plot output without leaving behind the configuration files.

        All arguments to this function are the same as gen_circos_files except
        that you do not specify a karyotype_name as this is unnecessary.

        Note that if you are creating plots for publication using Circos, you should
        cite the relevant publication: [Krzywinski2009]_.
        """
        try:
            from subprocess import run, PIPE
        except ImportError:
            warnings.warn("subprocess.run is not present; this routine is not supported on python2")
            return

        with tempfile.TemporaryDirectory() as d:
            # Generate the karyotype
            f_k = open(join(d, 'karyotype.txt'), 'w')
            f_k.write(self.karyotype())
            f_k.close()

            # Generate the config files
            self.gen_circos_files(data, 'karyotype.txt',
                                  'circos',
                                  radius=radius,
                                  circos_path=circos_path,
                                  output_dir=d,
                                  **kwargs)

            # Set up the symlinks which seem to be necessary
            makedirs(join(d, 'etc'))
            symlink(join(circos_path, 'tracks'), join(d, 'etc', 'tracks'))

            # Now run circos and check for the error code
            # Can't use check_output as we're still on python3.5 (Debian stretch)
            r = run(['circos', '-conf', 'circos.conf'], cwd=d,
                    stdout=PIPE, stderr=PIPE)

            if r.returncode != 0:
                raise CircosException(r.returncode, r.stdout, r.stderr)

            # Move files to final location
            copyfile(join(d, 'circos.png'), output_name + '.png')
            copyfile(join(d, 'circos.svg'), output_name + '.svg')

    def plot_netmat(self, data, ax=None, labels=True,
                    hregions='top', vregions='right',
                    show_xticks=True, show_yticks=True,
                    showgrid=True, **kwargs):
        """
        Plot a netmat with coloured bars to represent the grouping of the regions.

        Required arguments:
          data: a (N, N) matrix of data to be plotted

        Optional arguments:
          ax: An axes object on which to plot.  One will be created on a new figure
              if not provided.
          labels: If True, use the shortnames, if False do not plot labels,
                  if a list, use the list as the labels (must be N long)
          hregions: Location to place horizontal coloured bars indicating regions of ROIs.
                    One of 'top', 'bottom', 'off'.  Defaults to 'top'
          vregions: Location to place vertical coloured bars indicating regions of ROIs.
                    One of 'left', 'right', 'off'.  Defaults to 'right'
          show_xticks: Whether to show the xticks on the axis
          show_yticks: Whether to show the yticks on the axis
          showgrid: If True, place a grid on the image to delineate the regions.

        Keyword arguments:
          label_fontsize: will be passed to plot_netmat to set the font size

        Any additional keyword arguments will be passed down to pcolormesh to allow
        setting things such as the colormap
        """

        from sails.plotting import plot_netmat

        # We need the colours in a normal form
        colour_dict = self.colour_mapping(normalise=True)

        colour_names = []
        tick_pos = []
        count = 0

        if ax is None:
            plt.figure()
            ax = plt.subplot(1, 1, 1)

        # We need to know which colour each ROI is
        for group in self.netmat_groups:
            g = self.groups[group]
            colour_names.extend([g.circoscolour] * len(g))
            tick_pos.append(count + len(g))
            count += len(g)

        xtick_pos = None
        ytick_pos = None

        if show_xticks:
            xtick_pos = tick_pos

        if show_yticks:
            ytick_pos = tick_pos

        if labels is True:
            labels = self.netmat_shortnames
        elif labels is False:
            labels = None

        # Otherwise assume that they have provided a list of labels
        # which they want to use

        # Order data properly - can't think of a better way to do this
        idx = np.array(self.netmat_indices)
        new_data = data[idx, :][:, idx]

        return plot_netmat(new_data, ax=ax, colors=colour_dict, cnames=colour_names,
                           xtick_pos=xtick_pos, ytick_pos=ytick_pos, labels=labels,
                           hregions=hregions, vregions=vregions,
                           showgrid=showgrid, **kwargs)
