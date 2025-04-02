import room2
import Objects.AP as AP
import matplotlib.pyplot as plt
import plotter
from MAC import mac_top 
from Logging import transmission_logging
import results
import Clean_up.cleanup
import constants
import MirrorConfigs.Multi_Layer_Mirror_Setup.leftvertical as leftvertical
import MirrorConfigs.Multi_Layer_Mirror_Setup.rightvertical as rightvertical
import MirrorConfigs.Multi_Layer_Mirror_Setup.upperhorizontal as upperhorizontal
import MirrorConfigs.Multi_Layer_Mirror_Setup.lowerhorizontal as lowerhorizontal 


Clean_up.cleanup.delete_old_folders()

# Setup Room Parameters
room_l,room_w,room_h = 26.6,26.6,0


# Setup UE Parameters
UE_TX_Power             = 0.1 #Watts
maxNumUEDevices         = 50
UE_Device_Density       = 0.1
UE_UL_interarrival_time = 800e-6
UE_BeamWidth = 3
# Setup AP Parameters
number_AP = 1 
AP_TX_Power = 0.1 #Watts
AP_BeamWidth = 12


#Setup Channel
system_bandwidth = 69.12e9
txFrequency      = 284e9
 
# Setup Mirrors
left_vertical_mirror_map    = leftvertical.setup_vertical_mirror_leftv()
right_vertical_mirror_map   = rightvertical.setup_vertical_mirror_rightv()
upper_horizontal_mirror_map = upperhorizontal.setup_vertical_mirror_upperh()
lower_horizontal_mirror_map = lowerhorizontal.setup_vertical_mirror_lowerh()

mirrors = left_vertical_mirror_map|right_vertical_mirror_map|upper_horizontal_mirror_map|lower_horizontal_mirror_map
# mirrors = upper_horizontal_mirror_map

# Setup Simulation Room
simulation_room = room2.room2(room_l,room_w, "Square")

time_scale = 1e-3
# Setup Simulation Time
system_time   = [x*time_scale  for x in range(0,370)]
startTime = int(len(system_time) * 0.2)
#Setup Simulation Transmisstion Rate
transmission_lambda_ = 2000

Logging = transmission_logging.Logger()
Logging.setup_packetTrace()
Logging.setup_msgTrace()
MACSIMULATION = mac_top.MAC_Controller(constants.omniMacLabel,system_bandwidth, simulation_room, maxNumUEDevices)

# Setup the control Plane and Data Plane Bandwidht
control_BW_Allocation_Percentage = 5 #[%]
MACSIMULATION.control_BW = system_bandwidth * (control_BW_Allocation_Percentage/100)
MACSIMULATION.data_BW    = system_bandwidth * ((100 - control_BW_Allocation_Percentage)/100)

# Setup MAC Simulation Parameters 
MACSIMULATION.sectorTime = 3e-6
MACSIMULATION.UERandomBackOffTime = 20e-9

# Setup the max UE coordinates in the room
MACSIMULATION.maxUEXcord = 16
MACSIMULATION.maxUEYcord = 16


MACSIMULATION.blockage = False



# import os
# import RF
# gain = RF.define_gain(AP_BeamWidth)
# gainUE = RF.define_gain(3)
# AP_RFBox = RF.RFBox(gain,AP_TX_Power,txFrequency,AP_BeamWidth,69.12e9)
# UE_RFBox = RF.RFBox(gainUE,AP_TX_Power,txFrequency,3,69.12e9) 
# APDevice = AP.AP(AP_RFBox, 0)
# APDevice.setupAP()
# simulation_room.setup_mirrors_in_room(mirrors)
# simulation_room.setup_fov_generic(APDevice)
# import sys
# plt = plotter.results_plotSimulaitonRoom(simulation_room, APDevice, [])
# plt.show()
# sys.exit(1)


# for mirror_line in mirrors.keys():
#     sub_sub_folder = os.path.join("C:\\Users\\Hussam\\Desktop\\MAC_Simulaotr\\MirrorConfigs\\Multi_Layer_Mirror_Setup\\MirrorPlots2", str(mirror_line))
#     os.makedirs(sub_sub_folder, exist_ok=True)
#     for mirror in mirrors[mirror_line]:
#         print("Sector: " + str(mirror_line))
#         print("Tilt Angle: " + str(mirror.angleTilt))
#         # plt.figure()
#         # ax = plt.gca()
#         # ax.set_xlim([simulation_room.width*-1 , simulation_room.width*1 ])
#         # ax.set_ylim([simulation_room.length*-1 , simulation_room.length*1])
#         plt = plotter.results_plotUEFoV(simulation_room, APDevice, [],mirror)
#         fig_path = os.path.join(sub_sub_folder,"TiltAngle_"+str(mirror.angleTilt)+".png")
#         plt.savefig(fig_path)
#         # plt.show()
#         plt.close()


# sys.exit()



plot_avg_tput = 1
RESULTS = results.Results()


if (plot_avg_tput):
    avg_tput_data = []
    inter_arrival_time = [x for x in range(200,1050,100)]
    for i,iat in enumerate(inter_arrival_time):
        avg_tput_temp = 0
        print("Sim: " + str(i) + " out of: " + str(len(inter_arrival_time)) + " : Inter-Arrival  Time : " + str(iat))
        for j in range(1,6):
            MAC_Results,NLoSReflections = MACSIMULATION.setupMAC(number_AP, 
                                                            UE_Device_Density, 
                                                            AP_BeamWidth, 
                                                            UE_BeamWidth,
                                                            UE_TX_Power, 
                                                            AP_TX_Power,
                                                            txFrequency, 
                                                            iat*1e-6,
                                                            system_time[startTime-1], # System Start Time
                                                            system_time[-1], # System End Time
                                                            Logging,
                                                            None , # UE Coordinates [pre-defined for all runs]
                                                            mirrors)
                                                            
            avg_tput = RESULTS.process_results_generic(MAC_Results,64000*8,False,False)
            print("Tput: " + str(avg_tput))
            avg_tput_temp = avg_tput_temp+avg_tput
        avg_tput_temp = avg_tput_temp / 5
        print("Avg Tput: " + str(avg_tput_temp))
        avg_tput_data.append(avg_tput_temp)
    plotter.results_create_line_plot( inter_arrival_time,avg_tput_data, "Inter-Arrival Time [us]", "Avg. Tput [Gbps]", "Tput Fixed Node Density 0.05 nodes/m^2", None,"C:\\Users\\Hussam\\Desktop\\MAC_Simulaotr\\OMNIResults")
else:
    MAC_Results,NLoSReflections = MACSIMULATION.setupMAC(number_AP, 
                                                         UE_Device_Density, 
                                                         AP_BeamWidth,
                                                         UE_BeamWidth, 
                                                         UE_TX_Power, 
                                                         AP_TX_Power,
                                                         txFrequency, 
                                                         UE_UL_interarrival_time,
                                                         system_time[startTime-1], # System Start Time
                                                         system_time[-1], # System End Time
                                                         Logging,
                                                         None , # UE Coordinates [pre-defined for all runs]
                                                         mirrors) 
    AP,UE_list,MACUE_devices = MACSIMULATION.return_devices()
    avg_tput = RESULTS.process_results_generic(MAC_Results,MACSIMULATION.dataPacketLength_Encoded,False,True)
    print(avg_tput)
    RESULTS.setup_NLoSReflectionLog( NLoSReflections)
    
    plt = plotter.results_plotSimulaitonRoom(simulation_room, AP, UE_list)
    RESULTS.save_room(plt)
    plt = plotter.statistics_plot_sectorUsage(MAC_Results.sector_activity_RTS)
    plt = plotter.statistics_plot_sectorUsage(MAC_Results.sector_activity_UL)
    for mac_ue_device in MACUE_devices:
        ue_device = mac_ue_device.ue_device
        print("ue device: " +str(ue_device.id))
        plt = plotter.results_plotUESetup(simulation_room, AP, ue_device)
        RESULTS.save_mirrorRoom(plt,ue_device.id)
        plt.close()
        NLos_Signals = []
        for sector in range(0,AP.number_of_sectors):
            mirrrors = simulation_room.mirrors_with_coverage(ue_device,sector)
            plt = plotter.results_plotUEFoV(simulation_room, AP, ue_device,mirrrors[0])
            mirror_indicator = str(sector)
            RESULTS.save_mirrorFoV(plt,ue_device.id,mirror_indicator)
            plt.close()
            NLos_Signals.append(mac_ue_device.NLoS_Signal[sector])
        plt = plotter.results_plotAllSignals(simulation_room,AP, ue_device, NLos_Signals)
        RESULTS.save_AllNLoSSingals(plt,ue_device.id,sector)
        plt.close()
    from Logging import ue_logging
    UE_LOGGER = ue_logging.Logger()
    UE_LOGGER.write_UE_attr(UE_list)