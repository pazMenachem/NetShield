import pydivert
import netifaces
from utils import ADGUARD_DNS, CLOUDFLARE_DNS, ADGUARD_FAMILY_DNS


block_ads = False
block_adult_content = False

def get_default_gateway():
    """Get the default gateway (router) IP address."""
    try:
        gateways = netifaces.gateways()
        default_gateway = gateways['default'][netifaces.AF_INET][0]
        return default_gateway
    except Exception as e:
        print(f"Error getting default gateway: {e}")
        return None

def get_target_dns():
    """Determine which DNS server to use based on filtering options."""
    if block_ads and block_adult_content:
        return ADGUARD_FAMILY_DNS
    elif block_ads:
        return ADGUARD_DNS
    elif block_adult_content:
        return CLOUDFLARE_DNS
    return None

def redirect_dns_packets():
    """Intercept and modify DNS traffic."""
    default_gateway = get_default_gateway()
    target_dns = get_target_dns()
    
    if not target_dns:
        print("No filtering options selected. Exiting...")
        return

    try:
        with pydivert.WinDivert("udp.DstPort == 53 or udp.SrcPort == 53") as w:
            for packet in w:
                if packet.is_outbound:
                    packet.dst_addr = target_dns

                if packet.is_inbound:
                    packet.src_addr = default_gateway
                w.send(packet)

    except KeyboardInterrupt:
        print("\nDNS redirection stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    try:

        global block_ads, block_adult_content
        block_ads = True
        block_adult_content = True
        
        print("Starting DNS redirection with following settings:")
        print(f"Block ads: {block_ads}")
        print(f"Block adult content: {block_adult_content}")
        print(f"Using DNS: {get_target_dns()}")
        
        redirect_dns_packets()
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    finally:
        print("Cleanup completed.")

if __name__ == "__main__":
    main()