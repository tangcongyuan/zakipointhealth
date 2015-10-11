sudo hostname dis
sudo groupadd sftpAccess
sudo groupadd adminz
sudo yum -y update
sudo yum -y install vsftpd
sudo yum -y install openssh-server
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.orig
sudo vi /etc/ssh/sshd_config
sudo cp /etc/vsftpd/vsftpd.conf /etc/vsftpd/vsftpd.conf.orig
sudo vi /etc/vsftpd/vsftpd.conf
sudo systemctl restart sshd.service
sudo systemctl restart vsftpd.service

sudo useradd -m hsirx -g sftpAccess -s /sbin/nologin
sudo passwd hsirx
sudo chown root /home/hsirx
sudo chmod 750 /home/hsirx
sudo rm /home/hsirx/.bashrc /home/hsirx/.bash_profile /home/hsirx/.bash_logout
sudo mkdir /home/hsirx/filedir
sudo chown hsirx:sftpAccess /home/hsirx/filedir
