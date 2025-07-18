import socket
import pyaudio
import threading
import time
import random
import re
import hashlib
import binascii

class BetterSIPCall:
    def __init__(self, sip_user, sip_pass, sip_domain, sip_proxy_ip, sip_port=5060, rtp_port=4000):
        self.sip_user = sip_user
        self.sip_pass = sip_pass
        self.sip_domain = sip_domain
        self.sip_proxy_ip = sip_proxy_ip
        self.sip_port = sip_port
        self.rtp_port = rtp_port
        self.local_ip = self.get_local_ip()
        self.call_id = f"{random.randint(100000, 999999)}@{self.local_ip}"
        self.tag = str(random.randint(10000, 99999))
        self.branch = f"z9hG4bK{random.randint(100000, 999999)}"
        self.media_active = False
        self.remote_tag = None
        self.cseq = 1
        self.auth_header = None
        self.target_number = None
        self.remote_rtp_ip = None
        self.remote_rtp_port = None
        self.registered = False
        self.sock = None

    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        import pdb; pdb.set_trace()  # Debugging breakpoint to inspect local IP
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()

    def test_connectivity(self):
        """Test basic network connectivity to SIP server"""
        print(f"[NETWORK] Testing connectivity to {self.sip_proxy_ip}:{self.sip_port}")
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_sock.settimeout(3.0)
            test_sock.connect((self.sip_proxy_ip, self.sip_port))
            test_sock.close()
            print("[NETWORK] Basic connectivity test passed")
            return True
        except Exception as e:
            print(f"[NETWORK] Connectivity test failed: {e}")
            return False

    def sdp(self):
        return f"""v=0
o=- 0 0 IN IP4 {self.local_ip}
s=Python SIP Call
c=IN IP4 {self.local_ip}
t=0 0
m=audio {self.rtp_port} RTP/AVP 0 8
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=sendrecv"""

    def parse_auth_header(self, auth_header):
        """Parse WWW-Authenticate header"""
        auth_params = {}
        # Remove 'Digest ' prefix if present
        if auth_header.startswith('Digest '):
            auth_header = auth_header[7:]
        
        # Split by comma but handle quoted values
        parts = []
        current_part = ""
        in_quotes = False
        
        for char in auth_header:
            if char == '"' and (not current_part or current_part[-1] != '\\'):
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                parts.append(current_part.strip())
                current_part = ""
                continue
            current_part += char
        
        if current_part.strip():
            parts.append(current_part.strip())
        
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"')
                auth_params[key] = value
        
        print(f"[AUTH] Parsed auth params: {auth_params}")
        return auth_params

    def generate_auth_response(self, method, uri, auth_params):
        """Generate Authorization header for digest authentication"""
        realm = auth_params.get('realm', '')
        nonce = auth_params.get('nonce', '')
        
        print(f"[AUTH] Generating auth for {method} {uri} with realm='{realm}', nonce='{nonce}'")
        
        # Calculate response
        ha1 = hashlib.md5(f"{self.sip_user}:{realm}:{self.sip_pass}".encode()).hexdigest()
        ha2 = hashlib.md5(f"{method}:{uri}".encode()).hexdigest()
        response = hashlib.md5(f"{ha1}:{nonce}:{ha2}".encode()).hexdigest()
        
        auth_header = f'Digest username="{self.sip_user}", realm="{realm}", nonce="{nonce}", uri="{uri}", response="{response}"'
        print(f"[AUTH] Generated auth header: {auth_header}")
        return auth_header

    def create_socket(self):
        """Create and bind SIP socket"""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Try to bind to a specific port range
        for port in range(50000, 60000):
            try:
                self.sock.bind((self.local_ip, port))
                print(f"[SOCKET] Bound to {self.local_ip}:{port}")
                return True
            except OSError:
                continue
        
        print("[SOCKET] Failed to bind to any port")
        return False

    def register(self):
        """Register with the SIP server first"""
        print("[SIP] Starting registration process...")
        
        # Test connectivity first
        if not self.test_connectivity():
            print("[SIP] Network connectivity test failed")
            return False
        
        if not self.create_socket():
            return False
        
        self.sock.settimeout(10.0)  # Increased timeout
        
        register_uri = f"sip:{self.sip_domain}"
        local_port = self.sock.getsockname()[1]
        
        # Generate new identifiers for registration
        self.call_id = f"{random.randint(100000, 999999)}@{self.local_ip}"
        self.tag = str(random.randint(10000, 99999))
        self.branch = f"z9hG4bK{random.randint(100000, 999999)}"
        
        register_msg = f"""REGISTER {register_uri} SIP/2.0
Via: SIP/2.0/UDP {self.local_ip}:{local_port};branch={self.branch}
Max-Forwards: 70
From: <sip:{self.sip_user}@{self.sip_domain}>;tag={self.tag}
To: <sip:{self.sip_user}@{self.sip_domain}>
Call-ID: {self.call_id}
CSeq: {self.cseq} REGISTER
Contact: <sip:{self.sip_user}@{self.local_ip}:{local_port}>
User-Agent: Python SIP Client
Expires: 3600
Content-Length: 0

"""
        
        print(f"[SIP] Sending REGISTER to {self.sip_proxy_ip}:{self.sip_port}")
        print(f"[SIP] REGISTER message:\n{register_msg}")
        
        try:
            self.sock.sendto(register_msg.replace('\n', '\r\n').encode(), (self.sip_proxy_ip, self.sip_port))
            print("[SIP] REGISTER sent successfully")
        except Exception as e:
            print(f"[SIP] Failed to send REGISTER: {e}")
            return False
        
        # Wait for response with multiple attempts
        for attempt in range(3):
            try:
                print(f"[SIP] Waiting for REGISTER response (attempt {attempt + 1}/3)...")
                data, addr = self.sock.recvfrom(4096)
                msg = data.decode(errors='ignore')
                first_line = msg.splitlines()[0]
                print(f"[SIP] Received from {addr}: {first_line}")
                print(f"[SIP] Full response:\n{msg}")
                
                if "401 Unauthorized" in first_line or "407 Proxy Authentication Required" in first_line:
                    # Extract authentication challenge
                    auth_pattern = r"(?:WWW-Authenticate|Proxy-Authenticate): (.+)"
                    www_auth = re.search(auth_pattern, msg, re.IGNORECASE)
                    if www_auth:
                        auth_params = self.parse_auth_header(www_auth.group(1))
                        auth_header = self.generate_auth_response("REGISTER", register_uri, auth_params)
                        
                        # Send authenticated REGISTER
                        self.cseq += 1
                        self.branch = f"z9hG4bK{random.randint(100000, 999999)}"
                        
                        auth_field = "Authorization" if "401" in first_line else "Proxy-Authorization"
                        
                        auth_register = f"""REGISTER {register_uri} SIP/2.0
Via: SIP/2.0/UDP {self.local_ip}:{local_port};branch={self.branch}
Max-Forwards: 70
From: <sip:{self.sip_user}@{self.sip_domain}>;tag={self.tag}
To: <sip:{self.sip_user}@{self.sip_domain}>
Call-ID: {self.call_id}
CSeq: {self.cseq} REGISTER
Contact: <sip:{self.sip_user}@{self.local_ip}:{local_port}>
{auth_field}: {auth_header}
User-Agent: Python SIP Client
Expires: 3600
Content-Length: 0

"""
                        print(f"[SIP] Sending authenticated REGISTER")
                        print(f"[SIP] Auth REGISTER message:\n{auth_register}")
                        
                        self.sock.sendto(auth_register.replace('\n', '\r\n').encode(), (self.sip_proxy_ip, self.sip_port))
                        print("[SIP] Authenticated REGISTER sent")
                        
                        # Wait for final response
                        try:
                            data, addr = self.sock.recvfrom(4096)
                            msg = data.decode(errors='ignore')
                            first_line = msg.splitlines()[0]
                            print(f"[SIP] Final register response from {addr}: {first_line}")
                            print(f"[SIP] Final response:\n{msg}")
                            
                            if "200 OK" in first_line:
                                self.registered = True
                                print("[SIP] Registration successful!")
                                return True
                            else:
                                print(f"[SIP] Registration failed: {first_line}")
                                return False
                        except socket.timeout:
                            print("[SIP] Timeout waiting for authenticated REGISTER response")
                            continue
                            
                elif "200 OK" in first_line:
                    self.registered = True
                    print("[SIP] Registration successful (no auth required)")
                    return True
                elif "403 Forbidden" in first_line:
                    print("[SIP] Registration forbidden - check credentials")
                    return False
                elif "404 Not Found" in first_line:
                    print("[SIP] Registration failed - user not found")
                    return False
                else:
                    print(f"[SIP] Unexpected response: {first_line}")
                    continue
                    
            except socket.timeout:
                print(f"[SIP] Registration timeout on attempt {attempt + 1}")
                continue
            except Exception as e:
                print(f"[SIP] Registration error on attempt {attempt + 1}: {e}")
                continue
        
        print("[SIP] Registration failed after all attempts")
        return False

    def start_call(self, target_number):
        self.target_number = target_number
        self.target_uri = f"sip:{target_number}@{self.sip_domain}"
        
        # First register if not already registered
        if not self.registered:
            if not self.register():
                print("[SIP] Registration failed, cannot make call")
                return False
        
        # Reset for new call
        self.cseq += 1
        self.branch = f"z9hG4bK{random.randint(100000, 999999)}"
        self.call_id = f"{random.randint(100000, 999999)}@{self.local_ip}"
        
        self.send_invite()
        threading.Thread(target=self.listen_sip, daemon=True).start()
        return True

    def send_invite(self):
        sdp_body = self.sdp()
        local_port = self.sock.getsockname()[1]
        
        invite = f"""INVITE {self.target_uri} SIP/2.0
Via: SIP/2.0/UDP {self.local_ip}:{local_port};branch={self.branch}
Max-Forwards: 70
From: <sip:{self.sip_user}@{self.sip_domain}>;tag={self.tag}
To: <{self.target_uri}>
Call-ID: {self.call_id}
CSeq: {self.cseq} INVITE
Contact: <sip:{self.sip_user}@{self.local_ip}:{local_port}>
User-Agent: Python SIP Client
Content-Type: application/sdp
Content-Length: {len(sdp_body)}

{sdp_body}"""
        
        print(f"[SIP] Sending INVITE to {self.target_uri}")
        print(f"[SIP] INVITE message:\n{invite}")
        
        try:
            self.sock.sendto(invite.replace('\n', '\r\n').encode(), (self.sip_proxy_ip, self.sip_port))
            print("[SIP] INVITE sent successfully")
        except Exception as e:
            print(f"[SIP] Failed to send INVITE: {e}")

    def send_ack(self):
        local_port = self.sock.getsockname()[1]
        
        ack = f"""ACK {self.target_uri} SIP/2.0
Via: SIP/2.0/UDP {self.local_ip}:{local_port};branch={self.branch}
From: <sip:{self.sip_user}@{self.sip_domain}>;tag={self.tag}
To: <{self.target_uri}>;tag={self.remote_tag}
Call-ID: {self.call_id}
CSeq: {self.cseq} ACK
Contact: <sip:{self.sip_user}@{self.local_ip}:{local_port}>
User-Agent: Python SIP Client
Content-Length: 0

"""
        try:
            self.sock.sendto(ack.replace('\n', '\r\n').encode(), (self.sip_proxy_ip, self.sip_port))
            print("[SIP] ACK sent successfully")
        except Exception as e:
            print(f"[SIP] Failed to send ACK: {e}")

    def send_bye(self):
        """Send BYE to terminate the call"""
        if not self.remote_tag:
            print("[SIP] Cannot send BYE - no remote tag")
            return
            
        self.cseq += 1
        local_port = self.sock.getsockname()[1]
        
        bye = f"""BYE {self.target_uri} SIP/2.0
Via: SIP/2.0/UDP {self.local_ip}:{local_port};branch={self.branch}
From: <sip:{self.sip_user}@{self.sip_domain}>;tag={self.tag}
To: <{self.target_uri}>;tag={self.remote_tag}
Call-ID: {self.call_id}
CSeq: {self.cseq} BYE
Contact: <sip:{self.sip_user}@{self.local_ip}:{local_port}>
User-Agent: Python SIP Client
Content-Length: 0

"""
        try:
            self.sock.sendto(bye.replace('\n', '\r\n').encode(), (self.sip_proxy_ip, self.sip_port))
            print("[SIP] BYE sent successfully")
        except Exception as e:
            print(f"[SIP] Failed to send BYE: {e}")

    def parse_sdp(self, sdp_body):
        """Parse SDP to extract remote RTP information"""
        lines = sdp_body.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('c=IN IP4 '):
                self.remote_rtp_ip = line.split(' ')[2]
            elif line.startswith('m=audio '):
                parts = line.split(' ')
                if len(parts) >= 2:
                    self.remote_rtp_port = int(parts[1])
        
        print(f"[SDP] Remote RTP: {self.remote_rtp_ip}:{self.remote_rtp_port}")

    def listen_sip(self):
        self.sock.settimeout(None)  # Remove timeout for listening
        print("[SIP] Starting SIP listener...")
        
        while True:
            try:
                data, addr = self.sock.recvfrom(4096)
                msg = data.decode(errors='ignore')
                first_line = msg.splitlines()[0]
                print(f"[SIP] Received from {addr}: {first_line}")

                if "100 Trying" in first_line:
                    print("[SIP] Call is being processed...")
                    continue

                elif "180 Ringing" in first_line:
                    print("[SIP] Phone is ringing...")
                    continue

                elif "200 OK" in first_line and "INVITE" in msg:
                    print("[SIP] Call answered!")
                    # Extract To tag
                    to_match = re.search(r"To: .*?;tag=([^;\s]+)", msg)
                    if to_match:
                        self.remote_tag = to_match.group(1)
                        print(f"[SIP] Remote tag: {self.remote_tag}")
                    
                    # Parse SDP if present
                    if "Content-Type: application/sdp" in msg:
                        sdp_start = msg.find('\r\n\r\n')
                        if sdp_start != -1:
                            sdp_body = msg[sdp_start + 4:]
                            self.parse_sdp(sdp_body)
                    
                    self.send_ack()
                    self.media_active = True
                    print("[SIP] Call established! Starting RTP...")
                    threading.Thread(target=self.rtp_stream, daemon=True).start()
                    continue

                elif "401 Unauthorized" in first_line or "407 Proxy Authentication Required" in first_line:
                    print("[SIP] Authentication required for INVITE")
                    # Handle authentication for INVITE
                    auth_pattern = r"(?:WWW-Authenticate|Proxy-Authenticate): (.+)"
                    www_auth = re.search(auth_pattern, msg, re.IGNORECASE)
                    if www_auth:
                        auth_params = self.parse_auth_header(www_auth.group(1))
                        auth_header = self.generate_auth_response("INVITE", self.target_uri, auth_params)
                        
                        # Resend INVITE with authentication
                        self.cseq += 1
                        self.branch = f"z9hG4bK{random.randint(100000, 999999)}"
                        
                        auth_field = "Authorization" if "401" in first_line else "Proxy-Authorization"
                        local_port = self.sock.getsockname()[1]
                        
                        sdp_body = self.sdp()
                        auth_invite = f"""INVITE {self.target_uri} SIP/2.0
Via: SIP/2.0/UDP {self.local_ip}:{local_port};branch={self.branch}
Max-Forwards: 70
From: <sip:{self.sip_user}@{self.sip_domain}>;tag={self.tag}
To: <{self.target_uri}>
Call-ID: {self.call_id}
CSeq: {self.cseq} INVITE
Contact: <sip:{self.sip_user}@{self.local_ip}:{local_port}>
{auth_field}: {auth_header}
User-Agent: Python SIP Client
Content-Type: application/sdp
Content-Length: {len(sdp_body)}

{sdp_body}"""
                        
                        print("[SIP] Sending authenticated INVITE")
                        self.sock.sendto(auth_invite.replace('\n', '\r\n').encode(), (self.sip_proxy_ip, self.sip_port))
                        print("[SIP] Authenticated INVITE sent")
                    continue

                elif any(code in first_line for code in ["486 Busy", "487 Request Terminated", "404 Not Found", "403 Forbidden"]):
                    print(f"[SIP] Call failed: {first_line}")
                    break

                elif "BYE" in first_line:
                    print("[SIP] Call terminated by remote party")
                    # Send 200 OK response to BYE
                    local_port = self.sock.getsockname()[1]
                    response = f"""SIP/2.0 200 OK
Via: SIP/2.0/UDP {self.local_ip}:{local_port}
From: <sip:{self.sip_user}@{self.sip_domain}>;tag={self.tag}
To: <{self.target_uri}>;tag={self.remote_tag}
Call-ID: {self.call_id}
CSeq: {self.cseq} BYE
Content-Length: 0

"""
                    self.sock.sendto(response.replace('\n', '\r\n').encode(), (self.sip_proxy_ip, self.sip_port))
                    self.media_active = False
                    break

            except Exception as e:
                print(f"[SIP] Error in listen_sip: {e}")
                break

    def rtp_stream(self):
        if not self.remote_rtp_ip or not self.remote_rtp_port:
            print("[RTP] No remote RTP info available")
            return
            
        try:
            p = pyaudio.PyAudio()
            stream_out = p.open(format=pyaudio.paInt16, channels=1, rate=8000, output=True, frames_per_buffer=160)
            stream_in = p.open(format=pyaudio.paInt16, channels=1, rate=8000, input=True, frames_per_buffer=160)
            
            rtp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            rtp_sock.bind((self.local_ip, self.rtp_port))
            rtp_sock.settimeout(1.0)
            
            print(f"[RTP] Started RTP stream to {self.remote_rtp_ip}:{self.remote_rtp_port}")

            def send_audio():
                seq = random.randint(1000, 9999)
                timestamp = random.randint(10000, 99999)
                ssrc = random.randint(100000, 999999)
                
                while self.media_active:
                    try:
                        data = stream_in.read(160, exception_on_overflow=False)
                        
                        # Create RTP header
                        rtp_header = bytearray([
                            0x80, 0x00,  # V=2, P=0, X=0, CC=0, M=0, PT=0 (PCMU)
                            (seq >> 8) & 0xFF, seq & 0xFF,
                            (timestamp >> 24) & 0xFF, (timestamp >> 16) & 0xFF,
                            (timestamp >> 8) & 0xFF, timestamp & 0xFF,
                            (ssrc >> 24) & 0xFF, (ssrc >> 16) & 0xFF,
                            (ssrc >> 8) & 0xFF, ssrc & 0xFF
                        ])
                        
                        # Convert audio data to mu-law (simplified)
                        audio_data = self.linear_to_mulaw(data)
                        
                        rtp_packet = rtp_header + audio_data
                        rtp_sock.sendto(rtp_packet, (self.remote_rtp_ip, self.remote_rtp_port))
                        
                        seq = (seq + 1) & 0xFFFF
                        timestamp = (timestamp + 160) & 0xFFFFFFFF
                        
                        time.sleep(0.02)  # 20ms intervals
                        
                    except Exception as e:
                        if self.media_active:
                            print(f"[RTP] Send error: {e}")
                        break

            def receive_audio():
                while self.media_active:
                    try:
                        packet, _ = rtp_sock.recvfrom(2048)
                        if len(packet) > 12:
                            payload = packet[12:]  # Skip RTP header
                            # Convert mu-law to linear (simplified)
                            audio_data = self.mulaw_to_linear(payload)
                            stream_out.write(audio_data)
                    except socket.timeout:
                        continue
                    except Exception as e:
                        if self.media_active:
                            print(f"[RTP] Receive error: {e}")
                        break

            threading.Thread(target=send_audio, daemon=True).start()
            threading.Thread(target=receive_audio, daemon=True).start()
            
        except Exception as e:
            print(f"[RTP] Stream setup error: {e}")

    def linear_to_mulaw(self, linear_data):
        """Simple linear to mu-law conversion (placeholder)"""
        # This is a simplified version - you might want to use a proper library
        return linear_data

    def mulaw_to_linear(self, mulaw_data):
        """Simple mu-law to linear conversion (placeholder)"""
        # This is a simplified version - you might want to use a proper library
        return mulaw_data

    def hangup(self):
        """Hang up the call"""
        if self.media_active:
            self.media_active = False
            self.send_bye()
            print("[SIP] Call terminated")

    def close(self):
        """Clean up resources"""
        self.media_active = False
        if self.sock:
            self.sock.close()