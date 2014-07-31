"""
astrom_simple.py

A library containing functions that are useful for solving for the
astrometry of an image

Generic functions
 read_secat      - reads a catalog, probably generated by SExtractor

"""

import numpy as n
import pyfits as pf
import imfuncs as im
import wcs, coords 
from ccdredux import sigma_clip
from matplotlib import pyplot as plt
from math import pi

#------------------------------------------------------------------------------

class Secat:

   """

   ****** NB: Right now this code may be partially broken ******

   The __init__ method has been changed to return something like a record
   array, which has the same number of rows as the old 2D float array, but
   which stores each row as a single tuple.  It is thus a 1D array, sort of
   like a structure array in C.  The columns can be accessed by field name,
   which for now is just 'f0', 'f1', etc., unless the input catalog is in
   SExtractor's FITS LDAC format, in which case the field names actually
   correspond to the SExtractor variable names.

   The code used to expect the old 2D float array format.  It should have
   all been updated, but there may still be some issues.

   """

   def __init__(self, infile, catformat='ascii', verbose=True, namecol=None,
                racol=None, deccol=None):
      """
      This method gets called when the user types something like
         secat = Secat(infile)

      Inputs:
         infile - input file containing the catalog
      """

      """
      Define a flag for successful reading of input catalog
      """

      read_success = True

      """
      Start by loading the catalog information
      """
      if verbose:
         print ""
         print "Loading data from catalog file %s" % infile
         print "-----------------------------------------------"
         print "Expected catalog format: %s" % catformat
         print ""

      """ ASCII format """
      if catformat=='ascii':
         try:
            """ Set up the data format in the catalog """
            foo = n.loadtxt(infile,dtype='S30')
            ncols = foo.shape[1]
            del foo
            coltypes = n.ones(ncols,dtype='S3')
            coltypes[:] = 'f8'
            if namecol is not None:
               print "Object name column: %d" % namecol
               coltypes[namecol] = 'S30'
            colstr = ''
            for i in range(ncols):
               colstr = '%s,%s' % (colstr,coltypes[i])
            colstr = colstr[1:]
            dt = n.dtype(colstr)

            """ Actually read in the data """
            self.informat = 'ascii'
            self.data = n.loadtxt(infile,dtype=dt)

            """ Set the field names """
            if racol is not None:
               self.rafield = 'f%d' % racol
            else:
               self.rafield = None
            if deccol is not None:
               self.decfield = 'f%d' % deccol
            else:
               self.decfield = None

         except:
            print "  ERROR. Problem in loading file %s" % infile
            print "  Check to make sure filename matches an existing file."
            print "  "
            print "  This may have failed if there is a string column in"
            print "   the input catalog (e.g., for an object name).  "
            print "  If this is the case, use the namecol to indicate which "
            print "   column contains the string values (column numbers are "
            print "   zero-indexed)"
            print ""
            print "  This also may have failed if the input file is in the"
            print "   SExtractor FITS LDAC format.  Checking that..."
            print ""
            read_success = False

      """ FITS LDAC format """
      if catformat.lower()=='ldac' or read_success==False:
         try:
            hdu = pf.open(infile)
         except:
            print "  ERROR. Problem in loading file %s" % infile
            print "  Check to make sure filename matches an existing file."
            print "  "
            return

         self.informat = 'ldac'
         self.data = hdu[2].data.copy()
         ncols = hdu[2].header['tfields']

         """ Set the field names """
         self.rafield = 'alpha_j2000'
         self.decfield = 'delta_j2000'

      if verbose:
         print "Number of rows:    %d" % self.data.shape[0]
         print "Number of columns: %d" % ncols
      self.infile = infile

   #-----------------------------------------------------------------------

   def make_reg_file(self, outfile, labcol=None, fluxcol=None, 
                     fluxerrcol=None, plot_high_snr=False):
      """
      Uses the RA and Dec info in the catalog to make a region file that
      can be used with ds9.
      """

      """ 
      Start by putting the RA and Dec info into a somewhat more convenient
      format
      """

      self.get_radec()
      if self.ra is None:
         print ""
         print "ERROR: No columns for RA or Dec given."
         print "Cannot make region file unless those columns are specified."
         return

      """ 
      If the flux information is given, then report on high SNR detections
      """

      ngood = 0
      if fluxcol is not None and fluxerrcol is not None:
         if self.informat == 'ldac':
            if type(fluxcol) is int:
               flux = self.data.field(fluxcol)
               fluxerr = self.data.field(fluxerrcol)
            else:
               flux = self.data[fluxcol]
               fluxerr = self.data[fluxerrcol]
         else:
            flux = self.data['f%d' %fluxcol]
            fluxerr = self.data['f%d' % fluxerrcol]
         snr = flux / fluxerr
         ragood  = self.ra[snr>10.]
         decgood = self.dec[snr>10.]
         ntot = self.ra.size
         ngood = ragood.size
         print "Out of %d total objects, %d have SNR>10" %(ntot,ngood)

      """ Write the output region file """
      f = open(outfile,'w')
      f.write('global color=green\n')
      for i in range(self.ra.size):
         f.write('fk5;circle(%10.6f,%+10.6f,0.0007)\n'% (self.ra[i],self.dec[i]))
      if plot_high_snr and ngood>0:
         f.write('global color=red\n')
         for i in range(ragood.size):
            f.write('fk5;circle(%10.6f,%+10.6f,0.0011)\n' \
                       %(ragood[i],decgood[i]))

      """ Add labels if requested """
      if labcol is not None:
         if self.informat == 'ldac':
            if type(labcol) is int:
               lab = self.data.field(labcol)
            else:
               lab = self.data[labcol]
         else:
            lab = self.data['f%d' % labcol]
         cosdec = n.cos(pi * self.dec / 180.)
         xx = self.ra + 0.0012 * cosdec
         yy = self.dec + 0.0012
         f.write('global color=green\n')
         for i in range(self.ra.size):
            f.write('fk5;text(%10.6f,%+10.6f) # text={%s}\n'% \
                       (xx[i],yy[i],str(lab[i])))

      """ Wrap up """
      print "Wrote region file %s" % outfile
      f.close()


   #-----------------------------------------------------------------------

   def get_radec(self):
      """
      Extracts the RA and Dec information from the data container.  This
      is not necessary, and some of the data containers may not even have
      WCS info, but extracting the coordinates if it does simplifies some
      later tasks.
      """

      """ Extract the information into the new containers """
      self.ra = None
      self.dec = None
      if self.rafield is not None:
         self.ra  = self.data[self.rafield].copy()
      if self.decfield is not None:
         self.dec = self.data[self.decfield].copy()

   #-----------------------------------------------------------------------

   def print_ccmap(self, outfile, verbose=True):
      """
      Prints out a file that can be used as the input for the pyraf ccmap
      task.  This file has 4 columns:  x  y  RA  Dec

      Inputs:
         outfile   -  output file to be used as input for ccmap
         verbose   -  print task info
      """
      if verbose:
         print ""
         print "Printing to file for use in ccmap:  %s" % outfile
         print ""
      f = open(outfile,'w')
      f.write('# (x,y) catalog: %s\n' % self.infile)
      f.write('# Astrometric catalog: %s\n' % self.matchcat)
      f.write('# Columns are x y RA Dec\n')
      for i in range(self.nmatch):
         f.write('%8.2f %8.2f  %11.7f %+11.7f\n' % \
                    (self.matchx[i],self.matchy[i],self.matchra[i],
                     self.matchdec[i]))
      f.close()

   #-----------------------------------------------------------------------

   def find_closest_xy(self, xast, yast, xcol, ycol):

      """
      Finds the closest match, in (x,y) space to each member of the astrometric
      catalog (represented by xast,yast).
      """

      self.matchind = n.zeros(xast.size, dtype=int)

      xfield = 'f%d' % xcol
      yfield = 'f%d' % ycol

      for i in range(xast.size):
         dx = xast[i] - self.data[xfield]
         dy = yast[i] - self.data[yfield]
         dpos = dx**2 + dy**2
         sindex = n.argsort(dpos)
         self.matchind[i] = sindex[0]

      self.matchdx = xast - self.data[xfield][self.matchind]
      self.matchdy = yast - self.data[yfield][self.matchind]

   #-----------------------------------------------------------------------

   def match_xy(self, xa, ya, max_offset=None, xcol=8, ycol=9, verbose=True):

      """
      Find the closest match to each astrometric catalog object and calculate the
      offsets.
      Do two loops, to deal with possible confusion of sources on first pass
      through
      """
      dxmed = 0
      dymed = 0
      for i in range(2):
         if verbose:
            print ''
            print 'Pass %d' % (i+1)
            print '------------------------'
         xa0 = xa - dxmed
         ya0 = ya - dymed
         self.find_closest_xy(xa0,ya0,xcol,ycol)
         dxmed = n.median(self.matchdx)
         dymed = n.median(self.matchdy)
         if max_offset is not None:
            dpos = n.sqrt(self.matchdx**2 + self.matchdy**2)
            goodmask = dpos<max_offset
            if verbose:
               print "Applying a maximum offset cut of %7.1f pixels" % max_offset
               print "Median shifts before clipping: %7.2f %7.2f" % (dxmed,dymed)
         else:
            goodmask = n.ones(xa.size,dtype=bool)
         dxm  = self.matchdx[goodmask]
         dym  = self.matchdy[goodmask]
         dxmed = n.median(dxm)
         dymed = n.median(dym)
         if verbose:
            print "Median shifts after pass:   %7.2f %7.2f" % (dxmed,dymed)

      """
      Transfer information into object and clean up
      """
      if verbose:
         print ''
         print 'Found %d astrometric objects within FOV of image' % xa.size
         print 'Matched %d objects to astrometric catalog.' % dxm.size
      self.nmatch = dxm.size
      self.goodmask = goodmask.copy()
      self.matchind = self.matchind[goodmask]
      del xa0,ya0,goodmask

   #-----------------------------------------------------------------------

   def match_fits_to_ast(self, fitsfile, astcat, outfile=None, max_offset=None, 
                         racol=1, deccol=2, xcol=8, ycol=9, 
                         doplot=True, edgedist=50., imhdu=0, verbose=True):

      """
      Given the fits file from which this object (self) was defined 
      and an astrometric catalog, find the closest matches of the 
      astrometric objects to those contained in this object, using the WCS 
      information in the fits header.
      """

      if(verbose):
         print "Running match_fits_to_ast with:"
         print "   fitsfile = %s" % fitsfile
         print "   astcat   = %s" % astcat
      self.infits = fitsfile
      self.matchcat = astcat

      """
      Start by opening the fits file and reading the appropriate columns from
      the catalogs
      """
      hdulist = im.open_fits(fitsfile)
      hdr = hdulist[imhdu].header
      if verbose:
         print ""
         hdulist.info()

      """
      Select the astrometric catalog objects that fall within the fits file FOV
      (at least with its current WCS)
      """
      raa,deca,xa,ya,astmask = select_good_ast(astcat,hdr,racol,deccol,edgedist)
      if verbose:
         print 'Found %d astrometric objects within FOV of image' % raa.size
         
      """
      Find the closest match to each astrometric catalog object
      """
      self.match_xy(xa,ya,max_offset,xcol,ycol,verbose)

      """ Transfer info about matches into the object """
      xfield = 'f%d' % xcol
      yfield = 'f%d' % ycol
      self.astmask  = astmask.copy()
      self.matchx   = self.data[xfield][self.matchind].copy()
      self.matchy   = self.data[yfield][self.matchind].copy()
      self.matchra  = raa[self.goodmask].copy()
      self.matchdec = deca[self.goodmask].copy()
      self.matchdx  = self.matchdx[self.goodmask]
      self.matchdy  = self.matchdy[self.goodmask]

      """ Plot the offsets if desired """
      if doplot:
         dxmed = n.median(self.matchdx)
         dymed = n.median(self.matchdx)
         plt.figure()
         plt.scatter(self.matchdx,self.matchdy)
         plt.xlabel('x offset (pix)')
         plt.ylabel('y offset (pix)')
         plt.axhline(color='k')
         plt.axvline(color='k')
         plt.axvline(dxmed,color='r')
         plt.axhline(dymed,color='r')
         print ""
         print "Black lines represent x=0 and y=0 axes"
         print "Red lines show median offsets of dx_med=%7.2f and dy_med=%7.2f" \
             % (dxmed,dymed)
         #plt.show()

      """ Write the output file, in a format appropriate for input to ccmap """
      if outfile is not None:
         self.print_ccmap(outfile,verbose)

      """ Clean up """
      hdulist.close()
      del hdr,raa,deca,xa,ya,astmask

#------------------------------------------------------------------------------

def on_click(event):
   print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
      event.button, event.x, event.y, event.xdata, event.ydata)

#------------------------------------------------------------------------------

def select_good_ast(astcat, hdr, racol=0, deccol=1, edgedist=50.):
   """
   Creates a mask that identifies the astrometric objects that fall within
   the field of view of the detector.  Returns ra, dec, x, y for the good
   objects

   Inputs:
      astcat   - catalog containing astrometric information
      hdr      - header from the fits file
      racol    - column in astcat containing the RA (zero-indexed)
      deccol   - column in astcat containing the Dec (zero-indexed)
      edgedist - Distance from edge for objects to be considered good
   """

   nx = hdr['naxis1']
   ny = hdr['naxis2']

   mra0,mdec0 = n.loadtxt(astcat,usecols=(racol,deccol),unpack=True)
   mx0,my0 = wcs.sky2pix(hdr,mra0,mdec0)
   goodmask = (mx0>edgedist) & (mx0<nx-edgedist) & \
       (my0>edgedist) & (my0<ny-edgedist)
   mra  = mra0[goodmask]
   mdec = mdec0[goodmask]
   mx   = mx0[goodmask]
   my   = my0[goodmask]
   
   return mra, mdec, mx, my, goodmask

#------------------------------------------------------------------------------

def match_xy(xast, yast, xfits, yfits):
   """
   Finds the closest match, in (x,y) space to each member of the astrometric
   catalog (represented by xast,yast).
   """

   xmin = 0.*xast
   ymin = 0.*yast

   for i in range(xast.size):
      dx = xast[i] - xfits
      dy = yast[i] - yfits
      dpos = dx**2 + dy**2
      sindex = n.argsort(dpos)
      xmin[i] = xfits[sindex[0]]
      ymin[i] = yfits[sindex[0]]

   return xmin,ymin

#------------------------------------------------------------------------------

def calc_offsets(astcat, hdr, xfits, yfits, maxoffset=None, doplot=True,
                 racol=0, deccol=1, edgedist=50.):
   """
   Calculates the (x,y) offsets between the astrometric catalog and the
   catalog derived from the fits image.  The astrometric catalog (x,y) positions
   are derived from the (RA,Dec) values in the catalog, mapped to (x,y) using
   the fits header (hdr).

   """

   """
   Select the astrometric catalog objects that fall within the fits file FOV
   (at least with its current WCS)
   """
   raa,deca,xa,ya,astmask = select_good_ast(astcat,hdr,racol,deccol,edgedist)

   """
   Find the closest match to each astrometric catalog object and calculate the
   offsets.
   """
   xm,ym = match_xy(xa,ya,xfits,yfits)
   dx = xa - xm
   dy = ya - ym
   if maxoffset is not None:
      dpos = n.sqrt(dx**2 + dy**2)
      goodmask = dpos<maxoffset
   else:
      goodmask = n.ones(xast.size,dtype=bool)
   dxm = dx[goodmask]
   dym = dy[goodmask]
   

   """
   Plot the offsets if desired
   """
   if doplot:
      plt.figure()
      plt.scatter(dxm,dym)
      plt.xlabel('x offset (pix)')
      plt.ylabel('y offset (pix)')
      plt.axhline(color='k')
      plt.axvline(color='k')
      plt.axhline(n.median(dxm),color='r')
      plt.axvline(n.median(dym),color='r')
      plt.show()

   """
   Return the offsets
   """
   return dxm,dym

#------------------------------------------------------------------------------

def match_fits_to_ast(fitsfile, fitscat, astcat, outfile=None, max_offset=None, 
                      racol=1, deccol=2, xcol_fits=8, ycol_fits=9, 
                      doplot=True, edgedist=50., imhdu=0, verbose=True):

   """
   Given a fits file, its associated catalog, and an astrometric catalog,
   find the closest matches of the astrometric objects to those contained
   in the catalog derived from the fits file, using the WCS information
   in the fits header.
   """

   if(verbose):
      print "Running match_fits_to_ast with:"
      print "   fitsfile = %s" % fitsfile
      print "   fitscat  = %s" % fitscat
      print "   astcat   = %s" % astcat

   """
   Start by opening the fits file and reading the appropriate columns from
   the catalogs
   """
   hdulist = im.open_fits(fitsfile)
   if verbose:
      print ""
   hdulist.info()
   hdr         = hdulist[imhdu].header
   xfits,yfits = n.loadtxt(fitscat,unpack=True,usecols=(xcol_fits,ycol_fits))
   """
   Select the astrometric catalog objects that fall within the fits file FOV
   (at least with its current WCS)
   """
   raa,deca,xa,ya,astmask = select_good_ast(astcat,hdr,racol,deccol,edgedist)

   """
   Find the closest match to each astrometric catalog object and calculate the
   offsets.
   Do two loops, to deal with possible confusion of sources on first pass
   through
   """
   dxmed = 0
   dymed = 0
   for i in range(2):
      if verbose:
         print ''
         print 'Pass %d' % (i+1)
         print '------------------------'
      xa0 = xa - dxmed
      ya0 = ya - dymed
      xm0,ym0 = match_xy(xa0,ya0,xfits,yfits)
      if verbose:
         print 'Found %d matched objects' % xm0.size
      dx = xa - xm0
      dy = ya - ym0
      dxmed = n.median(dx)
      dymed = n.median(dy)
      if max_offset is not None:
         dpos = n.sqrt(dx**2 + dy**2)
         goodmask = dpos<max_offset
         if verbose:
            print "Applying a maximum offset cut of %7.1f pixels" % max_offset
            print "Median shifts before clipping: %7.2f %7.2f" % (dxmed,dymed)
      else:
         goodmask = n.ones(xa.size,dtype=bool)
      dxm  = dx[goodmask]
      dym  = dy[goodmask]
      xm   = xm0[goodmask]
      ym   = ym0[goodmask]
      ram  = raa[goodmask]
      decm = deca[goodmask]
      dxmed = n.median(dxm)
      dymed = n.median(dym)
      if verbose:
         print "Median shifts after pass:   %7.2f %7.2f" % (dxmed,dymed)

   """
   Plot the offsets if desired
   """
   if doplot:
      dxmed = n.median(dxm)
      dymed = n.median(dym)
      plt.figure()
      plt.scatter(dxm,dym)
      plt.xlabel('x offset (pix)')
      plt.ylabel('y offset (pix)')
      plt.axhline(color='k')
      plt.axvline(color='k')
      plt.axvline(n.median(dxm),color='r')
      plt.axhline(n.median(dym),color='r')
      print ""
      print "Black lines represent x=0 and y=0 axes"
      print "Red lines show median offsets of dx_med=%7.2f and dy_med=%7.2f" \
          % (dxmed,dymed)
      #plt.show()

   if outfile is not None:
      if verbose:
         print ""
         print "Printing to output file %s" % outfile
         print ""
      f = open(outfile,'w')
      f.write('# (x,y) catalog: %s\n' % fitscat)
      f.write('# Astrometric catalog: %s\n' % astcat)
      f.write('# Columns are x y RA Dec\n')
      for i in range(xm.size):
         f.write('%8.2f %8.2f  %11.7f %+11.7f\n' % (xm[i],ym[i],ram[i],decm[i]))
      f.close()
      return
   else:
      return ram,decm,xm,ym,dxm,dym,astmask,goodmask

#------------------------------------------------------------------------------

def rscale_ccmap(ccmap_in, database, images, xcol=1, ycol=2, racol=3, deccol=4,
                 lngunits='degrees', latunits='degrees', interactive=True):
   """
   Uses the pyraf ccmap task to update the WCS
   """

   from pyraf import iraf

   iraf.ccmap(ccmap_in,database,images=images,xcolumn=xcol,ycolumn=ycol,
              lngcolumn=racol,latcolumn=deccol,lngunits=lngunits,
              latunits=latunits,insystem='j2000',fitgeometry='rscale',
              maxiter=1,reject=2.5,update=True,interactive=interactive)

#------------------------------------------------------------------------------

def fit_trans(update_wcs, fitsfile, fitscat, astcat, racol_ast=1, deccol_ast=2,
              xcol_fits=8, ycol_fits=9, max_offset=None, doplot=True,
              edgedist=50., imhdu=0):
   """
   Solves for the astrometry by fitting for a simple translation between
   the fits file coordinates and the astrometric catalog
   """

   """
   Start by opening the fits file and reading the appropriate columns from
   the catalogs
   """
   if update_wcs:
      hdulist = im.open_fits(fitsfile,'update')
   else:
      hdulist = im.open_fits(fitsfile)
   print ""
   hdulist.info()
   hdr         = hdulist[imhdu].header
   xfits,yfits = n.loadtxt(fitscat,unpack=True,usecols=(xcol_fits,ycol_fits))

   """
   Calculate the offsets
   """
   dx,dy = calc_offsets(astcat,hdr,xfits,yfits,max_offset,doplot,racol_ast,
                        deccol_ast,edgedist)
   dx_crpix = n.median(dx)
   dy_crpix = n.median(dy)
   print ""
   print "Median offsets are: %+7.2f %+7.2f" % (dx_crpix,dy_crpix)

   """
   Apply the correction to the WCS, for now only in memory
   """
   print "Applying median offsets to the WCS CRPIX values"
   hdr['crpix1'] -= dx_crpix
   hdr['crpix2'] -= dy_crpix

   """
   Plot the offsets after the correction, if desired
   """
   if doplot:
      dx,dy = calc_offsets(astcat,hdr,xfits,yfits,max_offset,doplot,racol_ast,
                           deccol_ast,edgedist)

   """
   Save the corrected WCS if requested
   """
   if update_wcs:
      hdulist.flush()
   else:
      hdulist.close()

#------------------------------------------------------------------------------

def plot_astcat(infile, astcat, rmarker=10., racol=0, deccol=1, hext=0):

   # Turn on interactive, so that plot occurs first and then query
   plt.ion()

   """ Load fits file """
   fitsim = im.Image(infile)
   hdr = fitsim.hdulist[hext].header

   """ Select astrometric objects within the FOV of the detector """
   mra,mdec,mx,my,astmask = select_good_ast(astcat,hdr,racol,deccol)

   """ Plot the fits file and mark the astrometric objects """
   fig = plt.figure(1)
   fitsim.display(cmap='heat')
   plt.plot(mx,my,'o',ms=rmarker,mec='g',mfc='none',mew=2)
   plt.xlim(0,nx)
   plt.ylim(0,ny)

   plt.draw()
   #cid = fig.canvas.mpl_connect('button_press_event', on_click)

   """ 
   Be careful of the +1 offset between SExtractor pixels and python indices
   """

   return fitsim


#------------------------------------------------------------------------------

def init_shifts(fitsim, astcat, xycat, rmarker=10., racol=0, deccol=1, 
                xcol=6, ycol=7, hext=0):
   """
   The user selects a pair of objects, one from the astrometric catalog
   (green circles plotted in plot_astcat) and one from the fits image.
   The pixel offset between the two is calculated, converted into arcsec,
   and then applied to the crval header cards in the input fits image.
   """

   """ Read x and y positions for sources in input catalog """
   xfits,yfits = n.loadtxt(xycat,usecols=(xcol,ycol),unpack=True)

   """ Get WCS information from input fits file """
   hdr = fitsim.hdulist[hext].header.copy()
   wcsinfo = wcs.parse_header(hdr)
   cdelt1,cdelt2,crota1,crota2 = coords.cdmatrix_to_rscale(wcsinfo[2])
   print ""
   print "Current parameters of image"
   print "---------------------------"
   print " Pixel scales (arcsec/pix): %6.3f %6.3f" % (-cdelt1*3600.,cdelt2*3600.)
   print " Image rotation (deg N->E): %+7.2f" % (crota2 * 180./pi)

   """ Select astrometric objects within the FOV of the detector """
   mra,mdec,mx,my,astmask = select_good_ast(astcat,hdr,racol,deccol)

   """ Select astrometric object used to determine the shift """
   print ""
   print "Determining initial shifts"
   print "----------------------------------------------------------"
   print "Choose a green circle that can clearly matched to an object in the"
   print " image."
   foo = raw_input(
       'Enter position for the chosen circle (just need to be close) [x y]: ')
   while len(foo.split()) != 2:
      print "ERROR.  Need to enter as two space-separated numbers."
      foo = raw_input('Enter position again: ')
   xast0,yast0 = foo.split()
   dist = n.sqrt((mx - float(xast0))**2 + (my - float(yast0))**2)
   astind = n.argsort(dist)[0]
   print "Closest match in astrometric catalog found at %8.2f %8.2f" % \
       (mx[astind],my[astind])

   """ Select the matching object in the xy catalog """
   print ""
   print "Now hoose the matching object seen in the fits image."
   foo = raw_input(
       'Enter position for the chosen object (just need to be close) [x y]: ')
   while len(foo.split()) != 2:
      print "ERROR.  Need to enter as two space-separated numbers."
      foo = raw_input('Enter position again: ')
   xcat0,ycat0 = foo.split()
   dist = n.sqrt((xfits - float(xcat0))**2 + (yfits - float(ycat0))**2)
   catind = n.argsort(dist)[0]
   print "Closest match in image catalog found at %8.2f %8.2f" % \
       (xfits[catind],yfits[catind])

   """ Calculate the offets in arcsec """
   dxpix = xfits[catind] - mx[astind]
   dypix = yfits[catind] - my[astind]
   da = dxpix * cdelt1
   dd = dypix * cdelt2
   print ""
   print "Calculated Offsets (image - astrometric)"
   print "----------------------------------------"
   print "x:  %+7.2f pix  %+7.2f arcsec" % (dxpix,da*3600.)
   print "y:  %+7.2f pix  %+7.2f arcsec" % (dypix,dd*3600.)


   #fig = plt.figure(1)
   #cid = fig.canvas.mpl_connect('button_press_event', on_click)
   
   #print "Done with that"
   #fig.canvas.mpl_disconnect(cid)
