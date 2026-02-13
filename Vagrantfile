# -*- mode: ruby -*-
# vi: set ft=ruby :

def get_host_ip
  # This uses `route` to find the host's default IP address 
  # and pipes it through to `awk` and `ifconfig`  
  # to extract the IP address of the host machine.
  host_ip = `route -n get default | awk '/interface:/{print $2}' | xargs ifconfig | awk '/inet / {print $2}'`.strip

  return host_ip
end


Vagrant.configure(2) do |config|

  # Define host machine operating system variables
  # source: https://stackoverflow.com/questions/26811089/vagrant-how-to-have-host-platform-specific-provisioning-steps/26889312#26889312
  module OS
    def OS.windows?
      (/cygwin|mswin|mingw|bccwin|wince|emx/ =~ RUBY_PLATFORM) != nil
    end
    def OS.mac?
      (/darwin/ =~ RUBY_PLATFORM) != nil
    end
    def OS.unix?
      !OS.windows?
    end
    def OS.linux?
      OS.unix? and not OS.mac?
    end

  end

  if OS.mac?

    puts "- Mac OS detected"
    puts "  -- Provider: QEMU"
    
    # config.vm.box = "perk/ubuntu-2204-arm64"
    config.vm.box = "perk/ubuntu-24.04-arm64"

    config.vm.provider "qemu" do |qe|
      qe.memory = "4096" # 4GB
    end

    config.vm.network :forwarded_port, guest: 80, host: 8080  # nginx
    config.vm.network "forwarded_port", guest: 8000, host: 8000
    config.vm.network "forwarded_port", guest:5432, host:65432

    config.ssh.insert_key = true
    config.ssh.forward_agent = true

    # Automatically detect the SMB host IP
    smb_host_ip = get_host_ip

    config.vm.synced_folder "./", "/usr/local/apps/wcbluepages",
    type: "smb",
    smb_host: smb_host_ip,
    mount_options: ["sec=ntlmssp", "nounix", "noperm", "vers=3.0"]

  elsif OS.linux?

    # config.vm.box = "ubuntu/focal64"
    # config.vm.box = "ubuntu/jammy64"
    config.vm.box = "bento/ubuntu-24.04"
    # config.vm.box_check_update = true
    if Vagrant.has_plugin?("vagrant-vbguest")
      config.vbguest.auto_update = false
    end

    config.vm.network "forwarded_port", guest:8000, host:8000
    config.vm.network "forwarded_port", guest:80, host:8080
    config.vm.network "forwarded_port", guest:5432, host:65432

    config.ssh.insert_key = true
    config.ssh.forward_agent = true

    config.vm.synced_folder "./", "/usr/local/apps/wcbluepages"

  elsif OS.windows?

    puts "Windows OS detected"
    puts "Applying default Windows configuration"

    # Default synced folder setup for Windows
    smb_host_ip = "192.168.1.1" # Fallback IP for Windows

    config.vm.synced_folder "./", "/usr/local/apps/wcbluepages",
    type: "smb",
    smb_host: smb_host_ip,
    mount_options: ["sec=ntlmssp", "nounix", "noperm", "vers=3.0"]

    config.ssh.insert_key = true
    config.ssh.forward_agent = true
  else
    
    puts "Unknown OS detected"
    puts "Please add configuration to VagrantFile"

  end
      

end
