import os
import pandas as pd
import numpy as np
import colour
from math import pi
from pathlib import Path
from typing import Optional, Union
import scipy.interpolate as sip
from scipy.interpolate import RegularGridInterpolator
import msdb

from . import config
from . import MFT_info_dictionaries
from . import MFT_info_templates


def MFT_fotonowy(files: list, filenaming:Optional[str] = 'none', folder:Optional[str] = '.', db:Optional[bool] = False, comment:Optional[str] = '', device_nb:Optional[str] = 'default', authors:Optional[str] = 'XX', white_standard:Optional[bool] = 'default', interpolation:Optional[str] = 'He', step:Optional[float | int] = 0.1, average:Optional[int] = 20, observer:Optional[str] = 'default', illuminant:Optional[str] = 'default', background:Optional[str] = 'black', delete_files:Optional[bool] = True, return_filename:Optional[bool] = True):

            
    # check whether the objects and projects databases have been created
    
    if db:        
        db_name = config.get_config_info()['databases']['db_name']
        
        if db_name not in msdb.get_db_names():
            return 'The databases have not been created or registered.'
        
        else:   
            databases = msdb.DB(db_name)  
            db_projects = databases.get_projects()
            db_objects = databases.get_objects()
    
    else:
        filenaming = 'none'
   
    # define parameters for colorimetric calculations
    observers = {        
        '10deg': 'cie_10_1964',
        '2deg' : 'cie_2_1931',
    }
    
    cmfs_observers = {
        '10deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1964 10 Degree Standard Observer"],
        '2deg': colour.colorimetry.MSDS_CMFS_STANDARD_OBSERVER["CIE 1931 2 Degree Standard Observer"] 
    }

    if illuminant == 'default':
        if isinstance(databases.get_colorimetry_info(), str):
            illuminant = 'D65'
        else:
            illuminant = databases.get_colorimetry_info().loc['illuminant']['value']

    if observer == 'default':
        if isinstance(databases.get_colorimetry_info(), str):
            observer = '10deg'
        else:
            observer = databases.get_colorimetry_info().loc['observer']['value']

    illuminant_SDS = colour.SDS_ILLUMINANTS[illuminant]
    illuminant_CCS = colour.CCS_ILLUMINANTS[observers[observer]][illuminant]
    cmfs = cmfs_observers[observer]

    # wanted wavelength range
    wanted_wl = pd.Index(np.arange(380,781), name='wavelength_nm')
    
    # retrieve counts spectral files to be processed
    raw_files_counts = [Path(file) for file in files if 'spect_convert.txt' in Path(file).name]
    
    
    # process each spectral file
    for raw_file_counts in raw_files_counts:

                
        # retrieve the corresponding colorimetric file
        raw_file_cl = Path(str(raw_file_counts).replace('-spect_convert.txt', '.txt'))
        stemName = raw_file_cl.stem.replace(" ", "_")                                 

        # upload raw files into dataframes
        raw_df_counts = pd.read_csv(raw_file_counts, sep='\t', skiprows = 1)
        raw_df_cl = pd.read_csv(raw_file_cl, sep='\t', skiprows = 8)        

        # round up the first and last wavelength values
        raw_df_counts.rename(index={380.024:380},inplace=True)
        raw_df_counts.rename(index={779.910:780},inplace=True)

        # select white and dark spectral references (first and second columns respectively)
        white_ref = raw_df_counts.iloc[:,0].values
        dark_ref = raw_df_counts.iloc[:,1].values
        
        # remove the white and dark ref        
        df_counts = raw_df_counts.iloc[:,2:-1]  
        df_counts.columns = raw_df_counts.columns[3:] 

        # rename the index column
        df_counts.index.name = 'wavelength_nm'               

        # create an empty dataframe for the spectral reflectance values        
        raw_df_sp = pd.DataFrame(index=raw_df_counts.index)
        raw_df_sp.index.name = 'wavelength_nm'        

        # drop the before last column of df_counts
        df_counts = df_counts.drop(df_counts.iloc[:,-2].name,axis=1)
        
        # compute the reflectance values
        for col in df_counts.columns:  
            counts = df_counts[col].values
            sp = pd.Series(counts / white_ref, index=df_counts.index, name=col[15:])
            raw_df_sp = pd.concat([raw_df_sp,sp], axis=1)   
                
        # retrieve the times and energy values        
        times = raw_df_cl['#Time']
        interval_sec = int(np.round(times.values[3] - times.values[2],0))
        numDataPoints = len(times)        
        duration_min = int(np.round(times.values[-1] /60, 2))
        He = raw_df_cl['Watts']       # in MJ/m²
        Hv = raw_df_cl['Lux']         # in Mlxh
        total_He = He.values[-1]
        total_Hv = Hv.values[-1]
        ill = (60 * total_Hv) / duration_min
        irr = (total_He*1e6) / (duration_min * 60)
         
        
        # interpolate the data
        if interpolation == 'none':   
            df_sp = raw_df_sp
            df_sp.columns = [float(col[:-3]) for col in df_sp.columns]

            df_cl = np.round(raw_df_cl,3)
            df_cl = df_cl[['Watts', 'Lux', '#Time', 'L','a','b','dE76','dE2000']]
            df_cl.columns = ['He_MJ/m2', 'Hv_Mlxh','t_sec', 'L*', 'a*','b*', 'dE76', 'dE00']  

            LCh = np.round(colour.Lab_to_LCHab(df_cl[['L*','a*','b*']].values).T,3)

            df_cl['C*'] = LCh[1]
            df_cl['h'] = LCh[2]

            df_cl = df_cl[['He_MJ/m2', 'Hv_Mlxh','t_sec', 'L*','a*','b*','C*','h','dE76','dE00']]
                          
        else:
            # define abscissa units
            abs_scales = {'He': He, 'Hv': Hv, 't': times}
            abs_scales_name = {'He': 'He_MJ/m2', 'Hv': 'Hv_Mlxh', 't': 't_sec'}           

            #  define the abscissa range according to the choosen step value
            wanted_x = np.arange(0, abs_scales[interpolation].values[-1], step)            
                          
            # create a dataframe for the energy and time on the abscissa axis        
            df_abs = pd.DataFrame({'t_sec':times, 'He_MJ/m2': He,'Hv_Mlxh': Hv})
            df_abs = df_abs.set_index(abs_scales_name[interpolation])

            # create an interp1d function for each column of df_abs
            abs_interp_functions = [sip.interp1d(df_abs.index, df_abs[col], kind='linear', fill_value='extrapolate') for col in df_abs.columns]            

            # interpolate all columns of df_abs simultaneously
            interpolated_abs_data = np.vstack([f(wanted_x) for f in abs_interp_functions]).T

            # Create a new DataFrame with the interpolated data
            interpolated_df = pd.DataFrame(interpolated_abs_data, index=wanted_x, columns=df_abs.columns)

            interpolated_df.index.name = abs_scales_name[interpolation]
            interpolated_df = interpolated_df.reset_index()

            # insert a row at the top with the word 'value' as input
            df_value = pd.DataFrame({'He_MJ/m2':'value','t_sec':'value','Hv_Mlxh':'value'}, index=['value'])
            interpolated_df = pd.concat([df_value, interpolated_df])
            interpolated_df = interpolated_df.reset_index().drop('index', axis=1)          
            
            # modify the columns names according to the choosen abscissa unit
            raw_df_sp.columns = abs_scales[interpolation]
            
            # interpolate the reflectance values according to the wavelength and the abscissa range
            interp = RegularGridInterpolator((raw_df_sp.index,raw_df_sp.columns), raw_df_sp.values)

            pw, px = np.meshgrid(wanted_wl, wanted_x, indexing='ij')     
            interp_data = interp((pw, px))    
            df_sp_interp = pd.DataFrame(interp_data, index=wanted_wl, columns=wanted_x)
                   

            # empty list to store XYZ values
            XYZ = []

            # calculate the LabCh values
            for col in df_sp_interp.columns:
                sd = colour.SpectralDistribution(df_sp_interp[col], wanted_wl)
                XYZ.append(colour.sd_to_XYZ(sd, cmfs, illuminant=illuminant_SDS))        

            XYZ = np.array(XYZ)

            Lab = np.array([colour.XYZ_to_Lab(d / 100, illuminant_CCS) for d in XYZ])
            LCh = np.array([colour.Lab_to_LCHab(d) for d in Lab])
                    
            L = ['value']
            a = ['value']
            b = ['value']
            C = ['value']
            h = ['value']

            [L.append(np.round(i[0],3)) for i in Lab]
            [a.append(np.round(i[1],3)) for i in Lab]
            [b.append(np.round(i[2],3)) for i in Lab]
            [C.append(np.round(i[1],3)) for i in LCh]
            [h.append(np.round(i[2],3)) for i in LCh]

                
            # compute the delta E values
            dE76 = ['value'] + list(np.round(np.array([colour.delta_E(Lab[0], d, method="CIE 1976") for d in Lab]),3))
            dE00 = ['value'] + list(np.round(np.array([colour.delta_E(Lab[0], d) for d in Lab]),3))

            # calculate dR_VIS and dR
            dR_vis = ['value']                                                    # empty list to store the dRvis values                                   
            df_sp_vis = df_sp_interp.loc[400:740]                                 # reflectance spectra in the visible range
            sp_initial = (df_sp_vis.iloc[:,0].values) * 100                       # initial spectrum
        
            for col in df_sp_vis.columns:
                sp = df_sp_vis[col]
                dR_val = np.sum(np.absolute(sp*100-sp_initial)) / len(sp_initial)           
                dR_vis.append(np.round(dR_val,3))      
                        
            # create the colorimetric dataframe
            df_cl = pd.DataFrame({'L*': L,
                                'a*': a,
                                'b*': b,
                                'C*': C,
                                'h': h,
                                'dE76': dE76,
                                'dE00': dE00,
                                'dR_vis': dR_vis
                                })                
            
            # concatenate the energy values with df_cl
            df_cl = pd.concat([interpolated_df,df_cl], axis=1, ignore_index=False)

            # add a new row 'value' at the top
            df_value = pd.DataFrame(df_sp_interp.shape[1] * ['value'], columns=['value']).T
            df_value.index.name = 'wavelength_nm'            
            df_value.columns = df_sp_interp.columns
            df_sp_interp = pd.concat([df_value, df_sp_interp]) 
            
            # name the columns
            df_sp_interp.columns.name = abs_scales_name[interpolation]  
            
            # rename spectral dataframe
            df_sp = df_sp_interp
            

        ###### CREATE INFO DATAFRAME ####### 

        # retrieve the information about the analysis        
        lookfor = '#Time'
        file_raw_cl = open(raw_file_cl).read()

        infos = file_raw_cl[:file_raw_cl.index(lookfor)].splitlines()
        dic_infos = {}

        for i in infos:             
            key = i[2:i.index(':')]
            value = i[i.index(':')+2:]              
            dic_infos[key]=[value]

        dic_infos.pop('Illuminant') # remove the Illuminant info
        dic_infos['meas_id'] = f'{dic_infos["Object"][0]}_{dic_infos["Sample"][0]}'
        df_info = pd.DataFrame.from_dict(dic_infos).T 
            
            
        if db == False:          

            df_info.loc['illuminant'] = illuminant
            df_info.loc['observer'] = observer
            df_info.loc['duration_min'] = duration_min
            df_info.loc['interval_sec'] = interval_sec
            df_info.loc['numDataPoints'] = numDataPoints 
            df_info.loc['radiantExposure_He_MJ/m^2'] = np.round(total_He, 3)
            df_info.loc['exposureDose_Hv_Mlxh'] = np.round(total_Hv, 3)
            df_info.loc['illuminance_Ev_Mlx'] = np.round(ill, 4)
            df_info.loc['irradiance_Ee_W/m^2'] = int(irr)            

            current = int(df_info.loc['Curr'].values[0].split(' ')[0])
            df_info.loc['Curr'] = current
            df_info = df_info.rename(index={'Curr': 'current_mA'})

            df_info.index.name = 'parameter'
            df_info.columns = ['value']  
            df_info = df_info.reset_index()

        else:
                
            if 'project_id' in db_objects.columns:
                db_objects = db_objects.drop('project_id', axis=1)
                
            info_parameters = [
            "[SINGLE MICROFADING ANALYSIS]",
            "authors",
            "host_institution",
            "date_time",
            "comment",
            "[PROJECT INFO]"] + list(db_projects.columns) + ["[OBJECT INFO]"] + list(db_objects.columns) + MFT_info_templates.device_info + MFT_info_templates.analysis_info + MFT_info_templates.spot_info + MFT_info_templates.beam_info + MFT_info_templates.results_info

            df_authors = databases.get_users()

            if authors == 'XX':
                authors_names = 'unknown'

            elif '-' in authors or ' - ' in authors:                     
                list_authors = []
                for x in authors.split('-'):
                    x = x.strip()
                    df_author = df_authors[df_authors['initials'] == x]
                    list_authors.append(f"{df_author['surname'].values[0]}, {df_author['name'].values[0]}")                    
                authors_names = '_'.join(list_authors)
                    
            else:                    
                df_author = df_authors[df_authors['initials'] == authors]
                authors_names = f"{df_author['surname'].values[0]}, {df_author['name'].values[0]}"

            
            
            config_info = config.get_config_info()
            if len(config_info['institution']) > 0:
                institution_info = config.get_institution_info()['value']
                host_institution_name = institution_info['name']
                host_institution_department = institution_info['department']

                if len(host_institution_department) > 0:
                    host_institution = f'{host_institution_name}_{host_institution_department}'
                else:
                    host_institution = host_institution_name
            else:
                host_institution = 'undefined'
                print('You might want to register the info of your institution in the config_info.json file -> mf.set_institution_info().')

            date_time = pd.to_datetime(df_info.loc['Date'].values[0])
            date = date_time.date()
            project_id = raw_file_cl.stem.split(' ')[0]
            object_id = raw_file_cl.stem.split(' ')[1]
            group = raw_file_cl.stem.split(' ')[2]
            group_description = raw_file_cl.stem.split(' ')[3].split('_')[0]            
            project_info = list(db_projects.query(f'project_id == "{project_id}"').values[0])
            object_info = list(db_objects.query(f'object_id == "{object_id}"').values[0])


            # Retrieve the device info values
            LED_nb = df_info.loc['LED'].values[0]
            LED_ID = f'LED{LED_nb}'
            df_LEDs = databases.get_lamps().set_index('ID')
            existing_LEDs = list(df_LEDs.index)

            if LED_ID in existing_LEDs:
                LED_description = df_LEDs.loc[LED_ID]['description']
                LED_info = f'{LED_ID}_{LED_description}'

            else:
                LED_info = LED_ID
                print(f'The LED_ID ({LED_ID}) related to your analysis is not present in the registered lamps ({existing_LEDs}). Please make sure to register it.')
                          

            df_devices = databases.get_devices()
            if device_nb in df_devices['ID'].values:
                df_devices = df_devices.set_index('ID')                    
                device_name = df_devices.loc[device_nb]['name']
                device_description = df_devices.loc[device_nb]['description']

            elif device_nb == 'default':
                device_nb = 'none'
                device_name = 'unnamed'
                device_description = 'Fotonowy-MFT'

            else:
                print(f'The device you entered ({device_nb}) has not been registered. Please first register the device, by using the function mf.register_devices().')
                return

            # Retrieve the white standard information
            df_WR = databases.get_white_standards()
            if white_standard in df_WR['ID'].values:
                df_WR = df_WR.set_index('ID')
                WR_nb = white_standard
                WR_description = df_WR.loc[white_standard]['description']
            elif white_standard == 'default':
                WR_nb = 'none'
                WR_description = 'Fotonowy fotolon PTFE'
            elif white_standard == 'unknown':
                WR_nb = 'none'
                WR_description = 'unknown'
            else:
                print(f'The white reference you entered ({white_standard}) has not been registered. Please first register the white reference, by using the function mf.add_references().')
                return
                
            # Gather all the device info inside a list
            device_info = [
                " ",
                f'{device_nb}_{device_name}_{device_description}', 
                'none',
                'none',
                'none',
                '0° : 45°',
                'unknown',
                'unknown',
                'none',
                'none',
                'Thorlabs, FT030',
                f'{LED_info}',
                'none',
                'none',
                'none',
                f'{WR_nb}_{WR_description}'   
            ]


            # Retrieve the analysis info values
                
            meas_nb = raw_file_cl.stem.split('_')[1]
            meas_id = f'MF.{object_id}.{meas_nb}'
            spec_comp = 'SCE_excluded'

            int_time_sample = int(df_info.loc['Sample integration time [ms]'].values[0])
            int_time_whitestandard = int(df_info.loc['White standard integration time [ms]'].values[0])
            fwhm = MFT_info_dictionaries.beam_FWHM[LED_nb]

            area = pi * (((fwhm/1e6)/2)**2)
            power = np.round((irr * area) * 1e3, 3)
            lum = np.round(area * (ill * 1e6),3)
            current = int(df_info.loc['Curr'].values[0].split(' ')[0])       
                           
            analysis_info = [
                " ",
                meas_id,                
                spec_comp,
                int_time_sample,
                int_time_whitestandard,
                average, 
                duration_min, 
                interval_sec,
                1,
                illuminant,
                observer,
            ]


            # spot info
            spot_image = ""
            other_analyses = ""
            spot_color = ""
            spot_components = ""

            spot_info = [
                " ",
                group, 
                group_description,
                spot_color,
                spot_components,
                background,
                spot_image,
                other_analyses,
            ]


            # beam info               
            beam_info = [
                " ",
                'none',
                'none',
                fwhm,
                current,
                power,
                lum,
                int(irr),
                np.round(ill, 3),
                np.round(df_cl['He_MJ/m2'].values[-1], 4),
                np.round(df_cl['Hv_Mlxh'].values[-1], 4),                   
            ]

            info_values = [
                " ",
                authors_names,
                host_institution,
                date_time,
                comment,
                " "] + project_info + [" "] + object_info + device_info + analysis_info + spot_info + beam_info + [" ", " "]

            df_info = pd.DataFrame({'parameter':info_parameters})
            df_info["value"] = pd.Series(info_values)            
            
        df_info = df_info.set_index('parameter')

        # define the output filename
        if filenaming == 'none':
            filename = stemName

        elif filenaming == 'auto':
            group = stemName.split('_')[2]
            group_description = stemName.split('_')[3]
            object_type = df_info.loc['object_type']['value']
            filename = f'{project_id}_{meas_id}_{group}_{group_description}_{object_type}_{date}'

        elif isinstance(filenaming, list):

            if 'date' in filenaming:
                new_df_info = df_info.copy()
                new_df_info.loc['date'] = str(df_info.loc['date_time']['value'].date())                    

                filename = "_".join([new_df_info.loc[x]['value'].split("_")[0] if "_" in new_df_info.loc[x]['value'] else new_df_info.loc[x]['value'] for x in filenaming])                    

            else:                                  
                filename = "_".join([df_info.loc[x]['value'].split("_")[0] if "_" in df_info.loc[x]['value'] else df_info.loc[x]['value'] for x in filenaming])
               
               
        # export the dataframes to an excel file
        if not Path(folder).exists():
            print(f'The output folder you entered {folder} does not exist. Please make sure the output folder has been created.')
            return 
            
        with pd.ExcelWriter(Path(folder) / f'{filename}.xlsx') as writer:

            df_info.to_excel(writer, sheet_name='info', index=True)
            df_cl.to_excel(writer, sheet_name="CIELAB", index=False)

            if interpolation == 'none':
                df_sp.to_excel(writer, sheet_name="spectra", index=True, index_label=f'wl-nm_t-sec')

            else:
                df_sp.to_excel(writer, sheet_name="spectra", index=True, index_label=f'wl-nm_{abs_scales_name[interpolation].replace("_", "-")}')

            
        ###### DELETE FILE #######        
            
        if delete_files:
            meas_raw_files = [file for file in Path(os.getcwd()).iterdir() if str(raw_file_counts).replace('-spect_convert.txt', '') in file.name]            
            [os.remove(file) for file in meas_raw_files]
            
        print(f'{raw_file_cl} has been successfully processed !')
            

        ###### DELETE FILE #######
        if return_filename:
            return Path(folder) / f'{filename}.xlsx'
            
            
