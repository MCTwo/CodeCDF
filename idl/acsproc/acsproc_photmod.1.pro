function acsproc_datafile, subexposure, cutout=cutout, rectify=rectify, combine=combine, mask=mask, photmod=photmod, biz=biz, old=old, hst_root=hst_root, ext=ext, subext=subext
  
  common acsproc_photmod_data, acs_filter, dataroot

  if keyword_set(ext) then begin
    ftype = ''
    extension = '.' + ext 
  endif else begin
    ftype = '_flt'
    extension = '.fits'
  endelse
  
  if keyword_set(subext) then subext = '_' + subext else subext = ''

  if keyword_set(mask) then extension = '_mask' + extension $
  else if keyword_set(old) and keyword_set(photmod) then extension = '_photmod_old' + extension $
  else if keyword_set(photmod) then extension = '_photmod' + extension $
  else if keyword_set(biz) then extension = '_biz' + extension
  if keyword_set(old) and keyword_set(photmod) then old=0L

  if keyword_set(mask) or keyword_set(photmod) or keyword_set(biz) then combine = 1L

  if keyword_set(hst_root) then begin
    datafile = dataroot + subexposure + extension
  endif else if keyword_set(combine) then begin
    filter = acs_filter[subexposure[0].filtcode]
    datafile = dataroot + subexposure[0].visit + '/'+ subexposure[0].uniqname + '_' + $
               strtrim(string(subexposure[0].proposid, format='(i)'),2) + '_' + $
               strtrim(string(subexposure[0].expstart, format='(i)'),2) + '_' + $
               filter + '_' +  strtrim(subexposure[0].nexp,2) + subext + extension 
    if keyword_set(old) then datafile = dataroot  + 'old/'+ subexposure[0].uniqname + '_' + $
               strtrim(string(subexposure[0].proposid, format='(i)'),2) + '_' + $
               strtrim(string(subexposure[0].expstart, format='(i)'),2) + '_' + $
               filter + '_' +  strtrim(subexposure[0].nexp,2) + subext + extension 
  endif else begin
    datafile = dataroot + subexposure.visit + '/'+ subexposure.rootname + ftype
    if keyword_set(cutout) then datafile +=  '_cutout' + subext + extension $
    else if keyword_set(rectify) then datafile += '_recti' + subext + extension
  endelse
  
  return, datafile              
  
end

;---------------------------------------------------------------------
function acsproc_load_maskstruc, fits=fits
    
  if keyword_set(fits) then begin
    moffat = {modimID:fits.moffat_modimID, name:fits.moffat_name, modim:fits.moffat_modim, pars:fits.moffat_pars, pars_err:fits.moffat_pars_err, chi2:fits.moffat_chi2}
    bsplinecen = {modimID:fits.bsplinecen_modimID, name:fits.bsplinecen_name, modim:fits.bsplinecen_modim, dmodim:fits.bsplinecen_dmodim, pars:fits.bsplinecen_pars, pars_err:fits.bsplinecen_pars_err, chi2:fits.bsplinecen_chi2, nthetaID:fits.bsplinecen_nthetaID, rbkptID:fits.bsplinecen_rbkptID}
    bsplinefit = [{modimID:fits.bsplinecen_modimID, name:fits.bsplinecen_name, modim:fits.bsplinecen_modim, chi2:fits.bsplinecen_chi2, nthetaID:fits.bsplinecen_nthetaID, rbkptID:fits.bsplinecen_rbkptID}, $
                  {modimID:fits.bsplinefit_02_modimID, name:fits.bsplinefit_02_name, modim:fits.bsplinefit_02_modim, chi2:fits.bsplinefit_02_chi2, nthetaID:fits.bsplinefit_02_nthetaID, rbkptID:fits.bsplinefit_02_rbkptID}, $
                  {modimID:fits.bsplinefit_04_modimID, name:fits.bsplinefit_04_name, modim:fits.bsplinefit_04_modim, chi2:fits.bsplinefit_04_chi2, nthetaID:fits.bsplinefit_04_nthetaID, rbkptID:fits.bsplinefit_04_rbkptID}, $
                  {modimID:fits.bsplinefit_024_modimID, name:fits.bsplinefit_024_name, modim:fits.bsplinefit_024_modim, chi2:fits.bsplinefit_024_chi2, nthetaID:fits.bsplinefit_024_nthetaID, rbkptID:fits.bsplinefit_024_rbkptID}, $
                  {modimID:fits.bsplinefit_01_modimID, name:fits.bsplinefit_01_name, modim:fits.bsplinefit_01_modim, chi2:fits.bsplinefit_01_chi2, nthetaID:fits.bsplinefit_01_nthetaID, rbkptID:fits.bsplinefit_01_rbkptID}, $
                  {modimID:fits.bsplinefit_012_modimID, name:fits.bsplinefit_012_name, modim:fits.bsplinefit_012_modim, chi2:fits.bsplinefit_012_chi2, nthetaID:fits.bsplinefit_012_nthetaID, rbkptID:fits.bsplinefit_012_rbkptID}, $
                  {modimID:fits.bsplinefit_014_modimID, name:fits.bsplinefit_014_name, modim:fits.bsplinefit_014_modim, chi2:fits.bsplinefit_014_chi2, nthetaID:fits.bsplinefit_014_nthetaID, rbkptID:fits.bsplinefit_014_rbkptID}, $
                  {modimID:fits.bsplinefit_0124_modimID, name:fits.bsplinefit_0124_name, modim:fits.bsplinefit_0124_modim, chi2:fits.bsplinefit_0124_chi2, nthetaID:fits.bsplinefit_0124_nthetaID, rbkptID:fits.bsplinefit_0124_rbkptID}]
    maskstruc = {modimID:fits.modimID, xc:0L, yc:0L, has_modim:fits.has_modim, has_bizzle:fits.has_bizzle, has_photmod:fits.has_photmod, nthetaID:fits.nthetaID, lens_status:fits.lens_status, fmask:fits.fmask, jmask:fits.jmask, moffat:moffat, bsplinecen:bsplinecen, bsplinefit:bsplinefit}
  endif else begin
    mask = bytarr(imsize,imsize)
    modim = fltarr(2*hw+1,2*hw+1)
    moffat = {modimID:0L, name:'Moffat Fit', modim:modim, pars:fltarr(7), pars_err:fltarr(7), chi2:0.0}
    bsplinecen = {modimID:1L, name:'Bspline Cen', modim:modim, dmodim:modim, pars:fltarr(4), pars_err:fltarr(4), chi2:0.0, nthetaID:0L, rbkptID:0L}
    bsplinefit = replicate({modimID:2L, name:'Bspline Fit', modim:modim, pars:fltarr(4), pars_err:fltarr(4), chi2:0.0, nthetaID:0L, rbkptID:0L},8)
    maskstruc = {modimID:0L, xc:0L, yc:0L, nthetaID:0L, lens_status:0L, has_modim:0L, has_bizzle:0L, has_photmod:0L, fmask:mask, jmask:mask, moffat:moffat, bsplinecen:bsplinecen, bsplinefit:bsplinefit}
  endelse
  
  return, maskstruc
  
 end
;---------------------------------------------------------------------
function acsproc_get_maskstruc, maskfile, header=mask_header

  if file_test(maskfile) then begin
    maskstruc =  struct_addtags(acsproc_load_maskstruc(fits=mrdfits(maskfile, 1, mask_header, /silent)), {saved:1L})
  endif else begin
    maskstruc = struct_addtags(acsproc_load_maskstruc(), {saved:0L})
  endelse
  
  return, maskstruc
      
 end
;---------------------------------------------------------------------
pro acsproc_maskstruc_write, maskstruc, maskfile, header=mask_header

  ; flatten the maskstruc so it can be saved as a fits file.
    
  flat_maskstruc = {modimID:maskstruc.modimID, xc:maskstruc.xc, yc:maskstruc.yc, nthetaID:maskstruc.nthetaID, lens_status:maskstruc.lens_status, has_modim:maskstruc.has_modim, has_bizzle:maskstruc.has_bizzle, has_photmod:maskstruc.has_photmod, fmask:maskstruc.fmask, jmask:maskstruc.jmask, $
    moffat_modimID:maskstruc.moffat.modimID, moffat_name:maskstruc.moffat.name, moffat_modim:maskstruc.moffat.modim, moffat_pars:maskstruc.moffat.pars, moffat_pars_err:maskstruc.moffat.pars_err, moffat_chi2:maskstruc.moffat.chi2, $
    bsplinecen_modimID:maskstruc.bsplinecen.modimID, bsplinecen_name:maskstruc.bsplinecen.name, bsplinecen_modim:maskstruc.bsplinecen.modim, bsplinecen_dmodim:maskstruc.bsplinecen.dmodim, bsplinecen_pars:maskstruc.bsplinecen.pars, bsplinecen_pars_err:maskstruc.bsplinecen.pars_err, bsplinecen_chi2:maskstruc.bsplinecen.chi2, bsplinecen_nthetaID:maskstruc.bsplinecen.nthetaID, bsplinecen_rbkptID:maskstruc.bsplinecen.rbkptID, $
    bsplinefit_02_modimID:maskstruc.bsplinefit[1].modimID, bsplinefit_02_name:maskstruc.bsplinefit[1].name, bsplinefit_02_modim:maskstruc.bsplinefit[1].modim, bsplinefit_02_chi2:maskstruc.bsplinefit[1].chi2, bsplinefit_02_nthetaID:maskstruc.bsplinefit[1].nthetaID, bsplinefit_02_rbkptID:maskstruc.bsplinefit[1].rbkptID, $
    bsplinefit_04_modimID:maskstruc.bsplinefit[2].modimID, bsplinefit_04_name:maskstruc.bsplinefit[2].name, bsplinefit_04_modim:maskstruc.bsplinefit[2].modim, bsplinefit_04_chi2:maskstruc.bsplinefit[2].chi2, bsplinefit_04_nthetaID:maskstruc.bsplinefit[2].nthetaID, bsplinefit_04_rbkptID:maskstruc.bsplinefit[2].rbkptID, $
    bsplinefit_024_modimID:maskstruc.bsplinefit[3].modimID, bsplinefit_024_name:maskstruc.bsplinefit[3].name, bsplinefit_024_modim:maskstruc.bsplinefit[3].modim, bsplinefit_024_chi2:maskstruc.bsplinefit[3].chi2, bsplinefit_024_nthetaID:maskstruc.bsplinefit[3].nthetaID, bsplinefit_024_rbkptID:maskstruc.bsplinefit[3].rbkptID, $
    bsplinefit_01_modimID:maskstruc.bsplinefit[4].modimID, bsplinefit_01_name:maskstruc.bsplinefit[4].name, bsplinefit_01_modim:maskstruc.bsplinefit[4].modim, bsplinefit_01_chi2:maskstruc.bsplinefit[4].chi2, bsplinefit_01_nthetaID:maskstruc.bsplinefit[4].nthetaID, bsplinefit_01_rbkptID:maskstruc.bsplinefit[4].rbkptID, $
    bsplinefit_012_modimID:maskstruc.bsplinefit[5].modimID, bsplinefit_012_name:maskstruc.bsplinefit[5].name, bsplinefit_012_modim:maskstruc.bsplinefit[5].modim, bsplinefit_012_chi2:maskstruc.bsplinefit[5].chi2, bsplinefit_012_nthetaID:maskstruc.bsplinefit[5].nthetaID, bsplinefit_012_rbkptID:maskstruc.bsplinefit[5].rbkptID, $
    bsplinefit_014_modimID:maskstruc.bsplinefit[6].modimID, bsplinefit_014_name:maskstruc.bsplinefit[6].name, bsplinefit_014_modim:maskstruc.bsplinefit[6].modim, bsplinefit_014_chi2:maskstruc.bsplinefit[6].chi2, bsplinefit_014_nthetaID:maskstruc.bsplinefit[6].nthetaID, bsplinefit_014_rbkptID:maskstruc.bsplinefit[6].rbkptID, $
    bsplinefit_0124_modimID:maskstruc.bsplinefit[7].modimID, bsplinefit_0124_name:maskstruc.bsplinefit[7].name, bsplinefit_0124_modim:maskstruc.bsplinefit[7].modim, bsplinefit_0124_chi2:maskstruc.bsplinefit[7].chi2, bsplinefit_0124_nthetaID:maskstruc.bsplinefit[7].nthetaID, bsplinefit_0124_rbkptID:maskstruc.bsplinefit[7].rbkptID}

  splog, "CREATE: "+maskfile 
  mwrfits, flat_maskstruc, maskfile, mask_header, /create, /silent

 end
;---------------------------------------------------------------------
pro acsproc_database_update_photmod, program_number, visit_number, filename, message=message, confirm=confirm
  ;==============================================================================
  ; Database Function: insert exposure redux_name and receive message response from database
  ;==============================================================================

  cmd = 'photmod_update'
  arg = " -p "+strtrim(program_number,2) + " -v "+visit_number + " -f "+filename
  spawn, cmd+arg, response
  pos = strlen(cmd+" > ") & message = ""
  start = cmd+" > START*" & started = 0
  done = cmd+" > DONE*" & confirm = 0
  for i=0,n_elements(response)-1 do begin
    if not keyword_set(started) and strmatch(response[i],start) then started=1 $
    else if not keyword_set(confirm) and strmatch(response[i],done) then confirm=1 $
    else if keyword_set(started) and not keyword_set(confirm) then message += strmid(response[i],pos)
  endfor
end
;---------------------------------------------------------------------
pro acsproc_photmod, visit, flatweight=flatweight, cycle=cycle,program=program

  common acsproc_photmod_data

  smartguess = keyword_set(flatweight)   
  ;modim half-width
  hw = 140
  ;size of cutout
  imsize = 1024L
  
  ; PSF half-width:
  phw = 18
  ; pixel size:
  dpix = 0.05D
  
  acs_filter = ['','F435W','F555W','F814W']
  acs_filtwave = [0,4350,5550,8140] ;Angstroms

  fitfunc = ['asb_devauc_multi','asb_sersic_multi']
  fitfunc_label = ['de Vauc','Sersic']

  if not keyword_set(cycle) then cycle='18'
  if not keyword_set(program) then program='12210'
  hst_dataroot=getenv('HST_DATAROOT')
  cycle_program = strtrim(cycle,2) + '/' + strtrim(program,2)
  dataroot = djs_filepath('', root=hst_dataroot, subdir=cycle_program)
  metafile = djs_filepath('.metafile.fits', root=dataroot)
  metastruc = mrdfits(metafile, 1)

  nrows = n_elements(metastruc)
  maskflag = 4
  selected = where(metastruc.visit eq visit and metastruc.subexposure eq 1,nvis) 
      
  if (nvis gt 0) then begin
  
    metastruc_visit = metastruc[selected]
    for q = 0,nvis-1 do begin
    

      combfile = acsproc_datafile(metastruc_visit[q],/combine)
      photmodfile = acsproc_datafile(metastruc_visit[q],/photmod,old=1-keyword_set(flatweight))
      bizfile = acsproc_datafile(metastruc_visit[q],/biz)
            
      ;bz2file = strmid(combfile, 0,strpos(combfile,'.fits')) + '.bz2'

      maskfile = acsproc_datafile(metastruc_visit[q],/mask)
      maskstruc = acsproc_get_maskstruc(maskfile, header=mask_header)
  
      xc = round(sxpar(mask_header, 'CRPIX1'))-1L
      yc = round(sxpar(mask_header, 'CRPIX2'))-1L
      
      bspars = maskstruc.bsplinecen.pars

      img = mrdfits(combfile, 1, hdr)
      err = mrdfits(combfile, 2)
      nim = mrdfits(combfile, 3)
      
      ivar = (nim gt 0) * (err gt 0.) / (err^2 + (nim le 0) + (err le 0.))
      
      pixel_mask = (1B-maskstruc.fmask)*(1B-maskstruc.jmask)
      ivar = ivar * pixel_mask
      
      ; Make RA and Dec images:
      aimg = -dpix * (dindgen(2*hw+1) # replicate(1.d0, 2*hw+1) - hw)
      dimg = dpix * (replicate(1.d0, 2*hw+1) # dindgen(2*hw+1) -  hw)
  
      psf = mrdfits(combfile, 4)
      nx_psf = (size(psf))[1]
      junk = max(psf, wmax)
      pxc = wmax mod nx_psf
      pyc = wmax / nx_psf
      psf = psf[pxc-phw:pxc+phw,pyc-phw:pyc+phw]
      psf = psf / total(psf)
  
      ymask = 0B * byte(ivar)
      ymask[xc-hw:xc+hw,yc-hw:yc+hw] = 1B
      pmask = replicate(0B, imsize, imsize)
      pmask[phw:imsize-(phw+1),phw:imsize-(phw+1)] = 1B
      ivar = ivar * pmask
      pmask = 0

      ; Get the right pixel statistics:
      djs_iterstat, img * sqrt(ivar), sigma=errsig
      ivar = ivar / errsig^2
      
      ; A fit with flat weighting:
      if keyword_set(flatweight) then begin
        med_ivar = median(ivar[where(ivar gt 0.)])
        ivar_weight = med_ivar * (ivar gt 0.)
      endif else ivar_weight = ivar
        
      ; Do the initial deVaucouleurs fit:
      dspars = [10., 2., bspars]
      if keyword_set(smartguess) then begin
          ivar_weight0 = alog(maskstruc.bsplinecen.modim/min(maskstruc.bsplinecen.modim))
          img0 = maskstruc.bsplinecen.modim
          parinfo = replicate({value:0.D, fixed:1}, n_elements(dspars))
          parinfo[*].value = dspars
          parinfo[0:1].fixed = 0
          splog, "MPFIT > SMARTGUESS **************************************************************"
          devpars = mpfit2dfun(fitfunc[0], dimg, aimg, img0, 0.*img0, dspars, weights=ivar_weight0, functargs={psf: psf, rmin: 0.1*dpix}, bestnorm=bestnorm, perror=perror, niter=niter, yfit=yfit00, covar=covar, parinfo=parinfo, dof=dof, /silent)
          dspars = devpars
          dspars[1] = abs(dspars[1])
          splog, "MPFIT > SMARTGUESS completed with REDUCED CHI^2 ="+strtrim(bestnorm/dof,2)
      endif else dspars = [10., 2., bspars]
            
      ivar0 = ivar[xc-hw:xc+hw,yc-hw:yc+hw]
      ivar_weight0 = ivar_weight[xc-hw:xc+hw,yc-hw:yc+hw]
      img0 = img[xc-hw:xc+hw,yc-hw:yc+hw]

      splog, "MPFIT > Initial deVaucouleurs **************************************************************"
      devpars = mpfit2dfun(fitfunc[0], dimg, aimg, $
        img0, 0.*img0, dspars, weights=ivar_weight0, functargs={psf: psf, rmin: 0.1*dpix}, $
        bestnorm=bestnorm, perror=perror, niter=niter, yfit=yfit0, covar=covar)
                
      ndof = long(total(ivar0 gt 0.)) - n_elements(devpars)
      splog, "MPFIT > Initial deVaucouleurs fit completed with REDUCED CHI^2 ="+strtrim(bestnorm/ndof,2)
      yfit = img*0.
      yfit[xc-hw:xc+hw,yc-hw:yc+hw] = yfit0

      ; Make RA and Dec images:
      aimg = -dpix * (findgen(imsize) - xc) # replicate(1.0, imsize)
      dimg = dpix * replicate(1.0, imsize) # (findgen(imsize) - yc)

      ndof = long(total(ivar gt 0.)) - n_elements(devpars)
 
      ; Make a mask for any outlying junk:
      sigthresh = 4.0
            
      outermask = ((img-yfit) * sqrt(ivar)) ge sigthresh
      outermask = outermask * (ymask eq 0)
      ivar = ivar * (outermask eq 0)
      
      for i=0,n_elements(fitfunc)-1 do begin
      
        if (i eq 0) then pars = devpars $
        else if (i eq 1) then pars = [devpars, 4.]

        ; Do the smart mask fit for each fitfunc
        splog, "MPFIT > SMARTMASK: "+fitfunc_label[i]+" **************************************************************"
        pars = mpfit2dfun(fitfunc[i], dimg, aimg, $
          img, 0.*img, pars, weights=ivar_weight, functargs={psf: psf, rmin: 0.1*dpix}, $
          bestnorm=bestnorm, perror=perror, niter=niter, yfit=yfit, covar=covar)
            
        ;;; If you dare...
        ; Subsample the grid and do one last MPFIT:
        subs = 5
        xbase = 0.5 * (2.*findgen(imsize*subs) + 1. - float(subs))/float(subs)
        ybase = 0.5 * (2.*findgen(imsize*subs) + 1. - float(subs))/float(subs)
        abig = bilinear(aimg, xbase, ybase)
        dbig = bilinear(dimg, xbase, ybase)
        xbase = 0
        ybase = 0
        
        splog, "MPFIT > "+fitfunc_label[i]+" **************************************************************"
        pars = mpfit2dfun(fitfunc[i], dbig, abig, $
          img, 0.*img, pars, weights=ivar_weight, $
          functargs={psf: psf, rmin: 0.1*dpix, subs: subs}, $
          bestnorm=bestnorm, perror=perror, niter=niter, yfit=yfit, covar=covar)
        ; Keep it positive!
        pars[1] = abs(pars[1])
          
        ;-------------------------------------------------------------------------
              
        splog, "REDUCED CHI^2 of "+fitfunc_label[i]+" fit="+strtrim(bestnorm/ndof,2)

        if fitfunc[i] eq 'asb_devauc_multi' then photimg = asb_devauc_multi(dimg,aimg,pars,rmin=0.1*dpix,psf=psf) $
        else if fitfunc[i] eq 'asb_sersic_multi' then photimg = asb_sersic_multi(dimg,aimg,pars,rmin=0.1*dpix,psf=psf) $
        else photimg = img*0.0
   
        photmodstruc = {fitfunc: fitfunc[i], img:photimg, pars: pars, perror: perror, $
          covar: covar, chisq: bestnorm, ndof: ndof, xc: xc, yc: yc}
  
        abig = 0
        dbig = 0
        
        if (i eq 0) then begin
        
          ; Turn this all into proper band photometry:
          
          ; Get the deVaucouleurs fit parameters and the photometric
          ; header keyword parameters:
          photflam = sxpar(hdr, 'PHOTFLAM')
          photplam = sxpar(hdr, 'PHOTPLAM')
          
          ; Convert deVaucouleurs model amplitude to counts, and to AB magnitude:
          k_dev = 7.66925001
          cps_dev = ((2. * !pi * pars[0] * pars[1]^2) * 4. * gamma(8.) / k_dev^8.) / (dpix^2)
          abmag_zpt = -2.5 * alog10(photflam) - 21.10 - 5. * alog10(photplam) + 18.6921
          abmag_dev = -2.5 * alog10(cps_dev) + abmag_zpt
          
          cps_deverr = cps_dev * (perror[0] / pars[0])
          acs_rdev = pars[1]
          acs_rdeverr = perror[1]
          acs_qdev = pars[4]
          acs_qdeverr = perror[4]
          acs_padev = pars[5]
          acs_padeverr = perror[5]
          
          if (acs_qdev gt 1.) then begin
            acs_qdev = 1./acs_qdev
            acs_qdeverr = acs_qdeverr * acs_qdev^2
            acs_padev = acs_padev + 90.
          endif
          pa = acs_padev mod 180.
          ptest = pa ge 0.
          pa = pa * ptest + (180. - abs(pa)) * (1B - ptest)
          acs_padev = pa
                    
          mwrfits, photmodstruc, photmodfile, /create, /silent
          
        endif else if (i eq 1) then begin
        
          acs_nser = pars[6]
          acs_nsererr = perror[6]

          mwrfits, photmodstruc, photmodfile, /silent
          
        endif
       
      endfor 

      ;-------------------------------------------------------------------------
      ; Breakpoints for b-spline photometry:
      rbkpt = dpix*[1., 2., 4., 6., 8., 12., 16., 22., 30., 50., 60., 100., 150., 200., 300., 400., 500., 600., 800.]
      
      ; Do the b-spline photometry:
      bfit = bspline_ellip(dspars[2:*], x=dimg, y=aimg, invvar=ivar, data=img, psf=psf, ntheta=0, rbkpt=rbkpt, sset=sset)
      
      ; Store the bspline photometry of interest.
      ; Really we're just evaluating the ellipsoidal
      ; b-spline surface brightness on a baseline.
      ; Anything else we want to do can be done later.

      bsr_arcs = (findgen(800) + 1.) / 100.
      bsflux = bsr_arcs
      bsflux = bspline_valu(bsr_arcs, sset)

      ;-------------------------------------------------------------------------

      photmodstruc = {photflam: photflam, photplam: photplam, abmag_zpt:abmag_zpt, abmag_dev: abmag_dev, $
         cps_dev: cps_dev, cps_deverr: cps_deverr, acs_rdev: acs_rdev, acs_rdeverr: acs_rdeverr, acs_qdev: acs_qdev, $
         acs_qdeverr: acs_qdeverr, acs_padev: acs_padev, acs_padeverr: acs_padeverr, acs_nser: acs_nser, acs_nsererr: acs_nsererr, $
         bsr_arcs: bsr_arcs, bsflux: bsflux, outermask:outermask}
      
      mwrfits, photmodstruc, photmodfile, /silent
            
      has_photmod = maskstruc.has_photmod
      maskstruc.has_photmod = file_test(photmodfile)
      if has_photmod ne maskstruc.has_photmod then acsproc_maskstruc_write, maskstruc, maskfile, header=mask_header
      
      acsproc_database_update_photmod, metastruc_visit[q].proposid, metastruc_visit[q].visit, file_basename(photmodfile), confirm=confirm, message=message
      if confirm then splog, 'Database > '+message else splog, 'update photmod failed.'
      

    endfor
  
  endif
        
end
