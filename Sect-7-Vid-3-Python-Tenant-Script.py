from acitoolkit.acisession import Session
from acitoolkit.acitoolkit import Credentials, Tenant, AppProfile, EPG
from acitoolkit.acitoolkit import Context, BridgeDomain, Contract, FilterEntry

with open('tenant-inventory.txt') as config_file:
    data = config_file.readlines()

def main():

    description = ('Create 2 EPGs within the same Context and have'
                   '1 EPG provide a contract to the other EPG.')
    creds = Credentials('apic', description)
    args = creds.get()
    session = Session(args.url, args.login, args.password)
    session.login()
    for line in data:
            line = line.strip("\n")
            tnt = line.split(",")[0]
            appro = line.split(",")[1]
            epg1 = line.split(",")[2]
            epg2 = line.split(",")[3]
            contractn = line.split(",")[4]
            bd1 = line.split(",")[5]
            vrf1 = line.split(",")[6]
    # Create the Tenant
            tenant = Tenant(tnt)

    # Create the Application Profile
            app = AppProfile(appro, tenant)

    # Create the EPGs
            epg_obj1 = EPG(epg1, app)
            epg_obj2 = EPG(epg2, app)
            epg_obj1.set_intra_epg_isolation(False)
            epg_obj2.set_intra_epg_isolation(True)

    # Create a Context and BridgeDomain
    # Place both EPGs in the Context and in the same BD
            context = Context(vrf1, tenant)
            bd = BridgeDomain(bd1, tenant)
            bd.add_context(context)
            epg_obj1.add_bd(bd)
            epg_obj2.add_bd(bd)

    # Define a contract with a single entry
            contract = Contract(contractn, tenant)
            entry1 = FilterEntry('entry1',
                                applyToFrag='no',
                                arpOpc='unspecified',
                                dFromPort='3306',
                                dToPort='3306',
                                etherT='ip',
                                prot='tcp',
                                sFromPort='1',
                                sToPort='65535',
                                tcpRules='unspecified',
                                parent=contract)

    # Provide the contract from 1 EPG and consume from the other
            epg_obj2.provide(contract)
            epg_obj1.consume(contract)

    # Login to APIC and push the config

    # Cleanup (uncomment the next line to delete the config)
    # tenant.mark_as_deleted()
            resp = tenant.push_to_apic(session)

            if resp.ok:
        # Print what was sent
                print('Pushed the following JSON to the APIC')
                print('URL: ' + str(tenant.get_url()))
                print('JSON: ' + str(tenant.get_json()))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
