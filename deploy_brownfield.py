import sys
import time
import os

from utils_library import *


def main():
    """
        This is for Brownfield deployment which works as below,
            1) Based on required action like "ospf_enable", "ospf_disable" etc it execute relevant config (or) un-config
                by using NETCONF
            2) This also ensures Baseline verifications before and after required action initiated to verify Topology is
                in stable condition not impacted by Brownfield deployment changes

            Note: This is expandable by adding more cases like "mpls_enable", "mpls_disable" etc
    """

    # flag to identify success/failure of Brownfield deployment changes
    fail_flag = False

    # MySQL Database login credentials  taken through command line arguments for security reasons..
    if len(sys.argv) != 3:
        print(f"usage: {os.path.basename(__file__)} <database_username> <database_username>")
        sys.exit(1)

    # Connect to Database for Single Source of Truth
    DB = Database(ip='localhost', username=sys.argv[1], password=sys.argv[2])

    R1_DC = DB.fetch_by_device('R1')
    # R2_DC = DB.fetch_by_device('R2')

    # Gracefully close the Database connection
    DB.close()

    # Connect to Routers of topology
    R1 = Device(ip=R1_DC.mgmt_ip, username=R1_DC.user_name, password=R1_DC.password)
    # R2 = Device(ip=R2_DC.mgmt_ip, username=R2_DC.user_name, password=R2_DC.password)

    # Verify the Baseline health of topology
    if not verify_baseline_health(R1):
        print("Topology devices not per expected Baselines..")
        sys.exit(0)

    action = 'ospf_enable'

    match action:
        case 'ospf_enable':
            # Deploy OSPF on existing topology
            if not R1.edit_config_ospf(process_id='10',
                                router_id='1.1.1.1',
                                network_ip='19.1.0.0', network_mask='0.0.0.255',
                                area_id='0',
                                action='enable'):
                fail_flag = True

        case 'ospf_disable':
            # Remove OSPF from existing topology
            if not R1.edit_config_ospf(process_id='10',
                                router_id='1.1.1.1',
                                network_ip='19.1.0.0', network_mask='0.0.0.255',
                                area_id='0',
                                action='disable'):
                fail_flag = True

        case 'xxx_enable':
            # can be expanded easily adding more cases..
            pass

    # Verify if Brownfield deployment changes went through Success (or) Failure
    if fail_flag:
        print("ERROR : --- --- --- --- BrownField Deployment attempt failed --- --- --- ---")
    else:
        print("LOG : --- --- --- --- BrownField Deployment attempt success --- --- --- ---")

    # Verify the Baseline health of topology after convergence
    time.sleep(7)
    if not verify_baseline_health(R1):
        print("ERROR : FAILED: Topology devices not per expected Baselines after Brownfield deployment changes..")
    else:
        print("LOG : SUCCESS: Topology devices as per expected Baselines after Brownfield deployment changes..")

    # Gracefully close the Router NETCONF connections
    R1.close()
    # R2.close()


if __name__ == "__main__":
    main()

