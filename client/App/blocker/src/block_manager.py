from src.block_settings_cache import BlockSettingsCache
from src.communicator import Communicator
import threading
import pydivert
import dpkt
from src.logger import setup_logger
from src.handlers import HandlerFactory
from src.utils import *

class BlockManager:
    def __init__(self):
        self._block_settings_cache   = BlockSettingsCache()
        self._communicator           = Communicator(DEFAULT_PIPE_NAME)
        self._handler_factory        = HandlerFactory()
        self._logger                 = setup_logger("BlockManager")
        self._is_running_event       = threading.Event()

        self._communicator.connect()

    def run(self):
        """Start the blocking service with two threads: one for messages and one for packets."""
        self._is_running_event.set()
        self._logger.info("Starting blocking service...")

        try:
            listen_thread = threading.Thread(target=self._listen_for_messages, daemon=True)
            packet_thread = threading.Thread(target=self._redirect_dns_packets, daemon=True)

            listen_thread.start()
            packet_thread.start()

            listen_thread.join()
            packet_thread.join(timeout=1.0)  # wait for 1 second

        except Exception as e:
            self._logger.error(f"An unexpected error occurred: {e}")
    """
    Listen Thread
    """
    def _listen_for_messages(self):
        try:
            for data in self._communicator.listen():
                self._handle_message(data)

        except Exception as e:
            self._logger.error(f"Exiting listener thread: {e}")
            self._is_running_event.clear()

    def _handle_message(self, data: dict):
        try:
            self._handler_factory.get_handler(
                data=data,
                block_settings_cache=self._block_settings_cache
            ).handle_request()

        except Exception as e:
            self._logger.error(f"Error handling request: {e}")

    """
    Packet Interception Thread
    """
    def _redirect_dns_packets(self):
        """
        Intercept and modify DNS traffic.
        Redirects outbound DNS queries to REDIRECT_IP and modifies inbound responses.
        """

        try:
            with pydivert.WinDivert("udp.DstPort == 53 or udp.SrcPort == 53") as w:

                for packet in w:
                    if not self._is_running_event.is_set():
                        break
                    try:
                        if packet.is_outbound:
                            self._outbound_packet_handler(packet)

                        if packet.is_inbound:
                            self._inbound_packet_handler(packet)

                        w.send(packet)
                        
                    except Exception as packet_error:
                        self._logger.error(f"processing packet: {packet_error}")
        except KeyboardInterrupt:
            self._logger.info("*** Interception stopped by user ***")
        except Exception as e:
            self._logger.error(f"An unexpected error occurred: {e}")
    
    def _inbound_packet_handler(self, packet: pydivert.Packet):
        """
        Handle inbound DNS packets.
        If Domain is blocked, modify the packet to return 0.0.0.0
        """
        self._check_for_blocked_domain(packet)
        self._logger.info(f"Putting source address to: {self._block_settings_cache.get_gateway_ip()}")
        packet.src_addr = self._block_settings_cache.get_gateway_ip()
    
    def _outbound_packet_handler(self, packet: pydivert.Packet):
        packet.dst_addr = self._block_settings_cache.get_dns_server()

    def _check_for_blocked_domain(self, packet: pydivert.Packet) -> None:
        """
        Check if DNS response contains blocked domain and modify if needed.
        Modifies the packet in-place if domain is blocked.
        
        Args:
            packet: PyDivert packet object containing DNS data
        """
        try:
            # Parse DNS packet from the packet payload
            dns_packet = dpkt.dns.DNS(packet.payload)

            # Validate packet has queries
            if not dns_packet.qd:
                self._logger.info("DNS packet contains no queries, skipping")
                return

            # Extract domain from first query
            domain = dns_packet.qd[0].name

            # Only process A and AAAA records (IPv4 and IPv6)
            if dns_packet.qd[0].type not in (dpkt.dns.DNS_A, dpkt.dns.DNS_AAAA):
                self._logger.info(f"Skipping unsupported DNS record type: {dns_packet.qd[0].type}")
                return

            # Check if domain is blocked and modify packet if needed
            if self._block_settings_cache.is_blocked(domain):
                self._modify_dns_packet_for_blocking(dns_packet)
                packet.payload = bytes(dns_packet)

        except dpkt.UnpackError as e:
            self._logger.info(f"Failed to parse DNS packet (possibly unsupported record type): {e}")
            return
        except Exception as e:
            self._logger.error(f"Unexpected error processing DNS packet: {e}")
            return

    def _modify_dns_packet_for_blocking(self, dns_packet: dpkt.dns.DNS) -> None:
        """
        Modify DNS packet to return 0.0.0.0 for blocked domains.

        Args:
            dns_packet: The DNS packet to modify
        """
        # Set response code to domain not found
        dns_packet.rcode = dpkt.dns.DNS_RCODE_NXDOMAIN
        dns_packet.an = []  # Clear existing answers
        
        # Create new RR for each blocked response
        answer = dpkt.dns.DNS.RR()
        answer.cls = dpkt.dns.DNS_IN
        answer.type = dpkt.dns.DNS_A
        answer.rdata = b'\x00\x00\x00\x00'  # 0.0.0.0
        answer.ttl = 60  # Short TTL for blocked domains
        answer.name = dns_packet.qd[0].name

        dns_packet.an.append(answer)

    def __del__(self):
        self._communicator.cleanup()
