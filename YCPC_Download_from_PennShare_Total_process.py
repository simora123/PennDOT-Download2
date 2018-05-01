print """
#--------------------------------------------------------------------------------------------#
# Name:        request3_scheduled_network2_2.py (Consume Feature Services Rest URLS)         #
#                                                                                            #
# Purpose:     Script updates RMS and Bridge data in York Edits Database and also on         #
#              the \\YCPCFS\gisdata\Transportation Directory (N Drive). Scripts comsume      #
#              feature services from PennDOT and then proceesses the information so our      #
#              Transportation Division here has access to to the most up-to-date inforamtion #
#              from PennDOT. Final steps of this script will delete old information from RMS #
#              and Bridge Layer in the York Edit Database and append updated information.    #
#              We currently have this script scheduled on a weekly basis.                    #
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

        where = 'CTY_CODE = 66'
        where2 = 'CTY_CODE = 66 OR CTY_CODE = 01 OR CTY_CODE = 21'
        fields = '*'
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
        db_conn_path                               = r"\\YCPCFS\GIS_Projects\IS\GIS_Connections\GIS@York.sde\York.GIS"
        York_Edit_SDE                              = r"\\YCPCFS\GIS_Projects\IS\GIS_Connections\GIS_York_Edit.sde"
        transp_path_1                              = r"\\YCPCFS\GIS_Projects\Transportation"
        transp_arch_path                           = transp_path_1 + r"\Archives"
        Updated_Folder                             = r"\\Ycpcfs\wp-doc\GIS\York_County_GIS_coordination\implementation_plan\EnterprisePlan_Phase_II\Enterprise_Implementation\Enterprise_GDB_Physical_Design\DATA_LOAD_MODELS\RMS_Bridge\Enterprise_Load.gdb"

        # GDB/File Geodatabase variables:
        transp_arch_temp                           = transp_arch_path + r"\Temp\TempDb_PennDOT_Load.gdb"
        PennDOT_Copy_GDB                           = r"\\YCPCFS\GIS_Projects\Transportation\Archives\Temp\PennDot_MapService_Load.gdb"
        tran_agol_padot_pygdb                      = r"\\YCPCFS\GIS_Projects\Transportation\Archives\Temp\PennDot_MapService_Load.gdb"
        transp_arch_BMS_LOCAL                      = transp_arch_path + r"\BMS_Local.gdb"
        transp_arch_BMS_STATE                      = transp_arch_path + r"\BMS_State.gdb"
        transp_arch_RMS_ADMIN                      = transp_arch_path + r"\RMS_ADMIN.gdb"
        transp_arch_RMS_SEG                        = transp_arch_path + r"\RMS_SEG.gdb"
        transp_arch_RMS_TRAFFIC                    = transp_arch_path + r"\RMS_TRAFFIC.gdb"

        # DB_conn_path Feature Class Variables:
        County_Boundary                            = db_conn_path + ".DIST_County_Boundary"
        York_GIS_DIST_County_Boundary              = db_conn_path+".DIST_County_Boundary"
        York_GIS_TRANSP_Counts                     = db_conn_path+".TRANSP_Counts"

        # Variables used to update the Excel and DBF steps
        Bridge_YCPC_Group_dbf                      = transp_arch_path + r"\Temp\Bridge_YCPC_Group.dbf"
        Excel_name                                 = transp_arch_path + "\Temp\Bridge_YCPC_Group.xls"

        # Variables used to create Archive Feature Classes in O:IS\TRANSPORTATION\ARCHIVES Folder
        YEAR_MONTH_DAY_RMSTRAFFIC_shp              = transp_arch_RMS_TRAFFIC + r"\RMSTRAFFIC_YEAR_MONTH_DAY"
        YEAR_MONTH_DAY_RMSADMIN_shp                = transp_arch_RMS_ADMIN + r"\RMSADMIN_YEAR_MONTH_DAY"
        YEAR_MONTH_DAY_RMSSEG_shp                  = transp_arch_RMS_SEG + r"\RMSSEG_YEAR_MONTH_DAY"
        YEAR_MONTH_DAY_Bridges_BMS_STATE_shp       = transp_arch_BMS_STATE + r"\Bridges_BMS_STATE_YEAR_MONTH_DAY"
        YEAR_MONTH_DAY_Bridges_BMS_Local_shp       = transp_arch_BMS_LOCAL + r"\Bridges_BMS_LOCAL_YEAR_MONTH_DAY"
        #YEAR_MONTH_DAY_Bridges_BMS_State_Dssvl_shp = transp_arch_BMS_STATE + r"\YEAR_MONTH_DAY_Bridges_BMS_State_Dssvl"

        # Variables used to create Archive Feature Classes in O:\Transportation\Archives\Temp\PennDot_MapService_Load.gdb
        State_And_Local_Bridges                    = tran_agol_padot_pygdb + r"\State_And_Local_Bridges"
        RMSSEG                                     = tran_agol_padot_pygdb + r"\RMSSEG"
        RMSADMIN                                   = tran_agol_padot_pygdb + r"\RMSADMIN"
        RMSTRAFFIC                                 = tran_agol_padot_pygdb + r"\RMSTRAFFIC"
        RMSSEG_Project                             = tran_agol_padot_pygdb + r"\RMSSEG_Project"
        XRMSADMIN_Project_shp                      = tran_agol_padot_pygdb + r"\RMSADMIN_Project3"
        XRMSTRAFFIC_Project_shp                    = tran_agol_padot_pygdb + r"\RMSTRAFFIC_Project3"
        State_Bridges_Project                      = tran_agol_padot_pygdb + r"\State_Bridges_Project"
        Local_Bridges_Project                      = tran_agol_padot_pygdb + r"\Local_Bridges_Project"

        # Variables used to create Archive Feature Classes in O:\Transportation\Archives\Temp\TempDb_PennDOT_Load.gdb
        RMSADMIN_shp                               = transp_arch_temp + r"\RMSADMIN"
        RMSSEG_shp                                 = transp_arch_temp + r"\RMSSEG"
        RMSTRAFFIC_shp                             = transp_arch_temp + r"\RMSTRAFFIC"
        Bridges_BMS_State_shp                      = transp_arch_temp + r"\Bridges_BMS_State"
        Bridges_BMS_Local_shp                      = transp_arch_temp + r"\Bridges_BMS_Local"
        Bridges_BMS_State_Temp_shp                 = transp_arch_temp + r"\Bridges_BMS_State_Temp"
        Bridges_BMS_Local_Temp_shp                 = transp_arch_temp + r"\Bridges_BMS_Local_Temp"
        Bridges_BMS_Local_no_join_shp              = transp_arch_temp + r"\Bridges_BMS_Local_no_join"
        YEAR_MONTH_DAY_Bridges_BMS_State_Dssvl_shp = transp_arch_temp + r"\YEAR_MONTH_DAY_Bridges_BMS_State_Dssvl"
        State_Bridges_shp                          = transp_arch_temp + r"\State_Bridges"
        Local_Bridges_shp                          = transp_arch_temp + r"\Local_Bridges"
        Trans_Count_Select_shp                     = transp_arch_temp + r"\Trans_Count_Select"
        Trans_Count_Final_shp                      = transp_arch_temp + r"\Trans_Count_Final"
        Trans_Count_Dsslv1_shp                     = transp_arch_temp + r"\Trans_Count_Dsslv1"
        RMSSEG_temp_shp                            = transp_arch_temp + r"\RMSSEG_temp"
        NHS_Interstate_shp                         = transp_arch_temp + r"\NHS_Interstate"
        NHS_Interstate_Exc_shp                     = transp_arch_temp + r"\NHS_Interstate_Exc"
        NHS_NonInter_shp                           = transp_arch_temp + r"\NHS_NonInter"
        NonNHSGreater2000_shp                      = transp_arch_temp + r"\NonNHSGreater2000"
        NonNHSLess2000_shp                         = transp_arch_temp + r"\NonNHSLess2000"
        No_Data_shp                                = transp_arch_temp + r"\No_Data"
        NHS_Interstate_Good_shp                    = transp_arch_temp + r"\NHS_Interstate_Good"
        NHS_Interstate_Fair_shp                    = transp_arch_temp + r"\NHS_Interstate_Fair"
        NHS_Interstate_Poor_shp                    = transp_arch_temp + r"\NHS_Interstate_Poor"
        NHS_Interstate_Merge_shp                   = transp_arch_temp + r"\NHS_Interstate_Merge"
        NHS_NonInter_Exc_shp                       = transp_arch_temp + r"\NHS_NonInter_Exc"
        NHS_NonInter_Good_shp                      = transp_arch_temp + r"\NHS_NonInter_Good"
        NHS_NonInter_Fair_shp                      = transp_arch_temp + r"\NHS_NonInter_Fair"
        NHS_NonInter_Poor_shp                      = transp_arch_temp + r"\NHS_NonInter_Poor"
        NHS_NonInter_Merge_shp                     = transp_arch_temp + r"\NHS_NonInter_Merge"
        NonNHSGreater2000_Exc_shp                  = transp_arch_temp + r"\NonNHSGreater2000_Exc"
        NonNHSGreater2000_Good_shp                 = transp_arch_temp + r"\NonNHSGreater2000_Good"
        NonNHSGreater2000_Fair_shp                 = transp_arch_temp + r"\NonNHSGreater2000_Fair"
        NonNHSGreater2000_Poor_shp                 = transp_arch_temp + r"\NonNHSGreater2000_Poor"
        NonNHSGreater2000_Merge_shp                = transp_arch_temp + r"\NonNHSGreater2000_Merge"
        NonNHSLesser2000_Exc_shp                   = transp_arch_temp + r"\NonNHSLesser2000_Exc"
        NonNHSLesser2000_Good_shp                  = transp_arch_temp + r"\NonNHSLesser2000_Good"
        NonNHSLesser2000_Fair_shp                  = transp_arch_temp + r"\NonNHSLesser2000_Fair"
        NonNHSLesser2000_Poor_shp                  = transp_arch_temp + r"\NonNHSLesser2000_Poor"
        NonNHSLesser2000_Merge_shp                 = transp_arch_temp + r"\NonNHSLesser2000_Merge"
        State_Bridges_Project_Select_shp           = transp_arch_temp + r"\State_Bridges_Project_Select"
        temp_bridge_local_layer_shp                = transp_arch_temp + r"\temp_bridge_local_layer"

        # Layer files used in this script
        Bridges_BMS_Local_TEST_Layer               = "YEAR_MONTH_DAY_Bridges_BMS_L1"
        Bridges_BMS_Local_TEST_Layer2              = "YEAR_MONTH_DAY_Bridges_BMS_L"
        Bridges_BMS_STATE_NOV_2013_L__3_           = "YEAR_MONTH_DAY_Bridges_BMS_S"
        RMSADMIN_Layer                             = "RMSADMIN_Layer"
        RMSSEG_Layer                               = "RMSSEG_Layer"
        RMSTRAFFIC_Layer                           = "RMSTRAFFIC_Layer"
        Trans_Count_Dsslv_Layer                    = "Trans_Count_Dsslv1_Layer"
        Trans_Count_Final_Layer                    = "Trans_Count_Final_Layer"
        Trans_Count_Select_Layer                   = "Trans_Count_Select_Layer"
        YEAR_MONTH_DAY_Bridges_BMS_S               = "YEAR_MONTH_DAY_Bridges_BMS_S"
        YRMSSEG_Layer                              = "RMSSEG_Layer"
        v0_Layer                                   = "State_And_Local_Bridges_Layer1"
        v0_Layer1                                  = "State_And_Local_Bridges_Layer"
        v0_Layer2                                  = "State_And_Local_Bridges_Layer1"
        # Not sure if v0_Layer and v0_Layer2 are identicial

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

        # file_name = transp_arch_path + "\Temp\Bridge_YCPC_Group.xls"
        # file_name = r"N:\Transportation\archive\Bridge_and_YCPC_group.xls"

        # Sets exact time script is run
        now = datetime.datetime.now()
        # Subtracts the "now" variable by time set (days, hours, minutes, seconds)
        ago = now - datetime.timedelta(hours=168)

        # Variables used in below if statement to determine if Excel Spreadsheet was updated within particular timeframe dicated in "ago" variable
        path = Excel_name
        st = os.stat(path)
        mtime = datetime.datetime.fromtimestamp(st.st_mtime)

        # If statement. If Excel spreadsheet has been updated in the alloted  timeframe, update the Bridge_YCPC_Group.dbf
        if mtime > ago:
            message ("{} needs updated".format(Excel_name.split("\\")[-1]))
            message ("Starting Converting Excel XLS file to DBF")
            importallsheets(path, transp_arch_temp)

            # Set environment settings
            arcpy.env.workspace = transp_arch_temp

            # Set local variables
            inTables = ["Bridge_and_YCPC_group_xls_BRIDGE_KEY_JOIN"]
            outLocation = transp_arch_path + "\Temp"

            message ("Converting Table to DBF")
            # Execute TableToDBASE
            arcpy.TableToDBASE_conversion(inTables, outLocation)

            message ("Delete Old Bridge_YCPC_Group.dbf File")
            arcpy.Delete_management(transp_arch_path + "\Temp\Bridge_YCPC_Group.dbf")

            message ("Rename New DBF to Bridge_YCPC_Group.dbf")
            arcpy.Rename_management(transp_arch_path + "\Temp\Bridge_and_YCPC_group_xls_BRIDGE_KEY_JOIN.dbf", transp_arch_path + "\Temp\Bridge_YCPC_Group.dbf")

            arcpy.Delete_management(transp_arch_path + "\Temp\Bridge_and_YCPC_group_xls_BRIDGE_KEY_JOIN_1.dbf")

            message ("Finished Converting Excel XLS file to DBF")

        # Else. If Excel spreadsheet has "not" been updated in the alloted timeframe, ignore updating Bridge_YCPC_Group.dbf
        elif mtime < ago:
            message ("{} doesn't need updated".format(Excel_name.split("\\")[-1]))

        message ("Starting to Kickoff Old Model Builder Steps")

        ### Tried the below process (Run Model) but did not work. Should have worked but think there is but limitations with the license I am using ####
        #arcpy.ImportToolbox(r"\\ycpcfs\GIS_projects\IS\Model\Transportation\PenndotTOOLS.tbx")
        #arcpy.Model223_PennDOT()
        #print "Completed Model"
        ######################################################################################################################################################################################################################################
        #Below is the export of Model223_PennDOT illustrated below. Discovered that Model doesn't work correctly in a server environment. Also, steps in model that require arcinfo license. Server currently only has arceditor license.

        message ("Starting Local Bridge Steps")
        # Process: Copy Features (2)
        arcpy.CopyFeatures_management(Bridges_BMS_Local_no_join_shp, temp_bridge_local_layer_shp, "", "0", "0", "0")

        # Process: Make Feature Layer (4)
        arcpy.MakeFeatureLayer_management(State_And_Local_Bridges, v0_Layer1, "", "", "OBJECTID OBJECTID VISIBLE NONE;\
        Shape Shape VISIBLE NONE;\
        CTY_CODE CTY_CODE VISIBLE NONE;\
        ST_RT_NO ST_RT_NO VISIBLE NONE;\
        SEG_NO SEG_NO VISIBLE NONE;\
        OFFSET OFFSET VISIBLE NONE;\
        ADMIN_JURIS ADMIN_JURIS VISIBLE NONE;\
        DEC_LAT DEC_LAT VISIBLE NONE;\
        DEC_LONG DEC_LONG VISIBLE NONE;\
        BRIDGE_ID BRIDGE_ID VISIBLE NONE;\
        FEATINT FEATINT VISIBLE NONE;\
        DISTRICT DISTRICT VISIBLE NONE;\
        FACILITY FACILITY VISIBLE NONE;\
        LOCATION LOCATION VISIBLE NONE;\
        OWNER OWNER VISIBLE NONE;\
        YEARBUILT YEARBUILT VISIBLE NONE;\
        YEARRECON YEARRECON VISIBLE NONE;\
        SERVTYPON SERVTYPON VISIBLE NONE;\
        SERVTYPUND SERVTYPUND VISIBLE NONE;\
        MAINSPANS MAINSPANS VISIBLE NONE;\
        APPSPANS APPSPANS VISIBLE NONE;\
        LENGTH LENGTH VISIBLE NONE;\
        DECKWIDTH DECKWIDTH VISIBLE NONE;\
        DKSURFTYPE DKSURFTYPE VISIBLE NONE;\
        DKMEMBTYPE DKMEMBTYPE VISIBLE NONE;\
        DKPROTECT DKPROTECT VISIBLE NONE;\
        MAIN_WS_THICKNESS MAIN_WS_THICKNESS VISIBLE NONE;\
        APPR_DKSURFTYPE APPR_DKSURFTYPE VISIBLE NONE;\
        APPR_DKMEMBTYPE APPR_DKMEMBTYPE VISIBLE NONE;\
        APPR_DKPROTECT APPR_DKPROTECT VISIBLE NONE;\
        APPR_WS_THICKNESS APPR_WS_THICKNESS VISIBLE NONE;\
        FED_FUND FED_FUND VISIBLE NONE;\
        DECK_RECON_WORK_TYPE DECK_RECON_WORK_TYPE VISIBLE NONE;\
        SUP_RECON_WORK_TYPE SUP_RECON_WORK_TYPE VISIBLE NONE;\
        SUB_RECON_WORK_TYPE SUB_RECON_WORK_TYPE VISIBLE NONE;\
        DEPT_MAIN_MATERIAL_TYPE DEPT_MAIN_MATERIAL_TYPE VISIBLE NONE;\
        DEPT_MAIN_PHYSICAL_TYPE DEPT_MAIN_PHYSICAL_TYPE VISIBLE NONE;\
        DEPT_MAIN_SPAN_INTERACTION DEPT_MAIN_SPAN_INTERACTION VISIBLE NONE;\
        DEPT_MAIN_STRUC_CONFIG DEPT_MAIN_STRUC_CONFIG VISIBLE NONE;\
        DEPT_APPR_MATERIAL_TYPE DEPT_APPR_MATERIAL_TYPE VISIBLE NONE;\
        DEPT_APPR_PHYSICAL_TYPE DEPT_APPR_PHYSICAL_TYPE VISIBLE NONE;\
        DEPT_APPR_SPAN_INTERACTION DEPT_APPR_SPAN_INTERACTION VISIBLE NONE;\
        DEPT_APPR_STRUC_CONFIG DEPT_APPR_STRUC_CONFIG VISIBLE NONE;\
        SUB_AGENCY SUB_AGENCY VISIBLE NONE;\
        MAINT_RESP_DESC MAINT_RESP_DESC VISIBLE NONE;\
        CRIT_FACILITY CRIT_FACILITY VISIBLE NONE;\
        APPR_PAVEMENT_WIDTH APPR_PAVEMENT_WIDTH VISIBLE NONE;\
        COVERED_BRIDGE COVERED_BRIDGE VISIBLE NONE;\
        FLOOD_INSP FLOOD_INSP VISIBLE NONE;\
        DEPT_DKSTRUCTYP DEPT_DKSTRUCTYP VISIBLE NONE;\
        BYPASSLEN BYPASSLEN VISIBLE NONE;\
        AROADWIDTH AROADWIDTH VISIBLE NONE;\
        ROADWIDTH ROADWIDTH VISIBLE NONE;\
        MIN_OVER_VERT_CLEAR_RIGHT MIN_OVER_VERT_CLEAR_RIGHT VISIBLE NONE;\
        MIN_OVER_VERT_CLEAR_LEFT MIN_OVER_VERT_CLEAR_LEFT VISIBLE NONE;\
        POST_LIMIT_WEIGHT POST_LIMIT_WEIGHT VISIBLE NONE;\
        POST_LIMIT_COMB POST_LIMIT_COMB VISIBLE NONE;\
        INSPDATE INSPDATE VISIBLE NONE;\
        BRINSPFREQ BRINSPFREQ VISIBLE NONE;\
        POST_STATUS POST_STATUS VISIBLE NONE;\
        NBI_RATING NBI_RATING VISIBLE NONE;\
        SUFF_RATE SUFF_RATE VISIBLE NONE;\
        MAINT_DEF_RATE MAINT_DEF_RATE VISIBLE NONE;\
        HBRR_ELIG HBRR_ELIG VISIBLE NONE;\
        JURIS JURIS VISIBLE NONE;\
        SEG_END SEG_END VISIBLE NONE;\
        OFFSET_END OFFSET_END VISIBLE NONE;\
        SEG_PT_BGN SEG_PT_BGN VISIBLE NONE;\
        SEG_PT_END SEG_PT_END VISIBLE NONE;\
        SIDE_IND SIDE_IND VISIBLE NONE;\
        NLF_ID NLF_ID VISIBLE NONE;\
        NLF_CNTL_BGN NLF_CNTL_BGN VISIBLE NONE;\
        NLF_CNTL_END NLF_CNTL_END VISIBLE NONE;\
        CUM_OFFSET_BGN CUM_OFFSET_BGN VISIBLE NONE;\
        CUM_OFFSET_END CUM_OFFSET_END VISIBLE NONE;\
        DKRATING DKRATING VISIBLE NONE;\
        SUPRATING SUPRATING VISIBLE NONE;\
        SUBRATING SUBRATING VISIBLE NONE;\
        CULVRATING CULVRATING VISIBLE NONE;\
        STATE_LOCAL STATE_LOCAL VISIBLE NONE;\
        DECK_AREA DECK_AREA VISIBLE NONE;\
        BB_BRDGEID BB_BRDGEID VISIBLE NONE;\
        BB_PCT BB_PCT VISIBLE NONE;\
        BRIDGEMED BRIDGEMED VISIBLE NONE;\
        CUSTODIAN CUSTODIAN VISIBLE NONE;\
        DESIGNAPPR DESIGNAPPR VISIBLE NONE;\
        DESIGNMAIN DESIGNMAIN VISIBLE NONE;\
        DKSTRUCTYP DKSTRUCTYP VISIBLE NONE;\
        FIPS_STATE FIPS_STATE VISIBLE NONE;\
        HCLRULT HCLRULT VISIBLE NONE;\
        HCLRURT HCLRURT VISIBLE NONE;\
        HISTSIGN HISTSIGN VISIBLE NONE;\
        IMPLEN IMPLEN VISIBLE NONE;\
        LFTBRNAVCL LFTBRNAVCL VISIBLE NONE;\
        LFTCURBSW LFTCURBSW VISIBLE NONE;\
        MATERIALAPPR MATERIALAPPR VISIBLE NONE;\
        MATERIALMAIN MATERIALMAIN VISIBLE NONE;\
        MAXSPAN MAXSPAN VISIBLE NONE;\
        NAVCNTROL NAVCNTROL VISIBLE NONE;\
        NAVHC NAVHC VISIBLE NONE;\
        NAVVC NAVVC VISIBLE NONE;\
        NBIIMPCOST NBIIMPCOST VISIBLE NONE;\
        NBIRWCOST NBIRWCOST VISIBLE NONE;\
        NBISLEN NBISLEN VISIBLE NONE;\
        NBITOTCOST NBITOTCOST VISIBLE NONE;\
        NBIYRCOST NBIYRCOST VISIBLE NONE;\
        NSTATECODE NSTATECODE VISIBLE NONE;\
        PARALSTRUC PARALSTRUC VISIBLE NONE;\
        PLACECODE PLACECODE VISIBLE NONE;\
        PROPWORK PROPWORK VISIBLE NONE;\
        REFHUC REFHUC VISIBLE NONE;\
        REFVUC REFVUC VISIBLE NONE;\
        RTCURBSW RTCURBSW VISIBLE NONE;\
        SKEW SKEW VISIBLE NONE;\
        STRFLARED STRFLARED VISIBLE NONE;\
        STRUCT_NUM STRUCT_NUM VISIBLE NONE;\
        SUMLANES SUMLANES VISIBLE NONE;\
        TEMPSTRUC TEMPSTRUC VISIBLE NONE;\
        VCLROVER VCLROVER VISIBLE NONE;\
        ADTFUTURE ADTFUTURE VISIBLE NONE;\
        ADTFUTYEAR ADTFUTYEAR VISIBLE NONE;\
        ADTTOTAL ADTTOTAL VISIBLE NONE;\
        ADTYEAR ADTYEAR VISIBLE NONE;\
        DEFHWY DEFHWY VISIBLE NONE;\
        DIRSUFFIX DIRSUFFIX VISIBLE NONE;\
        FUNCCLASS FUNCCLASS VISIBLE NONE;\
        HCLRINV HCLRINV VISIBLE NONE;\
        KIND_HWY KIND_HWY VISIBLE NONE;\
        KMPOST KMPOST VISIBLE NONE;\
        LANES LANES VISIBLE NONE;\
        LEVL_SRVC LEVL_SRVC VISIBLE NONE;\
        NHS_IND NHS_IND VISIBLE NONE;\
        ON_UNDER ON_UNDER VISIBLE NONE;\
        TOLLFAC TOLLFAC VISIBLE NONE;\
        TRAFFICDIR TRAFFICDIR VISIBLE NONE;\
        TRUCKPCT TRUCKPCT VISIBLE NONE;\
        AENDRATING AENDRATING VISIBLE NONE;\
        APPRALIGN APPRALIGN VISIBLE NONE;\
        ARAILRATIN ARAILRATIN VISIBLE NONE;\
        CHANRATING CHANRATING VISIBLE NONE;\
        DECKGEOM DECKGEOM VISIBLE NONE;\
        NEXTINSP NEXTINSP VISIBLE NONE;\
        PIERPROT PIERPROT VISIBLE NONE;\
        RAILRATING RAILRATING VISIBLE NONE;\
        SCOURCRIT SCOURCRIT VISIBLE NONE;\
        STRRATING STRRATING VISIBLE NONE;\
        TRANSRATIN TRANSRATIN VISIBLE NONE;\
        UNDERCLR UNDERCLR VISIBLE NONE;\
        WATERADEQ WATERADEQ VISIBLE NONE;\
        BUS_PLAN_NETWORK BUS_PLAN_NETWORK VISIBLE NONE;\
        ROW_MODIFIED ROW_MODIFIED VISIBLE NONE;\
        ORIG_FID ORIG_FID VISIBLE NONE;\
        BRKEY BRKEY VISIBLE NONE")

        # Process: Select Layer By Attribute (5)
        arcpy.SelectLayerByAttribute_management(v0_Layer1, "NEW_SELECTION", "\"CTY_CODE\" = '66' OR \"CTY_CODE\" = '01' OR \"CTY_CODE\" = '21' OR \"CTY_CODE\" = '22' OR \"CTY_CODE\" = '36'")

        # Process: Select Layer By Attribute (3)
        arcpy.SelectLayerByAttribute_management(v0_Layer1, "REMOVE_FROM_SELECTION", "STATE_LOCAL = 'S'")

        # Process: Select (24)
        arcpy.Select_analysis(v0_Layer1, Local_Bridges_shp, "")

        # Process: Project
        arcpy.Project_management(Local_Bridges_shp, Local_Bridges_Project, "PROJCS['NAD_1983_StatePlane_Pennsylvania_South_FIPS_3702_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',1968500.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-77.75],PARAMETER['Standard_Parallel_1',39.93333333333333],PARAMETER['Standard_Parallel_2',40.96666666666667],PARAMETER['Latitude_Of_Origin',39.33333333333334],UNIT['Foot_US',0.3048006096012192]]", "", "PROJCS['Pennsylvania Polyconic',GEOGCS['NAD 83',DATUM['NAD 83',SPHEROID['GRS 80',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Polyconic'],PARAMETER['Central_Meridian',-77.75],PARAMETER['Latitude_Of_Origin',40.925],UNIT['Meter',1.0]]")

        # Process: Join Field (6)
        arcpy.JoinField_management(temp_bridge_local_layer_shp, "BRKEY", Local_Bridges_Project, "STRUCT_NUM",\
        "CTY_CODE;\
        ST_RT_NO;\
        SEG_NO;\
        OFFSET;\
        ADMIN_JURIS;\
        DEC_LAT;\
        DEC_LONG;\
        BRIDGE_ID;\
        FEATINT;\
        DISTRICT;\
        FACILITY;\
        LOCATION;\
        OWNER;\
        YEARBUILT;\
        YEARRECON;\
        SERVTYPON;\
        SERVTYPUND;\
        MAINSPANS;\
        APPSPANS;\
        LENGTH;\
        DECKWIDTH;\
        DKSURFTYPE;\
        DKMEMBTYPE;\
        DKPROTECT;\
        MAIN_WS_THICKNESS;\
        APPR_DKSURFTYPE;\
        APPR_DKMEMBTYPE;\
        APPR_DKPROTECT;\
        APPR_WS_THICKNESS;\
        FED_FUND;\
        DECK_RECON_WORK_TYPE;\
        SUP_RECON_WORK_TYPE;\
        DEPT_MAIN_MATERIAL_TYPE;\
        DEPT_MAIN_PHYSICAL_TYPE;\
        DEPT_MAIN_SPAN_INTERACTION;\
        DEPT_MAIN_STRUC_CONFIG;\
        DEPT_APPR_MATERIAL_TYPE;\
        DEPT_APPR_PHYSICAL_TYPE;\
        DEPT_APPR_SPAN_INTERACTION;\
        DEPT_APPR_STRUC_CONFIG;\
        SUB_AGENCY;\
        MAINT_RESP_DESC;\
        CRIT_FACILITY;\
        APPR_PAVEMENT_WIDTH;\
        COVERED_BRIDGE;\
        FLOOD_INSP;\
        DEPT_DKSTRUCTYP;\
        BYPASSLEN;\
        AROADWIDTH;\
        ROADWIDTH;\
        MIN_OVER_VERT_CLEAR_RIGHT;\
        MIN_OVER_VERT_CLEAR_LEFT;\
        POST_LIMIT_WEIGHT;\
        POST_LIMIT_COMB;\
        INSPDATE;\
        BRINSPFREQ;\
        POST_STATU;\
        NBI_RATING;\
        SUFF_RATE;\
        MAINT_DEF_RATE;\
        HBRR_ELIG;\
        JURIS;\
        SEG_END;\
        OFFSET_END;\
        SEG_PT_BGN;\
        SEG_PT_END;\
        SIDE_IND;\
        NLF_ID;\
        NLF_CNTL_BGN;\
        NLF_CNTL_END;\
        CUM_OFFSET_BGN;\
        CUM_OFFSET_END;\
        DKRATING;\
        SUPRATING;\
        SUBRATING;\
        CULVRATING;\
        STATE_LOCA;\
        DECK_AREA;\
        BB_BRDGEID;\
        BB_PCT;\
        BRIDGEMED;\
        CUSTODIAN;\
        DESIGNAPPR;\
        DESIGNMAIN;\
        DKSTRUCTYP;\
        FIPS_STATE;\
        HCLRULT;\
        HCLRURT;\
        HISTSIGN;\
        IMPLEN;\
        LFTBRNAVCL;\
        LFTCURBSW;\
        MATERIALAPPR;\
        MATERIALMAIN;\
        MAXSPAN;\
        NAVCNTROL;\
        NAVHC;\
        NAVVC;\
        NBIIMPCOST;\
        NBIRWCOST;\
        NBISLEN;\
        NBITOTCOST;\
        NBIYRCOST;\
        NSTATECODE;\
        PARALSTRUC;\
        PLACECODE;\
        PROPWORK;\
        REFHUC;\
        REFVUC;\
        RTCURBSW;\
        SKEW;\
        STRFLARED;\
        STRUCT_NUM;\
        SUMLANES;\
        TEMPSTRUC;\
        VCLROVER;\
        ADTFUTURE;\
        ADTFUTYEAR;\
        ADTTOTAL;\
        ADTYEAR;\
        DEFHWY;\
        DIRSUFFIX;\
        FUNCCLASS;\
        HCLRINV;\
        KIND_HWY;\
        KMPOST;\
        LANES;\
        LEVL_SRVC;\
        NHS_IND;\
        ON_UNDER;\
        TOLLFAC;\
        TRAFFICDIR;\
        TRUCKPCT;\
        AENDRATING;\
        APPRALIGN;\
        ARAILRATIN;\
        CHANRATING;\
        DECKGEOM;\
        NEXTINSP;\
        PIERPROT;\
        RAILRATING;\
        SCOURCRIT;\
        STRRATING;\
        TRANSRATIN;\
        UNDERCLR;\
        WATERADEQ;\
        BUS_PLAN_NETWORK;\
        ROW_MODIFIED;\
        ORIG_FID;\
        BRKEY")

        message ("Creating Archived Layer {}".format(YEAR_MONTH_DAY_Bridges_BMS_Local_shp))
        # Process: Clip
        arcpy.Clip_analysis(temp_bridge_local_layer_shp, York_GIS_DIST_County_Boundary, Bridges_BMS_Local_Temp_shp, "")

        # Process: Select (30)
        arcpy.Select_analysis(Bridges_BMS_Local_Temp_shp, YEAR_MONTH_DAY_Bridges_BMS_Local_shp, "")

        # Process: Join Field (2)
        arcpy.JoinField_management(YEAR_MONTH_DAY_Bridges_BMS_Local_shp, "BRKEY", Bridge_YCPC_Group_dbf, "BRIDGE_KEY", "YCPC_GROUP")

        # Process: Make Feature Layer (11)
        arcpy.MakeFeatureLayer_management(YEAR_MONTH_DAY_Bridges_BMS_Local_shp, Bridges_BMS_Local_TEST_Layer2, "", "", "FID FID VISIBLE NONE;\
        Shape Shape VISIBLE NONE;\
        Id Id VISIBLE NONE;\
        BRIDGE_ID1 BRIDGE_ID1 VISIBLE NONE;\
        BRKEY BRKEY VISIBLE NONE;\
        Local_br_n Local_br_n VISIBLE NONE;\
        CTY_CODE CTY_CODE VISIBLE NONE;\
        ST_RT_NO ST_RT_NO VISIBLE NONE;\
        SEG_NO SEG_NO VISIBLE NONE;\
        OFFSET OFFSET VISIBLE NONE;\
        ADMIN_JURI ADMIN_JURI VISIBLE NONE;\
        DEC_LAT DEC_LAT VISIBLE NONE;\
        DEC_LONG DEC_LONG VISIBLE NONE;\
        BRIDGE_ID BRIDGE_ID VISIBLE NONE;\
        FEATINT FEATINT VISIBLE NONE;\
        DISTRICT DISTRICT VISIBLE NONE;\
        FACILITY FACILITY VISIBLE NONE;\
        LOCATION LOCATION VISIBLE NONE;\
        OWNER OWNER VISIBLE NONE;\
        YEARBUILT YEARBUILT VISIBLE NONE;\
        YEARRECON YEARRECON VISIBLE NONE;\
        SERVTYPON SERVTYPON VISIBLE NONE;\
        SERVTYPUND SERVTYPUND VISIBLE NONE;\
        MAINSPANS MAINSPANS VISIBLE NONE;\
        APPSPANS APPSPANS VISIBLE NONE;\
        LENGTH LENGTH VISIBLE NONE;\
        DECKWIDTH DECKWIDTH VISIBLE NONE;\
        DKSURFTYPE DKSURFTYPE VISIBLE NONE;\
        DKMEMBTYPE DKMEMBTYPE VISIBLE NONE;\
        DKPROTECT DKPROTECT VISIBLE NONE;\
        MAIN_WS_TH MAIN_WS_TH VISIBLE NONE;\
        APPR_DKSUR APPR_DKSUR VISIBLE NONE;\
        APPR_DKMEM APPR_DKMEM VISIBLE NONE;\
        APPR_DKPRO APPR_DKPRO VISIBLE NONE;\
        APPR_WS_TH APPR_WS_TH VISIBLE NONE;\
        FED_FUND FED_FUND VISIBLE NONE;\
        DECK_RECON DECK_RECON VISIBLE NONE;\
        SUP_RECON_ SUP_RECON_ VISIBLE NONE;\
        SUB_RECON_ SUB_RECON_ VISIBLE NONE;\
        DEPT_MAIN_ DEPT_MAIN_ VISIBLE NONE;\
        DEPT_MAIN1 DEPT_MAIN1 VISIBLE NONE;\
        DEPT_MAI_1 DEPT_MAI_1 VISIBLE NONE;\
        DEPT_MAI_2 DEPT_MAI_2 VISIBLE NONE;\
        DEPT_APPR_ DEPT_APPR_ VISIBLE NONE;\
        DEPT_APPR1 DEPT_APPR1 VISIBLE NONE;\
        DEPT_APP_1 DEPT_APP_1 VISIBLE NONE;\
        DEPT_APP_2 DEPT_APP_2 VISIBLE NONE;\
        SUB_AGENCY SUB_AGENCY VISIBLE NONE;\
        MAINT_RESP MAINT_RESP VISIBLE NONE;\
        CRIT_FACIL CRIT_FACIL VISIBLE NONE;\
        APPR_PAVEM APPR_PAVEM VISIBLE NONE;\
        COVERED_BR COVERED_BR VISIBLE NONE;\
        FLOOD_INSP FLOOD_INSP VISIBLE NONE;\
        DEPT_DKSTR DEPT_DKSTR VISIBLE NONE;\
        BYPASSLEN BYPASSLEN VISIBLE NONE;\
        AROADWIDTH AROADWIDTH VISIBLE NONE;\
        ROADWIDTH ROADWIDTH VISIBLE NONE;\
        MIN_OVER_V MIN_OVER_V VISIBLE NONE;\
        MIN_OVER_1 MIN_OVER_1 VISIBLE NONE;\
        POST_LIMIT POST_LIMIT VISIBLE NONE;\
        POST_LIM_1 POST_LIM_1 VISIBLE NONE;\
        INSPDATE INSPDATE VISIBLE NONE;\
        BRINSPFREQ BRINSPFREQ VISIBLE NONE;\
        POST_STATU POST_STATU VISIBLE NONE;\
        NBI_RATING NBI_RATING VISIBLE NONE;\
        SUFF_RATE SUFF_RATE VISIBLE NONE;\
        MAINT_DEF_ MAINT_DEF_ VISIBLE NONE;\
        HBRR_ELIG HBRR_ELIG VISIBLE NONE;\
        JURIS JURIS VISIBLE NONE;\
        SEG_END SEG_END VISIBLE NONE;\
        OFFSET_END OFFSET_END VISIBLE NONE;\
        SEG_PT_BGN SEG_PT_BGN VISIBLE NONE;\
        SEG_PT_END SEG_PT_END VISIBLE NONE;\
        SIDE_IND SIDE_IND VISIBLE NONE;\
        NLF_ID NLF_ID VISIBLE NONE;\
        NLF_CNTL_B NLF_CNTL_B VISIBLE NONE;\
        NLF_CNTL_E NLF_CNTL_E VISIBLE NONE;\
        CUM_OFFSET CUM_OFFSET VISIBLE NONE;\
        CUM_OFFS_1 CUM_OFFS_1 VISIBLE NONE;\
        DKRATING DKRATING VISIBLE NONE;\
        SUPRATING SUPRATING VISIBLE NONE;\
        SUBRATING SUBRATING VISIBLE NONE;\
        CULVRATING CULVRATING VISIBLE NONE;\
        STATE_LOCA STATE_LOCA VISIBLE NONE;\
        DECK_AREA DECK_AREA VISIBLE NONE;\
        BB_BRDGEID BB_BRDGEID VISIBLE NONE;\
        BB_PCT BB_PCT VISIBLE NONE;\
        BRIDGEMED BRIDGEMED VISIBLE NONE;\
        CUSTODIAN CUSTODIAN VISIBLE NONE;\
        DESIGNAPPR DESIGNAPPR VISIBLE NONE;\
        DESIGNMAIN DESIGNMAIN VISIBLE NONE;\
        DKSTRUCTYP DKSTRUCTYP VISIBLE NONE;\
        FIPS_STATE FIPS_STATE VISIBLE NONE;\
        HCLRULT HCLRULT VISIBLE NONE;\
        HCLRURT HCLRURT VISIBLE NONE;\
        HISTSIGN HISTSIGN VISIBLE NONE;\
        IMPLEN IMPLEN VISIBLE NONE;\
        LFTBRNAVCL LFTBRNAVCL VISIBLE NONE;\
        LFTCURBSW LFTCURBSW VISIBLE NONE;\
        MATERIALAP MATERIALAP VISIBLE NONE;\
        MATERIALMA MATERIALMA VISIBLE NONE;\
        MAXSPAN MAXSPAN VISIBLE NONE;\
        NAVCNTROL NAVCNTROL VISIBLE NONE;\
        NAVHC NAVHC VISIBLE NONE;\
        NAVVC NAVVC VISIBLE NONE;\
        NBIIMPCOST NBIIMPCOST VISIBLE NONE;\
        NBIRWCOST NBIRWCOST VISIBLE NONE;\
        NBISLEN NBISLEN VISIBLE NONE;\
        NBITOTCOST NBITOTCOST VISIBLE NONE;\
        NBIYRCOST NBIYRCOST VISIBLE NONE;\
        NSTATECODE NSTATECODE VISIBLE NONE;\
        PARALSTRUC PARALSTRUC VISIBLE NONE;\
        PLACECODE PLACECODE VISIBLE NONE;\
        PROPWORK PROPWORK VISIBLE NONE;\
        REFHUC REFHUC VISIBLE NONE;\
        REFVUC REFVUC VISIBLE NONE;\
        RTCURBSW RTCURBSW VISIBLE NONE;\
        SKEW SKEW VISIBLE NONE;\
        STRFLARED STRFLARED VISIBLE NONE;\
        STRUCT_NUM STRUCT_NUM VISIBLE NONE;\
        SUMLANES SUMLANES VISIBLE NONE;\
        TEMPSTRUC TEMPSTRUC VISIBLE NONE;\
        VCLROVER VCLROVER VISIBLE NONE;\
        ADTFUTURE ADTFUTURE VISIBLE NONE;\
        ADTFUTYEAR ADTFUTYEAR VISIBLE NONE;\
        ADTTOTAL ADTTOTAL VISIBLE NONE;\
        ADTYEAR ADTYEAR VISIBLE NONE;\
        DEFHWY DEFHWY VISIBLE NONE;\
        DIRSUFFIX DIRSUFFIX VISIBLE NONE;\
        FUNCCLASS FUNCCLASS VISIBLE NONE;\
        HCLRINV HCLRINV VISIBLE NONE;\
        KIND_HWY KIND_HWY VISIBLE NONE;\
        KMPOST KMPOST VISIBLE NONE;\
        LANES LANES VISIBLE NONE;\
        LEVL_SRVC LEVL_SRVC VISIBLE NONE;\
        NHS_IND NHS_IND VISIBLE NONE;\
        ON_UNDER ON_UNDER VISIBLE NONE;\
        TOLLFAC TOLLFAC VISIBLE NONE;\
        TRAFFICDIR TRAFFICDIR VISIBLE NONE;\
        TRUCKPCT TRUCKPCT VISIBLE NONE;\
        AENDRATING AENDRATING VISIBLE NONE;\
        APPRALIGN APPRALIGN VISIBLE NONE;\
        ARAILRATIN ARAILRATIN VISIBLE NONE;\
        CHANRATING CHANRATING VISIBLE NONE;\
        DECKGEOM DECKGEOM VISIBLE NONE;\
        NEXTINSP NEXTINSP VISIBLE NONE;\
        PIERPROT PIERPROT VISIBLE NONE;\
        RAILRATING RAILRATING VISIBLE NONE;\
        SCOURCRIT SCOURCRIT VISIBLE NONE;\
        STRRATING STRRATING VISIBLE NONE;\
        TRANSRATIN TRANSRATIN VISIBLE NONE;\
        UNDERCLR UNDERCLR VISIBLE NONE;\
        WATERADEQ WATERADEQ VISIBLE NONE;\
        BUS_PLAN_N BUS_PLAN_N VISIBLE NONE;\
        ROW_MODIFI ROW_MODIFI VISIBLE NONE;\
        ORIG_FID ORIG_FID VISIBLE NONE;\
        BRKEY_1 BRKEY_1 VISIBLE NONE;\
        YCPC_GROUP YCPC_GROUP VISIBLE NONE")

        message ("Starting Trans Count Steps")
        # Process: Dissolve
        arcpy.Dissolve_management(York_GIS_TRANSP_Counts, Trans_Count_Dsslv1_shp, "BRKEY", "YEAR MAX", "MULTI_PART", "DISSOLVE_LINES")

        # Process: Add Field (4)
        arcpy.AddField_management(Trans_Count_Dsslv1_shp, "JOINFIELD", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

        arcpy.AddField_management(Trans_Count_Dsslv1_shp, "MAX_YEAR_1", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

        # Process: Calculate Field (20)
        arcpy.CalculateField_management(Trans_Count_Dsslv1_shp, "MAX_YEAR_1", "!MAX_YEAR!", "PYTHON", "")

        arcpy.CalculateField_management(Trans_Count_Dsslv1_shp, "JOINFIELD", "!BRKEY! + !MAX_YEAR_1!", "PYTHON", "")

        # Process: Make Feature Layer (3)
        arcpy.MakeFeatureLayer_management(Trans_Count_Dsslv1_shp, Trans_Count_Dsslv_Layer, "", "", "FID FID VISIBLE NONE;\
        Shape Shape VISIBLE NONE;\
        BRKEY BRKEY VISIBLE NONE;\
        MAX_YEAR MAX_YEAR VISIBLE NONE;\
        JOINFIELD JOINFIELD VISIBLE NONE")

        # Process: Select (28)
        arcpy.Select_analysis(York_GIS_TRANSP_Counts, Trans_Count_Select_shp, "")

        # Process: Add Field (2)
        arcpy.AddField_management(Trans_Count_Select_shp, "JOINFIELD", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

        arcpy.AddField_management(Trans_Count_Select_shp, "YEAR_NEW", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

        # Process: Calculate Field (19)
        arcpy.CalculateField_management(Trans_Count_Select_shp, "YEAR_NEW", "!YEAR!", "PYTHON", "")

        arcpy.CalculateField_management(Trans_Count_Select_shp, "JOINFIELD", "!BRKEY! + !YEAR_NEW!", "PYTHON", "")

        # Process: Make Feature Layer (9)
        arcpy.MakeFeatureLayer_management(Trans_Count_Select_shp, Trans_Count_Select_Layer, "", "", "FID FID VISIBLE NONE;\
        Shape Shape VISIBLE NONE;\
        COUNTER_ID COUNTER_ID VISIBLE NONE;\
        COUNT_TYPE COUNT_TYPE VISIBLE NONE;\
        BRIDGE_ID1 BRIDGE_ID1 VISIBLE NONE;\
        BRKEY BRKEY VISIBLE NONE;\
        PURPOSE PURPOSE VISIBLE NONE;\
        VOLUME VOLUME VISIBLE NONE;\
        AM_VOLUME AM_VOLUME VISIBLE NONE;\
        AM_PERCENT AM_PERCENT VISIBLE NONE;\
        AM_PEAK AM_PEAK VISIBLE NONE;\
        PM_VOLUME PM_VOLUME VISIBLE NONE;\
        PM_PERCENT PM_PERCENT VISIBLE NONE;\
        PM_PEAK PM_PEAK VISIBLE NONE;\
        PLN_REGION PLN_REGION VISIBLE NONE;\
        YEAR YEAR VISIBLE NONE;\
        OTHER_MODE OTHER_MODE VISIBLE NONE;\
        COMMENT COMMENT VISIBLE NONE;\
        CREATE_DAT CREATE_DAT VISIBLE NONE;\
        MODIFY_DAT MODIFY_DAT VISIBLE NONE;\
        EDIT_NAME EDIT_NAME VISIBLE NONE;\
        EDIT_TYPE EDIT_TYPE VISIBLE NONE;\
        JOINFIELD JOINFIELD VISIBLE NONE")

        # Process: Join Field (5)
        arcpy.JoinField_management(Trans_Count_Dsslv_Layer, "JOINFIELD", Trans_Count_Select_Layer, "JOINFIELD", "BRKEY;\
        VOLUME;\
        AM_VOLUME;\
        AM_PERCENT;\
        AM_PEAK;\
        PM_VOLUME;\
        PM_PERCENT;\
        PM_PEAK;\
        YEAR")

        # Process: Select (29)
        arcpy.Select_analysis(Trans_Count_Dsslv_Layer, Trans_Count_Final_shp, "NOT \"BRKEY\" = ' ' AND NOT \"BRKEY\" = '0'")

        # Process: Add Attribute Index
        #arcpy.AddIndex_management(Trans_Count_Final_shp, "BRKEY", "", "NON_UNIQUE", "NON_ASCENDING")

        # Process: Make Feature Layer (10)
        arcpy.MakeFeatureLayer_management(Trans_Count_Final_shp, Trans_Count_Final_Layer, "", "", "FID FID VISIBLE NONE;\
        Shape Shape VISIBLE NONE;\
        BRKEY BRKEY VISIBLE NONE;\
        MAX_YEAR MAX_YEAR VISIBLE NONE;\
        JOINFIELD JOINFIELD VISIBLE NONE;\
        BRKEY_1 BRKEY_1 VISIBLE NONE;\
        MAX_YEAR_1 MAX_YEAR_1 VISIBLE NONE;\
        VOLUME VOLUME VISIBLE NONE;\
        AM_VOLUME AM_VOLUME VISIBLE NONE;\
        AM_PERCENT AM_PERCENT VISIBLE NONE;\
        AM_PEAK AM_PEAK VISIBLE NONE;\
        PM_VOLUME PM_VOLUME VISIBLE NONE;\
        PM_PERCENT PM_PERCENT VISIBLE NONE;\
        PM_PEAK PM_PEAK VISIBLE NONE;\
        YEAR YEAR VISIBLE NONE")

        # Process: Join Field (4)
        arcpy.JoinField_management(Bridges_BMS_Local_TEST_Layer2, "BRKEY", Trans_Count_Final_Layer, "BRKEY", "VOLUME;\
        AM_VOLUME;\
        AM_PERCENT;\
        AM_PEAK;\
        PM_VOLUME;\
        PM_PERCENT;\
        PM_PEAK;\
        YEAR")

        message ("Starting State Bridges Steps")
        # Process: Make Feature Layer (5)
        arcpy.MakeFeatureLayer_management(State_And_Local_Bridges, v0_Layer, "", "", "OBJECTID OBJECTID VISIBLE NONE;\
        Shape Shape VISIBLE NONE;\
        CTY_CODE CTY_CODE VISIBLE NONE;\
        ST_RT_NO ST_RT_NO VISIBLE NONE;\
        SEG_NO SEG_NO VISIBLE NONE;\
        OFFSET OFFSET VISIBLE NONE;\
        ADMIN_JURIS ADMIN_JURIS VISIBLE NONE;\
        DEC_LAT DEC_LAT VISIBLE NONE;\
        DEC_LONG DEC_LONG VISIBLE NONE;\
        BRIDGE_ID BRIDGE_ID VISIBLE NONE;\
        FEATINT FEATINT VISIBLE NONE;\
        DISTRICT DISTRICT VISIBLE NONE;\
        FACILITY FACILITY VISIBLE NONE;\
        LOCATION LOCATION VISIBLE NONE;\
        OWNER OWNER VISIBLE NONE;\
        YEARBUILT YEARBUILT VISIBLE NONE;\
        YEARRECON YEARRECON VISIBLE NONE;\
        SERVTYPON SERVTYPON VISIBLE NONE;\
        SERVTYPUND SERVTYPUND VISIBLE NONE;\
        MAINSPANS MAINSPANS VISIBLE NONE;\
        APPSPANS APPSPANS VISIBLE NONE;\
        LENGTH LENGTH VISIBLE NONE;\
        DECKWIDTH DECKWIDTH VISIBLE NONE;\
        DKSURFTYPE DKSURFTYPE VISIBLE NONE;\
        DKMEMBTYPE DKMEMBTYPE VISIBLE NONE;\
        DKPROTECT DKPROTECT VISIBLE NONE;\
        MAIN_WS_THICKNESS MAIN_WS_THICKNESS VISIBLE NONE;\
        APPR_DKSURFTYPE APPR_DKSURFTYPE VISIBLE NONE;\
        APPR_DKMEMBTYPE APPR_DKMEMBTYPE VISIBLE NONE;\
        APPR_DKPROTECT APPR_DKPROTECT VISIBLE NONE;\
        APPR_WS_THICKNESS APPR_WS_THICKNESS VISIBLE NONE;\
        FED_FUND FED_FUND VISIBLE NONE;\
        DECK_RECON_WORK_TYPE DECK_RECON_WORK_TYPE VISIBLE NONE;\
        SUP_RECON_WORK_TYPE SUP_RECON_WORK_TYPE VISIBLE NONE;\
        SUB_RECON_WORK_TYPE SUB_RECON_WORK_TYPE VISIBLE NONE;\
        DEPT_MAIN_MATERIAL_TYPE DEPT_MAIN_MATERIAL_TYPE VISIBLE NONE;\
        DEPT_MAIN_PHYSICAL_TYPE DEPT_MAIN_PHYSICAL_TYPE VISIBLE NONE;\
        DEPT_MAIN_SPAN_INTERACTION DEPT_MAIN_SPAN_INTERACTION VISIBLE NONE;\
        DEPT_MAIN_STRUC_CONFIG DEPT_MAIN_STRUC_CONFIG VISIBLE NONE;\
        DEPT_APPR_MATERIAL_TYPE DEPT_APPR_MATERIAL_TYPE VISIBLE NONE;\
        DEPT_APPR_PHYSICAL_TYPE DEPT_APPR_PHYSICAL_TYPE VISIBLE NONE;\
        DEPT_APPR_SPAN_INTERACTION DEPT_APPR_SPAN_INTERACTION VISIBLE NONE;\
        DEPT_APPR_STRUC_CONFIG DEPT_APPR_STRUC_CONFIG VISIBLE NONE;\
        SUB_AGENCY SUB_AGENCY VISIBLE NONE;\
        MAINT_RESP_DESC MAINT_RESP_DESC VISIBLE NONE;\
        CRIT_FACILITY CRIT_FACILITY VISIBLE NONE;\
        APPR_PAVEMENT_WIDTH APPR_PAVEMENT_WIDTH VISIBLE NONE;\
        COVERED_BRIDGE COVERED_BRIDGE VISIBLE NONE;\
        FLOOD_INSP FLOOD_INSP VISIBLE NONE;\
        DEPT_DKSTRUCTYP DEPT_DKSTRUCTYP VISIBLE NONE;\
        BYPASSLEN BYPASSLEN VISIBLE NONE;\
        AROADWIDTH AROADWIDTH VISIBLE NONE;\
        ROADWIDTH ROADWIDTH VISIBLE NONE;\
        MIN_OVER_VERT_CLEAR_RIGHT MIN_OVER_VERT_CLEAR_RIGHT VISIBLE NONE;\
        MIN_OVER_VERT_CLEAR_LEFT MIN_OVER_VERT_CLEAR_LEFT VISIBLE NONE;\
        POST_LIMIT_WEIGHT POST_LIMIT_WEIGHT VISIBLE NONE;\
        POST_LIMIT_COMB POST_LIMIT_COMB VISIBLE NONE;\
        INSPDATE INSPDATE VISIBLE NONE;\
        BRINSPFREQ BRINSPFREQ VISIBLE NONE;\
        POST_STATUS POST_STATUS VISIBLE NONE;\
        NBI_RATING NBI_RATING VISIBLE NONE;\
        SUFF_RATE SUFF_RATE VISIBLE NONE;\
        MAINT_DEF_RATE MAINT_DEF_RATE VISIBLE NONE;\
        HBRR_ELIG HBRR_ELIG VISIBLE NONE;\
        JURIS JURIS VISIBLE NONE;\
        SEG_END SEG_END VISIBLE NONE;\
        OFFSET_END OFFSET_END VISIBLE NONE;\
        SEG_PT_BGN SEG_PT_BGN VISIBLE NONE;\
        SEG_PT_END SEG_PT_END VISIBLE NONE;\
        SIDE_IND SIDE_IND VISIBLE NONE;\
        NLF_ID NLF_ID VISIBLE NONE;\
        NLF_CNTL_BGN NLF_CNTL_BGN VISIBLE NONE;\
        NLF_CNTL_END NLF_CNTL_END VISIBLE NONE;\
        CUM_OFFSET_BGN CUM_OFFSET_BGN VISIBLE NONE;\
        CUM_OFFSET_END CUM_OFFSET_END VISIBLE NONE;\
        DKRATING DKRATING VISIBLE NONE;\
        SUPRATING SUPRATING VISIBLE NONE;\
        SUBRATING SUBRATING VISIBLE NONE;\
        CULVRATING CULVRATING VISIBLE NONE;\
        STATE_LOCAL STATE_LOCAL VISIBLE NONE;\
        DECK_AREA DECK_AREA VISIBLE NONE;\
        BB_BRDGEID BB_BRDGEID VISIBLE NONE;\
        BB_PCT BB_PCT VISIBLE NONE;\
        BRIDGEMED BRIDGEMED VISIBLE NONE;\
        CUSTODIAN CUSTODIAN VISIBLE NONE;\
        DESIGNAPPR DESIGNAPPR VISIBLE NONE;\
        DESIGNMAIN DESIGNMAIN VISIBLE NONE;\
        DKSTRUCTYP DKSTRUCTYP VISIBLE NONE;\
        FIPS_STATE FIPS_STATE VISIBLE NONE;\
        HCLRULT HCLRULT VISIBLE NONE;\
        HCLRURT HCLRURT VISIBLE NONE;\
        HISTSIGN HISTSIGN VISIBLE NONE;\
        IMPLEN IMPLEN VISIBLE NONE;\
        LFTBRNAVCL LFTBRNAVCL VISIBLE NONE;\
        LFTCURBSW LFTCURBSW VISIBLE NONE;\
        MATERIALAPPR MATERIALAPPR VISIBLE NONE;\
        MATERIALMAIN MATERIALMAIN VISIBLE NONE;\
        MAXSPAN MAXSPAN VISIBLE NONE;\
        NAVCNTROL NAVCNTROL VISIBLE NONE;\
        NAVHC NAVHC VISIBLE NONE;\
        NAVVC NAVVC VISIBLE NONE;\
        NBIIMPCOST NBIIMPCOST VISIBLE NONE;\
        NBIRWCOST NBIRWCOST VISIBLE NONE;\
        NBISLEN NBISLEN VISIBLE NONE;\
        NBITOTCOST NBITOTCOST VISIBLE NONE;\
        NBIYRCOST NBIYRCOST VISIBLE NONE;\
        NSTATECODE NSTATECODE VISIBLE NONE;\
        PARALSTRUC PARALSTRUC VISIBLE NONE;\
        PLACECODE PLACECODE VISIBLE NONE;\
        PROPWORK PROPWORK VISIBLE NONE;\
        REFHUC REFHUC VISIBLE NONE;\
        REFVUC REFVUC VISIBLE NONE;\
        RTCURBSW RTCURBSW VISIBLE NONE;\
        SKEW SKEW VISIBLE NONE;\
        STRFLARED STRFLARED VISIBLE NONE;\
        STRUCT_NUM STRUCT_NUM VISIBLE NONE;\
        SUMLANES SUMLANES VISIBLE NONE;\
        TEMPSTRUC TEMPSTRUC VISIBLE NONE;\
        VCLROVER VCLROVER VISIBLE NONE;\
        ADTFUTURE ADTFUTURE VISIBLE NONE;\
        ADTFUTYEAR ADTFUTYEAR VISIBLE NONE;\
        ADTTOTAL ADTTOTAL VISIBLE NONE;\
        ADTYEAR ADTYEAR VISIBLE NONE;\
        DEFHWY DEFHWY VISIBLE NONE;\
        DIRSUFFIX DIRSUFFIX VISIBLE NONE;\
        FUNCCLASS FUNCCLASS VISIBLE NONE;\
        HCLRINV HCLRINV VISIBLE NONE;\
        KIND_HWY KIND_HWY VISIBLE NONE;\
        KMPOST KMPOST VISIBLE NONE;\
        LANES LANES VISIBLE NONE;\
        LEVL_SRVC LEVL_SRVC VISIBLE NONE;\
        NHS_IND NHS_IND VISIBLE NONE;\
        ON_UNDER ON_UNDER VISIBLE NONE;\
        TOLLFAC TOLLFAC VISIBLE NONE;\
        TRAFFICDIR TRAFFICDIR VISIBLE NONE;\
        TRUCKPCT TRUCKPCT VISIBLE NONE;\
        AENDRATING AENDRATING VISIBLE NONE;\
        APPRALIGN APPRALIGN VISIBLE NONE;\
        ARAILRATIN ARAILRATIN VISIBLE NONE;\
        CHANRATING CHANRATING VISIBLE NONE;\
        DECKGEOM DECKGEOM VISIBLE NONE;\
        NEXTINSP NEXTINSP VISIBLE NONE;\
        PIERPROT PIERPROT VISIBLE NONE;\
        RAILRATING RAILRATING VISIBLE NONE;\
        SCOURCRIT SCOURCRIT VISIBLE NONE;\
        STRRATING STRRATING VISIBLE NONE;\
        TRANSRATIN TRANSRATIN VISIBLE NONE;\
        UNDERCLR UNDERCLR VISIBLE NONE;\
        WATERADEQ WATERADEQ VISIBLE NONE;\
        BUS_PLAN_NETWORK BUS_PLAN_NETWORK VISIBLE NONE;\
        ROW_MODIFIED ROW_MODIFIED VISIBLE NONE;\
        ORIG_FID ORIG_FID VISIBLE NONE;\
        BRKEY BRKEY VISIBLE NONE")

        # Process: Select Layer By Attribute (4)
        arcpy.SelectLayerByAttribute_management(v0_Layer, "NEW_SELECTION", "\"CTY_CODE\" = '66' OR \"CTY_CODE\" = '01' OR \"CTY_CODE\" = '21' OR \"CTY_CODE\" = '22' OR \"CTY_CODE\" = '36'")

        # Process: Select Layer By Attribute (2)
        arcpy.SelectLayerByAttribute_management(v0_Layer2, "REMOVE_FROM_SELECTION", "\"STATE_LOCAL\" = 'L'")

        # Process: Select (23)
        arcpy.Select_analysis(v0_Layer2, State_Bridges_shp, "")

        # Process: Project (2)
        arcpy.Project_management(State_Bridges_shp, State_Bridges_Project, "PROJCS['NAD_1983_StatePlane_Pennsylvania_South_FIPS_3702_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',1968500.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-77.75],PARAMETER['Standard_Parallel_1',39.93333333333333],PARAMETER['Standard_Parallel_2',40.96666666666667],PARAMETER['Latitude_Of_Origin',39.33333333333334],UNIT['Foot_US',0.3048006096012192]]", "", "PROJCS['Pennsylvania Polyconic',GEOGCS['NAD 83',DATUM['NAD 83',SPHEROID['GRS 80',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Polyconic'],PARAMETER['Central_Meridian',-77.75],PARAMETER['Latitude_Of_Origin',40.925],UNIT['Meter',1.0]]")

        # Process: Select (22)
        arcpy.Select_analysis(State_Bridges_Project, State_Bridges_Project_Select_shp, "\"CTY_CODE\" = '66'")

        message ("Starting RMS Admin Steps")

        # Process: Project (3)
        arcpy.Project_management(RMSADMIN, XRMSADMIN_Project_shp, "PROJCS['NAD_1983_StatePlane_Pennsylvania_South_FIPS_3702_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',1968500.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-77.75],PARAMETER['Standard_Parallel_1',39.93333333333333],PARAMETER['Standard_Parallel_2',40.96666666666667],PARAMETER['Latitude_Of_Origin',39.33333333333334],UNIT['Foot_US',0.3048006096012192]]", "", "PROJCS['Pennsylvania Polyconic',GEOGCS['NAD 83',DATUM['NAD 83',SPHEROID['GRS 80',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Polyconic'],PARAMETER['Central_Meridian',-77.75],PARAMETER['Latitude_Of_Origin',40.925],UNIT['Meter',1.0]]")

        # Process: Clip (3)
        arcpy.Clip_analysis(XRMSADMIN_Project_shp, County_Boundary, RMSADMIN_shp, "")

        # Process: Make Feature Layer (14)
        arcpy.MakeFeatureLayer_management(RMSADMIN_shp, RMSADMIN_Layer, "", "", "FID FID VISIBLE NONE;\
        Shape Shape VISIBLE NONE;\
        ST_RT_NO ST_RT_NO VISIBLE NONE;\
        CTY_CODE CTY_CODE VISIBLE NONE;\
        DISTRICT_N DISTRICT_N VISIBLE NONE;\
        JURIS JURIS VISIBLE NONE;\
        SEG_BGN SEG_BGN VISIBLE NONE;\
        OFFSET_BGN OFFSET_BGN VISIBLE NONE;\
        SEG_END SEG_END VISIBLE NONE;\
        OFFSET_END OFFSET_END VISIBLE NONE;\
        SEG_LNGTH_ SEG_LNGTH_ VISIBLE NONE;\
        SEG_PT_BGN SEG_PT_BGN VISIBLE NONE;\
        SEG_PT_END SEG_PT_END VISIBLE NONE;\
        SEQ_NO SEQ_NO VISIBLE NONE;\
        MAINT_FUNC MAINT_FUNC VISIBLE NONE;\
        POST_BOND_ POST_BOND_ VISIBLE NONE;\
        SPEED_LIMI SPEED_LIMI VISIBLE NONE;\
        FED_AID_SY FED_AID_SY VISIBLE NONE;\
        FED_AID_UR FED_AID_UR VISIBLE NONE;\
        FUNC_CLS FUNC_CLS VISIBLE NONE;\
        FED_ID FED_ID VISIBLE NONE;\
        FED_AID__1 FED_AID__1 VISIBLE NONE;\
        MAPID MAPID VISIBLE NONE;\
        NLF_ID NLF_ID VISIBLE NONE;\
        SIDE_IND SIDE_IND VISIBLE NONE;\
        NLF_CNTL_B NLF_CNTL_B VISIBLE NONE;\
        NLF_CNTL_E NLF_CNTL_E VISIBLE NONE;\
        CUM_OFFSET CUM_OFFSET VISIBLE NONE;\
        CUM_OFFS_1 CUM_OFFS_1 VISIBLE NONE;\
        RECORD_UPD RECORD_UPD VISIBLE NONE;\
        FIPS_AREA_ FIPS_AREA_ VISIBLE NONE;\
        GEOMETRY_L GEOMETRY_L VISIBLE NONE;\
        Shape_Leng Shape_Leng VISIBLE NONE;\
        Shape_le_1 Shape_le_1 VISIBLE NONE")

        message ("Creating Archived Layer {}".format(YEAR_MONTH_DAY_Bridges_BMS_STATE_shp))

        # Process: Select Layer By Attribute (11)
        arcpy.SelectLayerByAttribute_management(RMSADMIN_Layer, "NEW_SELECTION", "\"ST_RT_NO\" LIKE 'Q%' OR NOT \"CTY_CODE\" = '66'")

        # Process: Delete Rows (4)
        arcpy.DeleteRows_management(RMSADMIN_Layer)

        # Process: Spatial Join
        arcpy.SpatialJoin_analysis(State_Bridges_Project_Select_shp, RMSADMIN_Layer, Bridges_BMS_State_Temp_shp, "JOIN_ONE_TO_MANY", "KEEP_ALL", "", "INTERSECT", "5 Feet", "")

        # Process: Select (31)
        arcpy.Select_analysis(Bridges_BMS_State_Temp_shp, YEAR_MONTH_DAY_Bridges_BMS_STATE_shp, "")

        # Process: Make Feature Layer (2)
        arcpy.MakeFeatureLayer_management(YEAR_MONTH_DAY_Bridges_BMS_STATE_shp, YEAR_MONTH_DAY_Bridges_BMS_S, "", "", "FID FID VISIBLE NONE;\
        Shape Shape VISIBLE NONE;\
        Join_Count Join_Count VISIBLE NONE;\
        TARGET_FID TARGET_FID VISIBLE NONE;\
        JOIN_FID JOIN_FID VISIBLE NONE")

        # Process: Make Feature Layer
        arcpy.MakeFeatureLayer_management(YEAR_MONTH_DAY_Bridges_BMS_Local_shp, Bridges_BMS_Local_TEST_Layer, "", "", "FID FID VISIBLE NONE;\
        Shape Shape VISIBLE NONE;\
        Id Id VISIBLE NONE;\
        BRIDGE_ID1 BRIDGE_ID1 VISIBLE NONE;\
        BRKEY BRKEY VISIBLE NONE;\
        Local_br_n Local_br_n VISIBLE NONE;\
        CTY_CODE CTY_CODE VISIBLE NONE;\
        ST_RT_NO ST_RT_NO VISIBLE NONE;\
        SEG_NO SEG_NO VISIBLE NONE;\
        OFFSET OFFSET VISIBLE NONE;\
        ADMIN_JURI ADMIN_JURI VISIBLE NONE;\
        DEC_LAT DEC_LAT VISIBLE NONE;\
        DEC_LONG DEC_LONG VISIBLE NONE;\
        BRIDGE_ID BRIDGE_ID VISIBLE NONE;\
        FEATINT FEATINT VISIBLE NONE;\
        DISTRICT DISTRICT VISIBLE NONE;\
        FACILITY FACILITY VISIBLE NONE;\
        LOCATION LOCATION VISIBLE NONE;\
        OWNER OWNER VISIBLE NONE;\
        YEARBUILT YEARBUILT VISIBLE NONE;\
        YEARRECON YEARRECON VISIBLE NONE;\
        SERVTYPON SERVTYPON VISIBLE NONE;\
        SERVTYPUND SERVTYPUND VISIBLE NONE;\
        MAINSPANS MAINSPANS VISIBLE NONE;\
        APPSPANS APPSPANS VISIBLE NONE;\
        LENGTH LENGTH VISIBLE NONE;\
        DECKWIDTH DECKWIDTH VISIBLE NONE;\
        DKSURFTYPE DKSURFTYPE VISIBLE NONE;\
        DKMEMBTYPE DKMEMBTYPE VISIBLE NONE;\
        DKPROTECT DKPROTECT VISIBLE NONE;\
        MAIN_WS_TH MAIN_WS_TH VISIBLE NONE;\
        APPR_DKSUR APPR_DKSUR VISIBLE NONE;\
        APPR_DKMEM APPR_DKMEM VISIBLE NONE;\
        APPR_DKPRO APPR_DKPRO VISIBLE NONE;\
        APPR_WS_TH APPR_WS_TH VISIBLE NONE;\
        FED_FUND FED_FUND VISIBLE NONE;\
        DECK_RECON DECK_RECON VISIBLE NONE;\
        SUP_RECON_ SUP_RECON_ VISIBLE NONE;\
        SUB_RECON_ SUB_RECON_ VISIBLE NONE;\
        DEPT_MAIN_ DEPT_MAIN_ VISIBLE NONE;\
        DEPT_MAIN1 DEPT_MAIN1 VISIBLE NONE;\
        DEPT_MAI_1 DEPT_MAI_1 VISIBLE NONE;\
        DEPT_MAI_2 DEPT_MAI_2 VISIBLE NONE;\
        DEPT_APPR_ DEPT_APPR_ VISIBLE NONE;\
        DEPT_APPR1 DEPT_APPR1 VISIBLE NONE;\
        DEPT_APP_1 DEPT_APP_1 VISIBLE NONE;\
        DEPT_APP_2 DEPT_APP_2 VISIBLE NONE;\
        SUB_AGENCY SUB_AGENCY VISIBLE NONE;\
        MAINT_RESP MAINT_RESP VISIBLE NONE;\
        CRIT_FACIL CRIT_FACIL VISIBLE NONE;\
        APPR_PAVEM APPR_PAVEM VISIBLE NONE;\
        COVERED_BR COVERED_BR VISIBLE NONE;\
        FLOOD_INSP FLOOD_INSP VISIBLE NONE;\
        DEPT_DKSTR DEPT_DKSTR VISIBLE NONE;\
        BYPASSLEN BYPASSLEN VISIBLE NONE;\
        AROADWIDTH AROADWIDTH VISIBLE NONE;\
        ROADWIDTH ROADWIDTH VISIBLE NONE;\
        MIN_OVER_V MIN_OVER_V VISIBLE NONE;\
        MIN_OVER_1 MIN_OVER_1 VISIBLE NONE;\
        POST_LIMIT POST_LIMIT VISIBLE NONE;\
        POST_LIM_1 POST_LIM_1 VISIBLE NONE;\
        INSPDATE INSPDATE VISIBLE NONE;\
        BRINSPFREQ BRINSPFREQ VISIBLE NONE;\
        POST_STATU POST_STATU VISIBLE NONE;\
        NBI_RATING NBI_RATING VISIBLE NONE;\
        SUFF_RATE SUFF_RATE VISIBLE NONE;\
        MAINT_DEF_ MAINT_DEF_ VISIBLE NONE;\
        HBRR_ELIG HBRR_ELIG VISIBLE NONE;\
        JURIS JURIS VISIBLE NONE;\
        SEG_END SEG_END VISIBLE NONE;\
        OFFSET_END OFFSET_END VISIBLE NONE;\
        SEG_PT_BGN SEG_PT_BGN VISIBLE NONE;\
        SEG_PT_END SEG_PT_END VISIBLE NONE;\
        SIDE_IND SIDE_IND VISIBLE NONE;\
        NLF_ID NLF_ID VISIBLE NONE;\
        NLF_CNTL_B NLF_CNTL_B VISIBLE NONE;\
        NLF_CNTL_E NLF_CNTL_E VISIBLE NONE;\
        CUM_OFFSET CUM_OFFSET VISIBLE NONE;\
        CUM_OFFS_1 CUM_OFFS_1 VISIBLE NONE;\
        DKRATING DKRATING VISIBLE NONE;\
        SUPRATING SUPRATING VISIBLE NONE;\
        SUBRATING SUBRATING VISIBLE NONE;\
        CULVRATING CULVRATING VISIBLE NONE;\
        STATE_LOCA STATE_LOCA VISIBLE NONE;\
        DECK_AREA DECK_AREA VISIBLE NONE;\
        BB_BRDGEID BB_BRDGEID VISIBLE NONE;\
        BB_PCT BB_PCT VISIBLE NONE;\
        BRIDGEMED BRIDGEMED VISIBLE NONE;\
        CUSTODIAN CUSTODIAN VISIBLE NONE;\
        DESIGNAPPR DESIGNAPPR VISIBLE NONE;\
        DESIGNMAIN DESIGNMAIN VISIBLE NONE;\
        DKSTRUCTYP DKSTRUCTYP VISIBLE NONE;\
        FIPS_STATE FIPS_STATE VISIBLE NONE;\
        HCLRULT HCLRULT VISIBLE NONE;\
        HCLRURT HCLRURT VISIBLE NONE;\
        HISTSIGN HISTSIGN VISIBLE NONE;\
        IMPLEN IMPLEN VISIBLE NONE;\
        LFTBRNAVCL LFTBRNAVCL VISIBLE NONE;\
        LFTCURBSW LFTCURBSW VISIBLE NONE;\
        MATERIALAP MATERIALAP VISIBLE NONE;\
        MATERIALMA MATERIALMA VISIBLE NONE;\
        MAXSPAN MAXSPAN VISIBLE NONE;\
        NAVCNTROL NAVCNTROL VISIBLE NONE;\
        NAVHC NAVHC VISIBLE NONE;\
        NAVVC NAVVC VISIBLE NONE;\
        NBIIMPCOST NBIIMPCOST VISIBLE NONE;\
        NBIRWCOST NBIRWCOST VISIBLE NONE;\
        NBISLEN NBISLEN VISIBLE NONE;\
        NBITOTCOST NBITOTCOST VISIBLE NONE;\
        NBIYRCOST NBIYRCOST VISIBLE NONE;\
        NSTATECODE NSTATECODE VISIBLE NONE;\
        PARALSTRUC PARALSTRUC VISIBLE NONE;\
        PLACECODE PLACECODE VISIBLE NONE;\
        PROPWORK PROPWORK VISIBLE NONE;\
        REFHUC REFHUC VISIBLE NONE;\
        REFVUC REFVUC VISIBLE NONE;\
        RTCURBSW RTCURBSW VISIBLE NONE;\
        SKEW SKEW VISIBLE NONE;\
        STRFLARED STRFLARED VISIBLE NONE;\
        STRUCT_NUM STRUCT_NUM VISIBLE NONE;\
        SUMLANES SUMLANES VISIBLE NONE;\
        TEMPSTRUC TEMPSTRUC VISIBLE NONE;\
        VCLROVER VCLROVER VISIBLE NONE;\
        ADTFUTURE ADTFUTURE VISIBLE NONE;\
        ADTFUTYEAR ADTFUTYEAR VISIBLE NONE;\
        ADTTOTAL ADTTOTAL VISIBLE NONE;\
        ADTYEAR ADTYEAR VISIBLE NONE;\
        DEFHWY DEFHWY VISIBLE NONE;\
        DIRSUFFIX DIRSUFFIX VISIBLE NONE;\
        FUNCCLASS FUNCCLASS VISIBLE NONE;\
        HCLRINV HCLRINV VISIBLE NONE;\
        KIND_HWY KIND_HWY VISIBLE NONE;\
        KMPOST KMPOST VISIBLE NONE;\
        LANES LANES VISIBLE NONE;\
        LEVL_SRVC LEVL_SRVC VISIBLE NONE;\
        NHS_IND NHS_IND VISIBLE NONE;\
        ON_UNDER ON_UNDER VISIBLE NONE;\
        TOLLFAC TOLLFAC VISIBLE NONE;\
        TRAFFICDIR TRAFFICDIR VISIBLE NONE;\
        TRUCKPCT TRUCKPCT VISIBLE NONE;\
        AENDRATING AENDRATING VISIBLE NONE;\
        APPRALIGN APPRALIGN VISIBLE NONE;\
        ARAILRATIN ARAILRATIN VISIBLE NONE;\
        CHANRATING CHANRATING VISIBLE NONE;\
        DECKGEOM DECKGEOM VISIBLE NONE;\
        NEXTINSP NEXTINSP VISIBLE NONE;\
        PIERPROT PIERPROT VISIBLE NONE;\
        RAILRATING RAILRATING VISIBLE NONE;\
        SCOURCRIT SCOURCRIT VISIBLE NONE;\
        STRRATING STRRATING VISIBLE NONE;\
        TRANSRATIN TRANSRATIN VISIBLE NONE;\
        UNDERCLR UNDERCLR VISIBLE NONE;\
        WATERADEQ WATERADEQ VISIBLE NONE;\
        BUS_PLAN_N BUS_PLAN_N VISIBLE NONE;\
        ROW_MODIFI ROW_MODIFI VISIBLE NONE;\
        ORIG_FID ORIG_FID VISIBLE NONE;\
        BRKEY_1 BRKEY_1 VISIBLE NONE;\
        YCPC_GROUP YCPC_GROUP VISIBLE NONE")

        # Process: Add Join
        arcpy.AddJoin_management(YEAR_MONTH_DAY_Bridges_BMS_S, "STRUCT_NUM", Bridges_BMS_Local_TEST_Layer, "STRUCT_NUM", "KEEP_ALL")

        # Process: Select Layer By Attribute
        arcpy.SelectLayerByAttribute_management(YEAR_MONTH_DAY_Bridges_BMS_S, "NEW_SELECTION", "NOT \"Bridges_BMS_Local_YEAR_MONTH_DAY.BRKEY\" IS NULL")

        # Process: Delete Rows
        arcpy.DeleteRows_management(YEAR_MONTH_DAY_Bridges_BMS_S)

        # Process: Remove Join
        arcpy.RemoveJoin_management(Bridges_BMS_STATE_NOV_2013_L__3_, "")

        # Process: Join Field
        arcpy.JoinField_management(YEAR_MONTH_DAY_Bridges_BMS_STATE_shp, "STRUCT_NUM", Bridge_YCPC_Group_dbf, "BRIDGE_KEY", "YCPC_GROUP")

        # Process: Dissolve (2)
        arcpy.Dissolve_management(YEAR_MONTH_DAY_Bridges_BMS_STATE_shp, YEAR_MONTH_DAY_Bridges_BMS_State_Dssvl_shp, "STRUCT_NUM", "", "SINGLE_PART", "DISSOLVE_LINES")

        # Process: Join Field (3)
        arcpy.JoinField_management(YEAR_MONTH_DAY_Bridges_BMS_State_Dssvl_shp, "STRUCT_NUM", YEAR_MONTH_DAY_Bridges_BMS_STATE_shp, "STRUCT_NUM",\
         "CTY_CODE;\
        ST_RT_NO;\
        SEG_NO;\
        OFFSET;\
        ADMIN_JURIS;\
        DEC_LAT;\
        DEC_LONG;\
        BRIDGE_ID;\
        FEATINT;\
        DISTRICT;\
        FACILITY;\
        LOCATION;\
        OWNER;\
        YEARBUILT;\
        YEARRECON;\
        SERVTYPON;\
        SERVTYPUND;\
        MAINSPANS;\
        APPSPANS;\
        LENGTH;\
        DECKWIDTH;\
        DKSURFTYPE;\
        DKMEMBTYPE;\
        DKPROTECT;\
        MAIN_WS_THICKNESS;\
        APPR_DKSURFTYPE;\
        APPR_DKMEMBTYPE;\
        APPR_DKPROTECT;\
        APPR_WS_THICKNESS;\
        FED_FUND;\
        DECK_RECON_WORK_TYPE;\
        SUP_RECON_WORK_TYPE;\
        SUB_RECON_WORK_TYPE;\
        DEPT_MAIN_MATERIAL_TYPE;\
        DEPT_MAIN_PHYSICAL_TYPE;\
        DEPT_MAIN_SPAN_INTERACTION;\
        DEPT_MAIN_STRUC_CONFIG;\
        DEPT_APPR_MATERIAL_TYPE;\
        DEPT_APPR_PHYSICAL_TYPE;\
        DEPT_APPR_SPAN_INTERACTION;\
        DEPT_APPR_STRUC_CONFIG;\
        SUB_AGENCY;\
        MAINT_RESP_DESC;\
        CRIT_FACILITY;\
        APPR_PAVEMENT_WIDTH;\
        COVERED_BRIDGE;\
        FLOOD_INSP;\
        DEPT_DKSTRUCTYP;\
        BYPASSLEN;\
        AROADWIDTH;\
        ROADWIDTH;\
        MIN_OVER_VERT_CLEAR_RIGHT;\
        MIN_OVER_VERT_CLEAR_LEFT;\
        POST_LIMIT_WEIGHT;\
        POST_LIMIT_COMB;\
        INSPDATE;\
        BRINSPFREQ;\
        POST_STATUS;\
        NBI_RATING;\
        SUFF_RATE;\
        MAINT_DEF_RATE;\
        HBRR_ELIG;\
        JURIS;\
        SEG_END;\
        OFFSET_END;\
        SEG_PT_BGN;\
        SEG_PT_END;\
        SIDE_IND;\
        NLF_ID;\
        NLF_CNTL_BGN;\
        NLF_CNTL_END;\
        CUM_OFFSET_BGN;\
        CUM_OFFSET_END;\
        DKRATING;\
        SUPRATING;\
        SUBRATING;\
        CULVRATING;\
        STATE_LOCAL;\
        DECK_AREA;\
        BB_BRDGEID;\
        BB_PCT;\
        BRIDGEMED;\
        CUSTODIAN;\
        DESIGNAPPR;\
        DESIGNMAIN;\
        DKSTRUCTYP;\
        FIPS_STATE;\
        HCLRULT;\
        HCLRURT;\
        HISTSIGN;\
        IMPLEN;\
        LFTBRNAVCL;\
        LFTCURBSW;\
        MATERIALAPPR;\
        MATERIALMAIN;\
        MAXSPAN;\
        NAVCNTROL;\
        NAVHC;\
        NAVVC;\
        NBIIMPCOST;\
        NBIRWCOST;\
        NBISLEN;\
        NBITOTCOST;\
        NBIYRCOST;\
        NSTATECODE;\
        PARALSTRUC;\
        PLACECODE;\
        PROPWORK;\
        REFHUC;\
        REFVUC;\
        RTCURBSW;\
        SKEW;\
        STRFLARED;\
        STRUCT_NUM;\
        SUMLANES;\
        TEMPSTRUC;\
        VCLROVER;\
        ADTFUTURE;\
        ADTFUTYEAR;\
        ADTTOTAL;\
        ADTYEAR;\
        DEFHWY;\
        DIRSUFFIX;\
        FUNCCLASS;\
        HCLRINV;\
        KIND_HWY;\
        KMPOST;\
        LANES;\
        LEVL_SRVC;\
        NHS_IND;\
        ON_UNDER;\
        TOLLFAC;\
        TRAFFICDIR;\
        TRUCKPCT;\
        AENDRATING;\
        APPRALIGN;\
        ARAILRATIN;\
        CHANRATING;\
        DECKGEOM;\
        NEXTINSP;\
        PIERPROT;\
        RAILRATING;\
        SCOURCRIT;\
        STRRATING;\
        TRANSRATIN;\
        UNDERCLR;\
        WATERADEQ;\
        BUS_PLAN_NETWORK;\
        ROW_MODIFI;\
        ORIG_FID;\
        BRKEY;\
        DISTRICT_N;\
        SEG_BGN;\
        OFFSET_BGN;\
        SEG_LNGTH_;\
        SEQ_NO;\
        MAINT_FUNC;\
        POST_BOND_;\
        SPEED_LIMI;\
        FED_AID_SY;\
        FED_AID_UR;\
        FUNC_CLS;\
        FED_ID;\
        FED_AID__1;\
        MAPID;\
        RECORD_UPD;\
        FIPS_AREA_;\
        GEOMETRY_L;\
        Shape_Leng;\
        YCPC_GROUP")

        # Process: Delete Field
        arcpy.DeleteField_management(YEAR_MONTH_DAY_Bridges_BMS_State_Dssvl_shp, "BRKEY_1")

        # Process: Copy (3)
        arcpy.Copy_management(YEAR_MONTH_DAY_Bridges_BMS_State_Dssvl_shp, YEAR_MONTH_DAY_Bridges_BMS_STATE_shp, "")

        # Process: Copy (2)
        arcpy.Copy_management(YEAR_MONTH_DAY_Bridges_BMS_Local_shp, Bridges_BMS_Local_shp, "")

        # Process: Delete
        arcpy.Delete_management(Bridges_BMS_Local_Temp_shp, "ShapeFile")

        # Process: Copy
        arcpy.Copy_management(YEAR_MONTH_DAY_Bridges_BMS_STATE_shp, Bridges_BMS_State_shp, "")

        # Process: Delete (2)
        arcpy.Delete_management(Bridges_BMS_State_Temp_shp, "")

        message ("Starting RMS Traffic Steps")

        # Process: Project (5)
        arcpy.Project_management(RMSTRAFFIC, XRMSTRAFFIC_Project_shp, "PROJCS['NAD_1983_StatePlane_Pennsylvania_South_FIPS_3702_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',1968500.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-77.75],PARAMETER['Standard_Parallel_1',39.93333333333333],PARAMETER['Standard_Parallel_2',40.96666666666667],PARAMETER['Latitude_Of_Origin',39.33333333333334],UNIT['Foot_US',0.3048006096012192]]", "", "PROJCS['Pennsylvania Polyconic',GEOGCS['NAD 83',DATUM['NAD 83',SPHEROID['GRS 80',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Polyconic'],PARAMETER['Central_Meridian',-77.75],PARAMETER['Latitude_Of_Origin',40.925],UNIT['Meter',1.0]]")

        # Process: Clip (5)
        arcpy.Clip_analysis(XRMSTRAFFIC_Project_shp, County_Boundary, RMSTRAFFIC_shp, "")

        # Process: Make Feature Layer (13)
        arcpy.MakeFeatureLayer_management(RMSTRAFFIC_shp, RMSTRAFFIC_Layer, "", "", "FID FID VISIBLE NONE;\
        Shape Shape VISIBLE NONE;\
        RMSTRAFFIC RMSTRAFFIC VISIBLE NONE;\
        ST_RT_NO ST_RT_NO VISIBLE NONE;\
        CTY_CODE CTY_CODE VISIBLE NONE;\
        DISTRICT_N DISTRICT_N VISIBLE NONE;\
        JURIS JURIS VISIBLE NONE;\
        SEG_BGN SEG_BGN VISIBLE NONE;\
        OFFSET_BGN OFFSET_BGN VISIBLE NONE;\
        SEG_END SEG_END VISIBLE NONE;\
        OFFSET_END OFFSET_END VISIBLE NONE;\
        SEG_PT_BGN SEG_PT_BGN VISIBLE NONE;\
        SEG_PT_END SEG_PT_END VISIBLE NONE;\
        SEG_LNGTH_ SEG_LNGTH_ VISIBLE NONE;\
        SEQ_NO SEQ_NO VISIBLE NONE;\
        CUR_AADT CUR_AADT VISIBLE NONE;\
        ADTT_CUR ADTT_CUR VISIBLE NONE;\
        TRK_PCT TRK_PCT VISIBLE NONE;\
        WKDY_TRK_C WKDY_TRK_C VISIBLE NONE;\
        ADLR_TRK_C ADLR_TRK_C VISIBLE NONE;\
        ADLF_TRK_C ADLF_TRK_C VISIBLE NONE;\
        BASE_YR_CL BASE_YR_CL VISIBLE NONE;\
        BASE_ADT BASE_ADT VISIBLE NONE;\
        ADTT_BASE ADTT_BASE VISIBLE NONE;\
        WKDY_TRK_B WKDY_TRK_B VISIBLE NONE;\
        ADLR_TRK_B ADLR_TRK_B VISIBLE NONE;\
        ADLF_TRK_B ADLF_TRK_B VISIBLE NONE;\
        BASE_ADT_Y BASE_ADT_Y VISIBLE NONE;\
        DLY_VMT DLY_VMT VISIBLE NONE;\
        DLY_TRK_VM DLY_TRK_VM VISIBLE NONE;\
        K_FACTOR K_FACTOR VISIBLE NONE;\
        D_FACTOR D_FACTOR VISIBLE NONE;\
        T_FACTOR T_FACTOR VISIBLE NONE;\
        VOL_CNT_KE VOL_CNT_KE VISIBLE NONE;\
        VOL_CNT_DA VOL_CNT_DA VISIBLE NONE;\
        RAW_CNT_HI RAW_CNT_HI VISIBLE NONE;\
        TRAFF_PATT TRAFF_PATT VISIBLE NONE;\
        DUR_CLS_CN DUR_CLS_CN VISIBLE NONE;\
        TYPE_OF_CN TYPE_OF_CN VISIBLE NONE;\
        DIR_IND DIR_IND VISIBLE NONE;\
        MAPID MAPID VISIBLE NONE;\
        NLF_ID NLF_ID VISIBLE NONE;\
        SIDE_IND SIDE_IND VISIBLE NONE;\
        NLF_CNTL_B NLF_CNTL_B VISIBLE NONE;\
        NLF_CNTL_E NLF_CNTL_E VISIBLE NONE;\
        CUM_OFFSET CUM_OFFSET VISIBLE NONE;\
        CUM_OFFS_1 CUM_OFFS_1 VISIBLE NONE;\
        RECORD_UPD RECORD_UPD VISIBLE NONE;\
        GEOMETRY_L GEOMETRY_L VISIBLE NONE;\
        Shape_Leng Shape_Leng VISIBLE NONE;\
        Shape_le_1 Shape_le_1 VISIBLE NONE")

        # Process: Select Layer By Attribute (10)
        arcpy.SelectLayerByAttribute_management(RMSTRAFFIC_Layer, "NEW_SELECTION", "\"ST_RT_NO\" LIKE 'Q%' OR NOT \"CTY_CODE\" = '66'")

        # Process: Delete Rows (3)
        arcpy.DeleteRows_management(RMSTRAFFIC_Layer)

        # Process: Select (25)
        arcpy.Select_analysis(RMSTRAFFIC_Layer, YEAR_MONTH_DAY_RMSTRAFFIC_shp, "")

        # Process: Select (26)
        arcpy.Select_analysis(RMSADMIN_Layer, YEAR_MONTH_DAY_RMSADMIN_shp, "")

        message ("Starting RMS Steps")
        # Process: Project (4)
        arcpy.Project_management(RMSSEG, RMSSEG_Project, "PROJCS['NAD_1983_StatePlane_Pennsylvania_South_FIPS_3702_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',1968500.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-77.75],PARAMETER['Standard_Parallel_1',39.93333333333333],PARAMETER['Standard_Parallel_2',40.96666666666667],PARAMETER['Latitude_Of_Origin',39.33333333333334],UNIT['Foot_US',0.3048006096012192]]", "", "PROJCS['Pennsylvania Polyconic',GEOGCS['NAD 83',DATUM['NAD 83',SPHEROID['GRS 80',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Polyconic'],PARAMETER['Central_Meridian',-77.75],PARAMETER['Latitude_Of_Origin',40.925],UNIT['Meter',1.0]]")

        # Process: Clip (4)
        arcpy.Clip_analysis(RMSSEG_Project, County_Boundary, RMSSEG_temp_shp, "")

        # Process: Add Field
        arcpy.AddField_management(RMSSEG_temp_shp, "IRI_Group", "TEXT", "", "", "15", "", "NULLABLE", "NON_REQUIRED", "")

        # Process: Add Field
        #arcpy.AddField_management(RMSSEG_temp_shp, "IRI_Group", "TEXT", "", "", "15", "", "NON_NULLABLE", "NON_REQUIRED", "")

        # Process: Select
        arcpy.Select_analysis(RMSSEG_temp_shp, NHS_Interstate_shp, "\"INTERST_NETWRK_IND\" = 'Y'")

        # Process: Select (2)
        #arcpy.Select_analysis(NHS_Interstate_shp, NHS_Interstate_Exc_shp, "\"ROUGH_INDX\" >=  '1' AND \"ROUGH_INDX\" <= '69'")
        # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
        # The following inputs are layers or table views: "NHS_Interstate"
        arcpy.Select_analysis(NHS_Interstate_shp, NHS_Interstate_Exc_shp, "\"ROUGH_INDX\" >= 1 AND \"ROUGH_INDX\" <= 70")

        # Process: Calculate Field
        arcpy.CalculateField_management(NHS_Interstate_Exc_shp, "IRI_Group", "\"Excellent\"", "PYTHON", "")

        # Process: Select (9)
        arcpy.Select_analysis(NHS_Interstate_shp, NHS_Interstate_Fair_shp, "\"ROUGH_INDX\" >= 101 AND \"ROUGH_INDX\" <= 150")

        # Process: Calculate Field (2)
        arcpy.CalculateField_management(NHS_Interstate_Fair_shp, "IRI_Group", "\"Fair\"", "PYTHON", "")

        # Process: Select (7)
        arcpy.Select_analysis(NHS_Interstate_shp, NHS_Interstate_Poor_shp, "\"ROUGH_INDX\" >= 151")

        # Process: Calculate Field (3)
        arcpy.CalculateField_management(NHS_Interstate_Poor_shp, "IRI_Group", "\"Poor\"", "PYTHON", "")

        # Process: Select (8)
        arcpy.Select_analysis(NHS_Interstate_shp, NHS_Interstate_Good_shp, "\"ROUGH_INDX\" >= 71 AND \"ROUGH_INDX\" <= 100")

        # Process: Calculate Field (4)
        arcpy.CalculateField_management(NHS_Interstate_Good_shp, "IRI_Group", "\"Good\"", "PYTHON", "")

        message ("Starting Interstate Merge Step")
        # Process: Merge
        arcpy.Merge_management(""+transp_arch_temp+"\NHS_Interstate_Exc;\
        "+transp_arch_temp+"\NHS_Interstate_Fair;\
        "+transp_arch_temp+"\NHS_Interstate_Poor;\
        "+transp_arch_temp+"\NHS_Interstate_Good", NHS_Interstate_Merge_shp,\
         "ST_RT_NO \"ST_RT_NO\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,ST_RT_NO,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,ST_RT_NO,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,ST_RT_NO,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,ST_RT_NO,-1,-1;\
         CTY_CODE \"CTY_CODE\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,CTY_CODE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,CTY_CODE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,CTY_CODE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,CTY_CODE,-1,-1;\
         DISTRICT_NO \"DISTRICT_NO\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,DISTRICT_NO,-1,-1;\
         JURIS \"JURIS\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,JURIS,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,JURIS,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,JURIS,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,JURIS,-1,-1;\
         SEG_NO \"SEG_NO\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,SEG_NO,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,SEG_NO,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,SEG_NO,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,SEG_NO,-1,-1;\
         SEG_LNGTH_FEET \"SEG_LNGTH_FEET\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,SEG_LNGTH_FEET,-1,-1;\
         SEQ_NO \"SEQ_NO\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,SEQ_NO,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,SEQ_NO,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,SEQ_NO,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,SEQ_NO,-1,-1;\
         SUB_ROUTE \"SUB_ROUTE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,SUB_ROUTE,-1,-1;\
         YR_BUILT \"YR_BUILT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,YR_BUILT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,YR_BUILT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,YR_BUILT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,YR_BUILT,-1,-1;\
         YR_RESURF \"YR_RESURF\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,YR_RESURF,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,YR_RESURF,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,YR_RESURF,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,YR_RESURF,-1,-1;\
         DIR_IND \"DIR_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,DIR_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,DIR_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,DIR_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,DIR_IND,-1,-1;\
         FAC_TYPE \"FAC_TYPE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,FAC_TYPE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,FAC_TYPE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,FAC_TYPE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,FAC_TYPE,-1,-1;\
         TOTAL_WIDTH \"TOTAL_WIDTH\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,TOTAL_WIDTH,-1,-1;\
         SURF_TYPE \"SURF_TYPE\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,SURF_TYPE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,SURF_TYPE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,SURF_TYPE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,SURF_TYPE,-1,-1;\
         LANE_CNT \"LANE_CNT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,LANE_CNT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,LANE_CNT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,LANE_CNT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,LANE_CNT,-1,-1;\
         PARK_LANE \"PARK_LANE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,PARK_LANE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,PARK_LANE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,PARK_LANE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,PARK_LANE,-1,-1;\
         DIVSR_TYPE \"DIVSR_TYPE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,DIVSR_TYPE,-1,-1;\
         DIVSR_WIDTH \"DIVSR_WIDTH\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,DIVSR_WIDTH,-1,-1;\
         COND_DATE \"COND_DATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,COND_DATE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,COND_DATE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,COND_DATE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,COND_DATE,-1,-1;\
         ROUGH_INDX \"ROUGH_INDX\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,ROUGH_INDX,-1,-1;\
         FRICTN_COEFF \"FRICTN_COEFF\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,FRICTN_COEFF,-1,-1;\
         FRICTN_INDX \"FRICTN_INDX\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,FRICTN_INDX,-1,-1;\
         FRICTN_DATE \"FRICTN_DATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,FRICTN_DATE,-1,-1;\
         PVMNT_COND_RATE \"PVMNT_COND_RATE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,PVMNT_COND_RATE,-1,-1;\
         CUR_AADT \"CUR_AADT\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,CUR_AADT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,CUR_AADT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,CUR_AADT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,CUR_AADT,-1,-1;\
         ACCESS_CTRL \"ACCESS_CTRL\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,ACCESS_CTRL,-1,-1;\
         TOLL_CODE \"TOLL_CODE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,TOLL_CODE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,TOLL_CODE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,TOLL_CODE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,TOLL_CODE,-1,-1;\
         STREET_NAME \"STREET_NAME\" true true false 25 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,STREET_NAME,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,STREET_NAME,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,STREET_NAME,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,STREET_NAME,-1,-1;\
         TRAF_RT_NO_PREFIX \"TRAF_RT_NO_PREFIX\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,TRAF_RT_NO_PREFIX,-1,-1;\
         TRAF_RT_NO \"TRAF_RT_NO\" true true false 3 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,TRAF_RT_NO,-1,-1;\
         TRAF_RT_NO_SUF \"TRAF_RT_NO_SUF\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,TRAF_RT_NO_SUF,-1,-1;\
         BGN_DESC \"BGN_DESC\" true true false 20 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,BGN_DESC,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,BGN_DESC,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,BGN_DESC,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,BGN_DESC,-1,-1;\
         END_DESC \"END_DESC\" true true false 20 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,END_DESC,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,END_DESC,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,END_DESC,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,END_DESC,-1,-1;\
         MAINT_RESPON_IND \"MAINT_RESPON_IND\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,MAINT_RESPON_IND,-1,-1;\
         URBAN_RURAL \"URBAN_RURAL\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,URBAN_RURAL,-1,-1;\
         NHS_IND \"NHS_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,NHS_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,NHS_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,NHS_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,NHS_IND,-1,-1;\
         TANDEM_TRLR_TRK \"TANDEM_TRLR_TRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,TANDEM_TRLR_TRK,-1,-1;\
         ACCESS_TANDEM_TRLR \"ACCESS_TANDEM_TRLR\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,ACCESS_TANDEM_TRLR,-1,-1;\
         INTERST_NETWRK_IND \"INTERST_NETWRK_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,INTERST_NETWRK_IND,-1,-1;\
         NHPN_IND \"NHPN_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,NHPN_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,NHPN_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,NHPN_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,NHPN_IND,-1,-1;\
         NORM_ADMIN_BGN \"NORM_ADMIN_BGN\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,NORM_ADMIN_BGN,-1,-1;\
         NORM_TRAFF_BGN \"NORM_TRAFF_BGN\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,NORM_TRAFF_BGN,-1,-1;\
         NORM_SHLD_BGN \"NORM_SHLD_BGN\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,NORM_SHLD_BGN,-1,-1;\
         MAPID \"MAPID\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,MAPID,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,MAPID,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,MAPID,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,MAPID,-1,-1;\
         NLF_ID \"NLF_ID\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,NLF_ID,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,NLF_ID,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,NLF_ID,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,NLF_ID,-1,-1;\
         SIDE_IND \"SIDE_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,SIDE_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,SIDE_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,SIDE_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,SIDE_IND,-1,-1;\
         NLF_CNTL_BGN \"NLF_CNTL_BGN\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,NLF_CNTL_BGN,-1,-1;\
         NLF_CNTL_END \"NLF_CNTL_END\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,NLF_CNTL_END,-1,-1;\
         CUM_OFFSET_BGN_T1 \"CUM_OFFSET_BGN_T1\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,CUM_OFFSET_BGN_T1,-1,-1;\
         CUM_OFFSET_END_T1 \"CUM_OFFSET_END_T1\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,CUM_OFFSET_END_T1,-1,-1;\
         X_VALUE_BGN \"X_VALUE_BGN\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,X_VALUE_BGN,-1,-1;\
         Y_VALUE_BGN \"Y_VALUE_BGN\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,Y_VALUE_BGN,-1,-1;\
         X_VALUE_END \"X_VALUE_END\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,X_VALUE_END,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,X_VALUE_END,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,X_VALUE_END,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,X_VALUE_END,-1,-1;\
         Y_VALUE_END \"Y_VALUE_END\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,Y_VALUE_END,-1,-1;\
         GRAPHIC_LENGTH \"GRAPHIC_LENGTH\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,GRAPHIC_LENGTH,-1,-1;\
         KEY_UPDATE \"KEY_UPDATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,KEY_UPDATE,-1,-1;\
         ATTR_UPDATE \"ATTR_UPDATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,ATTR_UPDATE,-1,-1;\
         OVERALL_PVMNT_IDX \"OVERALL_PVMNT_IDX\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,OVERALL_PVMNT_IDX,-1,-1;\
         SEG_STATUS \"SEG_STATUS\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,SEG_STATUS,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,SEG_STATUS,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,SEG_STATUS,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,SEG_STATUS,-1,-1;\
         PAVMT_CYCLE \"PAVMT_CYCLE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,PAVMT_CYCLE,-1,-1;\
         DRAIN_CYCLE \"DRAIN_CYCLE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,DRAIN_CYCLE,-1,-1;\
         GDRAIL_CYCLE \"GDRAIL_CYCLE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,GDRAIL_CYCLE,-1,-1;\
         DISTRICT_SPECIAL \"DISTRICT_SPECIAL\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,DISTRICT_SPECIAL,-1,-1;\
         TRT_TYPE_NETWRK \"TRT_TYPE_NETWRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,TRT_TYPE_NETWRK,-1,-1;\
         PA_BYWAY_IND \"PA_BYWAY_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,PA_BYWAY_IND,-1,-1;\
         STREET_NAME2 \"STREET_NAME2\" true true false 25 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,STREET_NAME2,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,STREET_NAME2,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,STREET_NAME2,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,STREET_NAME2,-1,-1;\
         TRAF_RT_NO_PREFIX2 \"TRAF_RT_NO_PREFIX2\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,TRAF_RT_NO_PREFIX2,-1,-1;\
         TRAF_RT_NO2 \"TRAF_RT_NO2\" true true false 3 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,TRAF_RT_NO2,-1,-1;\
         TRAF_RT_NO_SUF2 \"TRAF_RT_NO_SUF2\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,TRAF_RT_NO_SUF2,-1,-1;\
         STREET_NAME3 \"STREET_NAME3\" true true false 25 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,STREET_NAME3,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,STREET_NAME3,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,STREET_NAME3,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,STREET_NAME3,-1,-1;\
         TRAF_RT_NO_PREFIX3 \"TRAF_RT_NO_PREFIX3\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,TRAF_RT_NO_PREFIX3,-1,-1;\
         TRAF_RT_NO3 \"TRAF_RT_NO3\" true true false 3 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,TRAF_RT_NO3,-1,-1;\
         TRAF_RT_NO_SUF3 \"TRAF_RT_NO_SUF3\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,TRAF_RT_NO_SUF3,-1,-1;\
         TRXN_FLAG \"TRXN_FLAG\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,TRXN_FLAG,-1,-1;\
         ROUTE_DIR \"ROUTE_DIR\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,ROUTE_DIR,-1,-1;\
         BUS_PLAN_NETWRK \"BUS_PLAN_NETWRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,BUS_PLAN_NETWRK,-1,-1;\
         EXP_WAY_NETWRK \"EXP_WAY_NETWRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,EXP_WAY_NETWRK,-1,-1;\
         HPMS_SAMP_CNT \"HPMS_SAMP_CNT\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,HPMS_SAMP_CNT,-1,-1;\
         MILE_POINT \"MILE_POINT\" true true false 5 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,MILE_POINT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,MILE_POINT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,MILE_POINT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,MILE_POINT,-1,-1;\
         IS_STRUCTURE \"IS_STRUCTURE\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,IS_STRUCTURE,-1,-1;\
         GOVT_LVL_CTRL \"GOVT_LVL_CTRL\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,GOVT_LVL_CTRL,-1,-1;\
         HOV_TYPE \"HOV_TYPE\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,HOV_TYPE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,HOV_TYPE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,HOV_TYPE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,HOV_TYPE,-1,-1;\
         HOV_LANES \"HOV_LANES\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,HOV_LANES,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,HOV_LANES,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,HOV_LANES,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,HOV_LANES,-1,-1;\
         PAR_SEG_IND \"PAR_SEG_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,PAR_SEG_IND,-1,-1;\
         HPMS_DIVSR_TYPE \"HPMS_DIVSR_TYPE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,HPMS_DIVSR_TYPE,-1,-1;\
         IRI_CUR_FLAG \"IRI_CUR_FLAG\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,IRI_CUR_FLAG,-1,-1;\
         DRAIN_SWT \"DRAIN_SWT\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,DRAIN_SWT,-1,-1;\
         GDRAIL_SWT \"GDRAIL_SWT\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,GDRAIL_SWT,-1,-1;\
         PAVMT_SWT \"PAVMT_SWT\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,PAVMT_SWT,-1,-1;\
         SHLD_COND_STATUS \"SHLD_COND_STATUS\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,SHLD_COND_STATUS,-1,-1;\
         FED_AID_PRIM_IND \"FED_AID_PRIM_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,FED_AID_PRIM_IND,-1,-1;\
         DRAIN_CNT \"DRAIN_CNT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,DRAIN_CNT,-1,-1;\
         GDRAIL_CNT \"GDRAIL_CNT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,GDRAIL_CNT,-1,-1;\
         PVMNT_TRTMT_DATA \"PVMNT_TRTMT_DATA\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,PVMNT_TRTMT_DATA,-1,-1;\
         PVMNT_IND \"PVMNT_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,PVMNT_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,PVMNT_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,PVMNT_IND,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,PVMNT_IND,-1,-1;\
         IRI_YEAR \"IRI_YEAR\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,IRI_YEAR,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,IRI_YEAR,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,IRI_YEAR,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,IRI_YEAR,-1,-1;\
         OPI_YEAR \"OPI_YEAR\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,OPI_YEAR,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,OPI_YEAR,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,OPI_YEAR,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,OPI_YEAR,-1,-1;\
         IRI_RATING_TEXT \"IRI_RATING_TEXT\" true true false 9 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,IRI_RATING_TEXT,-1,-1;\
         OPI_RATING_TEXT \"OPI_RATING_TEXT\" true true false 9 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,OPI_RATING_TEXT,-1,-1;\
         GEOMETRY_LEN \"GEOMETRY.LEN\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,GEOMETRY_LEN,-1,-1;\
         IRI_Group \"IRI_Group\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,IRI_Group,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,IRI_Group,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,IRI_Group,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,IRI_Group,-1,-1;\
         Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Exc,Shape_Length,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Fair,Shape_Length,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Good,Shape_Length,-1,-1,"+transp_arch_temp+"\NHS_Interstate_Poor,Shape_Length,-1,-1")


        # Process: Select (3)
        arcpy.Select_analysis(RMSSEG_temp_shp, NHS_NonInter_shp, "NOT \"NHS_IND\" = 'N' AND NOT \"INTERST_NETWRK_IND\" = 'Y'")

        # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
        # The following inputs are layers or table views: "NHS_NonInter"
        arcpy.MakeFeatureLayer_management(NHS_NonInter_shp, "NHS_NonInter_Layer", "ROUGH_INDX IS NULL", "", \
        "OBJECTID OBJECTID VISIBLE NONE;\
        Shape Shape VISIBLE NONE;\
        ST_RT_NO ST_RT_NO VISIBLE NONE;\
        CTY_CODE CTY_CODE VISIBLE NONE;\
        DISTRICT_NO DISTRICT_NO VISIBLE NONE;\
        JURIS JURIS VISIBLE NONE;\
        SEG_NO SEG_NO VISIBLE NONE;\
        SEG_LNGTH_FEET SEG_LNGTH_FEET VISIBLE NONE;\
        SEQ_NO SEQ_NO VISIBLE NONE;\
        SUB_ROUTE SUB_ROUTE VISIBLE NONE;\
        YR_BUILT YR_BUILT VISIBLE NONE;\
        YR_RESURF YR_RESURF VISIBLE NONE;\
        DIR_IND DIR_IND VISIBLE NONE;\
        FAC_TYPE FAC_TYPE VISIBLE NONE;\
        TOTAL_WIDTH TOTAL_WIDTH VISIBLE NONE;\
        SURF_TYPE SURF_TYPE VISIBLE NONE;\
        LANE_CNT LANE_CNT VISIBLE NONE;\
        PARK_LANE PARK_LANE VISIBLE NONE;\
        DIVSR_TYPE DIVSR_TYPE VISIBLE NONE;\
        DIVSR_WIDTH DIVSR_WIDTH VISIBLE NONE;\
        COND_DATE COND_DATE VISIBLE NONE;\
        ROUGH_INDX ROUGH_INDX VISIBLE NONE;\
        FRICTN_COEFF FRICTN_COEFF VISIBLE NONE;\
        FRICTN_INDX FRICTN_INDX VISIBLE NONE;\
        FRICTN_DATE FRICTN_DATE VISIBLE NONE;\
        PVMNT_COND_RATE PVMNT_COND_RATE VISIBLE NONE;\
        CUR_AADT CUR_AADT VISIBLE NONE;\
        ACCESS_CTRL ACCESS_CTRL VISIBLE NONE;\
        TOLL_CODE TOLL_CODE VISIBLE NONE;\
        STREET_NAME STREET_NAME VISIBLE NONE;\
        TRAF_RT_NO_PREFIX TRAF_RT_NO_PREFIX VISIBLE NONE;\
        TRAF_RT_NO TRAF_RT_NO VISIBLE NONE;\
        TRAF_RT_NO_SUF TRAF_RT_NO_SUF VISIBLE NONE;\
        BGN_DESC BGN_DESC VISIBLE NONE;\
        END_DESC END_DESC VISIBLE NONE;\
        MAINT_RESPON_IND MAINT_RESPON_IND VISIBLE NONE;\
        URBAN_RURAL URBAN_RURAL VISIBLE NONE;\
        NHS_IND NHS_IND VISIBLE NONE;\
        TANDEM_TRLR_TRK TANDEM_TRLR_TRK VISIBLE NONE;\
        ACCESS_TANDEM_TRLR ACCESS_TANDEM_TRLR VISIBLE NONE;\
        INTERST_NETWRK_IND INTERST_NETWRK_IND VISIBLE NONE;\
        NHPN_IND NHPN_IND VISIBLE NONE;\
        NORM_ADMIN_BGN NORM_ADMIN_BGN VISIBLE NONE;\
        NORM_TRAFF_BGN NORM_TRAFF_BGN VISIBLE NONE;\
        NORM_SHLD_BGN NORM_SHLD_BGN VISIBLE NONE;\
        MAPID MAPID VISIBLE NONE;\
        NLF_ID NLF_ID VISIBLE NONE;\
        SIDE_IND SIDE_IND VISIBLE NONE;\
        NLF_CNTL_BGN NLF_CNTL_BGN VISIBLE NONE;\
        NLF_CNTL_END NLF_CNTL_END VISIBLE NONE;\
        CUM_OFFSET_BGN_T1 CUM_OFFSET_BGN_T1 VISIBLE NONE;\
        CUM_OFFSET_END_T1 CUM_OFFSET_END_T1 VISIBLE NONE;\
        X_VALUE_BGN X_VALUE_BGN VISIBLE NONE;\
        Y_VALUE_BGN Y_VALUE_BGN VISIBLE NONE;\
        X_VALUE_END X_VALUE_END VISIBLE NONE;\
        Y_VALUE_END Y_VALUE_END VISIBLE NONE;\
        GRAPHIC_LENGTH GRAPHIC_LENGTH VISIBLE NONE;\
        KEY_UPDATE KEY_UPDATE VISIBLE NONE;\
        ATTR_UPDATE ATTR_UPDATE VISIBLE NONE;\
        OVERALL_PVMNT_IDX OVERALL_PVMNT_IDX VISIBLE NONE;\
        SEG_STATUS SEG_STATUS VISIBLE NONE;\
        PAVMT_CYCLE PAVMT_CYCLE VISIBLE NONE;\
        DRAIN_CYCLE DRAIN_CYCLE VISIBLE NONE;\
        GDRAIL_CYCLE GDRAIL_CYCLE VISIBLE NONE;\
        DISTRICT_SPECIAL DISTRICT_SPECIAL VISIBLE NONE;\
        TRT_TYPE_NETWRK TRT_TYPE_NETWRK VISIBLE NONE;\
        PA_BYWAY_IND PA_BYWAY_IND VISIBLE NONE;\
        STREET_NAME2 STREET_NAME2 VISIBLE NONE;\
        TRAF_RT_NO_PREFIX2 TRAF_RT_NO_PREFIX2 VISIBLE NONE;\
        TRAF_RT_NO2 TRAF_RT_NO2 VISIBLE NONE;\
        TRAF_RT_NO_SUF2 TRAF_RT_NO_SUF2 VISIBLE NONE;\
        STREET_NAME3 STREET_NAME3 VISIBLE NONE;\
        TRAF_RT_NO_PREFIX3 TRAF_RT_NO_PREFIX3 VISIBLE NONE;\
        TRAF_RT_NO3 TRAF_RT_NO3 VISIBLE NONE;\
        TRAF_RT_NO_SUF3 TRAF_RT_NO_SUF3 VISIBLE NONE;\
        TRXN_FLAG TRXN_FLAG VISIBLE NONE;\
        ROUTE_DIR ROUTE_DIR VISIBLE NONE;\
        BUS_PLAN_NETWRK BUS_PLAN_NETWRK VISIBLE NONE;\
        EXP_WAY_NETWRK EXP_WAY_NETWRK VISIBLE NONE;\
        HPMS_SAMP_CNT HPMS_SAMP_CNT VISIBLE NONE;\
        MILE_POINT MILE_POINT VISIBLE NONE;\
        IS_STRUCTURE IS_STRUCTURE VISIBLE NONE;\
        GOVT_LVL_CTRL GOVT_LVL_CTRL VISIBLE NONE;\
        HOV_TYPE HOV_TYPE VISIBLE NONE;\
        HOV_LANES HOV_LANES VISIBLE NONE;\
        PAR_SEG_IND PAR_SEG_IND VISIBLE NONE;\
        HPMS_DIVSR_TYPE HPMS_DIVSR_TYPE VISIBLE NONE;\
        IRI_CUR_FLAG IRI_CUR_FLAG VISIBLE NONE;\
        DRAIN_SWT DRAIN_SWT VISIBLE NONE;\
        GDRAIL_SWT GDRAIL_SWT VISIBLE NONE;\
        PAVMT_SWT PAVMT_SWT VISIBLE NONE;\
        SHLD_COND_STATUS SHLD_COND_STATUS VISIBLE NONE;\
        FED_AID_PRIM_IND FED_AID_PRIM_IND VISIBLE NONE;\
        DRAIN_CNT DRAIN_CNT VISIBLE NONE;\
        GDRAIL_CNT GDRAIL_CNT VISIBLE NONE;\
        PVMNT_TRTMT_DATA PVMNT_TRTMT_DATA VISIBLE NONE;\
        PVMNT_IND PVMNT_IND VISIBLE NONE;\
        IRI_YEAR IRI_YEAR VISIBLE NONE;OPI_YEAR OPI_YEAR VISIBLE NONE;\
        IRI_RATING_TEXT IRI_RATING_TEXT VISIBLE NONE;\
        OPI_RATING_TEXT OPI_RATING_TEXT VISIBLE NONE;\
        GEOMETRY_LEN GEOMETRY_LEN VISIBLE NONE;\
        IRI_Group IRI_Group VISIBLE NONE;\
        Shape_Length Shape_Length VISIBLE NONE")

        # Process: Calculate Field (5)
        arcpy.CalculateField_management("NHS_NonInter_Layer", "ROUGH_INDX", "0", "PYTHON", "")

        # Process: Select (10)
        arcpy.Select_analysis(NHS_NonInter_shp, NHS_NonInter_Exc_shp, "\"ROUGH_INDX\" >= 1 AND \"ROUGH_INDX\" <= 75")

        # Process: Calculate Field (5)
        arcpy.CalculateField_management(NHS_NonInter_Exc_shp, "IRI_Group", "\"Excellent\"", "PYTHON", "")

        # Process: Select (12)
        arcpy.Select_analysis(NHS_NonInter_shp, NHS_NonInter_Fair_shp, "\"ROUGH_INDX\" >= 121 AND \"ROUGH_INDX\" <= 170")

        # Process: Calculate Field (6)
        arcpy.CalculateField_management(NHS_NonInter_Fair_shp, "IRI_Group", "\"Fair\"", "PYTHON", "")

        # Process: Select (13)
        arcpy.Select_analysis(NHS_NonInter_shp, NHS_NonInter_Poor_shp, "\"ROUGH_INDX\" >= 171 OR \"ROUGH_INDX\" = 0")

        # Process: Calculate Field (7)
        arcpy.CalculateField_management(NHS_NonInter_Poor_shp, "IRI_Group", "\"Poor\"", "PYTHON", "")

        # Process: Select (11)
        arcpy.Select_analysis(NHS_NonInter_shp, NHS_NonInter_Good_shp, "\"ROUGH_INDX\" > 75 AND \"ROUGH_INDX\" <= 120")

        # Process: Calculate Field (8)
        arcpy.CalculateField_management(NHS_NonInter_Good_shp, "IRI_Group", "\"Good\"", "PYTHON", "")

        # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
        # The following inputs are layers or table views: "NHS_NonInter"
        arcpy.MakeFeatureLayer_management(NHS_NonInter_Poor_shp, "NHS_NonInter_Layer2", "", "", \
        "OBJECTID OBJECTID VISIBLE NONE;\
        Shape Shape VISIBLE NONE;\
        ST_RT_NO ST_RT_NO VISIBLE NONE;\
        CTY_CODE CTY_CODE VISIBLE NONE;\
        DISTRICT_NO DISTRICT_NO VISIBLE NONE;\
        JURIS JURIS VISIBLE NONE;\
        SEG_NO SEG_NO VISIBLE NONE;\
        SEG_LNGTH_FEET SEG_LNGTH_FEET VISIBLE NONE;\
        SEQ_NO SEQ_NO VISIBLE NONE;\
        SUB_ROUTE SUB_ROUTE VISIBLE NONE;\
        YR_BUILT YR_BUILT VISIBLE NONE;\
        YR_RESURF YR_RESURF VISIBLE NONE;\
        DIR_IND DIR_IND VISIBLE NONE;\
        FAC_TYPE FAC_TYPE VISIBLE NONE;\
        TOTAL_WIDTH TOTAL_WIDTH VISIBLE NONE;\
        SURF_TYPE SURF_TYPE VISIBLE NONE;\
        LANE_CNT LANE_CNT VISIBLE NONE;\
        PARK_LANE PARK_LANE VISIBLE NONE;\
        DIVSR_TYPE DIVSR_TYPE VISIBLE NONE;\
        DIVSR_WIDTH DIVSR_WIDTH VISIBLE NONE;\
        COND_DATE COND_DATE VISIBLE NONE;\
        ROUGH_INDX ROUGH_INDX VISIBLE NONE;\
        FRICTN_COEFF FRICTN_COEFF VISIBLE NONE;\
        FRICTN_INDX FRICTN_INDX VISIBLE NONE;\
        FRICTN_DATE FRICTN_DATE VISIBLE NONE;\
        PVMNT_COND_RATE PVMNT_COND_RATE VISIBLE NONE;\
        CUR_AADT CUR_AADT VISIBLE NONE;\
        ACCESS_CTRL ACCESS_CTRL VISIBLE NONE;\
        TOLL_CODE TOLL_CODE VISIBLE NONE;\
        STREET_NAME STREET_NAME VISIBLE NONE;\
        TRAF_RT_NO_PREFIX TRAF_RT_NO_PREFIX VISIBLE NONE;\
        TRAF_RT_NO TRAF_RT_NO VISIBLE NONE;\
        TRAF_RT_NO_SUF TRAF_RT_NO_SUF VISIBLE NONE;\
        BGN_DESC BGN_DESC VISIBLE NONE;\
        END_DESC END_DESC VISIBLE NONE;\
        MAINT_RESPON_IND MAINT_RESPON_IND VISIBLE NONE;\
        URBAN_RURAL URBAN_RURAL VISIBLE NONE;\
        NHS_IND NHS_IND VISIBLE NONE;\
        TANDEM_TRLR_TRK TANDEM_TRLR_TRK VISIBLE NONE;\
        ACCESS_TANDEM_TRLR ACCESS_TANDEM_TRLR VISIBLE NONE;\
        INTERST_NETWRK_IND INTERST_NETWRK_IND VISIBLE NONE;\
        NHPN_IND NHPN_IND VISIBLE NONE;\
        NORM_ADMIN_BGN NORM_ADMIN_BGN VISIBLE NONE;\
        NORM_TRAFF_BGN NORM_TRAFF_BGN VISIBLE NONE;\
        NORM_SHLD_BGN NORM_SHLD_BGN VISIBLE NONE;\
        MAPID MAPID VISIBLE NONE;\
        NLF_ID NLF_ID VISIBLE NONE;\
        SIDE_IND SIDE_IND VISIBLE NONE;\
        NLF_CNTL_BGN NLF_CNTL_BGN VISIBLE NONE;\
        NLF_CNTL_END NLF_CNTL_END VISIBLE NONE;\
        CUM_OFFSET_BGN_T1 CUM_OFFSET_BGN_T1 VISIBLE NONE;\
        CUM_OFFSET_END_T1 CUM_OFFSET_END_T1 VISIBLE NONE;\
        X_VALUE_BGN X_VALUE_BGN VISIBLE NONE;\
        Y_VALUE_BGN Y_VALUE_BGN VISIBLE NONE;\
        X_VALUE_END X_VALUE_END VISIBLE NONE;\
        Y_VALUE_END Y_VALUE_END VISIBLE NONE;\
        GRAPHIC_LENGTH GRAPHIC_LENGTH VISIBLE NONE;\
        KEY_UPDATE KEY_UPDATE VISIBLE NONE;\
        ATTR_UPDATE ATTR_UPDATE VISIBLE NONE;\
        OVERALL_PVMNT_IDX OVERALL_PVMNT_IDX VISIBLE NONE;\
        SEG_STATUS SEG_STATUS VISIBLE NONE;\
        PAVMT_CYCLE PAVMT_CYCLE VISIBLE NONE;\
        DRAIN_CYCLE DRAIN_CYCLE VISIBLE NONE;\
        GDRAIL_CYCLE GDRAIL_CYCLE VISIBLE NONE;\
        DISTRICT_SPECIAL DISTRICT_SPECIAL VISIBLE NONE;\
        TRT_TYPE_NETWRK TRT_TYPE_NETWRK VISIBLE NONE;\
        PA_BYWAY_IND PA_BYWAY_IND VISIBLE NONE;\
        STREET_NAME2 STREET_NAME2 VISIBLE NONE;\
        TRAF_RT_NO_PREFIX2 TRAF_RT_NO_PREFIX2 VISIBLE NONE;\
        TRAF_RT_NO2 TRAF_RT_NO2 VISIBLE NONE;\
        TRAF_RT_NO_SUF2 TRAF_RT_NO_SUF2 VISIBLE NONE;\
        STREET_NAME3 STREET_NAME3 VISIBLE NONE;\
        TRAF_RT_NO_PREFIX3 TRAF_RT_NO_PREFIX3 VISIBLE NONE;\
        TRAF_RT_NO3 TRAF_RT_NO3 VISIBLE NONE;\
        TRAF_RT_NO_SUF3 TRAF_RT_NO_SUF3 VISIBLE NONE;\
        TRXN_FLAG TRXN_FLAG VISIBLE NONE;\
        ROUTE_DIR ROUTE_DIR VISIBLE NONE;\
        BUS_PLAN_NETWRK BUS_PLAN_NETWRK VISIBLE NONE;\
        EXP_WAY_NETWRK EXP_WAY_NETWRK VISIBLE NONE;\
        HPMS_SAMP_CNT HPMS_SAMP_CNT VISIBLE NONE;\
        MILE_POINT MILE_POINT VISIBLE NONE;\
        IS_STRUCTURE IS_STRUCTURE VISIBLE NONE;\
        GOVT_LVL_CTRL GOVT_LVL_CTRL VISIBLE NONE;\
        HOV_TYPE HOV_TYPE VISIBLE NONE;\
        HOV_LANES HOV_LANES VISIBLE NONE;\
        PAR_SEG_IND PAR_SEG_IND VISIBLE NONE;\
        HPMS_DIVSR_TYPE HPMS_DIVSR_TYPE VISIBLE NONE;\
        IRI_CUR_FLAG IRI_CUR_FLAG VISIBLE NONE;\
        DRAIN_SWT DRAIN_SWT VISIBLE NONE;\
        GDRAIL_SWT GDRAIL_SWT VISIBLE NONE;\
        PAVMT_SWT PAVMT_SWT VISIBLE NONE;\
        SHLD_COND_STATUS SHLD_COND_STATUS VISIBLE NONE;\
        FED_AID_PRIM_IND FED_AID_PRIM_IND VISIBLE NONE;\
        DRAIN_CNT DRAIN_CNT VISIBLE NONE;\
        GDRAIL_CNT GDRAIL_CNT VISIBLE NONE;\
        PVMNT_TRTMT_DATA PVMNT_TRTMT_DATA VISIBLE NONE;\
        PVMNT_IND PVMNT_IND VISIBLE NONE;\
        IRI_YEAR IRI_YEAR VISIBLE NONE;OPI_YEAR OPI_YEAR VISIBLE NONE;\
        IRI_RATING_TEXT IRI_RATING_TEXT VISIBLE NONE;\
        OPI_RATING_TEXT OPI_RATING_TEXT VISIBLE NONE;\
        GEOMETRY_LEN GEOMETRY_LEN VISIBLE NONE;\
        IRI_Group IRI_Group VISIBLE NONE;\
        Shape_Length Shape_Length VISIBLE NONE")

        # Process: Select Layer By Attribute (9)
        arcpy.SelectLayerByAttribute_management("NHS_NonInter_Layer2", "NEW_SELECTION", "\"ROUGH_INDX\" = 0")

        # Process: Calculate Field (5)
        arcpy.CalculateField_management("NHS_NonInter_Layer2", "IRI_Group", "\"NO DATA\"", "PYTHON", "")

        message ("Starting NonInter Merge Steps")
        # Process: Merge (2)
        arcpy.Merge_management(""+transp_arch_temp+"\NHS_NonInter_Exc;\
        "+transp_arch_temp+"\NHS_NonInter_Fair;\
        "+transp_arch_temp+"\NHS_NonInter_Poor;\
        "+transp_arch_temp+"\NHS_NonInter_Good", NHS_NonInter_Merge_shp,\
         "ST_RT_NO \"ST_RT_NO\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,ST_RT_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,ST_RT_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,ST_RT_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,ST_RT_NO,-1,-1;\
         CTY_CODE \"CTY_CODE\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,CTY_CODE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,CTY_CODE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,CTY_CODE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,CTY_CODE,-1,-1;\
         DISTRICT_NO \"DISTRICT_NO\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,DISTRICT_NO,-1,-1;\
         JURIS \"JURIS\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,JURIS,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,JURIS,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,JURIS,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,JURIS,-1,-1;\
         SEG_NO \"SEG_NO\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,SEG_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,SEG_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,SEG_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,SEG_NO,-1,-1;\
         SEG_LNGTH_FEET \"SEG_LNGTH_FEET\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,SEG_LNGTH_FEET,-1,-1;\
         SEQ_NO \"SEQ_NO\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,SEQ_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,SEQ_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,SEQ_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,SEQ_NO,-1,-1;\
         SUB_ROUTE \"SUB_ROUTE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,SUB_ROUTE,-1,-1;\
         YR_BUILT \"YR_BUILT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,YR_BUILT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,YR_BUILT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,YR_BUILT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,YR_BUILT,-1,-1;\
         YR_RESURF \"YR_RESURF\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,YR_RESURF,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,YR_RESURF,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,YR_RESURF,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,YR_RESURF,-1,-1;\
         DIR_IND \"DIR_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,DIR_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,DIR_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,DIR_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,DIR_IND,-1,-1;\
         FAC_TYPE \"FAC_TYPE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,FAC_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,FAC_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,FAC_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,FAC_TYPE,-1,-1;\
         TOTAL_WIDTH \"TOTAL_WIDTH\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,TOTAL_WIDTH,-1,-1;\
         SURF_TYPE \"SURF_TYPE\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,SURF_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,SURF_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,SURF_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,SURF_TYPE,-1,-1;\
         LANE_CNT \"LANE_CNT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,LANE_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,LANE_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,LANE_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,LANE_CNT,-1,-1;\
         PARK_LANE \"PARK_LANE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,PARK_LANE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,PARK_LANE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,PARK_LANE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,PARK_LANE,-1,-1;\
         DIVSR_TYPE \"DIVSR_TYPE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,DIVSR_TYPE,-1,-1;\
         DIVSR_WIDTH \"DIVSR_WIDTH\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,DIVSR_WIDTH,-1,-1;\
         COND_DATE \"COND_DATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,COND_DATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,COND_DATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,COND_DATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,COND_DATE,-1,-1;\
         ROUGH_INDX \"ROUGH_INDX\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,ROUGH_INDX,-1,-1;\
         FRICTN_COEFF \"FRICTN_COEFF\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,FRICTN_COEFF,-1,-1;\
         FRICTN_INDX \"FRICTN_INDX\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,FRICTN_INDX,-1,-1;\
         FRICTN_DATE \"FRICTN_DATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,FRICTN_DATE,-1,-1;\
         PVMNT_COND_RATE \"PVMNT_COND_RATE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,PVMNT_COND_RATE,-1,-1;\
         CUR_AADT \"CUR_AADT\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,CUR_AADT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,CUR_AADT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,CUR_AADT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,CUR_AADT,-1,-1;\
         ACCESS_CTRL \"ACCESS_CTRL\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,ACCESS_CTRL,-1,-1;\
         TOLL_CODE \"TOLL_CODE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,TOLL_CODE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,TOLL_CODE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,TOLL_CODE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,TOLL_CODE,-1,-1;\
         STREET_NAME \"STREET_NAME\" true true false 25 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,STREET_NAME,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,STREET_NAME,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,STREET_NAME,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,STREET_NAME,-1,-1;\
         TRAF_RT_NO_PREFIX \"TRAF_RT_NO_PREFIX\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,TRAF_RT_NO_PREFIX,-1,-1;\
         TRAF_RT_NO \"TRAF_RT_NO\" true true false 3 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,TRAF_RT_NO,-1,-1;\
         TRAF_RT_NO_SUF \"TRAF_RT_NO_SUF\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,TRAF_RT_NO_SUF,-1,-1;\
         BGN_DESC \"BGN_DESC\" true true false 20 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,BGN_DESC,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,BGN_DESC,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,BGN_DESC,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,BGN_DESC,-1,-1;\
         END_DESC \"END_DESC\" true true false 20 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,END_DESC,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,END_DESC,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,END_DESC,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,END_DESC,-1,-1;\
         MAINT_RESPON_IND \"MAINT_RESPON_IND\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,MAINT_RESPON_IND,-1,-1;\
         URBAN_RURAL \"URBAN_RURAL\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,URBAN_RURAL,-1,-1;\
         NHS_IND \"NHS_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,NHS_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,NHS_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,NHS_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,NHS_IND,-1,-1;\
         TANDEM_TRLR_TRK \"TANDEM_TRLR_TRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,TANDEM_TRLR_TRK,-1,-1;\
         ACCESS_TANDEM_TRLR \"ACCESS_TANDEM_TRLR\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,ACCESS_TANDEM_TRLR,-1,-1;\
         INTERST_NETWRK_IND \"INTERST_NETWRK_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,INTERST_NETWRK_IND,-1,-1;\
         NHPN_IND \"NHPN_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,NHPN_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,NHPN_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,NHPN_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,NHPN_IND,-1,-1;\
         NORM_ADMIN_BGN \"NORM_ADMIN_BGN\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,NORM_ADMIN_BGN,-1,-1;\
         NORM_TRAFF_BGN \"NORM_TRAFF_BGN\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,NORM_TRAFF_BGN,-1,-1;\
         NORM_SHLD_BGN \"NORM_SHLD_BGN\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,NORM_SHLD_BGN,-1,-1;\
         MAPID \"MAPID\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,MAPID,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,MAPID,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,MAPID,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,MAPID,-1,-1;\
         NLF_ID \"NLF_ID\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,NLF_ID,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,NLF_ID,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,NLF_ID,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,NLF_ID,-1,-1;\
         SIDE_IND \"SIDE_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,SIDE_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,SIDE_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,SIDE_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,SIDE_IND,-1,-1;\
         NLF_CNTL_BGN \"NLF_CNTL_BGN\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,NLF_CNTL_BGN,-1,-1;\
         NLF_CNTL_END \"NLF_CNTL_END\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,NLF_CNTL_END,-1,-1;\
         CUM_OFFSET_BGN_T1 \"CUM_OFFSET_BGN_T1\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,CUM_OFFSET_BGN_T1,-1,-1;\
         CUM_OFFSET_END_T1 \"CUM_OFFSET_END_T1\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,CUM_OFFSET_END_T1,-1,-1;\
         X_VALUE_BGN \"X_VALUE_BGN\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,X_VALUE_BGN,-1,-1;\
         Y_VALUE_BGN \"Y_VALUE_BGN\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,Y_VALUE_BGN,-1,-1;\
         X_VALUE_END \"X_VALUE_END\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,X_VALUE_END,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,X_VALUE_END,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,X_VALUE_END,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,X_VALUE_END,-1,-1;\
         Y_VALUE_END \"Y_VALUE_END\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,Y_VALUE_END,-1,-1;\
         GRAPHIC_LENGTH \"GRAPHIC_LENGTH\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,GRAPHIC_LENGTH,-1,-1;\
         KEY_UPDATE \"KEY_UPDATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,KEY_UPDATE,-1,-1;\
         ATTR_UPDATE \"ATTR_UPDATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,ATTR_UPDATE,-1,-1;\
         OVERALL_PVMNT_IDX \"OVERALL_PVMNT_IDX\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,OVERALL_PVMNT_IDX,-1,-1;\
         SEG_STATUS \"SEG_STATUS\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,SEG_STATUS,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,SEG_STATUS,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,SEG_STATUS,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,SEG_STATUS,-1,-1;\
         PAVMT_CYCLE \"PAVMT_CYCLE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,PAVMT_CYCLE,-1,-1;\
         DRAIN_CYCLE \"DRAIN_CYCLE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,DRAIN_CYCLE,-1,-1;\
         GDRAIL_CYCLE \"GDRAIL_CYCLE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,GDRAIL_CYCLE,-1,-1;\
         DISTRICT_SPECIAL \"DISTRICT_SPECIAL\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,DISTRICT_SPECIAL,-1,-1;\
         TRT_TYPE_NETWRK \"TRT_TYPE_NETWRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,TRT_TYPE_NETWRK,-1,-1;\
         PA_BYWAY_IND \"PA_BYWAY_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,PA_BYWAY_IND,-1,-1;\
         STREET_NAME2 \"STREET_NAME2\" true true false 25 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,STREET_NAME2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,STREET_NAME2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,STREET_NAME2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,STREET_NAME2,-1,-1;\
         TRAF_RT_NO_PREFIX2 \"TRAF_RT_NO_PREFIX2\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,TRAF_RT_NO_PREFIX2,-1,-1;\
         TRAF_RT_NO2 \"TRAF_RT_NO2\" true true false 3 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,TRAF_RT_NO2,-1,-1;\
         TRAF_RT_NO_SUF2 \"TRAF_RT_NO_SUF2\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,TRAF_RT_NO_SUF2,-1,-1;\
         STREET_NAME3 \"STREET_NAME3\" true true false 25 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,STREET_NAME3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,STREET_NAME3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,STREET_NAME3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,STREET_NAME3,-1,-1;\
         TRAF_RT_NO_PREFIX3 \"TRAF_RT_NO_PREFIX3\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,TRAF_RT_NO_PREFIX3,-1,-1;\
         TRAF_RT_NO3 \"TRAF_RT_NO3\" true true false 3 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,TRAF_RT_NO3,-1,-1;\
         TRAF_RT_NO_SUF3 \"TRAF_RT_NO_SUF3\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,TRAF_RT_NO_SUF3,-1,-1;\
         TRXN_FLAG \"TRXN_FLAG\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,TRXN_FLAG,-1,-1;\
         ROUTE_DIR \"ROUTE_DIR\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,ROUTE_DIR,-1,-1;\
         BUS_PLAN_NETWRK \"BUS_PLAN_NETWRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,BUS_PLAN_NETWRK,-1,-1;\
         EXP_WAY_NETWRK \"EXP_WAY_NETWRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,EXP_WAY_NETWRK,-1,-1;\
         HPMS_SAMP_CNT \"HPMS_SAMP_CNT\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,HPMS_SAMP_CNT,-1,-1;\
         MILE_POINT \"MILE_POINT\" true true false 5 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,MILE_POINT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,MILE_POINT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,MILE_POINT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,MILE_POINT,-1,-1;\
         IS_STRUCTURE \"IS_STRUCTURE\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,IS_STRUCTURE,-1,-1;\
         GOVT_LVL_CTRL \"GOVT_LVL_CTRL\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,GOVT_LVL_CTRL,-1,-1;\
         HOV_TYPE \"HOV_TYPE\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,HOV_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,HOV_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,HOV_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,HOV_TYPE,-1,-1;\
         HOV_LANES \"HOV_LANES\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,HOV_LANES,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,HOV_LANES,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,HOV_LANES,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,HOV_LANES,-1,-1;\
         PAR_SEG_IND \"PAR_SEG_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,PAR_SEG_IND,-1,-1;\
         HPMS_DIVSR_TYPE \"HPMS_DIVSR_TYPE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,HPMS_DIVSR_TYPE,-1,-1;\
         IRI_CUR_FLAG \"IRI_CUR_FLAG\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,IRI_CUR_FLAG,-1,-1;\
         DRAIN_SWT \"DRAIN_SWT\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,DRAIN_SWT,-1,-1;\
         GDRAIL_SWT \"GDRAIL_SWT\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,GDRAIL_SWT,-1,-1;\
         PAVMT_SWT \"PAVMT_SWT\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,PAVMT_SWT,-1,-1;\
         SHLD_COND_STATUS \"SHLD_COND_STATUS\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,SHLD_COND_STATUS,-1,-1;\
         FED_AID_PRIM_IND \"FED_AID_PRIM_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,FED_AID_PRIM_IND,-1,-1;\
         DRAIN_CNT \"DRAIN_CNT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,DRAIN_CNT,-1,-1;\
         GDRAIL_CNT \"GDRAIL_CNT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,GDRAIL_CNT,-1,-1;\
         PVMNT_TRTMT_DATA \"PVMNT_TRTMT_DATA\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,PVMNT_TRTMT_DATA,-1,-1;\
         PVMNT_IND \"PVMNT_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,PVMNT_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,PVMNT_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,PVMNT_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,PVMNT_IND,-1,-1;\
         IRI_YEAR \"IRI_YEAR\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,IRI_YEAR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,IRI_YEAR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,IRI_YEAR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,IRI_YEAR,-1,-1;\
         OPI_YEAR \"OPI_YEAR\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,OPI_YEAR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,OPI_YEAR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,OPI_YEAR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,OPI_YEAR,-1,-1;\
         IRI_RATING_TEXT \"IRI_RATING_TEXT\" true true false 9 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,IRI_RATING_TEXT,-1,-1;\
         OPI_RATING_TEXT \"OPI_RATING_TEXT\" true true false 9 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,OPI_RATING_TEXT,-1,-1;\
         GEOMETRY_LEN \"GEOMETRY.LEN\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,GEOMETRY_LEN,-1,-1;\
         IRI_Group \"IRI_Group\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,IRI_Group,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,IRI_Group,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,IRI_Group,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,IRI_Group,-1,-1;\
         Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_NonInter_Exc,Shape_Length,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Fair,Shape_Length,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Good,Shape_Length,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Poor,Shape_Length,-1,-1")

        # Process: Select (6)
        arcpy.Select_analysis(RMSSEG_temp_shp, No_Data_shp, "\"ROUGH_INDX\" = 0")

        # Process: Calculate Field (17)
        arcpy.CalculateField_management(No_Data_shp, "IRI_Group", "\"\"", "PYTHON", "")

        # Process: Select (4)
        arcpy.Select_analysis(RMSSEG_temp_shp, NonNHSGreater2000_shp, "\"NHS_IND\" = 'N' AND \"CUR_AADT\" >= 2000")

        # Process: Select (14)
        arcpy.Select_analysis(NonNHSGreater2000_shp, NonNHSGreater2000_Exc_shp, "\"ROUGH_INDX\" >= 1 AND \"ROUGH_INDX\" <= 100")

        # Process: Calculate Field (9)
        arcpy.CalculateField_management(NonNHSGreater2000_Exc_shp, "IRI_Group", "\"Excellent\"", "PYTHON", "")

        # Process: Select (16)
        arcpy.Select_analysis(NonNHSGreater2000_shp, NonNHSGreater2000_Fair_shp, "\"ROUGH_INDX\" >= 151 AND \"ROUGH_INDX\" <= 195")

        # Process: Calculate Field (10)
        arcpy.CalculateField_management(NonNHSGreater2000_Fair_shp, "IRI_Group", "\"Fair\"", "PYTHON", "")

        # Process: Select (17)
        arcpy.Select_analysis(NonNHSGreater2000_shp, NonNHSGreater2000_Poor_shp, "\"ROUGH_INDX\" >= 196")

        # Process: Calculate Field (11)
        arcpy.CalculateField_management(NonNHSGreater2000_Poor_shp, "IRI_Group", "\"Poor\"", "PYTHON", "")

        # Process: Select (15)
        arcpy.Select_analysis(NonNHSGreater2000_shp, NonNHSGreater2000_Good_shp, "\"ROUGH_INDX\" > 100 AND \"ROUGH_INDX\" <= 150")

        # Process: Calculate Field (12)
        arcpy.CalculateField_management(NonNHSGreater2000_Good_shp, "IRI_Group", "\"Good\"", "PYTHON", "")

        message ("Starting NonNHSGreater2000 Merge Step")
        # Process: Merge (3)
        arcpy.Merge_management(""+transp_arch_temp+"\NonNHSGreater2000_Exc;\
        "+transp_arch_temp+"\NonNHSGreater2000_Fair;\
        "+transp_arch_temp+"\NonNHSGreater2000_Poor;\
        "+transp_arch_temp+"\NonNHSGreater2000_Good", NonNHSGreater2000_Merge_shp,\
          "ST_RT_NO \"ST_RT_NO\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,ST_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,ST_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,ST_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,ST_RT_NO,-1,-1;\
         CTY_CODE \"CTY_CODE\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,CTY_CODE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,CTY_CODE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,CTY_CODE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,CTY_CODE,-1,-1;\
         DISTRICT_NO \"DISTRICT_NO\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,DISTRICT_NO,-1,-1;\
         JURIS \"JURIS\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,JURIS,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,JURIS,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,JURIS,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,JURIS,-1,-1;\
         SEG_NO \"SEG_NO\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,SEG_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,SEG_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,SEG_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,SEG_NO,-1,-1;\
         SEG_LNGTH_FEET \"SEG_LNGTH_FEET\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,SEG_LNGTH_FEET,-1,-1;\
         SEQ_NO \"SEQ_NO\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,SEQ_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,SEQ_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,SEQ_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,SEQ_NO,-1,-1;\
         SUB_ROUTE \"SUB_ROUTE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,SUB_ROUTE,-1,-1;\
         YR_BUILT \"YR_BUILT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,YR_BUILT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,YR_BUILT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,YR_BUILT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,YR_BUILT,-1,-1;\
         YR_RESURF \"YR_RESURF\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,YR_RESURF,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,YR_RESURF,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,YR_RESURF,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,YR_RESURF,-1,-1;\
         DIR_IND \"DIR_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,DIR_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,DIR_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,DIR_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,DIR_IND,-1,-1;\
         FAC_TYPE \"FAC_TYPE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,FAC_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,FAC_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,FAC_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,FAC_TYPE,-1,-1;\
         TOTAL_WIDTH \"TOTAL_WIDTH\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,TOTAL_WIDTH,-1,-1;\
         SURF_TYPE \"SURF_TYPE\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,SURF_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,SURF_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,SURF_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,SURF_TYPE,-1,-1;\
         LANE_CNT \"LANE_CNT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,LANE_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,LANE_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,LANE_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,LANE_CNT,-1,-1;\
         PARK_LANE \"PARK_LANE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,PARK_LANE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,PARK_LANE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,PARK_LANE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,PARK_LANE,-1,-1;\
         DIVSR_TYPE \"DIVSR_TYPE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,DIVSR_TYPE,-1,-1;\
         DIVSR_WIDTH \"DIVSR_WIDTH\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,DIVSR_WIDTH,-1,-1;\
         COND_DATE \"COND_DATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,COND_DATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,COND_DATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,COND_DATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,COND_DATE,-1,-1;\
         ROUGH_INDX \"ROUGH_INDX\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,ROUGH_INDX,-1,-1;\
         FRICTN_COEFF \"FRICTN_COEFF\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,FRICTN_COEFF,-1,-1;\
         FRICTN_INDX \"FRICTN_INDX\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,FRICTN_INDX,-1,-1;\
         FRICTN_DATE \"FRICTN_DATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,FRICTN_DATE,-1,-1;\
         PVMNT_COND_RATE \"PVMNT_COND_RATE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,PVMNT_COND_RATE,-1,-1;\
         CUR_AADT \"CUR_AADT\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,CUR_AADT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,CUR_AADT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,CUR_AADT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,CUR_AADT,-1,-1;\
         ACCESS_CTRL \"ACCESS_CTRL\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,ACCESS_CTRL,-1,-1;\
         TOLL_CODE \"TOLL_CODE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,TOLL_CODE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,TOLL_CODE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,TOLL_CODE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,TOLL_CODE,-1,-1;\
         STREET_NAME \"STREET_NAME\" true true false 25 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,STREET_NAME,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,STREET_NAME,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,STREET_NAME,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,STREET_NAME,-1,-1;\
         TRAF_RT_NO_PREFIX \"TRAF_RT_NO_PREFIX\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,TRAF_RT_NO_PREFIX,-1,-1;\
         TRAF_RT_NO \"TRAF_RT_NO\" true true false 3 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,TRAF_RT_NO,-1,-1;\
         TRAF_RT_NO_SUF \"TRAF_RT_NO_SUF\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,TRAF_RT_NO_SUF,-1,-1;\
         BGN_DESC \"BGN_DESC\" true true false 20 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,BGN_DESC,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,BGN_DESC,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,BGN_DESC,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,BGN_DESC,-1,-1;\
         END_DESC \"END_DESC\" true true false 20 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,END_DESC,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,END_DESC,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,END_DESC,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,END_DESC,-1,-1;\
         MAINT_RESPON_IND \"MAINT_RESPON_IND\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,MAINT_RESPON_IND,-1,-1;\
         URBAN_RURAL \"URBAN_RURAL\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,URBAN_RURAL,-1,-1;\
         NHS_IND \"NHS_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,NHS_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,NHS_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,NHS_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,NHS_IND,-1,-1;\
         TANDEM_TRLR_TRK \"TANDEM_TRLR_TRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,TANDEM_TRLR_TRK,-1,-1;\
         ACCESS_TANDEM_TRLR \"ACCESS_TANDEM_TRLR\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,ACCESS_TANDEM_TRLR,-1,-1;\
         INTERST_NETWRK_IND \"INTERST_NETWRK_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,INTERST_NETWRK_IND,-1,-1;\
         NHPN_IND \"NHPN_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,NHPN_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,NHPN_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,NHPN_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,NHPN_IND,-1,-1;\
         NORM_ADMIN_BGN \"NORM_ADMIN_BGN\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,NORM_ADMIN_BGN,-1,-1;\
         NORM_TRAFF_BGN \"NORM_TRAFF_BGN\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,NORM_TRAFF_BGN,-1,-1;\
         NORM_SHLD_BGN \"NORM_SHLD_BGN\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,NORM_SHLD_BGN,-1,-1;\
         MAPID \"MAPID\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,MAPID,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,MAPID,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,MAPID,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,MAPID,-1,-1;\
         NLF_ID \"NLF_ID\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,NLF_ID,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,NLF_ID,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,NLF_ID,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,NLF_ID,-1,-1;\
         SIDE_IND \"SIDE_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,SIDE_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,SIDE_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,SIDE_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,SIDE_IND,-1,-1;\
         NLF_CNTL_BGN \"NLF_CNTL_BGN\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,NLF_CNTL_BGN,-1,-1;\
         NLF_CNTL_END \"NLF_CNTL_END\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,NLF_CNTL_END,-1,-1;\
         CUM_OFFSET_BGN_T1 \"CUM_OFFSET_BGN_T1\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,CUM_OFFSET_BGN_T1,-1,-1;\
         CUM_OFFSET_END_T1 \"CUM_OFFSET_END_T1\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,CUM_OFFSET_END_T1,-1,-1;\
         X_VALUE_BGN \"X_VALUE_BGN\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,X_VALUE_BGN,-1,-1;\
         Y_VALUE_BGN \"Y_VALUE_BGN\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,Y_VALUE_BGN,-1,-1;\
         X_VALUE_END \"X_VALUE_END\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,X_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,X_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,X_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,X_VALUE_END,-1,-1;\
         Y_VALUE_END \"Y_VALUE_END\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,Y_VALUE_END,-1,-1;\
         GRAPHIC_LENGTH \"GRAPHIC_LENGTH\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,GRAPHIC_LENGTH,-1,-1;\
         KEY_UPDATE \"KEY_UPDATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,KEY_UPDATE,-1,-1;\
         ATTR_UPDATE \"ATTR_UPDATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,ATTR_UPDATE,-1,-1;\
         OVERALL_PVMNT_IDX \"OVERALL_PVMNT_IDX\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,OVERALL_PVMNT_IDX,-1,-1;\
         SEG_STATUS \"SEG_STATUS\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,SEG_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,SEG_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,SEG_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,SEG_STATUS,-1,-1;\
         PAVMT_CYCLE \"PAVMT_CYCLE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,PAVMT_CYCLE,-1,-1;\
         DRAIN_CYCLE \"DRAIN_CYCLE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,DRAIN_CYCLE,-1,-1;\
         GDRAIL_CYCLE \"GDRAIL_CYCLE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,GDRAIL_CYCLE,-1,-1;\
         DISTRICT_SPECIAL \"DISTRICT_SPECIAL\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,DISTRICT_SPECIAL,-1,-1;\
         TRT_TYPE_NETWRK \"TRT_TYPE_NETWRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,TRT_TYPE_NETWRK,-1,-1;\
         PA_BYWAY_IND \"PA_BYWAY_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,PA_BYWAY_IND,-1,-1;\
         STREET_NAME2 \"STREET_NAME2\" true true false 25 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,STREET_NAME2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,STREET_NAME2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,STREET_NAME2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,STREET_NAME2,-1,-1;\
         TRAF_RT_NO_PREFIX2 \"TRAF_RT_NO_PREFIX2\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,TRAF_RT_NO_PREFIX2,-1,-1;\
         TRAF_RT_NO2 \"TRAF_RT_NO2\" true true false 3 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,TRAF_RT_NO2,-1,-1;\
         TRAF_RT_NO_SUF2 \"TRAF_RT_NO_SUF2\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,TRAF_RT_NO_SUF2,-1,-1;\
         STREET_NAME3 \"STREET_NAME3\" true true false 25 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,STREET_NAME3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,STREET_NAME3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,STREET_NAME3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,STREET_NAME3,-1,-1;\
         TRAF_RT_NO_PREFIX3 \"TRAF_RT_NO_PREFIX3\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,TRAF_RT_NO_PREFIX3,-1,-1;\
         TRAF_RT_NO3 \"TRAF_RT_NO3\" true true false 3 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,TRAF_RT_NO3,-1,-1;\
         TRAF_RT_NO_SUF3 \"TRAF_RT_NO_SUF3\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,TRAF_RT_NO_SUF3,-1,-1;\
         TRXN_FLAG \"TRXN_FLAG\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,TRXN_FLAG,-1,-1;\
         ROUTE_DIR \"ROUTE_DIR\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,ROUTE_DIR,-1,-1;\
         BUS_PLAN_NETWRK \"BUS_PLAN_NETWRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,BUS_PLAN_NETWRK,-1,-1;\
         EXP_WAY_NETWRK \"EXP_WAY_NETWRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,EXP_WAY_NETWRK,-1,-1;\
         HPMS_SAMP_CNT \"HPMS_SAMP_CNT\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,HPMS_SAMP_CNT,-1,-1;\
         MILE_POINT \"MILE_POINT\" true true false 5 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,MILE_POINT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,MILE_POINT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,MILE_POINT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,MILE_POINT,-1,-1;\
         IS_STRUCTURE \"IS_STRUCTURE\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,IS_STRUCTURE,-1,-1;\
         GOVT_LVL_CTRL \"GOVT_LVL_CTRL\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,GOVT_LVL_CTRL,-1,-1;\
         HOV_TYPE \"HOV_TYPE\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,HOV_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,HOV_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,HOV_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,HOV_TYPE,-1,-1;\
         HOV_LANES \"HOV_LANES\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,HOV_LANES,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,HOV_LANES,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,HOV_LANES,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,HOV_LANES,-1,-1;\
         PAR_SEG_IND \"PAR_SEG_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,PAR_SEG_IND,-1,-1;\
         HPMS_DIVSR_TYPE \"HPMS_DIVSR_TYPE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,HPMS_DIVSR_TYPE,-1,-1;\
         IRI_CUR_FLAG \"IRI_CUR_FLAG\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,IRI_CUR_FLAG,-1,-1;\
         DRAIN_SWT \"DRAIN_SWT\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,DRAIN_SWT,-1,-1;\
         GDRAIL_SWT \"GDRAIL_SWT\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,GDRAIL_SWT,-1,-1;\
         PAVMT_SWT \"PAVMT_SWT\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,PAVMT_SWT,-1,-1;\
         SHLD_COND_STATUS \"SHLD_COND_STATUS\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,SHLD_COND_STATUS,-1,-1;\
         FED_AID_PRIM_IND \"FED_AID_PRIM_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,FED_AID_PRIM_IND,-1,-1;\
         DRAIN_CNT \"DRAIN_CNT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,DRAIN_CNT,-1,-1;\
         GDRAIL_CNT \"GDRAIL_CNT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,GDRAIL_CNT,-1,-1;\
         PVMNT_TRTMT_DATA \"PVMNT_TRTMT_DATA\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,PVMNT_TRTMT_DATA,-1,-1;\
         PVMNT_IND \"PVMNT_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,PVMNT_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,PVMNT_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,PVMNT_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,PVMNT_IND,-1,-1;\
         IRI_YEAR \"IRI_YEAR\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,IRI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,IRI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,IRI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,IRI_YEAR,-1,-1;\
         OPI_YEAR \"OPI_YEAR\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,OPI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,OPI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,OPI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,OPI_YEAR,-1,-1;\
         IRI_RATING_TEXT \"IRI_RATING_TEXT\" true true false 9 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,IRI_RATING_TEXT,-1,-1;\
         OPI_RATING_TEXT \"OPI_RATING_TEXT\" true true false 9 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,OPI_RATING_TEXT,-1,-1;\
         GEOMETRY_LEN \"GEOMETRY.LEN\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,GEOMETRY_LEN,-1,-1;\
         IRI_Group \"IRI_Group\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,IRI_Group,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,IRI_Group,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,IRI_Group,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,IRI_Group,-1,-1;\
         Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSGreater2000_Exc,Shape_Length,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Fair,Shape_Length,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Good,Shape_Length,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Poor,Shape_Length,-1,-1")

        # Process: Select (5)
        arcpy.Select_analysis(RMSSEG_temp_shp, NonNHSLess2000_shp, "\"NHS_IND\" = 'N' AND \"CUR_AADT\" <= 2000")

        # Process: Select (18)
        arcpy.Select_analysis(NonNHSLess2000_shp, NonNHSLesser2000_Exc_shp, "\"ROUGH_INDX\" >= 1 AND \"ROUGH_INDX\" <= 120")

        # Process: Calculate Field (13)
        arcpy.CalculateField_management(NonNHSLesser2000_Exc_shp, "IRI_Group", "\"Excellent\"", "PYTHON", "")

        # Process: Select (20)
        arcpy.Select_analysis(NonNHSLess2000_shp, NonNHSLesser2000_Fair_shp, "\"ROUGH_INDX\" >= 171 AND \"ROUGH_INDX\" <= 220")

        # Process: Calculate Field (14)
        arcpy.CalculateField_management(NonNHSLesser2000_Fair_shp, "IRI_Group", "\"Fair\"", "PYTHON", "")

        # Process: Select (21)
        arcpy.Select_analysis(NonNHSLess2000_shp, NonNHSLesser2000_Poor_shp, "\"ROUGH_INDX\" >= 221")

        # Process: Calculate Field (15)
        arcpy.CalculateField_management(NonNHSLesser2000_Poor_shp, "IRI_Group", "\"Poor\"", "PYTHON", "")

        # Process: Select (19)
        arcpy.Select_analysis(NonNHSLess2000_shp, NonNHSLesser2000_Good_shp, "\"ROUGH_INDX\" > 120 AND \"ROUGH_INDX\" <= 170")

        # Process: Calculate Field (16)
        arcpy.CalculateField_management(NonNHSLesser2000_Good_shp, "IRI_Group", "\"Good\"", "PYTHON", "")

        message ("Starting NonNHSLesser2000 Merge Step")
        # Process: Merge (4)
        arcpy.Merge_management(""+transp_arch_temp+"\NonNHSLesser2000_Exc;\
        "+transp_arch_temp+"\NonNHSLesser2000_Fair;\
        "+transp_arch_temp+"\NonNHSLesser2000_Poor;\
        "+transp_arch_temp+"\NonNHSLesser2000_Good", NonNHSLesser2000_Merge_shp,\
          "ST_RT_NO \"ST_RT_NO\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,ST_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,ST_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,ST_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,ST_RT_NO,-1,-1;\
         CTY_CODE \"CTY_CODE\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,CTY_CODE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,CTY_CODE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,CTY_CODE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,CTY_CODE,-1,-1;\
         DISTRICT_NO \"DISTRICT_NO\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,DISTRICT_NO,-1,-1;\
         JURIS \"JURIS\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,JURIS,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,JURIS,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,JURIS,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,JURIS,-1,-1;\
         SEG_NO \"SEG_NO\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,SEG_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,SEG_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,SEG_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,SEG_NO,-1,-1;\
         SEG_LNGTH_FEET \"SEG_LNGTH_FEET\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,SEG_LNGTH_FEET,-1,-1;\
         SEQ_NO \"SEQ_NO\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,SEQ_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,SEQ_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,SEQ_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,SEQ_NO,-1,-1;\
         SUB_ROUTE \"SUB_ROUTE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,SUB_ROUTE,-1,-1;\
         YR_BUILT \"YR_BUILT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,YR_BUILT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,YR_BUILT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,YR_BUILT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,YR_BUILT,-1,-1;\
         YR_RESURF \"YR_RESURF\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,YR_RESURF,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,YR_RESURF,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,YR_RESURF,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,YR_RESURF,-1,-1;\
         DIR_IND \"DIR_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,DIR_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,DIR_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,DIR_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,DIR_IND,-1,-1;\
         FAC_TYPE \"FAC_TYPE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,FAC_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,FAC_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,FAC_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,FAC_TYPE,-1,-1;\
         TOTAL_WIDTH \"TOTAL_WIDTH\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,TOTAL_WIDTH,-1,-1;\
         SURF_TYPE \"SURF_TYPE\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,SURF_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,SURF_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,SURF_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,SURF_TYPE,-1,-1;\
         LANE_CNT \"LANE_CNT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,LANE_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,LANE_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,LANE_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,LANE_CNT,-1,-1;\
         PARK_LANE \"PARK_LANE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,PARK_LANE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,PARK_LANE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,PARK_LANE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,PARK_LANE,-1,-1;\
         DIVSR_TYPE \"DIVSR_TYPE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,DIVSR_TYPE,-1,-1;\
         DIVSR_WIDTH \"DIVSR_WIDTH\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,DIVSR_WIDTH,-1,-1;\
         COND_DATE \"COND_DATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,COND_DATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,COND_DATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,COND_DATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,COND_DATE,-1,-1;\
         ROUGH_INDX \"ROUGH_INDX\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,ROUGH_INDX,-1,-1;\
         FRICTN_COEFF \"FRICTN_COEFF\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,FRICTN_COEFF,-1,-1;\
         FRICTN_INDX \"FRICTN_INDX\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,FRICTN_INDX,-1,-1;\
         FRICTN_DATE \"FRICTN_DATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,FRICTN_DATE,-1,-1;\
         PVMNT_COND_RATE \"PVMNT_COND_RATE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,PVMNT_COND_RATE,-1,-1;\
         CUR_AADT \"CUR_AADT\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,CUR_AADT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,CUR_AADT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,CUR_AADT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,CUR_AADT,-1,-1;\
         ACCESS_CTRL \"ACCESS_CTRL\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,ACCESS_CTRL,-1,-1;\
         TOLL_CODE \"TOLL_CODE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,TOLL_CODE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,TOLL_CODE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,TOLL_CODE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,TOLL_CODE,-1,-1;\
         STREET_NAME \"STREET_NAME\" true true false 25 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,STREET_NAME,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,STREET_NAME,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,STREET_NAME,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,STREET_NAME,-1,-1;\
         TRAF_RT_NO_PREFIX \"TRAF_RT_NO_PREFIX\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,TRAF_RT_NO_PREFIX,-1,-1;\
         TRAF_RT_NO \"TRAF_RT_NO\" true true false 3 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,TRAF_RT_NO,-1,-1;\
         TRAF_RT_NO_SUF \"TRAF_RT_NO_SUF\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,TRAF_RT_NO_SUF,-1,-1;\
         BGN_DESC \"BGN_DESC\" true true false 20 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,BGN_DESC,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,BGN_DESC,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,BGN_DESC,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,BGN_DESC,-1,-1;\
         END_DESC \"END_DESC\" true true false 20 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,END_DESC,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,END_DESC,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,END_DESC,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,END_DESC,-1,-1;\
         MAINT_RESPON_IND \"MAINT_RESPON_IND\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,MAINT_RESPON_IND,-1,-1;\
         URBAN_RURAL \"URBAN_RURAL\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,URBAN_RURAL,-1,-1;\
         NHS_IND \"NHS_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,NHS_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,NHS_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,NHS_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,NHS_IND,-1,-1;\
         TANDEM_TRLR_TRK \"TANDEM_TRLR_TRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,TANDEM_TRLR_TRK,-1,-1;\
         ACCESS_TANDEM_TRLR \"ACCESS_TANDEM_TRLR\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,ACCESS_TANDEM_TRLR,-1,-1;\
         INTERST_NETWRK_IND \"INTERST_NETWRK_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,INTERST_NETWRK_IND,-1,-1;\
         NHPN_IND \"NHPN_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,NHPN_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,NHPN_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,NHPN_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,NHPN_IND,-1,-1;\
         NORM_ADMIN_BGN \"NORM_ADMIN_BGN\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,NORM_ADMIN_BGN,-1,-1;\
         NORM_TRAFF_BGN \"NORM_TRAFF_BGN\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,NORM_TRAFF_BGN,-1,-1;\
         NORM_SHLD_BGN \"NORM_SHLD_BGN\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,NORM_SHLD_BGN,-1,-1;\
         MAPID \"MAPID\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,MAPID,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,MAPID,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,MAPID,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,MAPID,-1,-1;\
         NLF_ID \"NLF_ID\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,NLF_ID,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,NLF_ID,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,NLF_ID,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,NLF_ID,-1,-1;\
         SIDE_IND \"SIDE_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,SIDE_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,SIDE_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,SIDE_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,SIDE_IND,-1,-1;\
         NLF_CNTL_BGN \"NLF_CNTL_BGN\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,NLF_CNTL_BGN,-1,-1;\
         NLF_CNTL_END \"NLF_CNTL_END\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,NLF_CNTL_END,-1,-1;\
         CUM_OFFSET_BGN_T1 \"CUM_OFFSET_BGN_T1\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,CUM_OFFSET_BGN_T1,-1,-1;\
         CUM_OFFSET_END_T1 \"CUM_OFFSET_END_T1\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,CUM_OFFSET_END_T1,-1,-1;\
         X_VALUE_BGN \"X_VALUE_BGN\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,X_VALUE_BGN,-1,-1;\
         Y_VALUE_BGN \"Y_VALUE_BGN\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,Y_VALUE_BGN,-1,-1;\
         X_VALUE_END \"X_VALUE_END\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,X_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,X_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,X_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,X_VALUE_END,-1,-1;\
         Y_VALUE_END \"Y_VALUE_END\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,Y_VALUE_END,-1,-1;\
         GRAPHIC_LENGTH \"GRAPHIC_LENGTH\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,GRAPHIC_LENGTH,-1,-1;\
         KEY_UPDATE \"KEY_UPDATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,KEY_UPDATE,-1,-1;\
         ATTR_UPDATE \"ATTR_UPDATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,ATTR_UPDATE,-1,-1;\
         OVERALL_PVMNT_IDX \"OVERALL_PVMNT_IDX\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,OVERALL_PVMNT_IDX,-1,-1;\
         SEG_STATUS \"SEG_STATUS\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,SEG_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,SEG_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,SEG_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,SEG_STATUS,-1,-1;\
         PAVMT_CYCLE \"PAVMT_CYCLE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,PAVMT_CYCLE,-1,-1;\
         DRAIN_CYCLE \"DRAIN_CYCLE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,DRAIN_CYCLE,-1,-1;\
         GDRAIL_CYCLE \"GDRAIL_CYCLE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,GDRAIL_CYCLE,-1,-1;\
         DISTRICT_SPECIAL \"DISTRICT_SPECIAL\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,DISTRICT_SPECIAL,-1,-1;\
         TRT_TYPE_NETWRK \"TRT_TYPE_NETWRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,TRT_TYPE_NETWRK,-1,-1;\
         PA_BYWAY_IND \"PA_BYWAY_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,PA_BYWAY_IND,-1,-1;\
         STREET_NAME2 \"STREET_NAME2\" true true false 25 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,STREET_NAME2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,STREET_NAME2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,STREET_NAME2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,STREET_NAME2,-1,-1;\
         TRAF_RT_NO_PREFIX2 \"TRAF_RT_NO_PREFIX2\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,TRAF_RT_NO_PREFIX2,-1,-1;\
         TRAF_RT_NO2 \"TRAF_RT_NO2\" true true false 3 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,TRAF_RT_NO2,-1,-1;\
         TRAF_RT_NO_SUF2 \"TRAF_RT_NO_SUF2\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,TRAF_RT_NO_SUF2,-1,-1;\
         STREET_NAME3 \"STREET_NAME3\" true true false 25 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,STREET_NAME3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,STREET_NAME3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,STREET_NAME3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,STREET_NAME3,-1,-1;\
         TRAF_RT_NO_PREFIX3 \"TRAF_RT_NO_PREFIX3\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,TRAF_RT_NO_PREFIX3,-1,-1;\
         TRAF_RT_NO3 \"TRAF_RT_NO3\" true true false 3 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,TRAF_RT_NO3,-1,-1;\
         TRAF_RT_NO_SUF3 \"TRAF_RT_NO_SUF3\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,TRAF_RT_NO_SUF3,-1,-1;\
         TRXN_FLAG \"TRXN_FLAG\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,TRXN_FLAG,-1,-1;\
         ROUTE_DIR \"ROUTE_DIR\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,ROUTE_DIR,-1,-1;\
         BUS_PLAN_NETWRK \"BUS_PLAN_NETWRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,BUS_PLAN_NETWRK,-1,-1;\
         EXP_WAY_NETWRK \"EXP_WAY_NETWRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,EXP_WAY_NETWRK,-1,-1;\
         HPMS_SAMP_CNT \"HPMS_SAMP_CNT\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,HPMS_SAMP_CNT,-1,-1;\
         MILE_POINT \"MILE_POINT\" true true false 5 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,MILE_POINT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,MILE_POINT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,MILE_POINT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,MILE_POINT,-1,-1;\
         IS_STRUCTURE \"IS_STRUCTURE\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,IS_STRUCTURE,-1,-1;\
         GOVT_LVL_CTRL \"GOVT_LVL_CTRL\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,GOVT_LVL_CTRL,-1,-1;\
         HOV_TYPE \"HOV_TYPE\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,HOV_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,HOV_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,HOV_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,HOV_TYPE,-1,-1;\
         HOV_LANES \"HOV_LANES\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,HOV_LANES,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,HOV_LANES,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,HOV_LANES,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,HOV_LANES,-1,-1;\
         PAR_SEG_IND \"PAR_SEG_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,PAR_SEG_IND,-1,-1;\
         HPMS_DIVSR_TYPE \"HPMS_DIVSR_TYPE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,HPMS_DIVSR_TYPE,-1,-1;\
         IRI_CUR_FLAG \"IRI_CUR_FLAG\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,IRI_CUR_FLAG,-1,-1;\
         DRAIN_SWT \"DRAIN_SWT\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,DRAIN_SWT,-1,-1;\
         GDRAIL_SWT \"GDRAIL_SWT\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,GDRAIL_SWT,-1,-1;\
         PAVMT_SWT \"PAVMT_SWT\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,PAVMT_SWT,-1,-1;\
         SHLD_COND_STATUS \"SHLD_COND_STATUS\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,SHLD_COND_STATUS,-1,-1;\
         FED_AID_PRIM_IND \"FED_AID_PRIM_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,FED_AID_PRIM_IND,-1,-1;\
         DRAIN_CNT \"DRAIN_CNT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,DRAIN_CNT,-1,-1;\
         GDRAIL_CNT \"GDRAIL_CNT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,GDRAIL_CNT,-1,-1;\
         PVMNT_TRTMT_DATA \"PVMNT_TRTMT_DATA\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,PVMNT_TRTMT_DATA,-1,-1;\
         PVMNT_IND \"PVMNT_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,PVMNT_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,PVMNT_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,PVMNT_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,PVMNT_IND,-1,-1;\
         IRI_YEAR \"IRI_YEAR\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,IRI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,IRI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,IRI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,IRI_YEAR,-1,-1;\
         OPI_YEAR \"OPI_YEAR\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,OPI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,OPI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,OPI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,OPI_YEAR,-1,-1;\
         IRI_RATING_TEXT \"IRI_RATING_TEXT\" true true false 9 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,IRI_RATING_TEXT,-1,-1;\
         OPI_RATING_TEXT \"OPI_RATING_TEXT\" true true false 9 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,OPI_RATING_TEXT,-1,-1;\
         GEOMETRY_LEN \"GEOMETRY.LEN\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,GEOMETRY_LEN,-1,-1;\
         IRI_Group \"IRI_Group\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,IRI_Group,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,IRI_Group,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,IRI_Group,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,IRI_Group,-1,-1;\
         Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NonNHSLesser2000_Exc,Shape_Length,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Fair,Shape_Length,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Good,Shape_Length,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Poor,Shape_Length,-1,-1")

        message ("Starting Final Merge Step")
        # Process: Merge (5)
        arcpy.Merge_management(""+transp_arch_temp+"\NHS_Interstate_Merge;\
        "+transp_arch_temp+"\NHS_NonInter_Merge;\
        "+transp_arch_temp+"\No_Data;\
        "+transp_arch_temp+"\NonNHSGreater2000_Merge;\
        "+transp_arch_temp+"\NonNHSLesser2000_Merge", RMSSEG_shp,\
        "ST_RT_NO \"ST_RT_NO\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,ST_RT_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,ST_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,ST_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,ST_RT_NO,-1,-1,"+transp_arch_temp+"\No_Data,ST_RT_NO,-1,-1;\
        CTY_CODE \"CTY_CODE\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,CTY_CODE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,CTY_CODE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,CTY_CODE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,CTY_CODE,-1,-1,"+transp_arch_temp+"\No_Data,CTY_CODE,-1,-1;\
        DISTRICT_NO \"DISTRICT_NO\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,DISTRICT_NO,-1,-1,"+transp_arch_temp+"\No_Data,DISTRICT_NO,-1,-1;\
        JURIS \"JURIS\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,JURIS,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,JURIS,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,JURIS,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,JURIS,-1,-1,"+transp_arch_temp+"\No_Data,JURIS,-1,-1;\
        SEG_NO \"SEG_NO\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,SEG_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,SEG_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,SEG_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,SEG_NO,-1,-1,"+transp_arch_temp+"\No_Data,SEG_NO,-1,-1;\
        SEG_LNGTH_FEET \"SEG_LNGTH_FEET\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,SEG_LNGTH_FEET,-1,-1,"+transp_arch_temp+"\No_Data,SEG_LNGTH_FEET,-1,-1;\
        SEQ_NO \"SEQ_NO\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,SEQ_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,SEQ_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,SEQ_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,SEQ_NO,-1,-1,"+transp_arch_temp+"\No_Data,SEQ_NO,-1,-1;\
        SUB_ROUTE \"SUB_ROUTE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,SUB_ROUTE,-1,-1,"+transp_arch_temp+"\No_Data,SUB_ROUTE,-1,-1;\
        YR_BUILT \"YR_BUILT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,YR_BUILT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,YR_BUILT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,YR_BUILT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,YR_BUILT,-1,-1,"+transp_arch_temp+"\No_Data,YR_BUILT,-1,-1;\
        YR_RESURF \"YR_RESURF\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,YR_RESURF,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,YR_RESURF,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,YR_RESURF,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,YR_RESURF,-1,-1,"+transp_arch_temp+"\No_Data,YR_RESURF,-1,-1;\
        DIR_IND \"DIR_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,DIR_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,DIR_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,DIR_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,DIR_IND,-1,-1,"+transp_arch_temp+"\No_Data,DIR_IND,-1,-1;\
        FAC_TYPE \"FAC_TYPE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,FAC_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,FAC_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,FAC_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,FAC_TYPE,-1,-1,"+transp_arch_temp+"\No_Data,FAC_TYPE,-1,-1;\
        TOTAL_WIDTH \"TOTAL_WIDTH\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,TOTAL_WIDTH,-1,-1,"+transp_arch_temp+"\No_Data,TOTAL_WIDTH,-1,-1;\
        SURF_TYPE \"SURF_TYPE\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,SURF_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,SURF_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,SURF_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,SURF_TYPE,-1,-1,"+transp_arch_temp+"\No_Data,SURF_TYPE,-1,-1;\
        LANE_CNT \"LANE_CNT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,LANE_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,LANE_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,LANE_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,LANE_CNT,-1,-1,"+transp_arch_temp+"\No_Data,LANE_CNT,-1,-1;\
        PARK_LANE \"PARK_LANE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,PARK_LANE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,PARK_LANE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,PARK_LANE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,PARK_LANE,-1,-1,"+transp_arch_temp+"\No_Data,PARK_LANE,-1,-1;\
        DIVSR_TYPE \"DIVSR_TYPE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\No_Data,DIVSR_TYPE,-1,-1;\
        DIVSR_WIDTH \"DIVSR_WIDTH\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,DIVSR_WIDTH,-1,-1,"+transp_arch_temp+"\No_Data,DIVSR_WIDTH,-1,-1;\
        COND_DATE \"COND_DATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,COND_DATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,COND_DATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,COND_DATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,COND_DATE,-1,-1,"+transp_arch_temp+"\No_Data,COND_DATE,-1,-1;\
        ROUGH_INDX \"ROUGH_INDX\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,ROUGH_INDX,-1,-1,"+transp_arch_temp+"\No_Data,ROUGH_INDX,-1,-1;\
        FRICTN_COEFF \"FRICTN_COEFF\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,FRICTN_COEFF,-1,-1,"+transp_arch_temp+"\No_Data,FRICTN_COEFF,-1,-1;\
        FRICTN_INDX \"FRICTN_INDX\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,FRICTN_INDX,-1,-1,"+transp_arch_temp+"\No_Data,FRICTN_INDX,-1,-1;\
        FRICTN_DATE \"FRICTN_DATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,FRICTN_DATE,-1,-1,"+transp_arch_temp+"\No_Data,FRICTN_DATE,-1,-1;\
        PVMNT_COND_RATE \"PVMNT_COND_RATE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,PVMNT_COND_RATE,-1,-1,"+transp_arch_temp+"\No_Data,PVMNT_COND_RATE,-1,-1;\
        CUR_AADT \"CUR_AADT\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,CUR_AADT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,CUR_AADT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,CUR_AADT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,CUR_AADT,-1,-1,"+transp_arch_temp+"\No_Data,CUR_AADT,-1,-1;\
        ACCESS_CTRL \"ACCESS_CTRL\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,ACCESS_CTRL,-1,-1,"+transp_arch_temp+"\No_Data,ACCESS_CTRL,-1,-1;\
        TOLL_CODE \"TOLL_CODE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,TOLL_CODE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,TOLL_CODE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,TOLL_CODE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,TOLL_CODE,-1,-1,"+transp_arch_temp+"\No_Data,TOLL_CODE,-1,-1;\
        STREET_NAME \"STREET_NAME\" true true false 25 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,STREET_NAME,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,STREET_NAME,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,STREET_NAME,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,STREET_NAME,-1,-1,"+transp_arch_temp+"\No_Data,STREET_NAME,-1,-1;\
        TRAF_RT_NO_PREFIX \"TRAF_RT_NO_PREFIX\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,TRAF_RT_NO_PREFIX,-1,-1,"+transp_arch_temp+"\No_Data,TRAF_RT_NO_PREFIX,-1,-1;\
        TRAF_RT_NO \"TRAF_RT_NO\" true true false 3 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,TRAF_RT_NO,-1,-1,"+transp_arch_temp+"\No_Data,TRAF_RT_NO,-1,-1;\
        TRAF_RT_NO_SUF \"TRAF_RT_NO_SUF\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,TRAF_RT_NO_SUF,-1,-1,"+transp_arch_temp+"\No_Data,TRAF_RT_NO_SUF,-1,-1;\
        BGN_DESC \"BGN_DESC\" true true false 20 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,BGN_DESC,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,BGN_DESC,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,BGN_DESC,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,BGN_DESC,-1,-1,"+transp_arch_temp+"\No_Data,BGN_DESC,-1,-1;\
        END_DESC \"END_DESC\" true true false 20 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,END_DESC,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,END_DESC,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,END_DESC,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,END_DESC,-1,-1,"+transp_arch_temp+"\No_Data,END_DESC,-1,-1;\
        MAINT_RESPON_IND \"MAINT_RESPON_IND\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,MAINT_RESPON_IND,-1,-1,"+transp_arch_temp+"\No_Data,MAINT_RESPON_IND,-1,-1;\
        URBAN_RURAL \"URBAN_RURAL\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,URBAN_RURAL,-1,-1,"+transp_arch_temp+"\No_Data,URBAN_RURAL,-1,-1;\
        NHS_IND \"NHS_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,NHS_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,NHS_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,NHS_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,NHS_IND,-1,-1,"+transp_arch_temp+"\No_Data,NHS_IND,-1,-1;\
        TANDEM_TRLR_TRK \"TANDEM_TRLR_TRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,TANDEM_TRLR_TRK,-1,-1,"+transp_arch_temp+"\No_Data,TANDEM_TRLR_TRK,-1,-1;\
        ACCESS_TANDEM_TRLR \"ACCESS_TANDEM_TRLR\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,ACCESS_TANDEM_TRLR,-1,-1,"+transp_arch_temp+"\No_Data,ACCESS_TANDEM_TRLR,-1,-1;\
        INTERST_NETWRK_IND \"INTERST_NETWRK_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,INTERST_NETWRK_IND,-1,-1,"+transp_arch_temp+"\No_Data,INTERST_NETWRK_IND,-1,-1;\
        NHPN_IND \"NHPN_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,NHPN_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,NHPN_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,NHPN_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,NHPN_IND,-1,-1,"+transp_arch_temp+"\No_Data,NHPN_IND,-1,-1;\
        NORM_ADMIN_BGN \"NORM_ADMIN_BGN\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,NORM_ADMIN_BGN,-1,-1,"+transp_arch_temp+"\No_Data,NORM_ADMIN_BGN,-1,-1;\
        NORM_TRAFF_BGN \"NORM_TRAFF_BGN\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,NORM_TRAFF_BGN,-1,-1,"+transp_arch_temp+"\No_Data,NORM_TRAFF_BGN,-1,-1;\
        NORM_SHLD_BGN \"NORM_SHLD_BGN\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,NORM_SHLD_BGN,-1,-1,"+transp_arch_temp+"\No_Data,NORM_SHLD_BGN,-1,-1;\
        MAPID \"MAPID\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,MAPID,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,MAPID,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,MAPID,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,MAPID,-1,-1,"+transp_arch_temp+"\No_Data,MAPID,-1,-1;\
        NLF_ID \"NLF_ID\" true true false 4 Long 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,NLF_ID,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,NLF_ID,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,NLF_ID,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,NLF_ID,-1,-1,"+transp_arch_temp+"\No_Data,NLF_ID,-1,-1;\
        SIDE_IND \"SIDE_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,SIDE_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,SIDE_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,SIDE_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,SIDE_IND,-1,-1,"+transp_arch_temp+"\No_Data,SIDE_IND,-1,-1;\
        NLF_CNTL_BGN \"NLF_CNTL_BGN\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,NLF_CNTL_BGN,-1,-1,"+transp_arch_temp+"\No_Data,NLF_CNTL_BGN,-1,-1;\
        NLF_CNTL_END \"NLF_CNTL_END\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,NLF_CNTL_END,-1,-1,"+transp_arch_temp+"\No_Data,NLF_CNTL_END,-1,-1;\
        CUM_OFFSET_BGN_T1 \"CUM_OFFSET_BGN_T1\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,CUM_OFFSET_BGN_T1,-1,-1,"+transp_arch_temp+"\No_Data,CUM_OFFSET_BGN_T1,-1,-1;\
        CUM_OFFSET_END_T1 \"CUM_OFFSET_END_T1\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,CUM_OFFSET_END_T1,-1,-1,"+transp_arch_temp+"\No_Data,CUM_OFFSET_END_T1,-1,-1;\
        X_VALUE_BGN \"X_VALUE_BGN\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,X_VALUE_BGN,-1,-1,"+transp_arch_temp+"\No_Data,X_VALUE_BGN,-1,-1;\
        Y_VALUE_BGN \"Y_VALUE_BGN\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,Y_VALUE_BGN,-1,-1,"+transp_arch_temp+"\No_Data,Y_VALUE_BGN,-1,-1;\
        X_VALUE_END \"X_VALUE_END\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,X_VALUE_END,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,X_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,X_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,X_VALUE_END,-1,-1,"+transp_arch_temp+"\No_Data,X_VALUE_END,-1,-1;\
        Y_VALUE_END \"Y_VALUE_END\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,Y_VALUE_END,-1,-1,"+transp_arch_temp+"\No_Data,Y_VALUE_END,-1,-1;\
        GRAPHIC_LENGTH \"GRAPHIC_LENGTH\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,GRAPHIC_LENGTH,-1,-1,"+transp_arch_temp+"\No_Data,GRAPHIC_LENGTH,-1,-1;\
        KEY_UPDATE \"KEY_UPDATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,KEY_UPDATE,-1,-1,"+transp_arch_temp+"\No_Data,KEY_UPDATE,-1,-1;\
        ATTR_UPDATE \"ATTR_UPDATE\" true true false 8 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,ATTR_UPDATE,-1,-1,"+transp_arch_temp+"\No_Data,ATTR_UPDATE,-1,-1;\
        OVERALL_PVMNT_IDX \"OVERALL_PVMNT_IDX\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,OVERALL_PVMNT_IDX,-1,-1,"+transp_arch_temp+"\No_Data,OVERALL_PVMNT_IDX,-1,-1;\
        SEG_STATUS \"SEG_STATUS\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,SEG_STATUS,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,SEG_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,SEG_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,SEG_STATUS,-1,-1,"+transp_arch_temp+"\No_Data,SEG_STATUS,-1,-1;\
        PAVMT_CYCLE \"PAVMT_CYCLE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,PAVMT_CYCLE,-1,-1,"+transp_arch_temp+"\No_Data,PAVMT_CYCLE,-1,-1;\
        DRAIN_CYCLE \"DRAIN_CYCLE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,DRAIN_CYCLE,-1,-1,"+transp_arch_temp+"\No_Data,DRAIN_CYCLE,-1,-1;\
        GDRAIL_CYCLE \"GDRAIL_CYCLE\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,GDRAIL_CYCLE,-1,-1,"+transp_arch_temp+"\No_Data,GDRAIL_CYCLE,-1,-1;\
        DISTRICT_SPECIAL \"DISTRICT_SPECIAL\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,DISTRICT_SPECIAL,-1,-1,"+transp_arch_temp+"\No_Data,DISTRICT_SPECIAL,-1,-1;\
        TRT_TYPE_NETWRK \"TRT_TYPE_NETWRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,TRT_TYPE_NETWRK,-1,-1,"+transp_arch_temp+"\No_Data,TRT_TYPE_NETWRK,-1,-1;\
        PA_BYWAY_IND \"PA_BYWAY_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,PA_BYWAY_IND,-1,-1,"+transp_arch_temp+"\No_Data,PA_BYWAY_IND,-1,-1;\
        STREET_NAME2 \"STREET_NAME2\" true true false 25 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,STREET_NAME2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,STREET_NAME2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,STREET_NAME2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,STREET_NAME2,-1,-1,"+transp_arch_temp+"\No_Data,STREET_NAME2,-1,-1;\
        TRAF_RT_NO_PREFIX2 \"TRAF_RT_NO_PREFIX2\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,TRAF_RT_NO_PREFIX2,-1,-1,"+transp_arch_temp+"\No_Data,TRAF_RT_NO_PREFIX2,-1,-1;\
        TRAF_RT_NO2 \"TRAF_RT_NO2\" true true false 3 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,TRAF_RT_NO2,-1,-1,"+transp_arch_temp+"\No_Data,TRAF_RT_NO2,-1,-1;\
        TRAF_RT_NO_SUF2 \"TRAF_RT_NO_SUF2\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,TRAF_RT_NO_SUF2,-1,-1,"+transp_arch_temp+"\No_Data,TRAF_RT_NO_SUF2,-1,-1;\
        STREET_NAME3 \"STREET_NAME3\" true true false 25 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,STREET_NAME3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,STREET_NAME3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,STREET_NAME3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,STREET_NAME3,-1,-1,"+transp_arch_temp+"\No_Data,STREET_NAME3,-1,-1;\
        TRAF_RT_NO_PREFIX3 \"TRAF_RT_NO_PREFIX3\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,TRAF_RT_NO_PREFIX3,-1,-1,"+transp_arch_temp+"\No_Data,TRAF_RT_NO_PREFIX3,-1,-1;\
        TRAF_RT_NO3 \"TRAF_RT_NO3\" true true false 3 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,TRAF_RT_NO3,-1,-1,"+transp_arch_temp+"\No_Data,TRAF_RT_NO3,-1,-1;\
        TRAF_RT_NO_SUF3 \"TRAF_RT_NO_SUF3\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,TRAF_RT_NO_SUF3,-1,-1,"+transp_arch_temp+"\No_Data,TRAF_RT_NO_SUF3,-1,-1;\
        TRXN_FLAG \"TRXN_FLAG\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,TRXN_FLAG,-1,-1,"+transp_arch_temp+"\No_Data,TRXN_FLAG,-1,-1;\
        ROUTE_DIR \"ROUTE_DIR\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,ROUTE_DIR,-1,-1,"+transp_arch_temp+"\No_Data,ROUTE_DIR,-1,-1;\
        BUS_PLAN_NETWRK \"BUS_PLAN_NETWRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,BUS_PLAN_NETWRK,-1,-1,"+transp_arch_temp+"\No_Data,BUS_PLAN_NETWRK,-1,-1;\
        EXP_WAY_NETWRK \"EXP_WAY_NETWRK\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,EXP_WAY_NETWRK,-1,-1,"+transp_arch_temp+"\No_Data,EXP_WAY_NETWRK,-1,-1;\
        HPMS_SAMP_CNT \"HPMS_SAMP_CNT\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,HPMS_SAMP_CNT,-1,-1,"+transp_arch_temp+"\No_Data,HPMS_SAMP_CNT,-1,-1;\
        MILE_POINT \"MILE_POINT\" true true false 5 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,MILE_POINT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,MILE_POINT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,MILE_POINT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,MILE_POINT,-1,-1,"+transp_arch_temp+"\No_Data,MILE_POINT,-1,-1;\
        IS_STRUCTURE \"IS_STRUCTURE\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,IS_STRUCTURE,-1,-1,"+transp_arch_temp+"\No_Data,IS_STRUCTURE,-1,-1;\
        GOVT_LVL_CTRL \"GOVT_LVL_CTRL\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,GOVT_LVL_CTRL,-1,-1,"+transp_arch_temp+"\No_Data,GOVT_LVL_CTRL,-1,-1;\
        HOV_TYPE \"HOV_TYPE\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,HOV_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,HOV_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,HOV_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,HOV_TYPE,-1,-1,"+transp_arch_temp+"\No_Data,HOV_TYPE,-1,-1;\
        HOV_LANES \"HOV_LANES\" true true false 2 Short 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,HOV_LANES,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,HOV_LANES,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,HOV_LANES,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,HOV_LANES,-1,-1,"+transp_arch_temp+"\No_Data,HOV_LANES,-1,-1;\
        PAR_SEG_IND \"PAR_SEG_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,PAR_SEG_IND,-1,-1,"+transp_arch_temp+"\No_Data,PAR_SEG_IND,-1,-1;\
        HPMS_DIVSR_TYPE \"HPMS_DIVSR_TYPE\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,HPMS_DIVSR_TYPE,-1,-1,"+transp_arch_temp+"\No_Data,HPMS_DIVSR_TYPE,-1,-1;\
        IRI_CUR_FLAG \"IRI_CUR_FLAG\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,IRI_CUR_FLAG,-1,-1,"+transp_arch_temp+"\No_Data,IRI_CUR_FLAG,-1,-1;\
        DRAIN_SWT \"DRAIN_SWT\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,DRAIN_SWT,-1,-1,"+transp_arch_temp+"\No_Data,DRAIN_SWT,-1,-1;\
        GDRAIL_SWT \"GDRAIL_SWT\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,GDRAIL_SWT,-1,-1,"+transp_arch_temp+"\No_Data,GDRAIL_SWT,-1,-1;\
        PAVMT_SWT \"PAVMT_SWT\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,PAVMT_SWT,-1,-1,"+transp_arch_temp+"\No_Data,PAVMT_SWT,-1,-1;\
        SHLD_COND_STATUS \"SHLD_COND_STATUS\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,SHLD_COND_STATUS,-1,-1,"+transp_arch_temp+"\No_Data,SHLD_COND_STATUS,-1,-1;\
        FED_AID_PRIM_IND \"FED_AID_PRIM_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,FED_AID_PRIM_IND,-1,-1,"+transp_arch_temp+"\No_Data,FED_AID_PRIM_IND,-1,-1;\
        DRAIN_CNT \"DRAIN_CNT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,DRAIN_CNT,-1,-1,"+transp_arch_temp+"\No_Data,DRAIN_CNT,-1,-1;\
        GDRAIL_CNT \"GDRAIL_CNT\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,GDRAIL_CNT,-1,-1,"+transp_arch_temp+"\No_Data,GDRAIL_CNT,-1,-1;\
        PVMNT_TRTMT_DATA \"PVMNT_TRTMT_DATA\" true true false 2 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,PVMNT_TRTMT_DATA,-1,-1,"+transp_arch_temp+"\No_Data,PVMNT_TRTMT_DATA,-1,-1;\
        PVMNT_IND \"PVMNT_IND\" true true false 1 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,PVMNT_IND,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,PVMNT_IND,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,PVMNT_IND,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,PVMNT_IND,-1,-1,"+transp_arch_temp+"\No_Data,PVMNT_IND,-1,-1;\
        IRI_YEAR \"IRI_YEAR\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,IRI_YEAR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,IRI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,IRI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,IRI_YEAR,-1,-1,"+transp_arch_temp+"\No_Data,IRI_YEAR,-1,-1;\
        OPI_YEAR \"OPI_YEAR\" true true false 4 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,OPI_YEAR,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,OPI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,OPI_YEAR,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,OPI_YEAR,-1,-1,"+transp_arch_temp+"\No_Data,OPI_YEAR,-1,-1;\
        IRI_RATING_TEXT \"IRI_RATING_TEXT\" true true false 9 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,IRI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\No_Data,IRI_RATING_TEXT,-1,-1;\
        OPI_RATING_TEXT \"OPI_RATING_TEXT\" true true false 9 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,OPI_RATING_TEXT,-1,-1,"+transp_arch_temp+"\No_Data,OPI_RATING_TEXT,-1,-1;\
        GEOMETRY_LEN \"GEOMETRY.LEN\" true true false 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,GEOMETRY_LEN,-1,-1,"+transp_arch_temp+"\No_Data,GEOMETRY_LEN,-1,-1;\
        IRI_Group \"IRI_Group\" true true false 15 Text 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,IRI_Group,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,IRI_Group,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,IRI_Group,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,IRI_Group,-1,-1,"+transp_arch_temp+"\No_Data,IRI_Group,-1,-1;\
        Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,"+transp_arch_temp+"\NHS_Interstate_Merge,Shape_Length,-1,-1,"+transp_arch_temp+"\NHS_NonInter_Merge,Shape_Length,-1,-1,"+transp_arch_temp+"\NonNHSGreater2000_Merge,Shape_Length,-1,-1,"+transp_arch_temp+"\NonNHSLesser2000_Merge,Shape_Length,-1,-1,"+transp_arch_temp+"\No_Data,Shape_Length,-1,-1")

        # Process: Make Feature Layer (12)
        arcpy.MakeFeatureLayer_management(RMSSEG_shp, RMSSEG_Layer, "", "", "ST_RT_NO ST_RT_NO VISIBLE NONE;\
        CTY_CODE CTY_CODE VISIBLE NONE;\
        DISTRICT_N DISTRICT_N VISIBLE NONE;\
        JURIS JURIS VISIBLE NONE;\
        SEG_NO SEG_NO VISIBLE NONE;\
        SEG_LNGTH_ SEG_LNGTH_ VISIBLE NONE;\
        SEQ_NO SEQ_NO VISIBLE NONE;\
        SUB_ROUTE SUB_ROUTE VISIBLE NONE;\
        YR_BUILT YR_BUILT VISIBLE NONE;\
        YR_RESURF YR_RESURF VISIBLE NONE;\
        DIR_IND DIR_IND VISIBLE NONE;\
        FAC_TYPE FAC_TYPE VISIBLE NONE;\
        TOTAL_WIDT TOTAL_WIDT VISIBLE NONE;\
        SURF_TYPE SURF_TYPE VISIBLE NONE;\
        LANE_CNT LANE_CNT VISIBLE NONE;\
        PARK_LANE PARK_LANE VISIBLE NONE;\
        DIVSR_TYPE DIVSR_TYPE VISIBLE NONE;\
        DIVSR_WIDT DIVSR_WIDT VISIBLE NONE;\
        COND_DATE COND_DATE VISIBLE NONE;\
        ROUGH_INDX ROUGH_INDX VISIBLE NONE;\
        PVMNT_COND PVMNT_COND VISIBLE NONE;\
        CUR_AADT CUR_AADT VISIBLE NONE;\
        ACCESS_CTR ACCESS_CTR VISIBLE NONE;\
        TOLL_CODE TOLL_CODE VISIBLE NONE;\
        STREET_NAM STREET_NAM VISIBLE NONE;\
        TRAF_RT_NO TRAF_RT_NO VISIBLE NONE;\
        TRAF_RT__1 TRAF_RT__1 VISIBLE NONE;\
        TRAF_RT__2 TRAF_RT__2 VISIBLE NONE;\
        BGN_DESC BGN_DESC VISIBLE NONE;\
        END_DESC END_DESC VISIBLE NONE;\
        MAINT_RESP MAINT_RESP VISIBLE NONE;\
        URBAN_RURA URBAN_RURA VISIBLE NONE;\
        NHS_IND NHS_IND VISIBLE NONE;\
        TANDEM_TRL TANDEM_TRL VISIBLE NONE;\
        ACCESS_TAN ACCESS_TAN VISIBLE NONE;\
        INTERST_NE INTERST_NE VISIBLE NONE;\
        NHPN_IND NHPN_IND VISIBLE NONE;\
        NORM_ADMIN NORM_ADMIN VISIBLE NONE;\
        NORM_TRAFF NORM_TRAFF VISIBLE NONE;\
        NORM_SHLD_ NORM_SHLD_ VISIBLE NONE;\
        MAPID MAPID VISIBLE NONE;\
        NLF_ID NLF_ID VISIBLE NONE;\
        SIDE_IND SIDE_IND VISIBLE NONE;\
        NLF_CNTL_B NLF_CNTL_B VISIBLE NONE;\
        NLF_CNTL_E NLF_CNTL_E VISIBLE NONE;\
        CUM_OFFSET CUM_OFFSET VISIBLE NONE;\
        CUM_OFFS_1 CUM_OFFS_1 VISIBLE NONE;\
        X_VALUE_BG X_VALUE_BG VISIBLE NONE;\
        Y_VALUE_BG Y_VALUE_BG VISIBLE NONE;\
        X_VALUE_EN X_VALUE_EN VISIBLE NONE;\
        Y_VALUE_EN Y_VALUE_EN VISIBLE NONE;\
        GRAPHIC_LE GRAPHIC_LE VISIBLE NONE;\
        KEY_UPDATE KEY_UPDATE VISIBLE NONE;\
        ATTR_UPDAT ATTR_UPDAT VISIBLE NONE;\
        OVERALL_PV OVERALL_PV VISIBLE NONE;\
        SEG_STATUS SEG_STATUS VISIBLE NONE;\
        PAVMT_CYCL PAVMT_CYCL VISIBLE NONE;\
        DRAIN_CYCL DRAIN_CYCL VISIBLE NONE;\
        GDRAIL_CYC GDRAIL_CYC VISIBLE NONE;\
        DISTRICT_S DISTRICT_S VISIBLE NONE;\
        TRT_TYPE_N TRT_TYPE_N VISIBLE NONE;\
        PA_BYWAY_I PA_BYWAY_I VISIBLE NONE;\
        STREET_N_1 STREET_N_1 VISIBLE NONE;\
        TRAF_RT__3 TRAF_RT__3 VISIBLE NONE;\
        TRAF_RT__4 TRAF_RT__4 VISIBLE NONE;\
        TRAF_RT__5 TRAF_RT__5 VISIBLE NONE;\
        STREET_N_2 STREET_N_2 VISIBLE NONE;\
        TRAF_RT__6 TRAF_RT__6 VISIBLE NONE;\
        TRAF_RT__7 TRAF_RT__7 VISIBLE NONE;\
        TRAF_RT__8 TRAF_RT__8 VISIBLE NONE;\
        TRXN_FLAG TRXN_FLAG VISIBLE NONE;\
        ROUTE_DIR ROUTE_DIR VISIBLE NONE;\
        BUS_PLAN_N BUS_PLAN_N VISIBLE NONE;\
        EXP_WAY_NE EXP_WAY_NE VISIBLE NONE;\
        HPMS_SAMP_ HPMS_SAMP_ VISIBLE NONE;\
        MILE_POINT MILE_POINT VISIBLE NONE;\
        IS_STRUCTU IS_STRUCTU VISIBLE NONE;\
        GOVT_LVL_C GOVT_LVL_C VISIBLE NONE;\
        HOV_TYPE HOV_TYPE VISIBLE NONE;\
        HOV_LANES HOV_LANES VISIBLE NONE;\
        PAR_SEG_IN PAR_SEG_IN VISIBLE NONE;\
        HPMS_DIVSR HPMS_DIVSR VISIBLE NONE;\
        IRI_CUR_FL IRI_CUR_FL VISIBLE NONE;\
        DRAIN_SWT DRAIN_SWT VISIBLE NONE;\
        GDRAIL_SWT GDRAIL_SWT VISIBLE NONE;\
        PAVMT_SWT PAVMT_SWT VISIBLE NONE;\
        SHLD_COND_ SHLD_COND_ VISIBLE NONE;\
        FED_AID_PR FED_AID_PR VISIBLE NONE;\
        DRAIN_CNT DRAIN_CNT VISIBLE NONE;\
        GDRAIL_CNT GDRAIL_CNT VISIBLE NONE;\
        PVMNT_TRTM PVMNT_TRTM VISIBLE NONE;\
        PVMNT_IND PVMNT_IND VISIBLE NONE;\
        GEOMETRY_L GEOMETRY_L VISIBLE NONE;\
        Shape_Leng Shape_Leng VISIBLE NONE;\
        Shape_le_1 Shape_le_1 VISIBLE NONE;\
        IRI_Group IRI_Group VISIBLE NONE")

        # Process: Select Layer By Attribute (9)
        arcpy.SelectLayerByAttribute_management(RMSSEG_Layer, "NEW_SELECTION", "\"ST_RT_NO\" LIKE 'Q%' OR NOT \"CTY_CODE\" = '66'")

        # Process: Delete Rows (2)
        arcpy.DeleteRows_management(RMSSEG_Layer)

        # Process: Select (27)
        arcpy.Select_analysis(RMSSEG_Layer, YEAR_MONTH_DAY_RMSSEG_shp, "")

        # Process: Delete (3)
        arcpy.Delete_management(YEAR_MONTH_DAY_Bridges_BMS_State_Dssvl_shp, "ShapeFile")


        ######################################################################################################################################################################################################################################

        ######################################################################################################################################################################################################################################

        Updated_Folder = r"\\Ycpcfs\wp-doc\GIS\York_County_GIS_coordination\implementation_plan\EnterprisePlan_Phase_II\Enterprise_Implementation\Enterprise_GDB_Physical_Design\DATA_LOAD_MODELS\RMS_Bridge\Enterprise_Load.gdb"

        message ("Copying RMS and Bridge Data to QA\QC Database")
        arcpy.FeatureClassToFeatureClass_conversion(YEAR_MONTH_DAY_Bridges_BMS_Local_shp, Updated_Folder , "Bridges_BMS_Local")
        arcpy.FeatureClassToFeatureClass_conversion(YEAR_MONTH_DAY_Bridges_BMS_STATE_shp, Updated_Folder , "Bridges_BMS_STATE")
        arcpy.FeatureClassToFeatureClass_conversion(YEAR_MONTH_DAY_RMSSEG_shp, Updated_Folder , "RMSSEG")
        arcpy.FeatureClassToFeatureClass_conversion(YEAR_MONTH_DAY_RMSADMIN_shp, Updated_Folder , "RMSADMIN")
        arcpy.FeatureClassToFeatureClass_conversion(YEAR_MONTH_DAY_RMSTRAFFIC_shp, Updated_Folder , "RMSTRAFFIC")

        # Target SDE Feature classes
        York_Edit_GIS_TRANSP_RMS_Traf          = os.path.join(York_Edit_SDE,"York_Edit.GIS.TRANSP_RMS_Traf")
        York_Edit_GIS_TRANSP_RMS_Admin         = os.path.join(York_Edit_SDE,"York_Edit.GIS.TRANSP_RMS_Admin")
        York_Edit_GIS_TRANSP_RMS_Seg           = os.path.join(York_Edit_SDE,"York_Edit.GIS.TRANSP_RMS_Seg")
        York_Edit_GIS_TRANSP_Bridges_BMS_State = os.path.join(York_Edit_SDE,"York_Edit.GIS.TRANSP_Bridges_BMS_State")
        York_Edit_GIS_TRANSP_Bridges_BMS_Local = os.path.join(York_Edit_SDE,"York_Edit.GIS.TRANSP_Bridges_BMS_Local")

        message ("Deleting\Appending RMS and BMS Data to York Edit Database")
        message ("Deleting\Appending RMS_Traf")
        # Process: Delete Features
        arcpy.DeleteFeatures_management(York_Edit_GIS_TRANSP_RMS_Traf)

        arcpy.Append_management(""+Updated_Folder+"\RMSTRAFFIC",York_Edit_GIS_TRANSP_RMS_Traf, "NO_TEST",\
        "RMSTRAFFIC_LRS_KEY \"RMSTRAFFIC_LRS_KEY\" true true false 23 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,RMSTRAFFIC_LRS_KEY,-1,-1;\
        ST_RT_NO \"ST_RT_NO\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,ST_RT_NO,-1,-1;\
        CTY_CODE \"CTY_CODE\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,CTY_CODE,-1,-1;\
        DISTRICT_NO \"DISTRICT_NO\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,DISTRICT_NO,-1,-1;\
        JURIS \"JURIS\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,JURIS,-1,-1;\
        SEG_BGN \"SEG_BGN\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,SEG_BGN,-1,-1;\
        OFFSET_BGN \"OFFSET_BGN\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,OFFSET_BGN,-1,-1;\
        SEG_END \"SEG_END\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,SEG_END,-1,-1;\
        OFFSET_END \"OFFSET_END\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,OFFSET_END,-1,-1;\
        SEG_PT_BGN \"SEG_PT_BGN\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,SEG_PT_BGN,-1,-1;\
        SEG_PT_END \"SEG_PT_END\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,SEG_PT_END,-1,-1;\
        SEG_LNGTH_FEET \"SEG_LNGTH_FEET\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,SEG_LNGTH_FEET,-1,-1;\
        SEQ_NO \"SEQ_NO\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,SEQ_NO,-1,-1;\
        CUR_AADT \"CUR_AADT\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,CUR_AADT,-1,-1;\
        ADTT_CUR \"ADTT_CUR\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,ADTT_CUR,-1,-1;\
        TRK_PCT \"TRK_PCT\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,TRK_PCT,-1,-1;\
        WKDY_TRK_CUR \"WKDY_TRK_CUR\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,WKDY_TRK_CUR,-1,-1;\
        ADLR_TRK_CUR \"ADLR_TRK_CUR\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,ADLR_TRK_CUR,-1,-1;\
        ADLF_TRK_CUR \"ADLF_TRK_CUR\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,ADLF_TRK_CUR,-1,-1;\
        BASE_YR_CLS_CNT \"BASE_YR_CLS_CNT\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,BASE_YR_CLS_CNT,-1,-1;\
        BASE_ADT \"BASE_ADT\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,BASE_ADT,-1,-1;\
        ADTT_BASE \"ADTT_BASE\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,ADTT_BASE,-1,-1;\
        WKDY_TRK_BASE \"WKDY_TRK_BASE\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,WKDY_TRK_BASE,-1,-1;\
        ADLR_TRK_BASE \"ADLR_TRK_BASE\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,ADLR_TRK_BASE,-1,-1;\
        ADLF_TRK_BASE \"ADLF_TRK_BASE\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,ADLF_TRK_BASE,-1,-1;\
        BASE_ADT_YR \"BASE_ADT_YR\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,BASE_ADT_YR,-1,-1;\
        DLY_VMT \"DLY_VMT\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,DLY_VMT,-1,-1;\
        DLY_TRK_VMT \"DLY_TRK_VMT\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,DLY_TRK_VMT,-1,-1;\
        K_FACTOR \"K_FACTOR\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,K_FACTOR,-1,-1;\
        D_FACTOR \"D_FACTOR\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,D_FACTOR,-1,-1;\
        T_FACTOR \"T_FACTOR\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,T_FACTOR,-1,-1;\
        VOL_CNT_KEY \"VOL_CNT_KEY\" true true false 14 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,VOL_CNT_KEY,-1,-1;\
        VOL_CNT_DATE \"VOL_CNT_DATE\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,VOL_CNT_DATE,-1,-1;\
        RAW_CNT_HIST_DATE \"RAW_CNT_HIST_DATE\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,RAW_CNT_HIST_DATE,-1,-1;\
        TRAFF_PATT_GRP \"TRAFF_PATT_GRP\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,TRAFF_PATT_GRP,-1,-1;\
        DUR_CLS_CNT \"DUR_CLS_CNT\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,DUR_CLS_CNT,-1,-1;\
        TYPE_OF_CNT \"TYPE_OF_CNT\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,TYPE_OF_CNT,-1,-1;\
        DIR_IND \"DIR_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,DIR_IND,-1,-1;\
        MAPID \"MAPID\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,MAPID,-1,-1;\
        NLF_ID \"NLF_ID\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,NLF_ID,-1,-1;\
        SIDE_IND \"SIDE_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,SIDE_IND,-1,-1;\
        NLF_CNTL_BGN \"NLF_CNTL_BGN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,NLF_CNTL_BGN,-1,-1;\
        NLF_CNTL_END \"NLF_CNTL_END\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,NLF_CNTL_END,-1,-1;\
        CUM_OFFSET_BGN_T1 \"CUM_OFFSET_BGN_T1\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,CUM_OFFSET_BGN_T1,-1,-1;\
        CUM_OFFSET_END_T1 \"CUM_OFFSET_END_T1\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,CUM_OFFSET_END_T1,-1,-1;\
        RECORD_UPDATE \"RECORD_UPDATE\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,RECORD_UPDATE,-1,-1;\
        GEOMETRY_LEN \"GEOMETRY_LEN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSTRAFFIC,GEOMETRY_LEN,-1,-1;\
        CREATE_DATE \"CREATE_DATE\" false true false 36 Date 0 0 ,First,#;\
        MODIFY_DATE \"MODIFY_DATE\" false true false 36 Date 0 0 ,First,#;\
        EDIT_NAME \"EDIT_NAME\" false true false 20 Text 0 0 ,First,#;\
        EDIT_TYPE \"EDIT_TYPE\" true true false 30 Text 0 0 ,First,#;\
        GlobalID \"GlobalID\" false false false 38 GlobalID 0 0 ,First,#;\
        Shape.STLength() \"Shape.STLength()\" false false true 0 Double 0 0 ,First,#""", subtype="")

        message ("Deleting\Appending RMS_Admin")
        # Process: Delete Features (3)
        arcpy.DeleteFeatures_management(York_Edit_GIS_TRANSP_RMS_Admin)

        # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
        # The following inputs are layers or table views: "York_Edit.GIS.TRANSP_RMS_Admin"
        arcpy.Append_management(""+Updated_Folder+"\"RMSADMIN", York_Edit_GIS_TRANSP_RMS_Admin, "NO_TEST",\
         "ST_RT_NO \"ST_RT_NO\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,ST_RT_NO,-1,-1;\
         CTY_CODE \"CTY_CODE\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,CTY_CODE,-1,-1;\
         DISTRICT_NO \"DISTRICT_NO\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,DISTRICT_NO,-1,-1;\
         JURIS \"JURIS\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,JURIS,-1,-1;\
         SEG_BGN \"SEG_BGN\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,SEG_BGN,-1,-1;\
         OFFSET_BGN \"OFFSET_BGN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSADMIN,OFFSET_BGN,-1,-1;\
         SEG_END \"SEG_END\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,SEG_END,-1,-1;\
         OFFSET_END \"OFFSET_END\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSADMIN,OFFSET_END,-1,-1;\
         SEG_LNGTH_FEET \"SEG_LNGTH_FEET\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSADMIN,SEG_LNGTH_FEET,-1,-1;\
         SEG_PT_BGN \"SEG_PT_BGN\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,SEG_PT_BGN,-1,-1;\
         SEG_PT_END \"SEG_PT_END\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,SEG_PT_END,-1,-1;\
         SEQ_NO \"SEQ_NO\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSADMIN,SEQ_NO,-1,-1;\
         MAINT_FUNC_CLS \"MAINT_FUNC_CLS\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,MAINT_FUNC_CLS,-1,-1;\
         POST_BOND_IND \"POST_BOND_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,POST_BOND_IND,-1,-1;\
         SPEED_LIMIT \"SPEED_LIMIT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSADMIN,SPEED_LIMIT,-1,-1;\
         FED_AID_SYS \"FED_AID_SYS\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,FED_AID_SYS,-1,-1;\
         FED_AID_URBAN_AREA \"FED_AID_URBAN_AREA\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,FED_AID_URBAN_AREA,-1,-1;\
         FUNC_CLS \"FUNC_CLS\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,FUNC_CLS,-1,-1;\
         FED_ID \"FED_ID\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,FED_ID,-1,-1;\
         FED_AID_SYS_STATUS \"FED_AID_SYS_STATUS\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,FED_AID_SYS_STATUS,-1,-1;\
         MAPID \"MAPID\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSADMIN,MAPID,-1,-1;\
         NLF_ID \"NLF_ID\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSADMIN,NLF_ID,-1,-1;\
         SIDE_IND \"SIDE_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,SIDE_IND,-1,-1;\
         NLF_CNTL_BGN \"NLF_CNTL_BGN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSADMIN,NLF_CNTL_BGN,-1,-1;\
         NLF_CNTL_END \"NLF_CNTL_END\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSADMIN,NLF_CNTL_END,-1,-1;\
         CUM_OFFSET_BGN_T1 \"CUM_OFFSET_BGN_T1\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSADMIN,CUM_OFFSET_BGN_T1,-1,-1;\
         CUM_OFFSET_END_T1 \"CUM_OFFSET_END_T1\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSADMIN,CUM_OFFSET_END_T1,-1,-1;\
         RECORD_UPDATE \"RECORD_UPDATE\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,RECORD_UPDATE,-1,-1;\
         FIPS_AREA_CODE \"FIPS_AREA_CODE\" true true false 5 Text 0 0 ,First,#,"+Updated_Folder+"\RMSADMIN,FIPS_AREA_CODE,-1,-1;\
         GEOMETRY_LEN \"GEOMETRY_LEN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSADMIN,GEOMETRY_LEN,-1,-1;\
         CREATE_DATE \"CREATE_DATE\" false true false 36 Date 0 0 ,First,#;\
         MODIFY_DATE \"MODIFY_DATE\" false true false 36 Date 0 0 ,First,#;\
         EDIT_NAME \"EDIT_NAME\" false true false 20 Text 0 0 ,First,#;\
         EDIT_TYPE \"EDIT_TYPE\" true true false 30 Text 0 0 ,First,#;\
         GlobalID \"GlobalID\" false false false 38 GlobalID 0 0 ,First,#;\
         Shape.STLength() \"Shape.STLength()\" false false true 0 Double 0 0 ,First,#""", subtype="")

        message ("Deleting\Appending RMS_Seg")
        # Process: Delete Features (2)
        arcpy.DeleteFeatures_management(York_Edit_GIS_TRANSP_RMS_Seg)

        arcpy.Append_management(""+Updated_Folder+"\RMSSEG", York_Edit_GIS_TRANSP_RMS_Seg, "NO_TEST",\
        "ST_RT_NO \"ST_RT_NO\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,ST_RT_NO,-1,-1;\
        CTY_CODE \"CTY_CODE\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,CTY_CODE,-1,-1;\
        DISTRICT_NO \"DISTRICT_NO\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,DISTRICT_NO,-1,-1;\
        JURIS \"JURIS\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,JURIS,-1,-1;\
        SEG_NO \"SEG_NO\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,SEG_NO,-1,-1;\
        SEG_LNGTH_FEET \"SEG_LNGTH_FEET\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,SEG_LNGTH_FEET,-1,-1;\
        SEQ_NO \"SEQ_NO\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSSEG,SEQ_NO,-1,-1;\
        SUB_ROUTE \"SUB_ROUTE\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,SUB_ROUTE,-1,-1;\
        YR_BUILT \"YR_BUILT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,YR_BUILT,-1,-1;\
        YR_RESURF \"YR_RESURF\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,YR_RESURF,-1,-1;\
        DIR_IND \"DIR_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,DIR_IND,-1,-1;\
        FAC_TYPE \"FAC_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,FAC_TYPE,-1,-1;\
        TOTAL_WIDTH \"TOTAL_WIDTH\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,TOTAL_WIDTH,-1,-1;\
        SURF_TYPE \"SURF_TYPE\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,SURF_TYPE,-1,-1;\
        LANE_CNT \"LANE_CNT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,LANE_CNT,-1,-1;\
        PARK_LANE \"PARK_LANE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,PARK_LANE,-1,-1;\
        DIVSR_TYPE \"DIVSR_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,DIVSR_TYPE,-1,-1;\
        DIVSR_WIDTH \"DIVSR_WIDTH\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,DIVSR_WIDTH,-1,-1;\
        COND_DATE \"COND_DATE\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,COND_DATE,-1,-1;\
        ROUGH_INDX \"ROUGH_INDX\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,ROUGH_INDX,-1,-1;\
        PVMNT_COND_RATE \"PVMNT_COND_RATE\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,PVMNT_COND_RATE,-1,-1;\
        CUR_AADT \"CUR_AADT\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSSEG,CUR_AADT,-1,-1;\
        ACCESS_CTRL \"ACCESS_CTRL\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,ACCESS_CTRL,-1,-1;\
        TOLL_CODE \"TOLL_CODE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,TOLL_CODE,-1,-1;\
        STREET_NAME \"STREET_NAME\" true true false 25 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,STREET_NAME,-1,-1;\
        TRAF_RT_NO_PREFIX \"TRAF_RT_NO_PREFIX\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,TRAF_RT_NO_PREFIX,-1,-1;\
        TRAF_RT_NO \"TRAF_RT_NO\" true true false 3 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,TRAF_RT_NO,-1,-1;\
        TRAF_RT_NO_SUF \"TRAF_RT_NO_SUF\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,TRAF_RT_NO_SUF,-1,-1;\
        BGN_DESC \"BGN_DESC\" true true false 20 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,BGN_DESC,-1,-1;\
        END_DESC \"END_DESC\" true true false 20 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,END_DESC,-1,-1;\
        MAINT_RESPON_IND \"MAINT_RESPON_IND\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,MAINT_RESPON_IND,-1,-1;\
        URBAN_RURAL \"URBAN_RURAL\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,URBAN_RURAL,-1,-1;\
        NHS_IND \"NHS_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,NHS_IND,-1,-1;\
        TANDEM_TRLR_TRK \"TANDEM_TRLR_TRK\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,TANDEM_TRLR_TRK,-1,-1;\
        ACCESS_TANDEM_TRLR \"ACCESS_TANDEM_TRLR\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,ACCESS_TANDEM_TRLR,-1,-1;\
        INTERST_NETWRK_IND \"INTERST_NETWRK_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,INTERST_NETWRK_IND,-1,-1;\
        NHPN_IND \"NHPN_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,NHPN_IND,-1,-1;\
        NORM_ADMIN_BGN \"NORM_ADMIN_BGN\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,NORM_ADMIN_BGN,-1,-1;\
        NORM_TRAFF_BGN \"NORM_TRAFF_BGN\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,NORM_TRAFF_BGN,-1,-1;\
        NORM_SHLD_BGN \"NORM_SHLD_BGN\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,NORM_SHLD_BGN,-1,-1;\
        MAPID \"MAPID\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSSEG,MAPID,-1,-1;\
        NLF_ID \"NLF_ID\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\RMSSEG,NLF_ID,-1,-1;\
        SIDE_IND \"SIDE_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,SIDE_IND,-1,-1;\
        NLF_CNTL_BGN \"NLF_CNTL_BGN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,NLF_CNTL_BGN,-1,-1;\
        NLF_CNTL_END \"NLF_CNTL_END\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,NLF_CNTL_END,-1,-1;\
        CUM_OFFSET_BGN_T1 \"CUM_OFFSET_BGN_T1\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,CUM_OFFSET_BGN_T1,-1,-1;\
        CUM_OFFSET_END_T1 \"CUM_OFFSET_END_T1\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,CUM_OFFSET_END_T1,-1,-1;\
        X_VALUE_BGN \"X_VALUE_BGN\" true true false 15 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,X_VALUE_BGN,-1,-1;\
        Y_VALUE_BGN \"Y_VALUE_BGN\" true true false 15 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,Y_VALUE_BGN,-1,-1;\
        X_VALUE_END \"X_VALUE_END\" true true false 15 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,X_VALUE_END,-1,-1;\
        Y_VALUE_END \"Y_VALUE_END\" true true false 15 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,Y_VALUE_END,-1,-1;\
        GRAPHIC_LENGTH \"GRAPHIC_LENGTH\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,GRAPHIC_LENGTH,-1,-1;\
        KEY_UPDATE \"KEY_UPDATE\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,KEY_UPDATE,-1,-1;\
        ATTR_UPDATE \"ATTR_UPDATE\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,ATTR_UPDATE,-1,-1;\
        OVERALL_PVMNT_IDX \"OVERALL_PVMNT_IDX\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,OVERALL_PVMNT_IDX,-1,-1;\
        SEG_STATUS \"SEG_STATUS\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,SEG_STATUS,-1,-1;\
        PAVMT_CYCLE \"PAVMT_CYCLE\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,PAVMT_CYCLE,-1,-1;\
        DRAIN_CYCLE \"DRAIN_CYCLE\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,DRAIN_CYCLE,-1,-1;\
        GDRAIL_CYCLE \"GDRAIL_CYCLE\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,GDRAIL_CYCLE,-1,-1;\
        DISTRICT_SPECIAL \"DISTRICT_SPECIAL\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,DISTRICT_SPECIAL,-1,-1;\
        TRT_TYPE_NETWRK \"TRT_TYPE_NETWRK\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,TRT_TYPE_NETWRK,-1,-1;\
        PA_BYWAY_IND \"PA_BYWAY_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,PA_BYWAY_IND,-1,-1;\
        STREET_NAME2 \"STREET_NAME2\" true true false 25 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,STREET_NAME2,-1,-1;\
        TRAF_RT_NO_PREFIX2 \"TRAF_RT_NO_PREFIX2\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,TRAF_RT_NO_PREFIX2,-1,-1;\
        TRAF_RT_NO2 \"TRAF_RT_NO2\" true true false 3 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,TRAF_RT_NO2,-1,-1;\
        TRAF_RT_NO_SUF2 \"TRAF_RT_NO_SUF2\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,TRAF_RT_NO_SUF2,-1,-1;\
        STREET_NAME3 \"STREET_NAME3\" true true false 25 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,STREET_NAME3,-1,-1;\
        TRAF_RT_NO_PREFIX3 \"TRAF_RT_NO_PREFIX3\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,TRAF_RT_NO_PREFIX3,-1,-1;\
        TRAF_RT_NO3 \"TRAF_RT_NO3\" true true false 3 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,TRAF_RT_NO3,-1,-1;\
        TRAF_RT_NO_SUF3 \"TRAF_RT_NO_SUF3\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,TRAF_RT_NO_SUF3,-1,-1;\
        TRXN_FLAG \"TRXN_FLAG\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,TRXN_FLAG,-1,-1;\
        ROUTE_DIR \"ROUTE_DIR\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,ROUTE_DIR,-1,-1;\
        BUS_PLAN_NETWRK \"BUS_PLAN_NETWRK\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,BUS_PLAN_NETWRK,-1,-1;\
        EXP_WAY_NETWRK \"EXP_WAY_NETWRK\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,EXP_WAY_NETWRK,-1,-1;\
        HPMS_SAMP_CNT \"HPMS_SAMP_CNT\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\RMSSEG,HPMS_SAMP_CNT,-1,-1;\
        MILE_POINT \"MILE_POINT\" true true false 5 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,MILE_POINT,-1,-1;\
        IS_STRUCTURE \"IS_STRUCTURE\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\RMSSEG,IS_STRUCTURE,-1,-1;\
        GOVT_LVL_CTRL \"GOVT_LVL_CTRL\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\RMSSEG,GOVT_LVL_CTRL,-1,-1;\
        HOV_TYPE \"HOV_TYPE\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\RMSSEG,HOV_TYPE,-1,-1;\
        HOV_LANES \"HOV_LANES\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\RMSSEG,HOV_LANES,-1,-1;\
        PAR_SEG_IND \"PAR_SEG_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,PAR_SEG_IND,-1,-1;\
        HPMS_DIVSR_TYPE \"HPMS_DIVSR_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,HPMS_DIVSR_TYPE,-1,-1;\
        IRI_CUR_FLAG \"IRI_CUR_FLAG\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,IRI_CUR_FLAG,-1,-1;\
        DRAIN_SWT \"DRAIN_SWT\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,DRAIN_SWT,-1,-1;\
        GDRAIL_SWT \"GDRAIL_SWT\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,GDRAIL_SWT,-1,-1;\
        PAVMT_SWT \"PAVMT_SWT\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,PAVMT_SWT,-1,-1;\
        SHLD_COND_STATUS \"SHLD_COND_STATUS\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,SHLD_COND_STATUS,-1,-1;\
        FED_AID_PRIM_IND \"FED_AID_PRIM_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,FED_AID_PRIM_IND,-1,-1;\
        DRAIN_CNT \"DRAIN_CNT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,DRAIN_CNT,-1,-1;\
        GDRAIL_CNT \"GDRAIL_CNT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,GDRAIL_CNT,-1,-1;\
        PVMNT_TRTMT_DATA \"PVMNT_TRTMT_DATA\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,PVMNT_TRTMT_DATA,-1,-1;\
        PVMNT_IND \"PVMNT_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,PVMNT_IND,-1,-1;\
        GEOMETRY_LEN \"GEOMETRY_LEN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\RMSSEG,GEOMETRY_LEN,-1,-1;\
        IRI_Group \"IRI_Group\" true true false 15 Text 0 0 ,First,#,"+Updated_Folder+"\RMSSEG,IRI_Group,-1,-1;\
        CREATE_DATE \"CREATE_DATE\" false true false 36 Date 0 0 ,First,#;\
        MODIFY_DATE \"MODIFY_DATE\" false true false 36 Date 0 0 ,First,#;\
        EDIT_NAME \"EDIT_NAME\" false true false 20 Text 0 0 ,First,#;\
        EDIT_TYPE \"EDIT_TYPE\" true true false 30 Text 0 0 ,First,#;\
        GlobalID \"GlobalID\" false false false 38 GlobalID 0 0 ,First,#;\
        Shape.STLength() \"Shape.STLength()\" false false true 0 Double 0 0 ,First,#""", subtype="")

        message ("Deleting\Appending BMS_State")
        # Process: Delete Features (4)
        arcpy.DeleteFeatures_management(York_Edit_GIS_TRANSP_Bridges_BMS_State)

        arcpy.Append_management(""+Updated_Folder+"\Bridges_BMS_STATE", York_Edit_GIS_TRANSP_Bridges_BMS_State, "NO_TEST",\
         "CTY_CODE \"CTY_CODE\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,CTY_CODE,-1,-1;\
         ST_RT_NO \"SEG_NO\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,ST_RT_NO,-1,-1;\
         SEG_NO \"SEG_NO\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SEG_NO,-1,-1;\
         OFFSET \"OFFSET\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,OFFSET,-1,-1;\
         ADMIN_JURIS \"ADMIN_JURIS\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,ADMIN_JURIS,-1,-1;\
         DEC_LAT \"DEC_LAT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DEC_LAT,-1,-1;\
         DEC_LONG \"DEC_LONG\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DEC_LONG,-1,-1;\
         BRIDGE_ID \"BRIDGE_ID\" true true false 30 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,BRIDGE_ID,-1,-1;\
         FEATINT \"FEATINT\" true true false 24 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,FEATINT,-1,-1;\
         DISTRICT \"DISTRICT\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DISTRICT,-1,-1;\
         FACILITY \"FACILITY\" true true false 18 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,FACILITY,-1,-1;\
         LOCATION \"LOCATION\" true true false 25 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,LOCATION,-1,-1;\
         OWNER \"OWNER\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,OWNER,-1,-1;\
         YEARBUILT \"YEARBUILT\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,YEARBUILT,-1,-1;\
         YEARRECON \"YEARRECON\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,YEARRECON,-1,-1;\
         SERVTYPON \"SERVTYPON\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SERVTYPON,-1,-1;\
         SERVTYPUND \"SERVTYPUND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SERVTYPUND,-1,-1;\
         MAINSPANS \"MAINSPANS\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,MAINSPANS,-1,-1;\
         APPSPANS \"APPSPANS\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,APPSPANS,-1,-1;\
         LENGTH \"LENGTH\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,LENGTH,-1,-1;\
         DECKWIDTH \"DECKWIDTH\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DECKWIDTH,-1,-1;\
         DKSURFTYPE \"DKSURFTYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DKSURFTYPE,-1,-1;\
         DKMEMBTYPE \"DKMEMBTYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DKMEMBTYPE,-1,-1;\
         DKPROTECT \"DKPROTECT\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DKPROTECT,-1,-1;\
         MAIN_WS_THICKNESS \"MAIN_WS_THICKNESS\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,MAIN_WS_THICKNESS,-1,-1;\
         APPR_DKSURFTYPE \"APPR_DKSURFTYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,APPR_DKSURFTYPE,-1,-1;\
         APPR_DKMEMBTYPE \"APPR_DKMEMBTYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,APPR_DKMEMBTYPE,-1,-1;\
         APPR_DKPROTECT \"APPR_DKPROTECT\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,APPR_DKPROTECT,-1,-1;\
         APPR_WS_THICKNESS \"APPR_WS_THICKNESS\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,APPR_WS_THICKNESS,-1,-1;\
         FED_FUND \"FED_FUND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,FED_FUND,-1,-1;\
         DECK_RECON_WORK_TYPE \"DECK_RECON_WORK_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DECK_RECON_WORK_TYPE,-1,-1;\
         SUP_RECON_WORK_TYPE \"SUP_RECON_WORK_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SUP_RECON_WORK_TYPE,-1,-1;\
         SUB_RECON_WORK_TYPE \"SUB_RECON_WORK_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SUB_RECON_WORK_TYPE,-1,-1;\
         DEPT_MAIN_MATERIAL_TYPE \"DEPT_MAIN_MATERIAL_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DEPT_MAIN_MATERIAL_TYPE,-1,-1;\
         DEPT_MAIN_PHYSICAL_TYPE \"DEPT_MAIN_PHYSICAL_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DEPT_MAIN_PHYSICAL_TYPE,-1,-1;\
         DEPT_MAIN_SPAN_INTERACTION \"DEPT_MAIN_SPAN_INTERACTION\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DEPT_MAIN_SPAN_INTERACTION,-1,-1;\
         DEPT_MAIN_STRUC_CONFIG \"DEPT_MAIN_STRUC_CONFIG\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DEPT_MAIN_STRUC_CONFIG,-1,-1;\
         DEPT_APPR_MATERIAL_TYPE \"DEPT_APPR_MATERIAL_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DEPT_APPR_MATERIAL_TYPE,-1,-1;\
         DEPT_APPR_PHYSICAL_TYPE \"DEPT_APPR_PHYSICAL_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DEPT_APPR_PHYSICAL_TYPE,-1,-1;\
         DEPT_APPR_SPAN_INTERACTION \"DEPT_APPR_SPAN_INTERACTION\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DEPT_APPR_SPAN_INTERACTION,-1,-1;\
         DEPT_APPR_STRUC_CONFIG \"DEPT_APPR_STRUC_CONFIG\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DEPT_APPR_STRUC_CONFIG,-1,-1;\
         SUB_AGENCY \"SUB_AGENCY\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SUB_AGENCY,-1,-1;\
         MAINT_RESP_DESC \"MAINT_RESP_DESC\" true true false 24 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,MAINT_RESP_DES,-1,-1;\
         CRIT_FACILITY \"CRIT_FACILITY\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,CRIT_FACILITY,-1,-1;\
         APPR_PAVEMENT_WIDTH \"APPR_PAVEMENT_WIDTH\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,APPR_PAVEMENT_WIDTH,-1,-1;\
         COVERED_BRIDGE \"COVERED_BRIDGE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,COVERED_BRIDGE,-1,-1;\
         FLOOD_INSP \"FLOOD_INSP\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,FLOOD_INSP,-1,-1;\
         DEPT_DKSTRUCTYP \"DEPT_DKSTRUCTYP\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DEPT_DKSTRUCTYP,-1,-1;\
         BYPASSLEN \"BYPASSLEN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,BYPASSLEN,-1,-1;\
         AROADWIDTH \"AROADWIDTH\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,AROADWIDTH,-1,-1;\
         ROADWIDTH \"ROADWIDTH\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,ROADWIDTH,-1,-1;\
         MIN_OVER_VERT_CLEAR_RIGHT \"MIN_OVER_VERT_CLEAR_RIGHT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,MIN_OVER_VERT_CLEAR_RIGHT,-1,-1;\
         MIN_OVER_VERT_CLEAR_LEFT \"MIN_OVER_VERT_CLEAR_LEFT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,MIN_OVER_VERT_CLEAR_RIGHT,-1,-1;\
         POST_LIMIT_WEIGHT \"POST_LIMIT_WEIGHT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,POST_LIMIT_WEIGHT,-1,-1;\
         POST_LIMIT_COMB \"POST_LIMIT_COMB\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,POST_LIMIT_COMB,-1,-1;\
         INSPDATE \"INSPDATE\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,INSPDATE,-1,-1;\
         BRINSPFREQ \"BRINSPFREQ\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,BRINSPFREQ,-1,-1;\
         POST_STATUS \"POST_STATUS\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,POST_STATUS,-1,-1;\
         NBI_RATING \"NBI_RATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,NBI_RATING,-1,-1;\
         SUFF_RATE \"SUFF_RATE\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SUFF_RATE,-1,-1;\
         MAINT_DEF_RATE \"MAINT_DEF_RATE\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,MAINT_DEF_RATE,-1,-1;\
         HBRR_ELIG \"HBRR_ELIG\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,HBRR_ELIG,-1,-1;\
         JURIS \"JURIS\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,JURIS,-1,-1;\
         SEG_END \"SEG_END\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SEG_END,-1,-1;\
         OFFSET_END \"OFFSET_END\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,OFFSET_END,-1,-1;\
         SEG_PT_BGN \"SEG_PT_BGN\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SEG_PT_BGN,-1,-1;\
         SEG_PT_END \"SEG_PT_END\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SEG_PT_END,-1,-1;\
         SIDE_IND \"SIDE_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SIDE_IND,-1,-1;\
         NLF_ID \"NLF_ID\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,NLF_ID,-1,-1;\
         NLF_CNTL_BGN \"NLF_CNTL_BGN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,NLF_CNTL_BGN,-1,-1;\
         NLF_CNTL_END \"NLF_CNTL_END\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,NLF_CNTL_END,-1,-1;\
         CUM_OFFSET_BGN \"CUM_OFFSET_BGN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,CUM_OFFSET,-1,-1;\
         CUM_OFFSET_END \"CUM_OFFSET_END\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,CUM_OFFSET_END,-1,-1;\
         DKRATING \"DKRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DKRATING,-1,-1;\
         SUPRATING \"SUPRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SUPRATING,-1,-1;\
         SUBRATING \"SUBRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SUBRATING,-1,-1;\
         CULVRATING \"CULVRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,CULVRATING,-1,-1;\
         STATE_LOCAL \"STATE_LOCAL\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,STATE_LOCAL,-1,-1;\
         DECK_AREA \"DECK_AREA\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DECK_AREA,-1,-1;\
         BB_BRDGEID \"BB_BRDGEID\" true true false 15 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,BB_BRDGEID,-1,-1;\
         BB_PCT \"BB_PCT\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,BB_PCT,-1,-1;\
         BRIDGEMED \"BRIDGEMED\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,BRIDGEMED,-1,-1;\
         CUSTODIAN \"CUSTODIAN\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,CUSTODIAN,-1,-1;\
         DESIGNAPPR \"DESIGNAPPR\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DESIGNAPPR,-1,-1;\
         DESIGNMAIN \"DESIGNMAIN\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DESIGNMAIN,-1,-1;\
         DKSTRUCTYP \"DKSTRUCTYP\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DKSTRUCTYP,-1,-1;\
         FIPS_STATE \"FIPS_STATE\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,FIPS_STATE,-1,-1;\
         HCLRULT \"HCLRULT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,HCLRULT,-1,-1;\
         HCLRURT \"HCLRURT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,HCLRURT,-1,-1;\
         HISTSIGN \"HISTSIGN\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,HISTSIGN,-1,-1;\
         IMPLEN \"IMPLEN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,IMPLEN,-1,-1;\
         LFTBRNAVCL \"LFTBRNAVCL\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,LFTBRNAVCL,-1,-1;\
         LFTCURBSW \"LFTCURBSW\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,LFTCURBSW,-1,-1;\
         MATERIALAPPR \"MATERIALAPPR\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,MATERIALAPPR,-1,-1;\
         MATERIALMAIN \"MATERIALMAIN\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,MATERIALMAIN,-1,-1;\
         MAXSPAN \"MAXSPAN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,MAXSPAN,-1,-1;\
         NAVCNTROL \"NAVCNTROL\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,NAVCNTROL,-1,-1;\
         NAVHC \"NAVHC\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,NAVHC,-1,-1;\
         NAVVC \"NAVVC\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,NAVVC,-1,-1;\
         NBIIMPCOST \"NBIIMPCOST\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,NBIIMPCOST,-1,-1;\
         NBIRWCOST \"NBIRWCOST\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,NBIRWCOST,-1,-1;\
         NBISLEN \"NBISLEN\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,NBISLEN,-1,-1;\
         NBITOTCOST \"NBITOTCOST\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,NBITOTCOST,-1,-1;\
         NBIYRCOST \"NBIYRCOST\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,NBIYRCOST,-1,-1;\
         NSTATECODE \"NSTATECODE\" true true false 3 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,NSTATECODE,-1,-1;\
         PARALSTRUC \"PARALSTRUC\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,PARALSTRUC,-1,-1;\
         PLACECODE \"PLACECODE\" true true false 5 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,PLACECODE,-1,-1;\
         PROPWORK \"PROPWORK\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,PROPWORK,-1,-1;\
         REFHUC \"REFHUC\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,REFHUC,-1,-1;\
         REFVUC \"REFVUC\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,REFVUC,-1,-1;\
         RTCURBSW \"RTCURBSW\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,RTCURBSW,-1,-1;\
         SKEW \"SKEW\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SKEW,-1,-1;\
         STRFLARED \"STRFLARED\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,STRFLARED,-1,-1;\
         STRUCT_NUM \"STRUCT_NUM\" true true false 15 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,STRUCT_NUM,-1,-1;\
         SUMLANES \"SUMLANES\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SUMLANES,-1,-1;\
         TEMPSTRUC \"TEMPSTRUC\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,TEMPSTRUC,-1,-1;\
         VCLROVER \"VCLROVER\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,VCLROVER,-1,-1;\
         ADTFUTURE \"ADTFUTURE\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,ADTFUTURE,-1,-1;\
         ADTFUTYEAR \"ADTFUTYEAR\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,ADTFUTYEAR,-1,-1;\
         ADTTOTAL \"ADTTOTAL\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,ADTTOTAL,-1,-1;\
         ADTYEAR \"ADTYEAR\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,ADTYEAR,-1,-1;\
         DEFHWY \"DEFHWY\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DEFHWY,-1,-1;\
         DIRSUFFIX \"DIRSUFFIX\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DIRSUFFIX,-1,-1;\
         FUNCCLASS \"FUNCCLASS\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,FUNCCLASS,-1,-1;\
         HCLRINV \"HCLRINV\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,HCLRINV,-1,-1;\
         KIND_HWY \"KIND_HWY\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,KIND_HWY,-1,-1;\
         KMPOST \"KMPOST\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,KMPOST,-1,-1;\
         LANES \"LANES\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,LANES,-1,-1;\
         LEVL_SRVC \"LEVL_SRVC\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,LEVL_SRVC,-1,-1;\
         NHS_IND \"NHS_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,NHS_IND,-1,-1;\
         ON_UNDER \"ON_UNDER\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,ON_UNDER,-1,-1;\
         TOLLFAC \"TOLLFAC\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,TOLLFAC,-1,-1;\
         TRAFFICDIR \"TRAFFICDIR\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,TRAFFICDIR,-1,-1;\
         TRUCKPCT \"TRUCKPCT\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,TRUCKPCT,-1,-1;\
         AENDRATING \"AENDRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,AENDRATING,-1,-1;\
         APPRALIGN \"APPRALIGN\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,APPRALIGN,-1,-1;\
         ARAILRATIN \"ARAILRATIN\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,ARAILRATIN,-1,-1;\
         CHANRATING \"CHANRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,CHANRATING,-1,-1;\
         DECKGEOM \"DECKGEOM\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,DECKGEOM,-1,-1;\
         NEXTINSP \"NEXTINSP\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,NEXTINSP,-1,-1;\
         PIERPROT \"PIERPROT\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,PIERPROT,-1,-1;\
         RAILRATING \"RAILRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,RAILRATING,-1,-1;\
         SCOURCRIT \"SCOURCRIT\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,SCOURCRIT,-1,-1;\
         STRRATING \"STRRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,STRRATING,-1,-1;\
         TRANSRATIN \"TRANSRATIN\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,TRANSRATIN,-1,-1;\
         UNDERCLR \"UNDERCLR\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,UNDERCLR,-1,-1;\
         WATERADEQ \"WATERADEQ\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,WATERADEQ,-1,-1;\
         BUS_PLAN_NETWORK \"BUS_PLAN_NETWORK\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,BUS_PLAN_NETWORK,-1,-1;\
         ROW_MODIFIED \"ROW_MODIFIED\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,ROW_MODIFIED,-1,-1;\
         ORIG_FID \"ORIG_FID\" true true false 4 Long 0 10 ,First,#;\
         BRKEY \"BRKEY\" true true false 255 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,BRKEY,-1,-1;\
         YCPC_GROUP \"YCPC_GROUP\" true true false 254 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_STATE,YCPC_GROUP,-1,-1;\
         CREATE_DATE \"CREATE_DATE\" false true false 36 Date 0 0 ,First,#;\
         MODIFY_DATE \"MODIFY_DATE\" false true false 36 Date 0 0 ,First,#;\
         EDIT_NAME \"EDIT_NAME\" false true false 20 Text 0 0 ,First,#;\
         EDIT_TYPE \"EDIT_TYPE\" true true false 30 Text 0 0 ,First,#;\
         GlobalID \"GlobalID\" false false false 38 GlobalID 0 0 ,First,#""", "")

        message ("Deleting\Appending BMS_Local\r")
        # Process: Delete Features (5)
        arcpy.DeleteFeatures_management(York_Edit_GIS_TRANSP_Bridges_BMS_Local)

        # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
        # The following inputs are layers or table views: "York_Edit.GIS.TRANSP_Bridges_BMS_Local"
        arcpy.Append_management(""+Updated_Folder+"\Bridges_BMS_Local", York_Edit_GIS_TRANSP_Bridges_BMS_Local, "NO_TEST",\
        "CTY_CODE \"CTY_CODE\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,CTY_CODE,-1,-1;\
        ST_RT_NO \"SEG_NO\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,ST_RT_NO,-1,-1;\
        SEG_NO \"SEG_NO\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,SEG_NO,-1,-1;\
        OFFSET \"OFFSET\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,OFFSET,-1,-1;\
        ADMIN_JURIS \"ADMIN_JURIS\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,ADMIN_JURIS,-1,-1;\
        DEC_LAT \"DEC_LAT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DEC_LAT,-1,-1;\
        DEC_LONG \"DEC_LONG\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DEC_LONG,-1,-1;\
        BRIDGE_ID \"BRIDGE_ID\" true true false 30 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,BRIDGE_ID,-1,-1;\
        FEATINT \"FEATINT\" true true false 24 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,FEATINT,-1,-1;\
        DISTRICT \"DISTRICT\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DISTRICT,-1,-1;\
        FACILITY \"FACILITY\" true true false 18 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,FACILITY,-1,-1;\
        LOCATION \"LOCATION\" true true false 25 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,LOCATION,-1,-1;\
        OWNER \"OWNER\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,OWNER,-1,-1;\
        YEARBUILT \"YEARBUILT\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,YEARBUILT,-1,-1;\
        YEARRECON \"YEARRECON\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,YEARRECON,-1,-1;\
        SERVTYPON \"SERVTYPON\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,SERVTYPON,-1,-1;\
        SERVTYPUND \"SERVTYPUND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,SERVTYPUND,-1,-1;\
        MAINSPANS \"MAINSPANS\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,MAINSPANS,-1,-1;\
        APPSPANS \"APPSPANS\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,APPSPANS,-1,-1;\
        LENGTH \"LENGTH\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,LENGTH,-1,-1;\
        DECKWIDTH \"DECKWIDTH\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DECKWIDTH,-1,-1;\
        DKSURFTYPE \"DKSURFTYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DKSURFTYPE,-1,-1;\
        DKMEMBTYPE \"DKMEMBTYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DKMEMBTYPE,-1,-1;\
        DKPROTECT \"DKPROTECT\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DKPROTECT,-1,-1;\
        MAIN_WS_THICKNESS \"MAIN_WS_THICKNESS\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,MAIN_WS_THICKNESS,-1,-1;\
        APPR_DKSURFTYPE \"APPR_DKSURFTYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,APPR_DKSURFTYPE,-1,-1;\
        APPR_DKMEMBTYPE \"APPR_DKMEMBTYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,APPR_DKMEMBTYPE,-1,-1;\
        APPR_DKPROTECT \"APPR_DKPROTECT\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,APPR_DKPROTECT,-1,-1;\
        APPR_WS_THICKNESS \"APPR_WS_THICKNESS\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,APPR_WS_THICKNESS,-1,-1;\
        FED_FUND \"FED_FUND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,FED_FUND,-1,-1;\
        DECK_RECON_WORK_TYPE \"DECK_RECON_WORK_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DECK_RECON_WORK_TYPE,-1,-1;\
        SUP_RECON_WORK_TYPE \"SUP_RECON_WORK_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,SUP_RECON_WORK_TYPE,-1,-1;\
        DEPT_MAIN_MATERIAL_TYPE \"DEPT_MAIN_MATERIAL_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DEPT_MAIN_MATERIAL_TYPE,-1,-1;\
        DEPT_MAIN_PHYSICAL_TYPE \"DEPT_MAIN_PHYSICAL_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DEPT_MAIN_PHYSICAL_TYPE,-1,-1;\
        DEPT_MAIN_SPAN_INTERACTION \"DEPT_MAIN_SPAN_INTERACTION\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DEPT_MAIN_SPAN_INTERACTION,-1,-1;\
        DEPT_MAIN_STRUC_CONFIG \"DEPT_MAIN_STRUC_CONFIG\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DEPT_MAIN_STRUC_CONFIG,-1,-1;\
        DEPT_APPR_MATERIAL_TYPE \"DEPT_APPR_MATERIAL_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DEPT_APPR_MATERIAL_TYPE,-1,-1;\
        DEPT_APPR_PHYSICAL_TYPE \"DEPT_APPR_PHYSICAL_TYPE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DEPT_APPR_PHYSICAL_TYPE,-1,-1;\
        DEPT_APPR_SPAN_INTERACTION \"DEPT_APPR_SPAN_INTERACTION\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DEPT_APPR_SPAN_INTERACTION,-1,-1;\
        DEPT_APPR_STRUC_CONFIG \"DEPT_APPR_STRUC_CONFIG\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DEPT_APPR_STRUC_CONFIG,-1,-1;\
        SUB_AGENCY \"SUB_AGENCY\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,SUB_AGENCY,-1,-1;\
        MAINT_RESP_DESC \"MAINT_RESP_DESC\" true true false 24 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,MAINT_RESP_DESC,-1,-1;\
        CRIT_FACILITY \"CRIT_FACILITY\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,CRIT_FACILITY,-1,-1;\
        APPR_PAVEMENT_WIDTH \"APPR_PAVEMENT_WIDTH\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,APPR_PAVEMENT_WIDTH,-1,-1;\
        COVERED_BRIDGE \"COVERED_BRIDGE\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,COVERED_BRIDGE,-1,-1;\
        FLOOD_INSP \"FLOOD_INSP\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,FLOOD_INSP,-1,-1;\
        DEPT_DKSTRUCTYP \"DEPT_DKSTRUCTYP\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DEPT_DKSTRUCTYP,-1,-1;\
        BYPASSLEN \"BYPASSLEN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,BYPASSLEN,-1,-1;\
        AROADWIDTH \"AROADWIDTH\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,AROADWIDTH,-1,-1;\
        ROADWIDTH \"ROADWIDTH\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,ROADWIDTH,-1,-1;\
        MIN_OVER_VERT_CLEAR_RIGHT \"MIN_OVER_VERT_CLEAR_RIGHT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,MIN_OVER_VERT_CLEAR_RIGHT,-1,-1;\
        MIN_OVER_VERT_CLEAR_LEFT \"MIN_OVER_VERT_CLEAR_LEFT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,MIN_OVER_VERT_CLEAR_LEFT,-1,-1;\
        POST_LIMIT_WEIGHT \"POST_LIMIT_WEIGHT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,POST_LIMIT_WEIGHT,-1,-1;\
        POST_LIMIT_COMB \"POST_LIMIT_COMB\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,POST_LIMIT_COMB,-1,-1;\
        INSPDATE \"INSPDATE\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,INSPDATE,-1,-1;\
        BRINSPFREQ \"BRINSPFREQ\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,BRINSPFREQ,-1,-1;\
        POST_STATUS \"POST_STATUS\" true true false 1 Text 0 0 ,First,#;\
        NBI_RATING \"NBI_RATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,NBI_RATING,-1,-1;\
        SUFF_RATE \"SUFF_RATE\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,SUFF_RATE,-1,-1;\
        MAINT_DEF_RATE \"MAINT_DEF_RATE\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,MAINT_DEF_RATE,-1,-1;\
        HBRR_ELIG \"HBRR_ELIG\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,HBRR_ELIG,-1,-1;\
        JURIS \"JURIS\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,JURIS,-1,-1;\
        SEG_END \"SEG_END\" true true false 4 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,SEG_END,-1,-1;\
        OFFSET_END \"OFFSET_END\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,OFFSET_END,-1,-1;\
        SEG_PT_BGN \"SEG_PT_BGN\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,SEG_PT_BGN,-1,-1;\
        SEG_PT_END \"SEG_PT_END\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,SEG_PT_END,-1,-1;\
        SIDE_IND \"SIDE_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,SIDE_IND,-1,-1;\
        NLF_ID \"NLF_ID\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,NLF_ID,-1,-1;\
        NLF_CNTL_BGN \"NLF_CNTL_BGN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,NLF_CNTL_BGN,-1,-1;\
        NLF_CNTL_END \"NLF_CNTL_END\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,NLF_CNTL_END,-1,-1;\
        CUM_OFFSET_BGN \"CUM_OFFSET_BGN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,CUM_OFFSET_BGN,-1,-1;\
        CUM_OFFSET_END \"CUM_OFFSET_END\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,CUM_OFFSET_END,-1,-1;\
        DKRATING \"DKRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DKRATING,-1,-1;\
        SUPRATING \"SUPRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,SUPRATING,-1,-1;\
        SUBRATING \"SUBRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,SUBRATING,-1,-1;\
        CULVRATING \"CULVRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,CULVRATING,-1,-1;\
        STATE_LOCAL \"STATE_LOCAL\" true true false 1 Text 0 0 ,First,#;\
        DECK_AREA \"DECK_AREA\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DECK_AREA,-1,-1;\
        BB_BRDGEID \"BB_BRDGEID\" true true false 15 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,BB_BRDGEID,-1,-1;\
        BB_PCT \"BB_PCT\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,BB_PCT,-1,-1;\
        BRIDGEMED \"BRIDGEMED\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,BRIDGEMED,-1,-1;\
        CUSTODIAN \"CUSTODIAN\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,CUSTODIAN,-1,-1;\
        DESIGNAPPR \"DESIGNAPPR\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DESIGNAPPR,-1,-1;\
        DESIGNMAIN \"DESIGNMAIN\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DESIGNMAIN,-1,-1;\
        DKSTRUCTYP \"DKSTRUCTYP\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DKSTRUCTYP,-1,-1;\
        FIPS_STATE \"FIPS_STATE\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,FIPS_STATE,-1,-1;\
        HCLRULT \"HCLRULT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,HCLRULT,-1,-1;\
        HCLRURT \"HCLRURT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,HCLRURT,-1,-1;\
        HISTSIGN \"HISTSIGN\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,HISTSIGN,-1,-1;\
        IMPLEN \"IMPLEN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,IMPLEN,-1,-1;\
        LFTBRNAVCL \"LFTBRNAVCL\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,LFTBRNAVCL,-1,-1;\
        LFTCURBSW \"LFTCURBSW\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,LFTCURBSW,-1,-1;\
        MATERIALAPPR \"MATERIALAPPR\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,MATERIALAPPR,-1,-1;\
        MATERIALMAIN \"MATERIALMAIN\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,MATERIALMAIN,-1,-1;\
        MAXSPAN \"MAXSPAN\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,MAXSPAN,-1,-1;\
        NAVCNTROL \"NAVCNTROL\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,NAVCNTROL,-1,-1;\
        NAVHC \"NAVHC\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,NAVHC,-1,-1;\
        NAVVC \"NAVVC\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,NAVVC,-1,-1;\
        NBIIMPCOST \"NBIIMPCOST\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,NBIIMPCOST,-1,-1;\
        NBIRWCOST \"NBIRWCOST\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,NBIRWCOST,-1,-1;\
        NBISLEN \"NBISLEN\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,NBISLEN,-1,-1;\
        NBITOTCOST \"NBITOTCOST\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,NBITOTCOST,-1,-1;\
        NBIYRCOST \"NBIYRCOST\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,NBIYRCOST,-1,-1;\
        NSTATECODE \"NSTATECODE\" true true false 3 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,NSTATECODE,-1,-1;\
        PARALSTRUC \"PARALSTRUC\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,PARALSTRUC,-1,-1;\
        PLACECODE \"PLACECODE\" true true false 5 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,PLACECODE,-1,-1;\
        PROPWORK \"PROPWORK\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,PROPWORK,-1,-1;\
        REFHUC \"REFHUC\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,REFHUC,-1,-1;\
        REFVUC \"REFVUC\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,REFVUC,-1,-1;\
        RTCURBSW \"RTCURBSW\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,RTCURBSW,-1,-1;\
        SKEW \"SKEW\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,SKEW,-1,-1;\
        STRFLARED \"STRFLARED\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,STRFLARED,-1,-1;\
        STRUCT_NUM \"STRUCT_NUM\" true true false 15 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,STRUCT_NUM,-1,-1;\
        SUMLANES \"SUMLANES\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,SUMLANES,-1,-1;\
        TEMPSTRUC \"TEMPSTRUC\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,TEMPSTRUC,-1,-1;\
        VCLROVER \"VCLROVER\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,VCLROVER,-1,-1;\
        ADTFUTURE \"ADTFUTURE\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,ADTFUTURE,-1,-1;\
        ADTFUTYEAR \"ADTFUTYEAR\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,ADTFUTYEAR,-1,-1;\
        ADTTOTAL \"ADTTOTAL\" true true false 4 Long 0 10 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,ADTTOTAL,-1,-1;\
        ADTYEAR \"ADTYEAR\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,ADTYEAR,-1,-1;\
        DEFHWY \"DEFHWY\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DEFHWY,-1,-1;\
        DIRSUFFIX \"DIRSUFFIX\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DIRSUFFIX,-1,-1;\
        FUNCCLASS \"FUNCCLASS\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,FUNCCLASS,-1,-1;\
        HCLRINV \"HCLRINV\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,HCLRINV,-1,-1;\
        KIND_HWY \"KIND_HWY\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,KIND_HWY,-1,-1;\
        KMPOST \"KMPOST\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,KMPOST,-1,-1;\
        LANES \"LANES\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,LANES,-1,-1;\
        LEVL_SRVC \"LEVL_SRVC\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,LEVL_SRVC,-1,-1;\
        NHS_IND \"NHS_IND\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,NHS_IND,-1,-1;\
        ON_UNDER \"ON_UNDER\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,ON_UNDER,-1,-1;\
        TOLLFAC \"TOLLFAC\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,TOLLFAC,-1,-1;\
        TRAFFICDIR \"TRAFFICDIR\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,TRAFFICDIR,-1,-1;\
        TRUCKPCT \"TRUCKPCT\" true true false 2 Short 0 5 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,TRUCKPCT,-1,-1;\
        AENDRATING \"AENDRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,AENDRATING,-1,-1;\
        APPRALIGN \"APPRALIGN\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,APPRALIGN,-1,-1;\
        ARAILRATIN \"ARAILRATIN\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,ARAILRATIN,-1,-1;\
        CHANRATING \"CHANRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,CHANRATING,-1,-1;\
        DECKGEOM \"DECKGEOM\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,DECKGEOM,-1,-1;\
        NEXTINSP \"NEXTINSP\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,NEXTINSP,-1,-1;\
        PIERPROT \"PIERPROT\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,PIERPROT,-1,-1;\
        RAILRATING \"RAILRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,RAILRATING,-1,-1;\
        SCOURCRIT \"SCOURCRIT\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,SCOURCRIT,-1,-1;\
        STRRATING \"STRRATING\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,STRRATING,-1,-1;\
        TRANSRATIN \"TRANSRATIN\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,TRANSRATIN,-1,-1;\
        UNDERCLR \"UNDERCLR\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,UNDERCLR,-1,-1;\
        WATERADEQ \"WATERADEQ\" true true false 1 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,WATERADEQ,-1,-1;\
        BUS_PLAN_NETWORK \"BUS_PLAN_NETWORK\" true true false 2 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,BUS_PLAN_NETWORK,-1,-1;\
        ROW_MODIFIED \"ROW_MODIFIED\" true true false 8 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,ROW_MODIFIED,-1,-1;\
        ORIG_FID \"ORIG_FID\" true true false 4 Long 0 10 ,First,#;\
        BRKEY \"BRKEY\" true true false 255 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,BRKEY,-1,-1;\
        YCPC_GROUP \"YCPC_GROUP\" true true false 254 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,YCPC_GROUP,-1,-1;\
        Local_br_n \"Local_br_n\" true true false 3 Text 0 0 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,Local_br_n,-1,-1;\
        VOLUME \"VOLUME\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,VOLUME,-1,-1;\
        AM_VOLUME \"AM_VOLUME\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,AM_VOLUME,-1,-1;\
        AM_PERCENT \"AM_PERCENT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,AM_PERCENT,-1,-1;\
        AM_PEAK \"AM_PEAK\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,AM_PEAK,-1,-1;\
        PM_VOLUME \"PM_VOLUME\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,PM_VOLUME,-1,-1;\
        PM_PERCENT \"PM_PERCENT\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,PM_PERCENT,-1,-1;\
        PM_PEAK \"PM_PEAK\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,PM_PEAK,-1,-1;\
        YEAR \"YEAR\" true true false 8 Double 8 38 ,First,#,"+Updated_Folder+"\Bridges_BMS_Local,YEAR,-1,-1;\
        CREATE_DATE \"CREATE_DATE\" false true false 36 Date 0 0 ,First,#;\
        MODIFY_DATE \"MODIFY_DATE\" false true false 36 Date 0 0 ,First,#;\
        EDIT_NAME \"EDIT_NAME\" false true false 20 Text 0 0 ,First,#;\
        EDIT_TYPE \"EDIT_TYPE\" true true false 30 Text 0 0 ,First,#;\
        GlobalID \"GlobalID\" false false false 38 GlobalID 0 0 ,First,#""","")

        #print "Compress to Default"
        #arcpy.ReconcileVersions_management(r"\\YCPCFS\GIS_Projects\IS\GIS_Connections\GIS_York_Edit.sde","ALL_VERSIONS","sde.DEFAULT","#","NO_LOCK_ACQUIRED","NO_ABORT","BY_OBJECT","FAVOR_TARGET_VERSION","POST","KEEP_VERSION","#")

    # end Try statement
    except EnvironmentError as e:
        ErrorMessageEnvironment(e)
    except Exception as e:
        ErrorMessageException(e)

    try:
        # Added section on May 1st. Helps identify state and local bridges that are not joining properly
        message ("Starting Step to Check Bridge Numbers for Local and State Bridges")
        message ("Checking Local Bridges")
        York_Edit_SDE = r"\\YCPCFS\GIS_Projects\IS\GIS_Connections\GIS_York_Edit.sde"
        York_Edit_GIS_TRANSP_Bridges_BMS_Local = os.path.join(York_Edit_SDE,"York_Edit.GIS.TRANSP_Bridges_BMS_Local")

        localfields = ['BRKEY','YCPC_GROUP']

        locallist = []

        with arcpy.da.SearchCursor(York_Edit_GIS_TRANSP_Bridges_BMS_Local,localfields) as cursor:
             for row in cursor:
                if row[1] == None:
                    message ("Local Bridge Number {}:\n\t\a Missing YCPC_Group Information".format(row[0]))
                    locallist.append(row[1])
                elif row[1] != None:
                    message ("Local Bridge Number {}:\n\t YCPC_Group Information Included".format(row[0]))
                    locallist.append(row[1])

        locallist.sort
        #print list
        NoInfo = locallist.count(None)
        Info = len(locallist) - NoInfo
        message ("There are a Total of {} Local Bridges Missing Information and {} are Correct\nTotal Local Bridges are {}".format(NoInfo, Info, len(locallist)))

        message ("\nChecking State Bridges")
        York_Edit_SDE = r"\\YCPCFS\GIS_Projects\IS\GIS_Connections\GIS_York_Edit.sde"
        York_Edit_GIS_TRANSP_Bridges_BMS_State = os.path.join(York_Edit_SDE,"York_Edit.GIS.TRANSP_Bridges_BMS_State")

        statefields = ['STRUCT_NUM','YCPC_GROUP']

        statelist = []

        with arcpy.da.SearchCursor(York_Edit_GIS_TRANSP_Bridges_BMS_State,statefields) as cursor:
             for row in cursor:
                if row[1] == None:
                    message ("State Bridge Number {}:\n\t\a Missing YCPC_Group Information".format(row[0]))
                    statelist.append(row[1])
                elif row[1] != None:
                    message ("State Bridge Number {}:\n\t YCPC_Group Information Included".format(row[0]))
                    statelist.append(row[1])

        statelist.sort
        #print list
        NoInfo = statelist.count(None)
        Info = len(statelist) - NoInfo
        message ("There are a Total of {} State Bridges Missing Information and {} are Correct\nTotal State Bridges are {}".format(NoInfo, Info, len(statelist)))
        message ("Finish Checking Bridge Numbers for Local and State Bridges\r")

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

def importallsheets(in_excel, out_gdb):
    workbook = xlrd.open_workbook(in_excel)
    sheets = [sheet.name for sheet in workbook.sheets()]

    print('{} sheets found: {}'.format(len(sheets), ','.join(sheets)))
    for sheet in sheets:
        # The out_table is based on the input excel file name
        # a underscore (_) separator followed by the sheet name
        out_table = os.path.join(
            out_gdb,
            arcpy.ValidateTableName(
                "{0}_{1}".format(os.path.basename(in_excel), sheet),
                out_gdb))

        print('Converting {} to {}'.format(sheet, out_table))

        # Perform the conversion
        arcpy.ExcelToTable_conversion(in_excel, out_table, sheet)

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
