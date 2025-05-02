#!/usr/bin/env python3
"""
Certificate Authority operations for TeddyCloudStarter.
"""
import os
import shutil
import time
import platform
import subprocess
import re
from pathlib import Path
from typing import Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()

class CertificateAuthority:
    """Handles Certificate Authority operations for TeddyCloudStarter."""
    
    def __init__(self, base_dir: str = None, translator=None):
        """
        Initialize the CertificateAuthority.
        
        Args:
            base_dir: The base directory for certificate operations. If None, use project path from config.
            translator: The translator instance for localization
        """
        # Store for later use
        self.base_dir_param = base_dir
        self.translator = translator
        
        # Don't try to resolve the actual base_dir yet, just store it for later
        if base_dir is not None:
            self.base_dir = Path(base_dir)
        else:
            # Will be resolved when needed
            self.base_dir = None
            
        # Don't set up these directories yet - they'll be set up when needed
        self.client_certs_dir = None
        self.ca_dir = None
        self.crl_dir = None
    
    def _ensure_directories(self):
        """Lazily initialize directories only when needed"""
        if self.client_certs_dir is not None:
            # Already initialized
            return
            
        # Now get the base directory
        if self.base_dir is None:
            # Try to get project path from config
            from ..config_manager import ConfigManager
            config_manager = ConfigManager()
            project_path = None
            try:
                if config_manager and config_manager.config:
                    project_path = config_manager.config.get("environment", {}).get("path")
            except Exception:
                pass
            
            if project_path:
                self.base_dir = Path(project_path)
            else:
                # Log an error if no project path is found
                console.print(f"[bold red]Warning: No project path found for certificate operations. Using current directory as fallback.[/]")
                self.base_dir = Path.cwd()
                if self.translator:
                    console.print(f"[yellow]{self.translator.get('Please set a project path to ensure certificates are stored in the correct location.')}[/]")
        
        # Set up directory paths
        self.client_certs_dir = self.base_dir / "data" / "client_certs"
        self.ca_dir = self.client_certs_dir / "ca"
        self.crl_dir = self.client_certs_dir / "crl"
        
        # Create the directories if they don't exist
        try:
            self.client_certs_dir.mkdir(parents=True, exist_ok=True)
            self.ca_dir.mkdir(parents=True, exist_ok=True)
            self.crl_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            console.print(f"[bold red]Error creating certificate directories: {e}[/]")
            # In case of error, try with absolute paths
            try:
                Path(str(self.client_certs_dir)).mkdir(parents=True, exist_ok=True)
                Path(str(self.ca_dir)).mkdir(parents=True, exist_ok=True)
                Path(str(self.crl_dir)).mkdir(parents=True, exist_ok=True)
            except Exception as e2:
                console.print(f"[bold red]Failed to create certificate directories: {e2}[/]")
    
    def _translate(self, text):
        """Helper method to translate text if translator is available."""
        if self.translator:
            return self.translator.get(text)
        return text
    
    def _check_openssl(self) -> bool:
        """
        Check if OpenSSL is available.
        
        Returns:
            bool: True if OpenSSL is available, False otherwise
        """
        try:
            subprocess.run(["openssl", "version"], check=True, capture_output=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            console.print(Panel(
                f"[bold red]{self._translate('OpenSSL is not available on your system.')}[/]\n\n"
                f"[bold yellow]{self._translate('Installation instructions:')}[/]\n"
                f"- [bold]{self._translate('Windows:')}[/] {self._translate('Download and install from https://slproweb.com/products/Win32OpenSSL.html')}\n"
                f"- [bold]{self._translate('macOS:')}[/] {self._translate('Use Homebrew: \'brew install openssl\'')}\n"
                f"- [bold]{self._translate('Linux (Debian/Ubuntu):')}[/] {self._translate('Run \'sudo apt install openssl\'')}\n"
                f"- [bold]{self._translate('Linux (Fedora/RHEL):')}[/] {self._translate('Run \'sudo dnf install openssl\'')}\n\n"
                f"{self._translate('After installing OpenSSL, restart the wizard or choose a different option.')}",
                box=box.ROUNDED,
                border_style="red"
            ))
            return False
    
    def create_ca_info_file(self) -> bool:
        """
        Create an info file in the CA directory with version information.
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Ensure directories are initialized
        self._ensure_directories()
        
        try:
            # Get OpenSSL version
            openssl_version = "Unknown"
            try:
                result = subprocess.run(
                    ["openssl", "version"],
                    capture_output=True, text=True, check=True
                )
                openssl_version = result.stdout.strip()
            except subprocess.SubprocessError:
                pass
            
            # Get current date and time
            current_datetime = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Get operating system info
            os_info = f"{platform.system()} {platform.release()}"                        
            from .. import __version__ as teddycloudstarter_version  # Dynamically fetch the version
            
            # Create the info file
            info_file = self.ca_dir / "ca_info.txt"
            with open(info_file, "w") as f:
                f.write(f"""# TeddyCloudStarter CA Certificate Information
# ======================================

Generated on: {current_datetime}
Operating System: {os_info}
OpenSSL Version: {openssl_version}
TeddyCloudStarter Version: {teddycloudstarter_version}

This Certificate Authority was generated by TeddyCloudStarter.
The CA is used to sign client certificates for secure access to TeddyCloud.

Files in this directory:
- ca.key: The Certificate Authority private key (KEEP SECURE!)
- ca.crt: The Certificate Authority public certificate
- ca_info.txt: This information file

For more information, visit: https://github.com/quentendo64/teddycloudstarter
""")
            
            return True
        except Exception as e:
            error_msg = f"Warning: Could not create CA info file: {e}"
            console.print(f"[bold yellow]{self._translate(error_msg)}[/]")
            return False
    
    def create_ca_certificate(self) -> Tuple[bool, str, str]:
        """
        Create a Certificate Authority certificate if it doesn't exist.
        
        Returns:
            Tuple[bool, str, str]: (success, certificate path, key path)
        """
        # Ensure directories exist
        self._ensure_directories()
        
        # Check if OpenSSL is available
        if not self._check_openssl():
            return False, "", ""
        
        # Check if CA already exists
        ca_key_path = self.ca_dir / "ca.key"
        ca_crt_path = self.ca_dir / "ca.crt"
        
        if ca_key_path.exists() and ca_crt_path.exists():
            return True, str(ca_crt_path), str(ca_key_path)
        
        # Generate CA certificate
        try:
            console.print(f"[bold cyan]{self._translate('Generating Certificate Authority...')}[/]")
            
            # Generate CA key and certificate
            subprocess.run([
                "openssl", "req", "-x509", "-newkey", "rsa:4096", "-nodes",
                "-keyout", str(ca_key_path),
                "-out", str(ca_crt_path),
                "-subj", "/CN=TeddyCloudStarterCA",
                "-days", "3650"
            ], check=True)
            
            # Create CA info file
            self.create_ca_info_file()
            
            # Setup the CA directory structure for certificate operations
            self._setup_ca_directory()
            
            console.print(f"[bold green]{self._translate('Certificate Authority created successfully!')}[/]")
            return True, str(ca_crt_path), str(ca_key_path)
            
        except subprocess.SubprocessError as e:
            error_msg = f"Error generating CA certificate: {e}"
            console.print(f"[bold red]{self._translate(error_msg)}[/]")
            return False, "", ""
        except Exception as e:
            error_msg = f"Error: {e}"
            console.print(f"[bold red]{self._translate(error_msg)}[/]")
            return False, "", ""
    
    def _setup_ca_directory(self) -> bool:
        """
        Set up the CA directory structure for certificate operations.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Initialize or update the certificate index file
            index_file = self.ca_dir / "index.txt"
            if not index_file.exists():
                # Create an empty index file
                with open(index_file, "w") as f:
                    pass
            
            # Create serial file if it doesn't exist
            serial_file = self.ca_dir / "serial"
            if not serial_file.exists():
                with open(serial_file, "w") as f:
                    f.write("01")
            
            # Create crlnumber file if it doesn't exist
            crlnumber_file = self.ca_dir / "crlnumber"
            if not crlnumber_file.exists():
                with open(crlnumber_file, "w") as f:
                    f.write("01")
            
            # Create OpenSSL config file for certificate operations
            openssl_conf_file = self.ca_dir / "openssl.cnf"
            if not openssl_conf_file.exists():
                # Get absolute paths for configuration
                ca_dir_abs = str(self.ca_dir.absolute())
                ca_crt_abs = str((self.ca_dir / "ca.crt").absolute())
                ca_key_abs = str((self.ca_dir / "ca.key").absolute())
                index_abs = str((self.ca_dir / "index.txt").absolute())
                serial_abs = str((self.ca_dir / "serial").absolute())
                newcerts_abs = str((self.ca_dir / "newcerts").absolute())
                crlnumber_abs = str((self.ca_dir / "crlnumber").absolute())
                
                # Create minimal OpenSSL configuration with absolute paths
                with open(openssl_conf_file, "w") as f:
                    f.write(f"""
[ ca ]
default_ca = TCS_default

[ TCS_default ]
dir               = {ca_dir_abs}
database         = {index_abs}
serial           = {serial_abs}
new_certs_dir    = {newcerts_abs}
certificate      = {ca_crt_abs}
private_key      = {ca_key_abs}
default_days     = 3650
default_crl_days = 30
default_md       = sha256
policy           = policy_any
crlnumber        = {crlnumber_abs}

[ policy_any ]
countryName            = optional
stateOrProvinceName    = optional
organizationName       = optional
organizationalUnitName = optional
commonName             = supplied
emailAddress           = optional

[ v3_ca ]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = critical,CA:true

[ crl_ext ]
authorityKeyIdentifier=keyid:always
""")
            
            return True
        except Exception as e:
            error_msg = f"Error setting up CA directory: {e}"
            console.print(f"[bold yellow]{self._translate(error_msg)}[/]")
            return False
    
    def generate_crl(self) -> Tuple[bool, str]:
        """
        Generate a Certificate Revocation List (CRL) from the CA.
        
        Returns:
            Tuple[bool, str]: (success, CRL path)
        """
        # Ensure directories are initialized
        self._ensure_directories()
        
        try:
            # Check if CA exists
            ca_key_path = self.ca_dir / "ca.key"
            ca_crt_path = self.ca_dir / "ca.crt"
            openssl_conf_path = self.ca_dir / "openssl.cnf"
            
            if not ca_key_path.exists() or not ca_crt_path.exists():
                console.print(f"[bold red]{self._translate('CA certificate or key not found. Cannot generate CRL.')}[/]")
                return False, ""
            
            # Create crl subfolder if it doesn't exist
            self.crl_dir.mkdir(exist_ok=True)
            
            # Generate CRL
            crl_path = self.crl_dir / "ca.crl"
            
            # Set up the CA directory structure if it doesn't exist
            self._setup_ca_directory()
            
            # Use absolute paths everywhere instead of changing directories
            subprocess.run([
                "openssl", "ca", 
                "-config", str(openssl_conf_path.absolute()),
                "-gencrl",
                "-keyfile", str(ca_key_path.absolute()),
                "-cert", str(ca_crt_path.absolute()),
                "-out", str(crl_path.absolute())
            ], check=True)
            
            if not crl_path.exists():
                return False, ""
                
            console.print(f"[bold green]{self._translate('CRL generated successfully')}[/]")
            return True, str(crl_path)
            
        except subprocess.SubprocessError as e:
            error_msg = f"Error generating CRL: {e}"
            console.print(f"[bold red]{self._translate(error_msg)}[/]")
            return False, ""
        except Exception as e:
            error_msg = f"Error: {e}"
            console.print(f"[bold red]{self._translate(error_msg)}[/]")
            return False, ""
    
    def validate_certificate(self, cert_path: str) -> Tuple[bool, str, Optional[dict]]:
        """
        Validate a certificate against the CA and extract its information.
        
        Args:
            cert_path: Path to the certificate to validate
            
        Returns:
            Tuple[bool, str, Optional[dict]]: (is_valid, error_message, certificate_info)
        """
        # Ensure directories are initialized
        self._ensure_directories()
        
        try:
            if not Path(cert_path).exists():
                return False, f"Certificate not found: {cert_path}", None
            
            # Verify certificate (check signature against CA)
            ca_crt_path = self.ca_dir / "ca.crt"
            if not ca_crt_path.exists():
                return False, "CA certificate not found", None
            
            # Verify the certificate signature
            verify_result = subprocess.run(
                ["openssl", "verify", "-CAfile", str(ca_crt_path), cert_path],
                capture_output=True, text=True
            )
            
            # Extract certificate information
            cert_info = {}
            
            # Get subject
            subject_result = subprocess.run(
                ["openssl", "x509", "-noout", "-subject", "-in", cert_path],
                capture_output=True, text=True, check=True
            )
            if subject_result.returncode == 0:
                cert_info['subject'] = subject_result.stdout.strip()
            
            # Get issuer
            issuer_result = subprocess.run(
                ["openssl", "x509", "-noout", "-issuer", "-in", cert_path],
                capture_output=True, text=True, check=True
            )
            if issuer_result.returncode == 0:
                cert_info['issuer'] = issuer_result.stdout.strip()
            
            # Get dates
            dates_result = subprocess.run(
                ["openssl", "x509", "-noout", "-dates", "-in", cert_path],
                capture_output=True, text=True, check=True
            )
            if dates_result.returncode == 0:
                dates = dates_result.stdout.strip().split('\n')
                for date in dates:
                    if date.startswith("notBefore="):
                        cert_info['not_before'] = date.replace("notBefore=", "")
                    elif date.startswith("notAfter="):
                        cert_info['not_after'] = date.replace("notAfter=", "")
            
            # Get serial
            serial_result = subprocess.run(
                ["openssl", "x509", "-noout", "-serial", "-in", cert_path],
                capture_output=True, text=True, check=True
            )
            if serial_result.returncode == 0:
                cert_info['serial'] = serial_result.stdout.strip().split('=')[1]
            
            if verify_result.returncode != 0:
                error_msg = f"Certificate verification failed: {verify_result.stderr.strip()}"
                return False, error_msg, cert_info
                
            return True, f"Certificate is valid until {cert_info.get('not_after', 'unknown')}", cert_info
            
        except subprocess.SubprocessError as e:
            error_msg = f"Error validating certificate: {e}"
            return False, error_msg, None
        except Exception as e:
            error_msg = f"Error: {e}"
            return False, error_msg, None
    
    def generate_self_signed_certificate(self, output_dir: str, domain_name: str, translator=None) -> Tuple[bool, str]:
        """
        Generate a self-signed certificate for a domain.
        
        Args:
            output_dir: Directory where certificate files will be saved
            domain_name: Domain name for the certificate
            translator: Optional translator for localization
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        # Ensure directories are initialized
        self._ensure_directories()
        
        # Use the provided translator or class translator
        trans = translator or self.translator
        
        try:
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Define paths for key and certificate
            key_path = os.path.join(output_dir, "server.key")
            crt_path = os.path.join(output_dir, "server.crt")
            
            # Check if OpenSSL is available
            if not self._check_openssl():
                return False, self._translate("OpenSSL is not available")
            
            console.print(f"[bold cyan]{self._translate('Generating self-signed certificate for')} {domain_name}...[/]")
            
            # Generate self-signed certificate with proper subject
            cmd = [
                "openssl", "req", "-x509", "-nodes",
                "-days", "3650",
                "-newkey", "rsa:2048",
                "-keyout", key_path,
                "-out", crt_path,
                "-subj", f"/CN={domain_name}"
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Check if files were created
            if not os.path.exists(key_path) or not os.path.exists(crt_path):
                return False, self._translate("Failed to create certificate files")
                
            msg = self._translate("Self-signed certificate created successfully")
            console.print(f"[bold green]{msg}[/]")
            return True, msg
            
        except subprocess.SubprocessError as e:
            error_msg = f"Error generating self-signed certificate: {e}"
            if translator:
                error_msg = translator.get("Error generating self-signed certificate: {error}").format(error=str(e))
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            if translator:
                error_msg = translator.get("Unexpected error: {error}").format(error=str(e))
            return False, error_msg