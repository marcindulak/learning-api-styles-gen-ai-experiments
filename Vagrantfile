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
    machine.vm.box = "almalinux/9"
    machine.vm.box_url = machine.vm.box
    # claude install is slow, due to large memory usage https://github.com/anthropics/claude-code/issues/12987
    config.vm.boot_timeout = 1800
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
    machine.vm.provision :shell, :inline => "fallocate -l 512M /swapfile"
    machine.vm.provision :shell, :inline => "dd if=/dev/zero of=/swapfile bs=1M count=512"
    machine.vm.provision :shell, :inline => "chmod 600 /swapfile"
    machine.vm.provision :shell, :inline => "mkswap /swapfile"
    machine.vm.provision :shell, :inline => "echo '/swapfile swap swap defaults 0 0' >> /etc/fstab"
    machine.vm.provision :shell, :inline => "swapon --show", run: "always"
    machine.vm.provision :shell, :inline => "dnf install -y epel-release"
    machine.vm.provision :shell, :inline => "dnf -y install --setopt=install_weak_deps=False curl dnf-plugins-core git podman podman-compose"
    machine.vm.provision :shell, :inline => "dnf -y install --setopt=install_weak_deps=False python-unversioned-command"
    machine.vm.provision :shell, :inline => "dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo"
    machine.vm.provision :shell, :inline => "dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin"
    machine.vm.provision :shell, :inline => "systemctl enable docker"
    machine.vm.provision :shell, :inline => "groupadd docker || true"
    machine.vm.provision :shell, :inline => "usermod -aG docker vagrant"
    machine.vm.provision :shell, :inline => "echo '[user]' > ~vagrant/.gitconfig"
    machine.vm.provision :shell, :inline => "echo 'email = marcindulak@users.noreply.github.com' >> ~vagrant/.gitconfig"
    machine.vm.provision :shell, :inline => "echo 'name = Marcin Dulak' >> ~vagrant/.gitconfig"
    machine.vm.provision :shell, :inline => "echo '[core]' >> ~vagrant/.gitconfig"
    machine.vm.provision :shell, :inline => "echo 'pager = cat' >> ~vagrant/.gitconfig"
    machine.vm.provision :shell, :inline => "echo 'export TERM=xterm-256color' >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo 'alias cp=\"cp -i\"' >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo 'alias mv=\"mv -i\"' >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo 'alias rm=\"rm -i\"' >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo 'export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1' >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo 'export DISABLE_AUTOUPDATER=1' >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo 'export CLAUDE_CODE_HIDE_ACCOUNT_INFO=1' >> ~vagrant/.bashrc"
    machine.vm.provision :shell, :inline => "echo 'export IS_DEMO=1' >> ~vagrant/.bashrc"
    # claude install is slow, due to large memory usage https://github.com/anthropics/claude-code/issues/12987
    # agent: Setting up Claude Code...
    # agent: ✘ Installation failed
    # agent: Download stalled: no data received for 60 seconds
    # agent: Try running with --force to override checks
    machine.vm.provision :shell, :inline => "cd /tmp && curl -sLO https://claude.ai/install.sh"
    machine.vm.provision :shell, :inline => "sed -i 's/ install / install --force /' /tmp/install.sh"
    machine.vm.provision :shell, :inline => "cat /tmp/install.sh | su - vagrant -c 'bash -s stable'"
    machine.vm.provision :shell, :inline => "su - vagrant -c 'claude --version'"
  end
end
