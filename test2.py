import paramiko
import time
import os # For ping functionality
from rich.console import Console
import matplotlib.pyplot as plt

# Switch configuration
switch_ip = "192.168.21.100"
switch_username = "admin"
switch_password = "123456"


# Function to send commands and retrieve output
def send_command(shell, command, wait_time=1):
    shell.send(command + '\n')
    time.sleep(wait_time)
    output = shell.recv(5000).decode('utf-8')
    return output

# Function to configure VLAN
def configure_vlan(shell, vlan_id):
    console.print(f"\n---- Configuring VLAN {vlan_id} ----", style="bold cyan")
    send_command(shell, 'conf t')
    send_command(shell, f'vlan {vlan_id}')
    send_command(shell, 'exit')
    console.print(f"VLAN {vlan_id} created successfully!", style="bold green")

# Function to show interface status
def show_interface_status(shell):
    console.print("\n---- Interface Status ----", style="bold yellow")
    interface_output = send_command(shell, 'do show interfaces status')
    console.print(interface_output, style="dim")

# Function to get bandwidth usage
def get_bandwidth_usage(shell):
    console.print("\n---- Bandwidth Usage ----", style="bold magenta")
    bandwidth_output = send_command(shell, 'show interfaces')
    lines = bandwidth_output.split('\n')
    total_bandwidth = 0
    for line in lines:
        if 'input rate' in line or 'output rate' in line:
            console.print(line.strip(), style="dim")
            rate = line.split()[3] # Assuming bandwidth rate is the 4th column in the output
            total_bandwidth += int(rate.replace(',', ''))
    return total_bandwidth

# Function to ping the device
def ping_device(ip):
    console.print("\n---- Pinging Device ----", style="bold blue")
    response = os.system(f"ping -c 3 {ip}" if os.name != 'nt' else f"ping -n 3 {ip}")
    if response == 0:
        console.print(f"Ping to {ip} successful!", style="bold green")
        return True
    else:
        console.print(f"Ping to {ip} failed!", style="bold red")
        return False

# Function to log the report to a file
def log_report(data, filename="monitoring_report.log"):
    with open(filename, "a") as file:
        file.write(data + "\n")

# Function to summarize the report
def summarize_report(ping_success, interfaces_up, bandwidth_usage):
    console.print("\n---- Summary Report ----", style="bold white")
    console.print(f"Ping Success: {ping_success}", style="bold green")
    console.print(f"Active Interfaces: {interfaces_up}", style="bold yellow")
    console.print(f"Total Bandwidth Usage: {bandwidth_usage} Kbps", style="bold magenta")

# Function to plot bandwidth usage
def plot_bandwidth(data):
    console.print("\n---- Plotting Bandwidth Usage ----", style="bold red")
    plt.plot(data, label="Bandwidth Usage")
    plt.xlabel("Time")
    plt.ylabel("Bandwidth (Kbps)")
    plt.title("Bandwidth Monitoring")
    plt.legend()
    plt.show()

# Function to monitor periodically
def periodic_monitoring(shell, ip, interval=30):
    bandwidth_data = [] # To store bandwidth data for plotting
    ping_success_count = 0
    total_bandwidth = 0
    while True:
        console.print("\n==== Monitoring Start ====", style="bold cyan")
        
        # Ping the device
        ping_success = ping_device(ip)
        if ping_success:
            ping_success_count += 1
        
        # Show interface status
        show_interface_status(shell)
        
        # Get bandwidth usage
        bandwidth_usage = get_bandwidth_usage(shell)
        total_bandwidth += bandwidth_usage
        bandwidth_data.append(bandwidth_usage)

        # Summarize the report
        summarize_report(ping_success_count, len(bandwidth_data), total_bandwidth)

        # Log the data
        log_report(f"Ping Success: {ping_success_count}, Bandwidth Usage: {bandwidth_usage} Kbps", filename="monitoring_report.log")

        # Plot the bandwidth usage
        if len(bandwidth_data) > 1: # To ensure at least two data points for plotting
            plot_bandwidth(bandwidth_data)

        console.print(f"\nWaiting {interval} seconds for next check...", style="bold white")
        time.sleep(interval)

# Set up SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
console = Console()

try:
    # Connect to the switch
    ssh.connect(switch_ip, username=switch_username, password=switch_password, look_for_keys=False)

    # Start an interactive shell session
    shell = ssh.invoke_shell()
    time.sleep(1) # Wait for shell initialization

    console.print("==== Connected to the Switch ====", style="bold green")
    
    # Configure VLAN
    configure_vlan(shell, vlan_id=200)
    
    # Start periodic monitoring
    periodic_monitoring(shell, switch_ip, interval=30)

finally:
    # Close SSH connection
    ssh.close()
    console.print("\n==== SSH Connection Closed ====", style="bold red")