# -*- mode: ruby -*-
# vi: set ft=ruby :

# http://stackoverflow.com/questions/23926945/specify-headless-or-gui-from-command-line
def gui_enabled?
  !ENV.fetch('GUI', '').empty?
end

# Stderr: VBoxManage: error: VirtualBox can't operate in VMX root mode. Please disable the KVM kernel extension, recompile your kernel and reboot (VERR_VMX_IN_VMX_ROOT_MODE)
# lsmod | grep kvm
# sudo rmmod kvm_intel
# sudo modprobe kvm_intel

Vagrant.configure(2) do |config|
  config.vm.define "agent" do |machine|
    # machine.vm.box = "almalinux/10"
    # ...
    #     agent: SSH auth method: private key
    # Timed out while waiting for the machine to boot.
    # And the console started with GUI=1 vagrant up shows:
    # Fatal glibc error: CPU does not support x86_64-v3
    # Check your CPU features https://rfc.archlinux.page/0002-x86-64-v3-microarchitecture/
    # for f in AVX AVX2 BMI1 BMI2 F16C FMA LZCNT MOVBE XSAVE; do lscpu | sed -n 's/^Flags:[[:space:]]*//p' | tr ' ' '\n' | grep -iqx "$f" || echo "missing: $f"; done
    # If any flags are missing, even --cpu-profile host won't help
    # p.customize ["modifyvm", :id, "--cpu-profile", "host"]
    machine.vm.box = "almalinux/10-x86_64_v2"
    machine.vm.box_url = machine.vm.box
    config.vm.boot_timeout = 1800 # claude is slow to download and install
    machine.vm.provider "virtualbox" do |p|
      p.memory = 12288
      p.cpus = 1
      p.gui = gui_enabled?
      # https://superuser.com/questions/301464/fixing-a-guest-screen-resolution-in-virtualbox
      p.customize ["modifyvm", :id, "--clipboard", "bidirectional"]
      p.customize ["setextradata", :id, "GUI\/LastGuestSizeHint", "1920,1080"]
    end
  end
  config.vm.define "agent" do |machine|
    machine.vm.provision :shell, :inline => "hostnamectl set-hostname agent", run: "always"
    machine.vm.provision :shell, :inline => "fallocate -l 1G /swapfile"
    machine.vm.provision :shell, :inline => "dd if=/dev/zero of=/swapfile bs=1M count=2048"
    machine.vm.provision :shell, :inline => "chmod 600 /swapfile"
    machine.vm.provision :shell, :inline => "mkswap /swapfile"
    machine.vm.provision :shell, :inline => "echo '/swapfile swap swap defaults 0 0' >> /etc/fstab"
    machine.vm.provision :shell, :inline => "swapon --show", run: "always"
    machine.vm.provision :shell, :inline => "dnf install epel-release"
    machine.vm.provision :shell, :inline => "dnf -y install curl git podman podman-compose"
    machine.vm.provision :shell, :inline => "dnf -y install python-unversioned-command"
    machine.vm.provision :shell, :inline => "echo '[user]' > ~vagrant/.gitconfig"
    machine.vm.provision :shell, :inline => "echo 'email = marcindulak@users.noreply.github.com' >> ~vagrant/.gitconfig"
    machine.vm.provision :shell, :inline => "echo 'name = Marcin Dulak' >> ~vagrant/.gitconfig"
    machine.vm.provision :shell, :inline => "echo '[core]' > ~vagrant/.gitconfig"
    machine.vm.provision :shell, :inline => "echo 'pager = cat' >> ~vagrant/.gitconfig"
    machine.vm.provision :shell, :inline => "echo 'export TERM=xterm-256color' >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo PS1=\"'$ '\" >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo alias docker=podman >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo 'alias cp=\"cp -i\"' >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo 'alias mv=\"mv -i\"' >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo 'alias rm=\"rm -i\"' >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo 'export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1' >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo 'export DISABLE_AUTOUPDATER=1' >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo 'export CLAUDE_CODE_HIDE_ACCOUNT_INFO=1' >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo 'export IS_DEMO=1' >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "curl -fsSL https://claude.ai/install.sh | bash -s stable"
    machine.vm.provision :shell, :inline => "claude --version"
  end
end
