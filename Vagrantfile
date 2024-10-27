# -*- mode: ruby -*-
# vi: set ft=ruby :

IP_BASE="10.30.1.220"
OS = "debian"
# OS = "almalinux"

case OS
when "debian"
    box = "generic/debian12"
when "almalinux"
    box = "almalinux/8"
end

Vagrant.configure("2") do |config|
    config.vm.box = box
    config.vm.provider "vmware_workstation" do |ws|
        ws.gui = "true"
        ws.vmx['displayname'] = "ztd-#{OS}"
    end
    config.vm.hostname = "ztd"
    config.vm.define "ztd"
    config.vm.synced_folder ".", "/vagrant"
    config.vm.network "public_network", ip: IP_BASE
    config.vm.provision "shell", path: "provisioner-#{OS}.sh", args: [IP_BASE]
end