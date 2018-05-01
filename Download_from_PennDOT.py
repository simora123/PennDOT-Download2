print """
#--------------------------------------------------------------------------------------------#
# Name:        request3_scheduled_network2_2.py (Consume Feature Services Rest URLS)         #
#                                                                                            #
# Purpose:     Script updates downloads RMS and Bridge data from PennShare                   #
#                                                                                            #
# Authors:     Joseph Simora - York County Planning (YCPC)                                   #
#                                                                                            #
# Created:     June 2015                                                                     #
# Revised:     May 2018                                                                      #
# Copyright:   (c) York County Planning Commission                                           #
#--------------------------------------------------------------------------------------------#
"""
import arcpy
import arceditor
import os
import time
import datetime
import xlrd

def main():
    try:
        """Consume Feature Services Rest URLS"""
        arcpy.env.overwriteOutput = True

        # Mark starting time in order to calculate total processing time
        start = time.clock()
        dt_now = datetime.datetime.today()

        # Modify the following variables:
        # URL to your service, where clause, fields and token if applicable
        baseURL  = "http://www.pdarcgissvr.pa.gov/penndotgis/rest/services/PennShare/PennShare/MapServer/3/query"
        baseURL2 = "http://www.pdarcgissvr.pa.gov/penndotgis/rest/services/PennShare/PennShare/MapServer/0/query"
        baseURL3 = "http://www.pdarcgissvr.pa.gov/penndotgis/rest/services/PennShare/PennShare/MapServer/1/query"
        baseURL4 = "http://www.pdarcgissvr.pa.gov/penndotgis/rest/services/PennShare/PennShare/MapServer/7/query"

        # Where clauses. Change the Cnty Code to your County Number. York County is 66. If you want to download multiple counties, you can use the syntax
        # I used in the where 2 variable
        where = 'CTY_CODE = 66'
        where2 = 'CTY_CODE = 66 OR CTY_CODE = 01 OR CTY_CODE = 21'
        # field variable selects the number or individual fields you want to add. If you want all records, the "*" will do this for you
        fields = '*'
        # token if website token requires a token
        token = ''

        #The above variables construct the query
        query = "?where={}&outFields={}&returnGeometry=true&f=json&token={}".format(where, fields, token)
        query2 = "?where={}&outFields={}&returnGeometry=true&f=json&token={}".format(where2, fields, token)

        # See http://services1.arcgis.com/help/index.html?fsQuery.html for more info on FS-Query
        fsURL  = baseURL  + query2
        fsURL2 = baseURL2 + query
        fsURL3 = baseURL3 + query2
        fsURL4 = baseURL4 + query2

        # Directory variables:
        PennDOT_Copy_GDB = r'' # Insert GDB Path here Example: r"\\YCPCFS\GIS_Projects\Transportation\Archives\Temp\PennDot_MapService_Load.gdb"

        message ("Starting PennDOT Update Script")
        message ("Loading RMS and Bridge Data from PennDOT")
        fs = arcpy.FeatureSet()
        fs.load(fsURL)
        arcpy.CopyFeatures_management(fs, os.path.join(PennDOT_Copy_GDB,"RMSADMIN"))
        message ("PennDOT RMSADMIN Map Service has been copied to the following location: {}".format(os.path.join(PennDOT_Copy_GDB,"RMSADMIN")))

        fs.load(fsURL2)
        arcpy.CopyFeatures_management(fs, os.path.join(PennDOT_Copy_GDB,"RMSSEG"))
        message ("PennDOT RMSSEG Map Service has been copied to the following location: {}".format(os.path.join(PennDOT_Copy_GDB,"RMSSEG")))

        fs.load(fsURL3)
        arcpy.CopyFeatures_management(fs, os.path.join(PennDOT_Copy_GDB,"RMSTRAFFIC"))
        message ("PennDOT RMSTRAFFIC Map Service has been copied to the following location: {}".format(os.path.join(PennDOT_Copy_GDB,"RMSTRAFFIC")))

        fs.load(fsURL4)
        arcpy.CopyFeatures_management(fs, os.path.join(PennDOT_Copy_GDB,"State_And_Local_Bridges"))
        message ("PennDOT State_And_Local_Bridges Map Service has been copied to the following location: {}".format(os.path.join(PennDOT_Copy_GDB,"State_And_Local_Bridges")))

    # end Try statement
    except EnvironmentError as e:
        ErrorMessageEnvironment(e)
    except Exception as e:
        ErrorMessageException(e)

    finally:
        message ("PennDOT Download Script is Completed")
        message ("Grand Total Processing Time: " + str(round((time.clock() - start) / 60, 2)) + " minutes")

def message(message):
    time_stamp = time.strftime("%b %d %Y %H:%M:%S")
    print(time_stamp + "  " + message + "\t")
    #arcpy.AddMessage(time_stamp + "  " + message)

def ErrorMessageEnvironment(e):
    tb = sys.exc_info()[2]
    message("\nFailed at Line %i \n" % tb.tb_lineno)
    message('Error: {0}\n'.format(str(e)))

def ErrorMessageException(e):
    tb = sys.exc_info()[2]
    message("\nFailed at Line %i \n" % tb.tb_lineno)
    message('Error: {0} \n'.format(e.message))

if __name__ == "__main__":
	main()