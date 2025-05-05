#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 17:04:19 2023

@author: javiera.quiroz
"""


import pandas as pd
import fnmatch
import requests
from ftplib import FTP
import re
import os
from dotenv import load_dotenv
from ..utilities.downloads import RTD

from .download_tsv import Download_tsv
from .download_json import Download_json
from .download_obo import Download_obo
from .download_fb import Download_fb
from .download_fasta import Download_fasta



class Downloads(Download_tsv, Download_json,
                Download_obo, Download_fb,
                Download_fasta):
    
    def __init__(self, url, internet):
        
        if re.search("fasta", url):
            self.url = url
        else:
            MAIN_URL = os.getenv("MAIN_URL")
            self.url = MAIN_URL + url
            
        self.rtd = RTD()
        if self.rtd.user_id == '00':
            self.internet = False
        else:
           self.internet = internet 
           
    def save_file(self, file):
        if self.internet:
            self.rtd.save_reg(file)
        
    def download_file(self):
        url = self.url
        file = url.split('/')[-1]
        file = file.split('*')[0]

        archivos_encontrados = os.listdir("../")
        for archivo in archivos_encontrados:
            if archivo.startswith(file):
                archivo_path = os.path.join("..", archivo)
                return archivo_path

        if self.internet:
            try:
                response = requests.get(url, stream=True, timeout=10)
                if response.status_code == 200:
                    file_path = os.path.join("..", file)
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    self.save_file(file)  # Si tu clase tiene esta función definida
                    return file_path
                else:
                    print(f"Error {response.status_code}: No se pudo descargar el archivo.")
                    return None
            except Exception as e:
                print(f"Error al descargar: {e}")
                return None

        else:
            print('The file is not in your environment')
            return None   
    
    def get(self, header = None):
        
        file = None
        
        try:
            file = self.download_file()
        except:
            print("Error downloading the file")
        patron = r"##?\s?\w+"
        
        def df_r(df):
            if re.search(r"FB\w{9}", df.columns[0]): 
                df_columns = pd.DataFrame(df.columns).T

                df.columns = range(len(df.columns))
                
               
                df = pd.concat([df_columns, df], ignore_index=True, axis = 0)
            
            if re.search(patron, df.iloc[-1,0]):
                df = df.iloc[:-1, :]
            
            return df
        
        
        try:
            if file is not None:
                if re.search('.obo', self.url):
                    return Download_obo.open_obo(self,file)
                elif re.search('.json', self.url):
                    try:
                        return df_r(Download_json.open_file_json(self, file))
                        
                    except:
                        try:
                            df = Download_json.open_file_json(self, file)
                            df = pd.concat([df.drop(['driver'], axis=1), df['driver'].apply(pd.Series)], axis=1)
    
                            df = df.replace({None: pd.NA})
                            return df_r(df)
                        except:
                            return Download_json.open_file_json(self,file)
                        
                elif re.search('.fasta', self.url):
                    return Download_fasta.open_fasta(self, file)
                else:
                    return df_r(Download_tsv.open_file_tsv(self, file, header))
            return file
        except:
            print("Error reading the file")
    
