# -*- coding: utf-8 -*-
"""
Created on Sun Jul 24 20:06:14 2016

@author: Javier Palma-Espinosa
"""

'''
info extracted from 
http://stackoverflow.com/questions/12360999/pypdf-retrieve-page-numbers-from-document 
http://stackoverflow.com/questions/26494211/extracting-text-from-a-pdf-file-using-pdfminer-in-python
'''
import csv
import sys
import json
import googlemaps
reload(sys)
sys.setdefaultencoding("utf-8")

from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pyPdf import PdfFileReader



def convert(fname, pages=None):
'''
This function converts a pagre from a pdf file into a stream of text.
Thanks to the libraries imported.
'''
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = file(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue().split('\n')
    output.close
    return text 
    


def servelParser(rutaPdf):
    pdf = PdfFileReader(open(rutaPdf,'rb'))
    paginas = pdf.getNumPages() #will fetch all the pages from the PDF. It could take a LOT of time
    #paginas = 2
    
    #Define fields 
    nombres = range(paginas)
    rut = range(paginas)
    circunscripcion = range(paginas)
    comuna = range(paginas)
    direccion = range(paginas)
    provincia = range(paginas)
    Region = range(paginas)
    Mesa = range(paginas)
    pages = range(paginas)


    votantes = 0
    for i in range(paginas):
        pages[i]    = convert(rutaPdf,[i]) 
        
        indexNombre = pages[i].index('NOMBRE')
        indexRegion = pages[i].index('REGION')
        indexComuna = pages[i].index('COMUNA:')
        indexCI     = pages[i].index('C.IDENTIDAD SEXO')
        indexCirc   = pages[i].index('CIRCUNSCRIPCIÓN')
        indexDomEle = pages[i].index('DOMICILIO ELECTORAL')
        indexMesa   = pages[i].index('MESA')
        
        print "Procesando la hoja ", i
        print '\n'
        
        #Extract the data for each field in "pages" and sort in an structured way   
        if(indexCirc == indexDomEle-1): 
            nombres[i]           = pages[i][indexNombre+1:indexCI-1]
            rut[i]               = pages[i][indexCI+2:indexCI+2+len(nombres[i])]
            comuna[i]            = pages[i][indexComuna+2]
            circunscripcion[i]   = pages[i][indexCirc+1:indexCirc+1+2*len(nombres[1]):2]
            direccion[i]         = pages[i][indexDomEle+1:indexDomEle+1+2*len(nombres[i]):2]
            provincia[i]         = str(pages[i][indexRegion+4]).replace(":","").lstrip()
            Region[i]            = str(pages[i][indexRegion+3]).replace(":","").lstrip()
            Mesa[i]              = pages[i][indexMesa+1:len(pages[i])-1]
        else:
            nombres[i]           = pages[i][indexNombre+1:indexCI-1]
            rut[i]               = pages[i][indexCI+2:indexCI+2+len(nombres[i])]
            circunscripcion[i]   = pages[i][indexCirc+1:indexCirc+1+len(nombres[i])]
            comuna[i]            = pages[i][indexComuna+2]
            direccion[i]         = pages[i][indexDomEle+1:indexDomEle+1+len(nombres[i])]
            provincia[i]         = str(pages[i][indexRegion+4]).replace(":","").lstrip()
            Region[i]            = str(pages[i][indexRegion+3]).replace(":","").lstrip()
            Mesa[i]              = pages[i][indexMesa+1:len(pages[i])-1]
        
        votantes +=len(nombres[i])
        
    
    

    myKey = 'AIz...' #your google API key
    
    datosServel = [dict() for x in range(votantes)] #diccionario se mandará a MongoDB
    k=0
    for i in range(paginas): 
        for j in range(len(nombres[i])):
            rutSexo = rut[i][j].split(" ") 
            #GoogleMaps API query
            #Will search the address that appears in the Servel Record, for EACH person
            gmaps = googlemaps.Client(myKey)
            queryAddr = direccion[i][j] + ", "  + comuna[i] + ", " + Region[i] + ", Chile"
            # Geocoding an address
            geocode_result = gmaps.geocode(queryAddr)
            
            #datosServel will be a data structure, containing the information of each person.  Also, it
            #will record the lat and long of its address, in order to show it in googleMap
            print "Guardando datos número ",k+1
            datosServel[k] = {  'Nombre':str(nombres[i][j]),
                                'Rut':str(rutSexo[0].replace(".","")),
                                'Circunscripcion':circunscripcion[i][j],
                                'Mesa':Mesa[i][j],
                                'Sexo':rutSexo[1][0].replace("V", "H"),
                                'direccion':direccion[i][j],
                                'Comuna':comuna[i],
                                'Region':Region[i],
                                'Lat':geocode_result[0]["geometry"]["location"]["lat"],
                                'Lng':geocode_result[0]["geometry"]["location"]["lng"]}
            k+=1
                                
    return datosServel
    
