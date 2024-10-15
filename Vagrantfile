# -*- mode: ruby -*-
# vi: set ft=ruby :

IP_BASE="10.30.1.220"
IP_MASK=24

Vagrant.configure("2") do |config|
    config.vm.box = "generic/debian12"
    config.vm.provider "vmware_workstation" do |ws|
        ws.gui = "true"
        ws.vmx['displayname'] = "ztd"
    end
    config.vm.hostname = "ztd"
    config.vm.define "ztd"
    config.vm.synced_folder ".", "/vagrant"
    config.vm.network "public_network", ip: "#{IP_BASE}/#{IP_MASK}"
    config.vm.provision "shell", path: "provisioner.sh", args: [IP_BASE]
end
  