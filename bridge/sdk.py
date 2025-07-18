import socket
import time
import threading
import random
import logging
import hashlib
from datetime import datetime

class SIPClient:
    def __init__(self, username, password, server, port=5060):
        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.call_id = None
        self.cseq = 1
        self.tag = str(random.randint(1000, 9999))
        self.branch_prefix = "z9hG4bK"
        self.sock = None
        self.running = False
        self.auth_info = None  # Stores auth challenge info
        self.current_transactions = {}
        
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sip_client_auth.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Connect to the SIP server with error handling"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('0.0.0.0', 5060))
            self.sock.settimeout(1.0)
            self.running = True
            
            # Start receive thread
            threading.Thread(target=self._receive_thread, daemon=True).start()
            
            # Register with the server
            self.register()
            
            self.logger.info("Successfully connected to SIP server")
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            raise

    def register(self):
        """Send initial REGISTER message (without auth)"""
        branch = self._generate_branch()
        call_id = f"{random.randint(100000, 999999)}@{self.get_local_ip()}"
        
        msg = f"REGISTER sip:{self.server} SIP/2.0\r\n" \
              f"Via: SIP/2.0/UDP {self.get_local_ip()}:5060;branch={branch}\r\n" \
              f"Max-Forwards: 70\r\n" \
              f"From: <sip:{self.username}@{self.server}>;tag={self.tag}\r\n" \
              f"To: <sip:{self.username}@{self.server}>\r\n" \
              f"Call-ID: {call_id}\r\n" \
              f"CSeq: {self.cseq} REGISTER\r\n" \
              f"Contact: <sip:{self.username}@{self.get_local_ip()}:5060>\r\n" \
              f"Expires: 3600\r\n" \
              f"Content-Length: 0\r\n\r\n"
        
        self.current_transactions[call_id] = {
            'type': 'REGISTER',
            'start_time': datetime.now(),
            'branch': branch,
            'retries': 0
        }
        
        self._send_message(msg)
        self.cseq += 1

    def make_call(self, dest_number):
        """Initiate a call with authentication handling"""
        self.call_id = f"{random.randint(100000, 999999)}@{self.get_local_ip()}"
        branch = self._generate_branch()
        
        # First try without auth
        msg = f"INVITE sip:{dest_number}@{self.server} SIP/2.0\r\n" \
              f"Via: SIP/2.0/UDP {self.get_local_ip()}:5060;branch={branch}\r\n" \
              f"Max-Forwards: 70\r\n" \
              f"From: <sip:{self.username}@{self.server}>;tag={self.tag}\r\n" \
              f"To: <sip:{dest_number}@{self.server}>\r\n" \
              f"Call-ID: {self.call_id}\r\n" \
              f"CSeq: {self.cseq} INVITE\r\n" \
              f"Contact: <sip:{self.username}@{self.get_local_ip()}:5060>\r\n" \
              f"Content-Type: application/sdp\r\n" \
              f"Content-Length: 0\r\n\r\n"
        
        self.current_transactions[self.call_id] = {
            'type': 'INVITE',
            'start_time': datetime.now(),
            'branch': branch,
            'dest_number': dest_number,
            'retries': 0
        }
        
        self._send_message(msg)
        self.cseq += 1

    def _handle_401_unauthorized(self, message):
        """Handle 401 Unauthorized response"""
        lines = message.split('\r\n')
        www_auth = None
        
        # Parse WWW-Authenticate header
        for line in lines:
            if line.startswith("WWW-Authenticate:"):
                www_auth = line[len("WWW-Authenticate:"):].strip()
                break
        
        if not www_auth:
            self.logger.error("No WWW-Authenticate header in 401 response")
            return
        
        # Parse auth parameters
        auth_params = {}
        parts = www_auth.split(',')
        for part in parts:
            if '=' in part:
                key, val = part.split('=', 1)
                auth_params[key.strip()] = val.strip().strip('"')
        
        # Store auth info for later use
        self.auth_info = {
            'realm': auth_params.get('realm', ''),
            'nonce': auth_params.get('nonce', ''),
            'algorithm': auth_params.get('algorithm', 'MD5'),
            'qop': auth_params.get('qop', '')
        }
        
        # Get call-id from message to find the original transaction
        call_id = None
        for line in lines:
            if line.startswith("Call-ID:"):
                call_id = line[len("Call-ID:"):].strip()
                break
        
        if not call_id:
            self.logger.error("No Call-ID in 401 response")
            return
        
        # Retry the original request with auth
        if call_id in self.current_transactions:
            transaction = self.current_transactions[call_id]
            if transaction['type'] == 'INVITE':
                self._retry_invite_with_auth(transaction['dest_number'], call_id)
            elif transaction['type'] == 'REGISTER':
                self._retry_register_with_auth(call_id)

    def _calculate_auth_response(self, method, uri):
        """Calculate the SIP Digest authentication response"""
        if not self.auth_info:
            return None
            
        # HA1 = MD5(username:realm:password)
        ha1 = hashlib.md5(
            f"{self.username}:{self.auth_info['realm']}:{self.password}".encode()
        ).hexdigest()
        
        # HA2 = MD5(method:uri)
        ha2 = hashlib.md5(f"{method}:{uri}".encode()).hexdigest()
        
        # Response = MD5(HA1:nonce:HA2)
        response = hashlib.md5(
            f"{ha1}:{self.auth_info['nonce']}:{ha2}".encode()
        ).hexdigest()
        
        return response

    def _retry_invite_with_auth(self, dest_number, call_id):
        """Retry INVITE with authentication"""
        if not self.auth_info:
            self.logger.error("No auth info available for retry")
            return
            
        branch = self._generate_branch()
        uri = f"sip:{dest_number}@{self.server}"
        response = self._calculate_auth_response("INVITE", uri)
        
        if not response:
            self.logger.error("Failed to calculate auth response")
            return
        
        auth_header = f'Digest username="{self.username}", realm="{self.auth_info["realm"]}", ' \
                     f'nonce="{self.auth_info["nonce"]}", uri="{uri}", ' \
                     f'response="{response}", algorithm={self.auth_info["algorithm"]}'
        
        msg = f"INVITE {uri} SIP/2.0\r\n" \
              f"Via: SIP/2.0/UDP {self.get_local_ip()}:5060;branch={branch}\r\n" \
              f"Max-Forwards: 70\r\n" \
              f"From: <sip:{self.username}@{self.server}>;tag={self.tag}\r\n" \
              f"To: <sip:{dest_number}@{self.server}>\r\n" \
              f"Call-ID: {call_id}\r\n" \
              f"CSeq: {self.cseq} INVITE\r\n" \
              f"Contact: <sip:{self.username}@{self.get_local_ip()}:5060>\r\n" \
              f"Authorization: {auth_header}\r\n" \
              f"Content-Type: application/sdp\r\n" \
              f"Content-Length: 0\r\n\r\n"
        
        self.current_transactions[call_id] = {
            'type': 'INVITE',
            'start_time': datetime.now(),
            'branch': branch,
            'dest_number': dest_number,
            'retries': 1  # Mark as retry
        }
        
        self._send_message(msg)
        self.cseq += 1

    def _retry_register_with_auth(self, call_id):
        """Retry REGISTER with authentication"""
        if not self.auth_info:
            self.logger.error("No auth info available for retry")
            return
            
        branch = self._generate_branch()
        uri = f"sip:{self.server}"
        response = self._calculate_auth_response("REGISTER", uri)
        
        if not response:
            self.logger.error("Failed to calculate auth response")
            return
        
        auth_header = f'Digest username="{self.username}", realm="{self.auth_info["realm"]}", ' \
                     f'nonce="{self.auth_info["nonce"]}", uri="{uri}", ' \
                     f'response="{response}", algorithm={self.auth_info["algorithm"]}'
        
        msg = f"REGISTER {uri} SIP/2.0\r\n" \
              f"Via: SIP/2.0/UDP {self.get_local_ip()}:5060;branch={branch}\r\n" \
              f"Max-Forwards: 70\r\n" \
              f"From: <sip:{self.username}@{self.server}>;tag={self.tag}\r\n" \
              f"To: <sip:{self.username}@{self.server}>\r\n" \
              f"Call-ID: {call_id}\r\n" \
              f"CSeq: {self.cseq} REGISTER\r\n" \
              f"Contact: <sip:{self.username}@{self.get_local_ip()}:5060>\r\n" \
              f"Authorization: {auth_header}\r\n" \
              f"Expires: 3600\r\n" \
              f"Content-Length: 0\r\n\r\n"
        
        self.current_transactions[call_id] = {
            'type': 'REGISTER',
            'start_time': datetime.now(),
            'branch': branch,
            'retries': 1  # Mark as retry
        }
        
        self._send_message(msg)
        self.cseq += 1

    def _receive_thread(self):
        """Thread to handle incoming SIP messages"""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                message = data.decode()
                self.logger.debug(f"Received message:\n{message}")
                self._handle_message(message)
            except socket.timeout:
                self._handle_timeouts()
                continue
            except Exception as e:
                self.logger.error(f"Error receiving message: {str(e)}")
                time.sleep(1)

    def _handle_message(self, message):
        """Handle incoming SIP messages"""
        if not message:
            return
            
        first_line = message.split('\r\n')[0]
        
        if "SIP/2.0 401 Unauthorized" in first_line:
            self._handle_401_unauthorized(message)
        elif "SIP/2.0 200 OK" in first_line:
            self._handle_200_ok(message)
        elif "INVITE" in first_line:
            self._handle_incoming_invite(message)
        # Add handling for other response codes as needed

    def _handle_200_ok(self, message):
        """Handle successful responses"""
        lines = message.split('\r\n')
        call_id = None
        
        for line in lines:
            if line.startswith("Call-ID:"):
                call_id = line[len("Call-ID:"):].strip()
                break
        
        if call_id and call_id in self.current_transactions:
            transaction = self.current_transactions[call_id]
            self.logger.info(f"{transaction['type']} transaction succeeded")
            del self.current_transactions[call_id]  # Clean up completed transaction

    def _handle_incoming_invite(self, message):
        """Handle incoming call INVITE"""
        self.logger.info("Received incoming call INVITE")
        # Extract call details and notify application
        # You would typically answer with 180 Ringing and then 200 OK

    def _handle_timeouts(self):
        """Check for and handle timed out transactions"""
        now = datetime.now()
        timed_out = []
        
        for call_id, transaction in list(self.current_transactions.items()):
            elapsed = (now - transaction['start_time']).total_seconds()
            
            if elapsed > 30:  # 30 second timeout
                timed_out.append(call_id)
                self.logger.warning(f"Transaction timeout for {transaction['type']} {call_id}")
            elif elapsed > 2 and transaction['retries'] < 3:
                transaction['retries'] += 1
                self.logger.info(f"Retrying {transaction['type']} transaction (attempt {transaction['retries']})")
                
                if transaction['type'] == 'INVITE':
                    if self.auth_info:
                        self._retry_invite_with_auth(transaction['dest_number'], call_id)
                    else:
                        self.make_call(transaction['dest_number'])
                elif transaction['type'] == 'REGISTER':
                    if self.auth_info:
                        self._retry_register_with_auth(call_id)
                    else:
                        self.register()
        
        # Clean up timed out transactions
        for call_id in timed_out:
            del self.current_transactions[call_id]

    def _generate_branch(self):
        """Generate a unique branch ID"""
        return self.branch_prefix + str(random.randint(10000, 99999))

    def _send_message(self, message):
        """Send message with error handling"""
        try:
            self.sock.sendto(message.encode(), (self.server, self.port))
            self.logger.debug(f"Sent message:\n{message}")
        except Exception as e:
            self.logger.error(f"Failed to send message: {str(e)}")
            raise

    def get_local_ip(self):
        """Get local IP address"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def disconnect(self):
        """Cleanup and disconnect"""
        self.running = False
        if self.sock:
            self.sock.close()
        self.logger.info("Disconnected from SIP server")